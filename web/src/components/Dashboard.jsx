import React,{useEffect,useState} from "react";
import {api} from "../api";

export default function Dashboard({user}){
  const [data,setData]=useState(null);
  useEffect(()=>{api.get("/api/v1/dashboard").then(r=>setData(r.data))},[user.role]);
  if(!data) return <div>Loading dashboard...</div>;

  return <>
    <div className="page-title">
      <div><h1>{data.title}</h1><p>Role-specific workspace for {user.role}.</p></div>
      <button className="primary">+ Quick Action</button>
    </div>
    <div className="cards">
      {data.cards.map(c=><div className="kpi" key={c.label}><small>{c.label}</small><strong>{c.value}</strong><span>{c.hint}</span></div>)}
    </div>
    <div className="dashboard-grid">
      <section className="panel chart-panel">
        <div className="panel-title"><b>Activity Trend</b><span>Last 7 days</span></div>
        <div className="bars">{[55,72,63,87,68,91,83,95,79,90,85,97].map((h,i)=><div key={i} style={{height:`${h}%`}} />)}</div>
      </section>
      <section className="panel">
        <div className="panel-title"><b>Quick Actions</b></div>
        <div className="actions">
          {data.quick_actions.map(a=><button key={a}>＋ {a}<span>›</span></button>)}
        </div>
      </section>
      <section className="panel">
        <div className="panel-title"><b>Recent Activity</b></div>
        <div className="activity">
          {["Attendance updated","Fee receipt generated","Semester results published","Transport sync completed"].map((x,i)=><div key={x}><span className="dot">{String.fromCharCode(65+i)}</span><div><b>{x}</b><small>{i*14+2} min ago</small></div></div>)}
        </div>
      </section>
      <section className="panel insight">
        <b>✦ GAINT AI Insight</b>
        <p>AI adapter is ready. Connect your approved provider for role-safe institutional insights.</p>
        <button className="purple">Open Assistant</button>
      </section>
    </div>
  </>
}
