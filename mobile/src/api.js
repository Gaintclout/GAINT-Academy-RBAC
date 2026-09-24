import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
const api=axios.create({baseURL:process.env.EXPO_PUBLIC_API_URL||"http://10.0.2.2:8000",timeout:15000});
api.interceptors.request.use(async config=>{
  const token=await AsyncStorage.getItem("gaint_token");
  if(token) config.headers.Authorization=`Bearer ${token}`;
  return config;
});
export default api;
