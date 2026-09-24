import React,{useEffect,useState} from "react";
import {api} from "../api";

export default function Records({title}){
  const [rows,setRows]=useState([]);
  const [name,setName]=useState("");
  const [error,setError]=useState("");
  async function load(){
    try{
      const {data}=await api.get("/api/v1/records",{params:{module:title}});
      setRows(data);
    }catch(e){setError(e?.response?.data?.detail||e.message)}
  }
  useEffect(()=>{load()},[title]);

  async function add(){
    try{
      await api.post("/api/v1/records",{module:title,name,category:"General",status:"Active",code:"",notes:""});
      setName(""); load();
    }catch(e){setError(e?.response?.data?.detail||e.message)}
  }

  return <div>
    <div className="page-title"><div><h1>{title}</h1><p>Module workspace</p></div></div>
    <section className="panel">
      <div className="inline-form">
        <input placeholder={`Add ${title} record`} value={name} onChange={e=>setName(e.target.value)}/>
        <button className="primary" onClick={add}>Add</button>
      </div>
      {error && <div className="error">{error}</div>}
      <table><thead><tr><th>Name</th><th>Code</th><th>Category</th><th>Status</th></tr></thead>
      <tbody>{rows.map(r=><tr key={r.id}><td>{r.name}</td><td>{r.code}</td><td>{r.category}</td><td>{r.status}</td></tr>)}</tbody></table>
    </section>
  </div>
}
