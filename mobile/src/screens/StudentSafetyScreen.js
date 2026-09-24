import React,{useEffect,useState} from "react";
import {View,Text,Pressable,StyleSheet,Alert} from "react-native";
import * as Location from "expo-location";
import api from "../api";

export default function StudentSafetyScreen(){
  const [current,setCurrent]=useState(null);
  async function load(){try{const {data}=await api.get("/api/v1/location/me");setCurrent(data)}catch(e){}}
  useEffect(()=>{load()},[]);
  async function share(){
    const {status}=await Location.requestForegroundPermissionsAsync();
    if(status!=="granted") return Alert.alert("Permission required","Location permission was not granted.");
    const loc=await Location.getCurrentPositionAsync({});
    await api.post("/api/v1/location/update",{
      latitude:loc.coords.latitude,longitude:loc.coords.longitude,accuracy:loc.coords.accuracy||0,
      source:"MOBILE",tracking_context:"TRANSPORT",status:"ACTIVE"
    });
    await load();
    Alert.alert("Updated","Your approved safety location was updated.");
  }
  async function sos(){
    const {status}=await Location.requestForegroundPermissionsAsync();
    if(status!=="granted") return Alert.alert("Permission required");
    const loc=await Location.getCurrentPositionAsync({});
    await api.post("/api/v1/sos",{latitude:loc.coords.latitude,longitude:loc.coords.longitude,message:"Student SOS"});
    Alert.alert("SOS sent","Emergency location has been recorded.");
  }
  return <View style={s.page}>
    <Text style={s.title}>My Location & Safety</Text>
    <Text style={s.copy}>Location is shared only for approved safety contexts such as school transport, field trips or SOS.</Text>
    <View style={s.card}>
      <Text style={s.label}>Current status</Text>
      <Text style={s.value}>{current?.available?current.status:"Location unavailable"}</Text>
      {current?.available&&<><Text>{current.latitude}, {current.longitude}</Text><Text>Context: {current.tracking_context}</Text></>}
    </View>
    <Pressable style={s.btn} onPress={share}><Text style={s.btnt}>Update safety location</Text></Pressable>
    <Pressable style={s.sos} onPress={sos}><Text style={s.btnt}>SOS / Emergency</Text></Pressable>
  </View>
}
const s=StyleSheet.create({page:{flex:1,padding:20,backgroundColor:"#F4F7FB"},title:{fontSize:24,fontWeight:"900"},copy:{color:"#687C90",lineHeight:20,marginVertical:12},card:{backgroundColor:"#fff",padding:18,borderRadius:14,marginBottom:18},label:{color:"#687C90"},value:{fontSize:21,fontWeight:"900",marginVertical:7},btn:{backgroundColor:"#3E63DD",padding:15,borderRadius:12,alignItems:"center",marginBottom:10},sos:{backgroundColor:"#B42318",padding:15,borderRadius:12,alignItems:"center"},btnt:{color:"#fff",fontWeight:"900"}})
