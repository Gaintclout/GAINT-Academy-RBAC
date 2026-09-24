import React,{useEffect,useState} from "react";
import {View,Text,Pressable,StyleSheet,ScrollView} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import api from "../api";

export default function DashboardScreen({navigation,route}){
  const [user,setUser]=useState(route.params?.user||null);
  const [data,setData]=useState(null);
  useEffect(()=>{
    if(!user) AsyncStorage.getItem("gaint_user").then(v=>v&&setUser(JSON.parse(v)));
  },[]);
  useEffect(()=>{if(user) api.get("/api/v1/dashboard").then(r=>setData(r.data))},[user]);
  if(!user||!data) return <View style={s.center}><Text>Loading...</Text></View>;
  const safetyAction=user.role==="Student"?()=>navigation.navigate("StudentSafety"):user.role==="Parent / Guardian"?()=>navigation.navigate("ParentTracking"):null;
  return <ScrollView style={s.page} contentContainerStyle={{padding:18}}>
    <Text style={s.eyebrow}>GAINT ACADEMY</Text>
    <Text style={s.name}>{user.name}</Text>
    <Text style={s.role}>{user.role}</Text>
    <Text style={s.title}>{data.title}</Text>
    <View style={s.grid}>{data.cards.map(c=><View style={s.card} key={c.label}><Text style={s.label}>{c.label}</Text><Text style={s.value}>{c.value}</Text><Text style={s.hint}>{c.hint}</Text></View>)}</View>
    <Text style={s.section}>Quick actions</Text>
    {data.quick_actions.map(a=><Pressable key={a} style={s.action} onPress={a.toLowerCase().includes("safety")||a.toLowerCase().includes("location")||a.toLowerCase().includes("track")?safetyAction:undefined}><Text>{a}</Text><Text>›</Text></Pressable>)}
  </ScrollView>
}
const s=StyleSheet.create({page:{flex:1,backgroundColor:"#F4F7FB",paddingTop:42},center:{flex:1,justifyContent:"center",alignItems:"center"},eyebrow:{fontWeight:"900",color:"#2A8A67"},name:{fontSize:25,fontWeight:"900",marginTop:5},role:{color:"#6B7C93"},title:{fontSize:20,fontWeight:"800",marginTop:24,marginBottom:12},grid:{flexDirection:"row",flexWrap:"wrap",gap:10},card:{width:"48%",backgroundColor:"#fff",padding:14,borderRadius:14,borderWidth:1,borderColor:"#E0E8F1"},label:{fontSize:12,color:"#687C90"},value:{fontSize:22,fontWeight:"900",marginVertical:5},hint:{fontSize:11,color:"#74879A"},section:{fontSize:18,fontWeight:"900",marginTop:24,marginBottom:10},action:{backgroundColor:"#fff",padding:15,borderRadius:12,marginBottom:8,flexDirection:"row",justifyContent:"space-between"}})
