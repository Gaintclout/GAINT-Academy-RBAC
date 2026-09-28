import React,{useEffect,useState} from "react";
import {api} from "../api";

export default function TeacherAcademicWorkspace({title,ui}){
 const [data,setData]=useState({classes:[],students:[]}),[error,setError]=useState("");
 useEffect(()=>{api.get("/api/v1/teacher-roster").then(r=>{setData(r.data);setError("")}).catch(e=>setError(e?.response?.data?.detail||"Unable to load faculty roster."))},[]);
 const rows=title==="My Students"?data.students:data.classes;
 return <div>
  <section className="module-context"><div><span className="eyebrow">{ui.label} • Faculty</span><h1>{title}</h1><p>Live faculty assignments and enrolled students from the academic structure.</p></div><div className="hero-badge">{rows.length} {title==="My Students"?"Students":"Classes"}</div></section>
  {error&&<div className="error">{error}</div>}
  {title==="My Classes"?<section className="panel structure-table"><div className="panel-title"><b>Assigned Classes</b><span>{data.classes.length} active assignments</span></div><div className="table-scroll"><table><thead><tr><th>Class / Course</th><th>Code</th><th>Type</th><th>Assignment</th><th>Students</th></tr></thead><tbody>{data.classes.length?data.classes.map(r=><tr key={r.assignment_id}><td><b>{r.name}</b></td><td>{r.code}</td><td>{r.unit_type.replaceAll("_"," ")}</td><td>{r.assignment_type.replaceAll("_"," ")}</td><td>{r.student_count}</td></tr>):<tr><td colSpan="5" className="empty-cell">No course or section assignments yet.</td></tr>}</tbody></table></div></section>
  :<section className="panel structure-table"><div className="panel-title"><b>My Students</b><span>{data.students.length} unique enrolled students</span></div><div className="table-scroll"><table><thead><tr><th>Student</th><th>Assigned Classes</th><th>Class Count</th></tr></thead><tbody>{data.students.length?data.students.map(r=><tr key={r.student_user_id}><td><b>{r.student_name}</b></td><td>{r.classes.map(x=>x.name+" ("+x.code+")").join(", ")}</td><td>{r.classes.length}</td></tr>):<tr><td colSpan="3" className="empty-cell">No enrolled students found in your assigned classes.</td></tr>}</tbody></table></div></section>}
 </div>
}
