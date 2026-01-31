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
        // console.log("[Request Interceptor]: Start");
        const auth = useAuthStore();
        if (auth.accessToken) { 
            config.headers.Authorization = `Bearer ${auth.accessToken}`; 
        }
        console.log("[Request Interceptor]: Attached bearer token to header");
        return config;
    }, 
    (error) => { return Promise.reject(error); }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.log("[Response Interceptor]: Error");
        const firstRequest = error.config;
        const auth = useAuthStore();
        if (error.response && error.response.status == 401 && !firstRequest._retry) {
            console.log("[Response Interceptor]: 401, first");
            firstRequest._retry = true;
            try {
                const newAccessToken = auth.refresh();
                firstRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                console.log("[Response Interceptor]: Retrying original request with new bearer header");
                return api(firstRequest);
            }
            catch (error) {
                return Promise.reject(error);
            }
        }
        return Promise.reject(error);
    }
);

export { api, refreshApi }