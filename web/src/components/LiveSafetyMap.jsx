import React,{useEffect,useState} from "react";
import {api} from "../api";
export default function LiveSafetyMap(){
  const [rows,setRows]=useState([]);
  const [error,setError]=useState("");
  useEffect(()=>{api.get("/api/v1/admin/live-locations").then(r=>setRows(r.data)).catch(e=>setError(e?.response?.data?.detail||e.message))},[]);
  return <>
    <div className="page-title"><div><h1>Live Safety Map</h1><p>Authorized campus/transport monitoring.</p></div></div>
    {error && <div className="error">{error}</div>}
    <section className="panel">
      <div className="map-placeholder large">AUTHORIZED LIVE LOCATION MAP</div>
      <table><thead><tr><th>Student</th><th>Status</th><th>Context</th><th>Latitude</th><th>Longitude</th></tr></thead>
      <tbody>{rows.map(x=><tr key={x.student_id}><td>{x.name}</td><td>{x.status}</td><td>{x.tracking_context}</td><td>{x.latitude}</td><td>{x.longitude}</td></tr>)}</tbody></table>
    </section>
  </>
}
