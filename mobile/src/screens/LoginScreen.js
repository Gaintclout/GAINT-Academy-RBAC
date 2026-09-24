import React,{useState} from "react";
import {View,Text,TextInput,Pressable,StyleSheet,Alert} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import api from "../api";

export default function LoginScreen({navigation}){
  const [email,setEmail]=useState("student@gaintacademy.com");
  const [password,setPassword]=useState("Password@123");
  async function login(){
    try{
      const {data}=await api.post("/api/v1/auth/login",{email,password});
      await AsyncStorage.setItem("gaint_token",data.access_token);
      await AsyncStorage.setItem("gaint_user",JSON.stringify(data.user));
      navigation.replace("Dashboard",{user:data.user});
    }catch(e){Alert.alert("Login failed",e?.response?.data?.detail||e.message)}
  }
  return <View style={s.page}>
    <Text style={s.brand}>GAINT ACADEMY</Text>
    <Text style={s.title}>Welcome back</Text>
    <TextInput style={s.input} value={email} onChangeText={setEmail} autoCapitalize="none"/>
    <TextInput style={s.input} value={password} onChangeText={setPassword} secureTextEntry/>
    <Pressable style={s.btn} onPress={login}><Text style={s.btnt}>Sign in</Text></Pressable>
    <Text style={s.hint}>All demo roles use Password@123</Text>
  </View>
}
const s=StyleSheet.create({page:{flex:1,justifyContent:"center",padding:24,backgroundColor:"#F4F7FB"},brand:{fontSize:28,fontWeight:"900",color:"#176B4D"},title:{fontSize:22,fontWeight:"800",marginVertical:20},input:{backgroundColor:"#fff",padding:14,borderRadius:12,borderWidth:1,borderColor:"#DDE6EE",marginBottom:10},btn:{backgroundColor:"#3E63DD",padding:15,borderRadius:12,alignItems:"center"},btnt:{color:"#fff",fontWeight:"800"},hint:{textAlign:"center",marginTop:15,color:"#6B7C93"}})
