import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";

const cell=v=>'"'+String(v??"").replaceAll('"','""')+'"';
function saveCsv(name,rows){const header=["Report","Category","Records","Details"];const csv=[header,...rows.map(x=>[x.name,x.category,x.records,x.detail])].map(r=>r.map(cell).join(",")).join("\n");const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));const a=document.createElement("a");a.href=url;a.download=name;a.click();URL.revokeObjectURL(url)}
export default function AdminReports({ui}){
 const[data,setData]=useState(null),[error,setError]=useState(""),[query,setQuery]=useState("");
 useEffect(()=>{api.get("/api/v1/admin/reports").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load institution reports."))},[]);
 const rows=useMemo(()=>{if(!data)return[];const q=query.trim().toLowerCase();return data.reports.filter(x=>!q||[x.name,x.category,x.detail].some(v=>String(v).toLowerCase().includes(q)))},[data,query]);
 return <div>
  <section className="module-context"><div><span className="eyebrow">{ui.label} • Institution Admin</span><h1>Institution Reports</h1><p>Cross-module reporting for academics, administration, finance, operations and governance.</p></div></section>
  {error&&<div className="error">{error}</div>}
  {data&&<>
   <div className="module-kpis"><article><small>Students</small><strong>{data.summary.students}</strong></article><article><small>Staff</small><strong>{data.summary.staff}</strong></article><article><small>Academic Units</small><strong>{data.summary.academic_units}</strong></article><article><small>Fee Collection</small><strong>₹{Number(data.summary.fee_collection).toLocaleString()}</strong></article><article><small>Open Grievances</small><strong>{data.summary.open_grievances}</strong></article></div>
   <section className="panel structure-table"><div className="panel-title"><b>Report Centre</b><span>Institution-wide • tenant scoped</span></div>
    <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search reports..." /><button type="button" disabled={!rows.length} onClick={()=>saveCsv("gaint-academy-institution-reports.csv",rows)}>Export visible reports</button></div>
    <div className="table-scroll"><table><thead><tr><th>Report</th><th>Category</th><th>Records</th><th>Details</th><th>Export</th></tr></thead><tbody>{rows.length?rows.map(x=><tr key={x.key}><td><b>{x.name}</b></td><td>{x.category}</td><td>{x.records}</td><td>{x.detail}</td><td><button type="button" onClick={()=>saveCsv("gaint-academy-"+x.key+"-report.csv",[x])}>CSV</button></td></tr>):<tr><td colSpan="5" className="empty-cell">No reports match this search.</td></tr>}</tbody></table></div>
   </section>
  </>}
 </div>
}
