import React,{useEffect,useState} from "react";
import {api} from "../api";

export default function StudentDashboard({ user, ui }) {
  const firstName = user?.name?.split(/\s+/)[0] || "Student";
  const [sessions,setSessions]=useState([]);
  const [attendance,setAttendance]=useState(null);
  const [work,setWork]=useState([]);
  const [fees,setFees]=useState([]);
  const [error,setError]=useState("");

  useEffect(()=>{
    Promise.all([
      api.get("/api/v1/class-sessions"),
      api.get("/api/v1/my-attendance"),
      api.get("/api/v1/academic-work"),
      api.get("/api/v1/fee-ledger")
    ]).then(([s,a,w,f])=>{
      setSessions(s.data||[]); setAttendance(a.data); setWork(w.data||[]); setFees(f.data||[]); setError("");
    }).catch(e=>setError(e?.response?.data?.detail||"Unable to load dashboard data."));
  },[]);

  const now=new Date();
  const upcomingSessions=sessions.filter(x=>new Date(x.starts_at)>=now).sort((a,b)=>new Date(a.starts_at)-new Date(b.starts_at)).slice(0,4);
  const submittableWork=work.filter(x=>["HOMEWORK","ASSIGNMENT"].includes(x.work_type));
  const pendingWork=submittableWork.filter(x=>(!x.submission||!["SUBMITTED","GRADED"].includes(x.submission.status))&&(!x.due_at||new Date(x.due_at)>=now)).length;
  const upcomingWork=work.filter(x=>x.due_at&&new Date(x.due_at)>=now).sort((a,b)=>new Date(a.due_at)-new Date(b.due_at)).slice(0,4);
  const balance=fees.reduce((sum,row)=>sum+Number(row.balance||0),0);
  const money=n=>"₹"+Number(n||0).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2});
  const cards=[
    ["Attendance",attendance?.percentage==null?"—":attendance.percentage+"%","Current marked attendance"],
    ["Pending Work",pendingWork,"Homework / assignments"],
    ["Upcoming Classes",upcomingSessions.length,"Next scheduled sessions"],
    ["Fee Balance",money(balance),"Outstanding assigned fees"]
  ];
  const timeline=upcomingSessions.length?upcomingSessions.map(x=>({
    key:"session-"+x.id,time:new Date(x.starts_at).toLocaleString(),title:x.title,meta:x.room||"Room not assigned"
  })):upcomingWork.map(x=>({
    key:"work-"+x.id,time:new Date(x.due_at).toLocaleString(),title:x.title,meta:x.work_type
  }));

  return <div className={"institution-dashboard institution-"+ui.label.toLowerCase()}>
    <section className="student-hero"><div><span className="eyebrow">{ui.label} Student</span><h1>{ui.dashboard.greeting}, {firstName}! 👋</h1><p>{ui.dashboard.subtitle}</p></div><div className="hero-badge">{ui.label}</div></section>
    {error&&<div className="error">{error}</div>}
    <div className="student-kpis">{cards.map(([label,value,hint])=><article className="student-kpi" key={label}><small>{label}</small><strong>{value}</strong><span>{hint}</span></article>)}</div>
    <div className="student-grid">
      <section className="panel"><div className="panel-title"><b>Upcoming Academic Activity</b><span>{timeline.length}</span></div>
        <div className="timeline-list">{timeline.length?timeline.map(x=><div className="timeline-row" key={x.key}><span>{x.time}</span><b>{x.title}</b><small>{x.meta}</small></div>):<div className="empty-cell">No upcoming classes or deadlines.</div>}</div>
      </section>
      <section className="panel"><div className="panel-title"><b>My Academic Snapshot</b><span>Live</span></div>
        <div className="timeline-list">
          <div className="timeline-row"><span>Attendance</span><b>{attendance?.attended||0} attended</b><small>{attendance?.absent||0} absent · {attendance?.late||0} late</small></div>
          <div className="timeline-row"><span>Work</span><b>{work.length} published</b><small>{pendingWork} actionable homework / assignments</small></div>
          <div className="timeline-row"><span>Fees</span><b>{money(balance)}</b><small>Outstanding balance</small></div>
        </div>
      </section>
    </div>
  </div>;
}
