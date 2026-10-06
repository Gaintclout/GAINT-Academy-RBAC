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
export default function AuditorExportReports({ui}){ const terms=ui.label==="School"?{title:"School Audit Export Reports",desc:"Prepare read-only audit, compliance, exception, evidence and access summaries for the current school scope.",reports:"School Reports",centre:"School Audit Report Centre",scope:"CSV export • school tenant scoped",search:"Search school report...",file:"gaint-academy-school-auditor-report-index.csv",empty:"No school reports match this search."}:ui.label==="College"?{title:"College Audit Export Reports",desc:"Prepare read-only audit, compliance, exception, evidence and access summaries for the current college scope.",reports:"College Reports",centre:"College Audit Report Centre",scope:"CSV export • college tenant scoped",search:"Search college report...",file:"gaint-academy-college-auditor-report-index.csv",empty:"No college reports match this search."}:{title:"University Audit Export Reports",desc:"Prepare read-only audit, compliance, exception, evidence and access summaries for the current university scope.",reports:"University Reports",centre:"University Audit Report Centre",scope:"CSV export • university tenant scoped",search:"Search university report...",file:"gaint-academy-university-auditor-report-index.csv",empty:"No university reports match this search."};
  const[data,setData]=useState(null),[error,setError]=useState(""),[query,setQuery]=useState("");
  useEffect(()=>{api.get("/api/v1/auditor/export-reports").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load export reports."))},[]);
  const rows=useMemo(()=>{if(!data)return[];const q=query.trim().toLowerCase();return data.reports.filter(x=>!q||[x.name,x.category,x.description,x.status].some(v=>String(v||"").toLowerCase().includes(q)))},[data,query]);
  const exportOne=x=>downloadCsv("gaint-academy-"+x.key+".csv",[x]);
  return <div>
    <section className="module-context"><div><span className="eyebrow">{ui.label} • Auditor • Export Only</span><h1>{terms.title}</h1><p>{terms.desc}</p></div></section>
    {error&&<div className="error">{error}</div>}
    {data&&<>
      <div className="module-kpis"><article><small>{terms.reports}</small><strong>{data.summary.reports}</strong></article><article><small>Ready</small><strong>{data.summary.ready}</strong></article><article><small>Audit Events</small><strong>{data.summary.audit_events}</strong></article><article><small>Exceptions</small><strong>{data.summary.exceptions}</strong></article></div>
      <section className="panel structure-table">
        <div className="panel-title"><b>{terms.centre}</b><span>{terms.scope}</span></div>
        <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder={terms.search} /><button type="button" onClick={()=>downloadCsv(terms.file,rows)} disabled={!rows.length}>Export visible reports</button></div>
        <div className="table-scroll"><table><thead><tr><th>Report</th><th>Category</th><th>Description</th><th>Records</th><th>Status</th><th>Generated</th><th>Action</th></tr></thead><tbody>
          {rows.length?rows.map(x=><tr key={x.key}><td><b>{x.name}</b></td><td>{x.category}</td><td>{x.description}</td><td>{x.records}</td><td><b>{x.status}</b></td><td>{new Date(x.generated_at).toLocaleString()}</td><td><button type="button" onClick={()=>exportOne(x)}>Export CSV</button></td></tr>):<tr><td colSpan="7" className="empty-cell">{terms.empty}</td></tr>}
        </tbody></table></div>
      </section>
    </>}
  </div>
}
