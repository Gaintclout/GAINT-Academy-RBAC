import React,{useEffect,useState} from "react";
import {View,Text,StyleSheet,ScrollView,Pressable,ActivityIndicator} from "react-native";
import api from "../api";

export default function ParentTrackingScreen(){
  const [children,setChildren]=useState([]);
  const [child,setChild]=useState(null);
  const [loc,setLoc]=useState(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");

  async function loadLocation(student){
    if(!student)return;
    try{
      setLoading(true); setError(""); setLoc(null);
      const x=await api.get(`/api/v1/parents/children/${student.id}/location`);
      setLoc(x.data);
    }catch(e){
      setError(e?.response?.data?.detail||"Unable to load child location.");
    }finally{setLoading(false)}
  }

  useEffect(()=>{
    api.get("/api/v1/parents/children").then(async r=>{
      const rows=r.data||[]; setChildren(rows);
      if(rows[0]){setChild(rows[0]); await loadLocation(rows[0]);}
      else setLoading(false);
    }).catch(e=>{setError(e?.response?.data?.detail||"Unable to load linked children.");setLoading(false)});
  },[]);

  useEffect(()=>{
    if(!child)return;
    const timer=setInterval(()=>loadLocation(child),15000);
    return ()=>clearInterval(timer);
  },[child?.id]);

  async function selectChild(x){setChild(x);await loadLocation(x)}

  return <ScrollView contentContainerStyle={s.page}>
    <Text style={s.title}>My Children</Text>
    {children.length===0?<View style={s.card}><Text>No students are linked to this parent account.</Text></View>:
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.children}>
        {children.map(x=><Pressable key={x.id} style={[s.childCard,child?.id===x.id&&s.active]} onPress={()=>selectChild(x)}>
          <Text style={s.name}>{x.name}</Text><Text>{x.relationship}</Text>
        </Pressable>)}
      </ScrollView>}
    <Text style={s.title}>Live Safety Status</Text>
    {error?<View style={s.error}><Text>{error}</Text></View>:null}
    <View style={s.card}>
      {loading?<ActivityIndicator/>:loc?.available?<><Text style={s.name}>{loc.name}</Text><Text style={s.status}>{loc.status||"ACTIVE"}</Text><Text>Tracking: {loc.tracking_context||"—"}</Text><Text>Accuracy: {loc.accuracy==null?"—":Math.round(loc.accuracy)+" m"}</Text><Text>Location: {loc.latitude}, {loc.longitude}</Text><Text>Last updated: {loc.recorded_at?new Date(loc.recorded_at).toLocaleString():"—"}</Text></>:<Text>{child?"Location is currently unavailable for this child.":"Select a linked child to view location."}</Text>}
    </View>
    <View style={s.map}><Text>MAP PREVIEW</Text><Text style={s.mapNote}>Connect the production map provider for native map rendering.</Text></View>
  </ScrollView>
}
const s=StyleSheet.create({page:{padding:20,backgroundColor:"#F4F7FB",flexGrow:1},title:{fontSize:21,fontWeight:"900",marginBottom:10},children:{marginBottom:20},childCard:{backgroundColor:"#fff",padding:16,borderRadius:14,marginRight:10,minWidth:150},active:{borderWidth:2,borderColor:"#2A8A67"},card:{backgroundColor:"#fff",padding:18,borderRadius:14,marginBottom:20},name:{fontSize:18,fontWeight:"900"},status:{fontSize:22,fontWeight:"900",color:"#2A8A67",marginVertical:8},error:{padding:12,backgroundColor:"#fff",borderRadius:10,marginBottom:12},map:{height:240,borderRadius:14,backgroundColor:"#EAF4FF",alignItems:"center",justifyContent:"center",gap:5},mapNote:{fontSize:11,textAlign:"center"}})
