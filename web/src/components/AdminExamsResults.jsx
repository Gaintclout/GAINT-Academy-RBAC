import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";
export default function AdminExamsResults({ui}){
 const[data,setData]=useState(null),[error,setError]=useState(""),[query,setQuery]=useState(""),[status,setStatus]=useState("ALL");
 useEffect(()=>{api.get("/api/v1/admin/exams-results").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load exams and results."))},[]);
 const rows=useMemo(()=>{if(!data)return[];const q=query.trim().toLowerCase();return data.exams.filter(x=>(status==="ALL"||x.status===status)&&(!q||[x.title,x.unit_name,x.teacher_name,x.status].some(v=>String(v||"").toLowerCase().includes(q))))},[data,query,status]);
 return <div>
  <section className="module-context"><div><span className="eyebrow">{ui.label} • Institution Admin</span><h1>Exams & Results</h1><p>Institution-wide oversight of exams, result entry, publication status and academic outcomes.</p></div></section>
  {error&&<div className="error">{error}</div>}
  {data&&<>
   <div className="module-kpis"><article><small>Exams</small><strong>{data.summary.exams}</strong></article><article><small>Result Records</small><strong>{data.summary.results}</strong></article><article><small>Published</small><strong>{data.summary.published}</strong></article><article><small>Draft</small><strong>{data.summary.draft}</strong></article><article><small>Pass Rate</small><strong>{data.summary.pass_rate==null?"—":data.summary.pass_rate+"%"}</strong></article></div>
   <section className="panel structure-table"><div className="panel-title"><b>Exam Register</b><span>{rows.length} visible exams</span></div>
    <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search exam, course or faculty..." /><select value={status} onChange={e=>setStatus(e.target.value)}><option value="ALL">All statuses</option><option value="AWAITING RESULTS">Awaiting Results</option><option value="DRAFT">Draft</option><option value="PUBLISHED">Published</option></select></div>
    <div className="table-scroll"><table><thead><tr><th>Exam</th><th>Course</th><th>Faculty</th><th>Max Marks</th><th>Results</th><th>Pass / Fail</th><th>Average</th><th>Publication</th></tr></thead><tbody>{rows.length?rows.map(x=><tr key={x.id}><td><b>{x.title}</b>{x.due_at&&<><br/><small>{new Date(x.due_at).toLocaleString()}</small></>}</td><td>{x.unit_name}</td><td>{x.teacher_name}</td><td>{x.max_marks}</td><td>{x.results}</td><td>{x.passed} / {x.failed}</td><td>{x.average_percentage==null?"—":x.average_percentage+"%"}</td><td><b>{x.status}</b>{x.results>0&&<><br/><small>{x.published}/{x.results} published</small></>}</td></tr>):<tr><td colSpan="8" className="empty-cell">No exams match these filters.</td></tr>}</tbody></table></div>
   </section>
  </>}
 </div>
}
