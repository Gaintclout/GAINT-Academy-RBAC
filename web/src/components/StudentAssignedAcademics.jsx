import React,{useEffect,useState} from "react";
import {api} from "../api";

export default function StudentAssignedAcademics({title,ui}){
 const [units,setUnits]=useState([]);
 const [rows,setRows]=useState([]);
 const [error,setError]=useState("");
 const module=title==="Courses"?"Courses":title;

 useEffect(()=>{
  api.get("/api/v1/my-academics")
    .then((u)=>{setUnits(u.data||[]);setRows((u.data||[]).filter(x=>x.unit_type==="COURSE"));setError("")})
    .catch(e=>setError(e?.response?.data?.detail||"Unable to load your academics."));
 },[module]);

 return <div>
  <div className="page-title"><div><span className="eyebrow">{ui.label} Student</span><h1>{title}</h1><p>Information shown here comes only from your active enrollment and course assignments.</p></div></div>
  {error&&<div className="error">{error}</div>}
  <div className="module-kpis">
   <article><small>Academic Links</small><strong>{units.length}</strong></article>
   <article><small>Courses / Sections</small><strong>{units.filter(x=>["COURSE","SECTION_BATCH"].includes(x.unit_type)).length}</strong></article>
   <article><small>Assigned Courses</small><strong>{rows.length}</strong></article>
   <article><small>Scope</small><strong>My Enrollment</strong></article>
  </div>
  <section className="panel">
   <div className="panel-title"><b>My Assigned Academic Structure</b><span>Current</span></div>
   <div className="structure-flow">{units.length?units.map(x=><span key={x.assignment_id}>{x.name} · {x.assignment_type.replaceAll("_"," ")}</span>):<span>No enrollment or course assignments yet.</span>}</div>
  </section>
  <section className="panel structure-table">
   <div className="panel-title"><b>{title}</b><span>{rows.length} records</span></div>
   <div className="table-scroll"><table><thead><tr><th>Course Code</th><th>Course / Subject</th><th>Assignment</th><th>Status</th></tr></thead><tbody>
    {rows.length?rows.map(r=><tr key={r.assignment_id}><td><b>{r.code||"—"}</b></td><td>{r.name}</td><td>{r.assignment_type.replaceAll("_"," ")}</td><td>{r.status}</td></tr>):<tr><td colSpan="4" className="empty-cell">No courses are assigned to your enrollment.</td></tr>}
   </tbody></table></div>
  </section>
 </div>
}
