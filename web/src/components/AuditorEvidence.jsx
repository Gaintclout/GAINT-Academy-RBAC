import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";

export default function AuditorEvidence({ui}){ const terms=ui.label==="School"?{title:"School Audit Evidence",desc:"Traceable evidence derived from school records. Auditor access is view-only.",total:"School Evidence",register:"School Evidence Register",scope:"Read only • school tenant scoped",search:"Search school evidence, reference, owner...",empty:"No school evidence matches these filters."}:ui.label==="College"?{title:"College Audit Evidence",desc:"Traceable evidence derived from college records. Auditor access is view-only.",total:"College Evidence",register:"College Evidence Register",scope:"Read only • college tenant scoped",search:"Search college evidence, reference, owner...",empty:"No college evidence matches these filters."}:{title:"University Audit Evidence",desc:"Traceable evidence derived from university records. Auditor access is view-only.",total:"University Evidence",register:"University Evidence Register",scope:"Read only • university tenant scoped",search:"Search university evidence, reference, owner...",empty:"No university evidence matches these filters."};
  const[data,setData]=useState(null),[error,setError]=useState(""),[moduleFilter,setModuleFilter]=useState("ALL"),[statusFilter,setStatusFilter]=useState("ALL"),[query,setQuery]=useState("");
  useEffect(()=>{api.get("/api/v1/auditor/evidence").then(r=>setData(r.data)).catch(e=>setError(e?.response?.data?.detail||"Unable to load evidence."))},[]);
  const rows=useMemo(()=>{if(!data)return[];const q=query.trim().toLowerCase();return data.evidence.filter(x=>(moduleFilter==="ALL"||x.module===moduleFilter)&&(statusFilter==="ALL"||x.status===statusFilter)&&(!q||[x.id,x.reference,x.title,x.owner,x.evidence_type,x.detail].some(v=>String(v||"").toLowerCase().includes(q))))},[data,moduleFilter,statusFilter,query]);
  const modules=useMemo(()=>data?[...new Set(data.evidence.map(x=>x.module))].sort():[],[data]);
  return <div>
    <section className="module-context"><div><span className="eyebrow">{ui.label} • Auditor • Read Only</span><h1>{terms.title}</h1><p>{terms.desc}</p></div></section>
    {error&&<div className="error">{error}</div>}
    {data&&<>
      <div className="module-kpis"><article><small>{terms.total}</small><strong>{data.summary.total}</strong></article><article><small>Available</small><strong>{data.summary.available}</strong></article><article><small>Missing</small><strong>{data.summary.missing}</strong></article><article><small>Source Modules</small><strong>{data.summary.modules}</strong></article></div>
      <section className="panel structure-table">
        <div className="panel-title"><b>{terms.register}</b><span>{terms.scope}</span></div>
        <div className="form-grid">
          <input value={query} onChange={e=>setQuery(e.target.value)} placeholder={terms.search} />
          <select value={moduleFilter} onChange={e=>setModuleFilter(e.target.value)}><option value="ALL">All modules</option>{modules.map(x=><option key={x}>{x}</option>)}</select>
          <select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}><option value="ALL">All statuses</option><option value="AVAILABLE">Available</option><option value="MISSING">Missing</option></select>
        </div>
        <div className="table-scroll"><table><thead><tr><th>Status</th><th>Module</th><th>Evidence Type</th><th>Reference</th><th>Record</th><th>Owner</th><th>Source Status</th><th>Evidence Reference</th><th>Recorded</th></tr></thead><tbody>
          {rows.length?rows.map(x=><tr key={x.id}><td><b>{x.status}</b></td><td>{x.module}</td><td>{x.evidence_type}</td><td>{x.reference||"—"}</td><td><b>{x.title}</b><br/><small>{x.detail}</small></td><td>{x.owner}</td><td>{x.source_status}</td><td>{x.evidence_ref||"—"}</td><td>{x.created_at?new Date(x.created_at).toLocaleString():"—"}</td></tr>):<tr><td colSpan="9" className="empty-cell">{terms.empty}</td></tr>}
        </tbody></table></div>
      </section>
    </>}
  </div>
}
