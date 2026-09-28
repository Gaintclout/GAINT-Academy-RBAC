import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api";
const ROLES=["Institution Admin","Teacher","Student","Parent / Guardian","Accounts","HR","Campus Admin","Auditor"];
export default function UsersRoles({currentUser}){
 const [rows,setRows]=useState([]),[query,setQuery]=useState(""),[error,setError]=useState(""),[message,setMessage]=useState(""),[saving,setSaving]=useState(null);
 const load=()=>api.get("/api/v1/users").then(r=>{setRows(r.data);setError("")}).catch(e=>setError(e?.response?.data?.detail||"Unable to load users."));
 useEffect(()=>{load()},[]);
 const visible=useMemo(()=>rows.filter(x=>(x.name+" "+x.email+" "+x.role).toLowerCase().includes(query.toLowerCase())),[rows,query]);
 async function update(id,patch){try{setSaving(id);setError("");setMessage("");const r=await api.patch("/api/v1/users/"+id,patch);setRows(xs=>xs.map(x=>x.id===id?r.data:x));setMessage("User updated successfully.")}catch(e){setError(e?.response?.data?.detail||"Unable to update user.")}finally{setSaving(null)}}
 return <div className="workspace-page"><div className="page-heading"><div><span className="eyebrow">Administration</span><h1>Users & Roles</h1><p>Manage users within this institution. Institution membership cannot be changed here.</p></div></div>
 {error&&<div className="error-banner">{error}</div>}{message&&<div className="success-banner">{message}</div>}
 <section className="panel"><div className="panel-title"><b>Institution Users</b><span>{rows.length} users</span></div><input className="search-input" placeholder="Search name, email or role" value={query} onChange={e=>setQuery(e.target.value)}/>
 <div className="table-scroll"><table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Campus</th><th>Status</th></tr></thead><tbody>{visible.length?visible.map(x=><tr key={x.id}>
 <td><input value={x.name} disabled={saving===x.id} onChange={e=>setRows(rs=>rs.map(r=>r.id===x.id?{...r,name:e.target.value}:r))} onBlur={()=>update(x.id,{name:x.name})}/></td>
 <td>{x.email}{x.id===currentUser.id&&<><br/><small>Current account</small></>}</td>
 <td><select value={x.role} disabled={saving===x.id||x.id===currentUser.id} onChange={e=>update(x.id,{role:e.target.value})}>{ROLES.map(r=><option key={r}>{r}</option>)}</select></td>
 <td><input type="number" min="1" value={x.campus_id} disabled={saving===x.id} onChange={e=>setRows(rs=>rs.map(r=>r.id===x.id?{...r,campus_id:Number(e.target.value)}:r))} onBlur={()=>update(x.id,{campus_id:x.campus_id})}/></td>
 <td><select value={x.is_active?"Active":"Inactive"} disabled={saving===x.id||x.id===currentUser.id} onChange={e=>update(x.id,{is_active:e.target.value==="Active"})}><option>Active</option><option>Inactive</option></select></td>
 </tr>):<tr><td colSpan="5" className="empty-cell">No users found.</td></tr>}</tbody></table></div></section></div>;
}
