import React,{useEffect,useState} from "react";
import {api} from "../api";
export default function StudentSafety(){
  const [loc,setLoc]=useState(null),[error,setError]=useState("");
  useEffect(()=>{api.get("/api/v1/location/me").then(r=>setLoc(r.data)).catch(e=>setError(e?.response?.data?.detail||e.message))},[]);
  return <><div className="page-title"><div><h1>My Safety</h1><p>Your own approved safety/location status.</p></div></div>
  {error&&<div className="error">{error}</div>}<section className="panel"><h3>Location Sharing</h3>
  <p><b>Status:</b> {loc?.available?loc.status:"Unavailable"}</p>{loc?.available&&<><p><b>Context:</b> {loc.tracking_context}</p><p><b>Location:</b> {loc.latitude}, {loc.longitude}</p></>}
  <div className="readonly-note">Use the mobile app to send real GPS updates with permission.</div></section></>
}
