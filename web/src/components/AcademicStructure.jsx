import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";

const LABELS={
 School:[["CAMPUS","Campus"],["SCHOOL_FACULTY","School / Wing"],["DEPARTMENT","Department"],["PROGRAM","Grade / Program"],["ACADEMIC_PERIOD","Academic Year / Term"],["COURSE","Subject"],["SECTION_BATCH","Class / Section"]],
 College:[["CAMPUS","Campus"],["SCHOOL_FACULTY","School / Faculty"],["DEPARTMENT","Department"],["PROGRAM","Program"],["ACADEMIC_PERIOD","Academic Year / Semester"],["COURSE","Course"],["SECTION_BATCH","Section / Batch"]],
 University:[["CAMPUS","Campus"],["SCHOOL_FACULTY","School / Faculty"],["DEPARTMENT","Department"],["PROGRAM","Degree Program"],["ACADEMIC_PERIOD","Academic Year / Semester"],["COURSE","Course"],["SECTION_BATCH","Cohort / Section"]],
 "Training Institute":[["CAMPUS","Center"],["SCHOOL_FACULTY","Division"],["DEPARTMENT","Department"],["PROGRAM","Program"],["ACADEMIC_PERIOD","Cohort Period"],["COURSE","Course"],["SECTION_BATCH","Batch"]]
};

export default function AcademicStructure({ui}){
 const labels=LABELS[ui.label]||LABELS.University;
 const [rows,setRows]=useState([]),[type,setType]=useState(labels[0][0]),[name,setName]=useState(""),[code,setCode]=useState(""),[parent,setParent]=useState(""),[msg,setMsg]=useState(""),[err,setErr]=useState("");
 const load=()=>api.get("/api/v1/academic-structure").then(r=>setRows(r.data)).catch(e=>setErr(e?.response?.data?.detail||"Unable to load academic structure."));
 useEffect(()=>{load()},[]);
 const parents=useMemo(()=>rows.filter(r=>r.id!==Number(parent)),[rows,parent]);
 async function add(){try{setErr("");setMsg("");await api.post("/api/v1/academic-structure",{unit_type:type,name,code,parent_id:parent?Number(parent):null,campus_id:1,status:"Active"});setName("");setCode("");setParent("");setMsg("Academic unit added.");load()}catch(e){setErr(e?.response?.data?.detail||"Unable to add academic unit.")}}
 async function remove(id){if(!window.confirm("Delete this academic unit?"))return;try{await api.delete("/api/v1/academic-structure/"+id);setMsg("Academic unit deleted.");load()}catch(e){setErr(e?.response?.data?.detail||"Unable to delete academic unit.")}}
 const labelFor=t=>labels.find(x=>x[0]===t)?.[1]||t;
 return <div>
  <section className="role-hero"><div><span className="eyebrow">{ui.label} Configuration</span><h1>Academic Structure</h1><p>Build the hierarchy used for academics, enrollment and reporting.</p></div><div className="hero-badge">{rows.length} Units</div></section>
  <div className="setup-grid">
   <section className="panel"><div className="panel-title"><b>Add Academic Unit</b><span>Institution Admin</span></div>
    <div className="setup-form">
     <label>Unit Type<select value={type} onChange={e=>setType(e.target.value)}>{labels.map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label>
     <label>Name<input value={name} onChange={e=>setName(e.target.value)} placeholder={"Enter "+labelFor(type)+" name"}/></label>
     <label>Code<input value={code} onChange={e=>setCode(e.target.value.toUpperCase())} placeholder="Unique academic code"/></label>
     <label>Parent Unit<select value={parent} onChange={e=>setParent(e.target.value)}><option value="">No parent / top level</option>{parents.map(r=><option value={r.id} key={r.id}>{labelFor(r.unit_type)} — {r.name}</option>)}</select></label>
    </div>
    {err&&<div className="error">{err}</div>}{msg&&<div className="success-message">{msg}</div>}
    <button className="primary" disabled={!name.trim()||!code.trim()} onClick={add}>Add Unit</button>
   </section>
   <section className="panel"><div className="panel-title"><b>Recommended Hierarchy</b><span>{ui.label}</span></div>
    <div className="structure-flow">{labels.map(([,l],i)=><React.Fragment key={l}><span>{l}</span>{i<labels.length-1&&<b>↓</b>}</React.Fragment>)}</div>
   </section>
  </div>
  <section className="panel structure-table"><div className="panel-title"><b>Configured Structure</b><span>{rows.length} records</span></div>
   <div className="table-scroll"><table><thead><tr><th>Type</th><th>Name</th><th>Code</th><th>Parent</th><th>Status</th><th>Action</th></tr></thead><tbody>
   {rows.length===0?<tr><td colSpan="6" className="empty-cell">No academic structure configured yet.</td></tr>:rows.map(r=><tr key={r.id}><td>{labelFor(r.unit_type)}</td><td><b>{r.name}</b></td><td>{r.code}</td><td>{rows.find(x=>x.id===r.parent_id)?.name||"—"}</td><td>{r.status}</td><td><button className="table-action danger" onClick={()=>remove(r.id)}>Delete</button></td></tr>)}
   </tbody></table></div>
  </section>
 </div>
}
