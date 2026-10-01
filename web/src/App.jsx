import React,{useEffect,useState} from "react";
import {api} from "./api";
import Login from "./components/Login";
import Shell from "./components/Shell";

export default function App(){
  const [user,setUser]=useState(null);
  const [loading,setLoading]=useState(true);

  useEffect(()=>{
    const token=localStorage.getItem("gaint_token");
    if(!token){setLoading(false);return;}
    api.get("/api/v1/auth/me")
      .then(r=>setUser(r.data))
      .catch(()=>localStorage.removeItem("gaint_token"))
      .finally(()=>setLoading(false));
  },[]);

  if(loading) return <div className="center">Loading GAINT Academy...</div>;
  if(!user) return <Login onLogin={setUser}/>;
  return <Shell user={user} onUserChange={setUser} onLogout={()=>{
    localStorage.removeItem("gaint_token");
    setUser(null);
  }}/>;
}
