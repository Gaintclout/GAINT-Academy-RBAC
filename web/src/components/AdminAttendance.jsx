import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";
export default function AdminAttendance({ui}){
 const[data,setData]=useState(null),[error,setError]=useState(""),[query,setQuery]=useState(""),[status,setStatus]=useState("ALL");
 useEffect(()=>{api.get("/api/v1/admin/attendance-overview").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load attendance."))},[]);
 const rows=useMemo(()=>{if(!data)return[];const q=query.trim().toLowerCase();return data.entries.filter(x=>(status==="ALL"||x.status===status)&&(!q||[x.student_name,x.session_title,x.unit_name,x.note].some(v=>String(v||"").toLowerCase().includes(q))))},[data,query,status]);
 return <div>
  <section className="module-context"><div><span className="eyebrow">{ui.label} • Institution Admin</span><h1>Attendance</h1><p>Institution-wide student attendance oversight based on faculty-marked class sessions.</p></div></section>
  {error&&<div className="error">{error}</div>}
  {data&&<>
   <div className="module-kpis"><article><small>Attendance Records</small><strong>{data.summary.records}</strong></article><article><small>Present</small><strong>{data.summary.present}</strong></article><article><small>Absent</small><strong>{data.summary.absent}</strong></article><article><small>Late</small><strong>{data.summary.late}</strong></article><article><small>Excused</small><strong>{data.summary.excused}</strong></article><article><small>Attendance Rate</small><strong>{data.summary.attendance_percentage==null?"—":data.summary.attendance_percentage+"%"}</strong></article></div>
   <section className="panel structure-table"><div className="panel-title"><b>Attendance Register</b><span>{rows.length} visible records</span></div>
    <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search student, session or academic unit..." /><select value={status} onChange={e=>setStatus(e.target.value)}><option value="ALL">All statuses</option>{["PRESENT","ABSENT","LATE","EXCUSED"].map(x=><option key={x}>{x}</option>)}</select></div>
    <div className="table-scroll"><table><thead><tr><th>Student</th><th>Academic Unit</th><th>Session</th><th>Status</th><th>Note</th><th>Marked</th></tr></thead><tbody>{rows.length?rows.map(x=><tr key={x.id}><td><b>{x.student_name}</b></td><td>{x.unit_name}</td><td>{x.session_title}</td><td><b>{x.status}</b></td><td>{x.note||"—"}</td><td>{new Date(x.marked_at).toLocaleString()}</td></tr>):<tr><td colSpan="6" className="empty-cell">No attendance records match these filters.</td></tr>}</tbody></table></div>
   </section>
  </>}
 </div>
}
