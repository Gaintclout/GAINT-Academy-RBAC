import React,{useEffect,useState} from "react";
import {api} from "../api";
export default function Audit(){
  const [rows,setRows]=useState([]);
  useEffect(()=>{api.get("/api/v1/audit").then(r=>setRows(r.data))},[]);
  return <>
    <div className="page-title"><div><h1>Audit Trail</h1><p>Privileged and safety-sensitive access history.</p></div></div>
    <section className="panel">
      <table><thead><tr><th>Actor</th><th>Action</th><th>Resource</th><th>Details</th><th>Time</th></tr></thead>
      <tbody>{rows.map(x=><tr key={x.id}><td>{x.actor}</td><td>{x.action}</td><td>{x.resource}</td><td>{x.details}</td><td>{String(x.created_at)}</td></tr>)}</tbody></table>
    </section>
  </>
}
