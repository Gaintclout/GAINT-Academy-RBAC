import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";

function csvCell(value){const s=String(value??"");return '"'+s.replaceAll('"','""')+'"'}
function downloadCsv(report,rows){
  const header=["Report","Category","Description","Records","Status","Generated"];
  const values=rows.map(x=>[x.name,x.category,x.description,x.records,x.status,x.generated_at]);
  const csv=[header,...values].map(row=>row.map(csvCell).join(",")).join("\n");
  const blob=new Blob([csv],{type:"text/csv;charset=utf-8"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download=report||"gaint-academy-auditor-reports.csv";a.click();URL.revokeObjectURL(url);
}
export default function AuditorExportReports({ui}){
  const[data,setData]=useState(null),[error,setError]=useState(""),[query,setQuery]=useState("");
  useEffect(()=>{api.get("/api/v1/auditor/export-reports").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load export reports."))},[]);
  const rows=useMemo(()=>{if(!data)return[];const q=query.trim().toLowerCase();return data.reports.filter(x=>!q||[x.name,x.category,x.description,x.status].some(v=>String(v||"").toLowerCase().includes(q)))},[data,query]);
  const exportOne=x=>downloadCsv("gaint-academy-"+x.key+".csv",[x]);
  return <div>
    <section className="module-context"><div><span className="eyebrow">{ui.label} • Auditor • Export Only</span><h1>Export Reports</h1><p>Prepare read-only audit, compliance, exception, evidence and access summaries from the current institution scope.</p></div></section>
    {error&&<div className="error">{error}</div>}
    {data&&<>
      <div className="module-kpis"><article><small>Reports</small><strong>{data.summary.reports}</strong></article><article><small>Ready</small><strong>{data.summary.ready}</strong></article><article><small>Audit Events</small><strong>{data.summary.audit_events}</strong></article><article><small>Exceptions</small><strong>{data.summary.exceptions}</strong></article></div>
      <section className="panel structure-table">
        <div className="panel-title"><b>Report Centre</b><span>CSV export • tenant scoped</span></div>
        <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search report..." /><button type="button" onClick={()=>downloadCsv("gaint-academy-auditor-report-index.csv",rows)} disabled={!rows.length}>Export visible reports</button></div>
        <div className="table-scroll"><table><thead><tr><th>Report</th><th>Category</th><th>Description</th><th>Records</th><th>Status</th><th>Generated</th><th>Action</th></tr></thead><tbody>
          {rows.length?rows.map(x=><tr key={x.key}><td><b>{x.name}</b></td><td>{x.category}</td><td>{x.description}</td><td>{x.records}</td><td><b>{x.status}</b></td><td>{new Date(x.generated_at).toLocaleString()}</td><td><button type="button" onClick={()=>exportOne(x)}>Export CSV</button></td></tr>):<tr><td colSpan="7" className="empty-cell">No reports match this search.</td></tr>}
        </tbody></table></div>
      </section>
    </>}
  </div>
}
