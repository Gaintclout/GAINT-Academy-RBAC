import React,{useEffect,useMemo,useState} from "react";
import {api} from "../api";
const money=n=>"₹"+Number(n||0).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2});
export default function AdminFeesPayments({ui}){
 const[rows,setRows]=useState([]),[students,setStudents]=useState([]),[summary,setSummary]=useState(null),[payments,setPayments]=useState([]),[error,setError]=useState(""),[query,setQuery]=useState(""),[status,setStatus]=useState("ALL");
 const load=()=>Promise.all([api.get("/api/v1/fee-ledger"),api.get("/api/v1/finance/summary"),api.get("/api/v1/finance/students"),api.get("/api/v1/finance/payments")]).then(([l,s,u,p])=>{setRows(l.data);setSummary(s.data);setStudents(u.data);setPayments(p.data);setError("")}).catch(e=>setError(e?.response?.data?.detail||"Unable to load fees and payments."));
 useEffect(()=>{load()},[]);
 const names=useMemo(()=>Object.fromEntries(students.map(x=>[x.id,x])),[students]);
 const visible=useMemo(()=>{const q=query.trim().toLowerCase();return rows.filter(x=>(status==="ALL"||x.status===status)&&(!q||[x.fee_code,x.title,names[x.student_user_id]?.name,names[x.student_user_id]?.email].some(v=>String(v||"").toLowerCase().includes(q))))},[rows,names,query,status]);
 return <div>
  <section className="module-context"><div><span className="eyebrow">{ui.label} • Institution Admin</span><h1>Fees & Payments</h1><p>Institution-wide finance oversight for student fee assignments, collections, outstanding balances and receipts.</p></div></section>
  {error&&<div className="error">{error}</div>}
  <div className="finance-kpis"><article><small>Assigned</small><strong>{money(summary?.assigned)}</strong></article><article><small>Collected</small><strong>{money(summary?.collected)}</strong></article><article><small>Outstanding</small><strong>{money(summary?.outstanding)}</strong></article><article><small>Paid / Partial / Due</small><strong>{summary?summary.paid_count+" / "+summary.partial_count+" / "+summary.due_count:"—"}</strong></article><article><small>Payments</small><strong>{payments.length}</strong></article></div>
  <section className="panel structure-table"><div className="panel-title"><b>Student Fee Ledger</b><span>{visible.length} visible entries</span></div>
   <div className="form-grid"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search student, fee code or description..." /><select value={status} onChange={e=>setStatus(e.target.value)}><option value="ALL">All statuses</option>{["DUE","PARTIAL","PAID","CANCELLED"].map(x=><option key={x}>{x}</option>)}</select></div>
   <div className="table-scroll"><table><thead><tr><th>Student</th><th>Fee</th><th>Description</th><th>Assigned</th><th>Collected</th><th>Balance</th><th>Status</th></tr></thead><tbody>{visible.length?visible.map(x=><tr key={x.id}><td><b>{names[x.student_user_id]?.name||("Student #"+x.student_user_id)}</b><br/><small>{names[x.student_user_id]?.email||""}</small></td><td>{x.fee_code}</td><td>{x.title}</td><td>{money(x.amount_due)}</td><td>{money(x.amount_paid)}</td><td>{money(x.balance)}</td><td><b>{x.status}</b></td></tr>):<tr><td colSpan="7" className="empty-cell">No fee records match these filters.</td></tr>}</tbody></table></div>
  </section>
  <section className="panel structure-table"><div className="panel-title"><b>Recent Payments</b><span>{payments.length} recorded payments</span></div><div className="table-scroll"><table><thead><tr><th>Receipt</th><th>Student</th><th>Fee</th><th>Amount</th><th>Reference</th><th>Paid At</th></tr></thead><tbody>{payments.slice(0,100).map(x=><tr key={x.id}><td><b>{x.receipt_no}</b></td><td>{x.student_name}</td><td>{x.fee_title}<br/><small>{x.fee_code}</small></td><td>{money(x.amount)}</td><td>{x.reference||"—"}</td><td>{new Date(x.paid_at).toLocaleString()}</td></tr>)}</tbody></table></div></section>
 </div>
}
