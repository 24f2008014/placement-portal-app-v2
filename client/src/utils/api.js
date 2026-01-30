import axios from "axios"
import { useAuthStore } from "@/stores/auth"

const api = axios.create({
    baseURL: "/api",
    withCredentials: true,
    headers: { "Content-Type": "application-json" }
})

const refreshApi = axios.create({
    baseURL: "/api",
    withCredentials: true
})

api.interceptors.request.use(
    (config) => { // If access token is present, attach it to header before sending request.
        console.log("Request interceptor start");
        const auth = useAuthStore();
        const accessToken = auth.accessToken;
        if (accessToken) { config.headers.Authorization = `Bearer ${accessToken}`; }
        console.log(`${accessToken}`);
        return config;
    }, 
    (error) => { return Promise.reject(error); }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        const firstRequest = error.config;
        const auth = useAuthStore();
        if (error.response && error.response.status == 401 && !firstRequest._retry) {
            firstRequest._retry = true;
            auth.refresh();
            return api(firstRequest);
        }
        return Promise.reject(error);
    }
);

export { api, refreshApi }