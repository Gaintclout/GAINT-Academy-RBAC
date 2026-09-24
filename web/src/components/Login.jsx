import React,{useState} from "react";
import {api} from "../api";

export default function Login({onLogin}){
  const [email,setEmail]=useState("student@gaintacademy.com");
  const [password,setPassword]=useState("Password@123");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);

  async function submit(e){
    e.preventDefault(); setBusy(true); setError("");
    try{
      const {data}=await api.post("/api/v1/auth/login",{email,password});
      localStorage.setItem("gaint_token",data.access_token);
      onLogin(data.user);
    }catch(err){
      setError(err?.response?.data?.detail || "Login failed");
    }finally{setBusy(false)}
  }

  return <div className="login-page">
    <div className="login-brand">
      <div className="brand-mark">G</div>
      <h1>GAINT <span>ACADEMY</span></h1>
      <h3>AI-Powered Unified Education & Campus Management Platform</h3>
      <div className="brand-strip"><b>One Platform</b><small>Academics • Campus • Finance • Learning • AI • Safety</small></div>
    </div>
    <form className="login-card" onSubmit={submit}>
      <div className="login-icon">🏫</div>
      <h2>Welcome back</h2>
      <p>Sign in to your institution workspace</p>
      <label>Work email</label>
      <input value={email} onChange={e=>setEmail(e.target.value)} />
      <label>Password</label>
      <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      {error && <div className="error">{error}</div>}
      <button disabled={busy}>{busy?"Signing in...":"Sign in"}</button>
      <small>Demo password for all roles: <b>Password@123</b></small>
    </form>
  </div>
}
