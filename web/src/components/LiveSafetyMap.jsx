import React,{useEffect,useMemo,useState} from "react";
import {GoogleMap,MarkerF,useJsApiLoader} from "@react-google-maps/api";
import {api} from "../api";

const mapContainerStyle={width:"100%",height:"460px"};
const defaultCenter={lat:17.385,lng:78.4867};

export default function LiveSafetyMap(){
  const [rows,setRows]=useState([]),[vehicles,setVehicles]=useState([]),[vehicleId,setVehicleId]=useState(""),[error,setError]=useState(""),[message,setMessage]=useState(""),[updating,setUpdating]=useState(false),[loading,setLoading]=useState(false);
  const {isLoaded,loadError}=useJsApiLoader({googleMapsApiKey:import.meta.env.VITE_GOOGLE_MAPS_API_KEY||""});

  async function load(){
    try{
      setLoading(true);setError("");
      const [locations,transport]=await Promise.all([api.get("/api/v1/campus/live-locations"),api.get("/api/v1/campus/transport")]);
      setRows(locations.data||[]);
      const active=(transport.data?.vehicles||[]).filter(x=>x.status==="Active");
      setVehicles(active);
      setVehicleId(current=>current||(active.length?String(active[0].id):""));
    }catch(e){setError(e?.response?.data?.detail||e.message)}
    finally{setLoading(false)}
  }

  useEffect(()=>{load();const timer=setInterval(load,15000);return()=>clearInterval(timer)},[]);

  const validRows=useMemo(()=>rows.filter(x=>Number.isFinite(Number(x.latitude))&&Number.isFinite(Number(x.longitude))),[rows]);
  const mapCenter=validRows.length?{lat:Number(validRows[0].latitude),lng:Number(validRows[0].longitude)}:defaultCenter;

  function publishDeviceLocation(){
    if(!vehicleId){setError("Select an active school bus / vehicle first.");return}
    if(!navigator.geolocation){setError("This browser does not support GPS location.");return}
    setUpdating(true);setError("");setMessage("");
    navigator.geolocation.getCurrentPosition(async pos=>{
      try{
        const {latitude,longitude,accuracy}=pos.coords;
        const {data}=await api.post("/api/v1/campus/transport/location",{vehicle_id:Number(vehicleId),latitude,longitude,accuracy:accuracy||0});
        setMessage(`Live bus location updated for ${data.updated_students} allocated student(s).`);
        await load();
      }catch(e){setError(e?.response?.data?.detail||e.message||"Unable to publish bus location.")}
      finally{setUpdating(false)}
    },err=>{setError(err.message||"Location permission was denied.");setUpdating(false)},{enableHighAccuracy:true,timeout:15000,maximumAge:0});
  }

  return <>
    <div className="page-title"><div><h1>Live Safety Map</h1><p>Authorized campus/transport monitoring. Locations refresh automatically every 15 seconds.</p></div><button className="secondary" type="button" onClick={load} disabled={loading}>{loading?"Refreshing...":"Refresh Locations"}</button></div>
    {error&&<div className="error">{error}</div>}
    {message&&<div className="success">{message}</div>}
    <section className="panel">
      <div className="panel-title"><b>School Bus / Vehicle GPS</b><span>Campus Admin only</span></div>
      <div className="form-grid">
        <label>Bus / Vehicle<select value={vehicleId} onChange={e=>setVehicleId(e.target.value)}><option value="">Select vehicle</option>{vehicles.map(v=><option key={v.id} value={v.id}>{v.vehicle_number}{v.label?` — ${v.label}`:""}</option>)}</select></label>
        <div><button type="button" onClick={publishDeviceLocation} disabled={updating||!vehicleId}>{updating?"Updating GPS...":"Use This Device GPS for Bus"}</button></div>
      </div>
      <div className="readonly-note">For UAT, this securely publishes this device's current GPS as the selected bus location to students actively allocated to that vehicle. A production vehicle GPS/telematics device can use the protected transport location workflow through an approved integration.</div>
    </section>
    <section className="panel">
      <div className="panel-title"><b>Authorized Live Location Monitor</b><span>{validRows.length} live location{validRows.length===1?"":"s"}</span></div>
      {loadError?<div className="error">Google Maps could not be loaded. Check the Maps JavaScript API configuration.</div>:!isLoaded?<div className="map-placeholder large">Loading Google Map...</div>:validRows.length===0?<div className="map-placeholder large">No live campus locations available yet.</div>:
        <div className="google-map-wrapper"><GoogleMap mapContainerStyle={mapContainerStyle} center={mapCenter} zoom={15} options={{streetViewControl:false,mapTypeControl:false,fullscreenControl:true,zoomControl:true}}>
          {validRows.map(x=><MarkerF key={x.student_id} position={{lat:Number(x.latitude),lng:Number(x.longitude)}} title={`${x.name} — ${x.tracking_context||"Location"}`} />)}
        </GoogleMap></div>}
      <div className="table-scroll"><table><thead><tr><th>Student</th><th>Status</th><th>Context</th><th>Source</th><th>Latitude</th><th>Longitude</th><th>Updated</th></tr></thead>
      <tbody>{rows.length?rows.map(x=><tr key={x.student_id}><td>{x.name}</td><td>{x.status}</td><td>{x.tracking_context}</td><td>{x.source||"—"}</td><td>{x.latitude}</td><td>{x.longitude}</td><td>{x.recorded_at?new Date(x.recorded_at).toLocaleString():"—"}</td></tr>):<tr><td colSpan="7">No live campus locations available yet.</td></tr>}</tbody></table></div>
    </section>
  </>
}