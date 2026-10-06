import React,{useEffect,useState} from "react";
import {api} from "../api";

const ROLE_COPY = {
  "Institution Admin": {School:["School Administration","Manage students, teachers, classes, fees and school operations."],College:["College Administration","Manage departments, programs, semesters, faculty and campus operations."],University:["University Administration","Manage schools, faculties, programs, research and university operations."]},
  Teacher:{School:["Teacher Workspace","Classes, homework, attendance and student progress."],College:["Faculty Workspace","Courses, assignments, attendance and semester assessments."],University:["Faculty & Research Workspace","Teaching, assessments, advisees and research activities."]},
  "Parent / Guardian":{School:["Parent Dashboard","Your child's school day, homework, fees, bus and safety."],College:["Guardian Overview","Academic progress, fees and important student updates."],University:["Sponsor / Guardian Overview","Authorized academic, finance and student support information."]},
  Accounts:{School:["School Finance","Fee collection, receipts, concessions and reconciliation."],College:["College Finance","Semester fees, scholarships, refunds and reconciliation."],University:["University Finance","Student accounts, program charges, aid, sponsors and financial reporting."]},
  HR:{School:["School HR","Teachers, non-teaching staff, leave and recruitment."],College:["College HR","Faculty, staff, departments, leave and recruitment."],University:["University HR","Faculty and staff lifecycle, appointments, performance and workforce reporting."]},
  "Campus Admin":{School:["School Operations","Campus attendance, buses, visitors, assets and student safety."],College:["Campus Operations","Facilities, transport, visitors, inventory and campus safety."],University:["University Campus Operations","Multi-facility operations, services, assets and campus safety."]},
  Auditor:{School:["Audit & Compliance","Review school controls, evidence, exceptions and audit activity."],College:["Audit & Compliance","Review academic, finance and campus controls with read-only access."],University:["Governance, Audit & Compliance","Review institutional controls, evidence, exceptions and audit trails."]}
};

export default function InstitutionRoleDashboard({user,ui}){
  const copy=ROLE_COPY[user.role]?.[ui.label] || [user.role+" Dashboard",ui.label+" workspace"];
  const [teacher,setTeacher]=useState(null),[error,setError]=useState("");
  useEffect(()=>{
    if(user.role!=="Teacher") return;
    Promise.all([api.get("/api/v1/teacher-roster"),api.get("/api/v1/class-sessions"),api.get("/api/v1/academic-work")])
      .then(([r,s,w])=>{setTeacher({roster:r.data,sessions:s.data||[],work:w.data||[]});setError("")})
      .catch(e=>setError(e?.response?.data?.detail||"Unable to load teacher dashboard."));
  },[user.role]);
  if(user.role==="Teacher"){
    const now=new Date(), roster=teacher?.roster||{classes:[],students:[]}, sessions=teacher?.sessions||[], work=teacher?.work||[];
    const upcoming=sessions.filter(x=>new Date(x.starts_at)>=now).sort((a,b)=>new Date(a.starts_at)-new Date(b.starts_at)).slice(0,5);
    const grading=work.filter(x=>["HOMEWORK","ASSIGNMENT","EXAM"].includes(x.work_type)).length;
    const cards=[["Assigned Classes",roster.classes.length],["My Students",roster.students.length],["Scheduled Sessions",sessions.length],["Published Academic Work",grading]];
    return <div className={"role-dashboard role-"+ui.label.toLowerCase()}>
      <section className="role-hero"><div><span className="eyebrow">{ui.label} • Teacher</span><h1>{copy[0]}</h1><p>{copy[1]}</p></div><div className="hero-badge">{ui.label}</div></section>
      {error&&<div className="error">{error}</div>}
      <div className="module-kpis">{cards.map(([l,v])=><article key={l}><small>{l}</small><strong>{v}</strong></article>)}</div>
      <div className="student-grid"><section className="panel"><div className="panel-title"><b>Upcoming Classes</b><span>{upcoming.length}</span></div><div className="timeline-list">{upcoming.length?upcoming.map(x=><div className="timeline-row" key={x.id}><span>{new Date(x.starts_at).toLocaleString()}</span><b>{x.unit_name||x.title}</b><small>{x.room||"Room not assigned"}</small></div>):<div className="empty-cell">No upcoming classes scheduled.</div>}</div></section>
      <section className="panel"><div className="panel-title"><b>Teaching Scope</b><span>Live</span></div><div className="timeline-list">{roster.classes.length?roster.classes.slice(0,5).map(x=><div className="timeline-row" key={x.assignment_id}><span>{x.code||"—"}</span><b>{x.name}</b><small>{x.student_count} students</small></div>):<div className="empty-cell">No active teaching assignments.</div>}</div></section></div>
    </div>;
  }
  return <div className={"role-dashboard role-"+ui.label.toLowerCase()}><section className="role-hero"><div><span className="eyebrow">{ui.label} • {user.role}</span><h1>{copy[0]}</h1><p>{copy[1]}</p></div><div className="hero-badge">{ui.label}</div></section><section className="panel"><div className="panel-title"><b>{ui.label} Workspace</b><span>{user.role}</span></div><p>Role-specific operational data will appear here as its dedicated workflow is connected.</p></section></div>;
}
