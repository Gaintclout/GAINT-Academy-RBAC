import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";
export default function AdminTimetable({ui}){
 const[data,setData]=useState(null),[error,setError]=useState(""),[query,setQuery]=useState(""),[scope,setScope]=useState("ALL");
 const load=()=>api.get("/api/v1/admin/timetable").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load timetable."));
 useEffect(()=>{load()},[]);
 const rows=useMemo(()=>{if(!data)return[];const now=new Date();const q=query.trim().toLowerCase();return data.sessions.filter(x=>(scope==="ALL"||(scope==="UPCOMING"&&new Date(x.ends_at)>=now)||(scope==="PAST"&&new Date(x.ends_at)<now))&&(!q||[x.title,x.unit_name,x.teacher_name,x.room,x.status].some(v=>String(v||"").toLowerCase().includes(q))))},[data,query,scope]);
 return <div>
  <section className="module-context"><div><span className="eyebrow">{ui.label} • Institution Admin</span><h1>Timetable</h1><p>Institution-wide class schedule visibility across academic units, faculty and rooms.</p></div></section>
  {error&&<div className="error">{error}</div>}
  {data&&<>
   <div className="module-kpis"><article><small>Total Sessions</small><strong>{data.summary.total}</strong></article><article><small>Upcoming</small><strong>{data.summary.upcoming}</strong></article><article><small>Teachers Scheduled</small><strong>{data.summary.teachers}</strong></article><article><small>Academic Units</small><strong>{data.summary.academic_units}</strong></article><article><small>Rooms in Use</small><strong>{data.summary.rooms}</strong></article></div>
   <section className="panel structure-table"><div className="panel-title"><b>Institution Timetable</b><span>{rows.length} visible sessions</span></div>
    <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search session, faculty, course or room..." /><select value={scope} onChange={e=>setScope(e.target.value)}><option value="ALL">All sessions</option><option value="UPCOMING">Upcoming</option><option value="PAST">Past</option></select></div>
    <div className="table-scroll"><table><thead><tr><th>Session</th><th>Academic Unit</th><th>Faculty</th><th>Starts</th><th>Ends</th><th>Room</th><th>Status</th></tr></thead><tbody>{rows.length?rows.map(x=><tr key={x.id}><td><b>{x.title}</b></td><td>{x.unit_name}<br/><small>{String(x.unit_type||"").replaceAll("_"," ")}</small></td><td>{x.teacher_name}</td><td>{new Date(x.starts_at).toLocaleString()}</td><td>{new Date(x.ends_at).toLocaleString()}</td><td>{x.room||"TBA"}</td><td>{x.status}</td></tr>):<tr><td colSpan="7" className="empty-cell">No timetable sessions match these filters.</td></tr>}</tbody></table></div>
   </section>
  </>}
 </div>
}
