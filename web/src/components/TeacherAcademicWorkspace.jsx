import React,{useEffect,useState} from "react";
import {api} from "../api";

const MODULE_MAP={"My Classes":"Courses","My Students":"Courses",Timetable:"Timetable",Attendance:"Attendance",Homework:"Homework",Assignments:"Assignments",Exams:"Exams",Results:"Results"};

export default function TeacherAcademicWorkspace({title,ui}){
 const module=MODULE_MAP[title]||title;
 const [units,setUnits]=useState([]);
 const [rows,setRows]=useState([]);
 const [error,setError]=useState("");

 useEffect(()=>{
  Promise.all([
   api.get("/api/v1/my-academics"),
   api.get("/api/v1/academic-activities",{params:{module}})
  ]).then(([u,a])=>{setUnits(u.data);setRows(a.data);setError("")})
    .catch(e=>setError(e?.response?.data?.detail||"Unable to load assigned academics."));
 },[module]);

 return <div>
  <section className="module-context">
   <div><span className="eyebrow">{ui.label} • Faculty</span><h1>{title}</h1><p>This workspace is restricted to courses and sections assigned to this faculty account.</p></div>
   <div className="hero-badge">{units.length} Assigned</div>
  </section>
  {error&&<div className="error">{error}</div>}
  <section className="panel">
   <div className="panel-title"><b>My Academic Scope</b><span>Assignment driven</span></div>
   <div className="structure-flow">{units.length?units.map(x=><span key={x.assignment_id}>{x.name} · {x.unit_type.replaceAll("_"," ")}</span>):<span>No course or section assignments yet</span>}</div>
  </section>
  <section className="panel structure-table">
   <div className="panel-title"><b>{title}</b><span>{rows.length} scoped records</span></div>
   <div className="table-scroll"><table><thead><tr><th>Title</th><th>Code</th><th>Category</th><th>Status</th><th>Details</th></tr></thead><tbody>
    {rows.length?rows.map(r=><tr key={r.id}><td><b>{r.name}</b></td><td>{r.code||"—"}</td><td>{r.category}</td><td>{r.status}</td><td>{r.notes||"—"}</td></tr>):<tr><td colSpan="5" className="empty-cell">No records in your assigned academic scope.</td></tr>}
   </tbody></table></div>
  </section>
 </div>
}
