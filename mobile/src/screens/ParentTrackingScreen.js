import React,{useEffect,useState} from "react";
import {View,Text,StyleSheet} from "react-native";
import api from "../api";

export default function ParentTrackingScreen(){
  const [loc,setLoc]=useState(null);
  const [child,setChild]=useState(null);
  useEffect(()=>{
    api.get("/api/v1/parents/children").then(async r=>{
      if(r.data[0]){
        setChild(r.data[0]);
        const x=await api.get(`/api/v1/parents/children/${r.data[0].id}/location`);
        setLoc(x.data);
      }
    });
  },[]);
  return <View style={s.page}>
    <Text style={s.title}>Linked Child</Text>
    <View style={s.card}>
      <Text style={s.name}>{child?.name||"Loading..."}</Text>
      <Text>{child?.relationship||""}</Text>
    </View>
    <Text style={s.title}>Live Safety Status</Text>
    <View style={s.card}>
      {loc?.available?<><Text style={s.status}>{loc.status}</Text><Text>Route: {loc.bus?.route}</Text><Text>Vehicle: {loc.bus?.vehicle}</Text><Text>ETA: {loc.bus?.eta_minutes} min</Text><Text>Location: {loc.latitude}, {loc.longitude}</Text></>:<Text>Location unavailable</Text>}
    </View>
    <View style={s.map}><Text>MAP PREVIEW</Text><Text style={{fontSize:11,textAlign:"center"}}>Connect your production map provider key.</Text></View>
  </View>
}
const s=StyleSheet.create({page:{flex:1,padding:20,backgroundColor:"#F4F7FB"},title:{fontSize:21,fontWeight:"900",marginBottom:10},card:{backgroundColor:"#fff",padding:18,borderRadius:14,marginBottom:20},name:{fontSize:20,fontWeight:"900"},status:{fontSize:22,fontWeight:"900",color:"#2A8A67",marginBottom:8},map:{height:240,borderRadius:14,backgroundColor:"#EAF4FF",alignItems:"center",justifyContent:"center",gap:5}})
