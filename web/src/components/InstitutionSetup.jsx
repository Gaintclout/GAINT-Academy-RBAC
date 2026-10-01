import React,{useState} from "react";
import {api} from "../api";

const STRUCTURE={
 SCHOOL:{academic:"Academic Year + Terms",unit:"Classes / Grades",leader:"Principal"},
 COLLEGE:{academic:"Academic Year + Semesters",unit:"Departments / Programs",leader:"Principal / Dean"},
 UNIVERSITY:{academic:"Academic Year + Semesters",unit:"Schools / Faculties / Programs",leader:"Vice Chancellor / Registrar"},
 TRAINING_INSTITUTE:{academic:"Batches + Cohorts",unit:"Programs / Courses",leader:"Director"}
};

export default function InstitutionSetup({user,onUpdated}){
 const current=user.institution||{};
 const [form,setForm]=useState({name:current.name||"",code:current.code||"",institution_type:current.institution_type||"UNIVERSITY"});
 const [saving,setSaving]=useState(false),[message,setMessage]=useState(""),[error,setError]=useState("");
 const meta=STRUCTURE[form.institution_type]||STRUCTURE.UNIVERSITY;
 const set=(k,v)=>setForm(x=>({...x,[k]:v}));
 async function save(){
  try{
   setSaving(true);setError("");setMessage("");
   const {data}=await api.put("/api/v1/institution",form);
   setMessage("Institution configuration saved.");
   onUpdated?.(data);
  }catch(e){setError(e?.response?.data?.detail||"Unable to save institution settings.");}
  finally{setSaving(false);}
 }
 return <div className="institution-setup">
  <section className="role-hero"><div><span className="eyebrow">GAINT Academy Setup</span><h1>Institution Setup</h1><p>Configure the institution identity and operating model used across the platform.</p></div><div className="hero-badge">{form.institution_type.replaceAll("_"," ")}</div></section>
  <div className="setup-grid">
   <section className="panel">
    <div className="panel-title"><b>Institution Identity</b><span>Tenant #{user.tenant_id}</span></div>
    <div className="setup-form">
     <label>Institution Name<input value={form.name} onChange={e=>set("name",e.target.value)} placeholder="Institution name"/></label>
     <label>Institution Code<input value={form.code} onChange={e=>set("code",e.target.value.toUpperCase())} placeholder="Example: GAINT-UNI"/></label>
     <label>Institution Type<select value={form.institution_type} onChange={e=>set("institution_type",e.target.value)}><option value="SCHOOL">School</option><option value="COLLEGE">College</option><option value="UNIVERSITY">University</option><option value="TRAINING_INSTITUTE">Training Institute</option></select></label>
    </div>
    {error&&<div className="error">{error}</div>}{message&&<div className="success-message">{message}</div>}
    <button className="primary" type="button" disabled={saving||!form.name.trim()||!form.code.trim()} onClick={save}>{saving?"Saving...":"Save Institution Setup"}</button>
   </section>
   <section className="panel setup-preview">
    <div className="panel-title"><b>Operating Model</b><span>Auto configured</span></div>
    <div className="setup-summary"><div><small>Academic Structure</small><strong>{meta.academic}</strong></div><div><small>Primary Units</small><strong>{meta.unit}</strong></div><div><small>Typical Leadership</small><strong>{meta.leader}</strong></div><div><small>UI Experience</small><strong>{form.institution_type.replaceAll("_"," ")} terminology</strong></div></div>
    <div className="readonly-note">Changing the institution type changes labels and experiences. Existing RBAC permissions remain enforced by the backend.</div>
   </section>
  </div>
 </div>
}
