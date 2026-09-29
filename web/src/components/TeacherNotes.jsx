import React,{useEffect,useState} from "react";
import {api} from "../api";

export default function TeacherNotes({ui}){
 const [roster,setRoster]=useState({classes:[],students:[]}),[rows,setRows]=useState([]),[student,setStudent]=useState(""),[unit,setUnit]=useState(""),[subject,setSubject]=useState(""),[note,setNote]=useState(""),[visibility,setVisibility]=useState("PRIVATE"),[err,setErr]=useState(""),[msg,setMsg]=useState("");
 const load=()=>Promise.all([api.get("/api/v1/teacher-roster"),api.get("/api/v1/teacher/notes")]).then(([r,n])=>{setRoster(r.data);setRows(n.data||[]);setErr("")}).catch(e=>setErr(e?.response?.data?.detail||"Unable to load teacher notes."));
 useEffect(()=>{load()},[]);
 const selected=roster.students.find(x=>String(x.student_user_id)===student);
 useEffect(()=>{if(selected?.classes?.length&&!selected.classes.some(x=>String(x.unit_id)===unit))setUnit(String(selected.classes[0].unit_id));},[student,roster]);
 async function save(){try{await api.post("/api/v1/teacher/notes",{student_user_id:Number(student),unit_id:unit?Number(unit):null,subject:subject.trim(),note:note.trim(),visibility});setSubject("");setNote("");setMsg("Teacher note saved.");load()}catch(e){setErr(e?.response?.data?.detail||"Unable to save teacher note.")}}
 return <div><section className="module-context"><div><span className="eyebrow">{ui.label} • Faculty</span><h1>Teacher Notes</h1><p>Create student-specific notes only for students enrolled in your assigned classes.</p></div></section>
 {err&&<div className="error">{err}</div>}{msg&&<div className="success">{msg}</div>}
 <div className="setup-grid"><section className="panel"><div className="panel-title"><b>New Student Note</b><span>Teacher scoped</span></div><div className="setup-form">
 <label>Student<select value={student} onChange={e=>setStudent(e.target.value)}><option value="">Select student</option>{roster.students.map(x=><option key={x.student_user_id} value={x.student_user_id}>{x.student_name}</option>)}</select></label>
 <label>Class / Course<select value={unit} onChange={e=>setUnit(e.target.value)} disabled={!selected}><option value="">Select class</option>{(selected?.classes||[]).map(x=><option key={x.unit_id} value={x.unit_id}>{x.name} ({x.code})</option>)}</select></label>
 <label>Subject<input value={subject} onChange={e=>setSubject(e.target.value)} /></label>
 <label>Visibility<select value={visibility} onChange={e=>setVisibility(e.target.value)}><option value="PRIVATE">Private</option><option value="STUDENT">Student</option><option value="GUARDIAN">Guardian</option></select></label>
 <label>Note<textarea value={note} onChange={e=>setNote(e.target.value)} /></label></div><button className="primary" disabled={!student||!unit||!subject.trim()||!note.trim()} onClick={save}>Save Note</button></section>
 <section className="panel structure-table"><div className="panel-title"><b>My Notes</b><span>{rows.length}</span></div><div className="table-scroll"><table><thead><tr><th>Student</th><th>Class</th><th>Subject</th><th>Visibility</th><th>Created</th></tr></thead><tbody>{rows.length?rows.map(x=><tr key={x.id}><td><b>{x.student_name}</b></td><td>{x.unit_name||"—"}</td><td>{x.subject}</td><td>{x.visibility}</td><td>{new Date(x.created_at).toLocaleString()}</td></tr>):<tr><td colSpan="5" className="empty-cell">No teacher notes created yet.</td></tr>}</tbody></table></div></section></div></div>
}