import React,{useEffect,useState} from "react";
import {NavigationContainer} from "@react-navigation/native";
import {createNativeStackNavigator} from "@react-navigation/native-stack";
import AsyncStorage from "@react-native-async-storage/async-storage";
import LoginScreen from "./src/screens/LoginScreen";
import DashboardScreen from "./src/screens/DashboardScreen";
import StudentSafetyScreen from "./src/screens/StudentSafetyScreen";
import ParentTrackingScreen from "./src/screens/ParentTrackingScreen";

const Stack=createNativeStackNavigator();

export default function App(){
  return <NavigationContainer>
    <Stack.Navigator>
      <Stack.Screen name="Login" component={LoginScreen} options={{headerShown:false}}/>
      <Stack.Screen name="Dashboard" component={DashboardScreen} options={{headerShown:false}}/>
      <Stack.Screen name="StudentSafety" component={StudentSafetyScreen} options={{title:"My Safety"}}/>
      <Stack.Screen name="ParentTracking" component={ParentTrackingScreen} options={{title:"Child Live Tracking"}}/>
    </Stack.Navigator>
  </NavigationContainer>
}
