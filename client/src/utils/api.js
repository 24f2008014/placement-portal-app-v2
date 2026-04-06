import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import { useAlertStore } from "@/stores/alert";

// Main axios instance
const api = axios.create({
    baseURL: "/api",
    withCredentials: true,
    headers: { "Content-Type": "application/json" }
});

// Separate instance solely for token refresh requests
const refreshApi = axios.create({
    baseURL: "/api",
    withCredentials: true
});

// Attach access token to auth header before sending requests, if present
api.interceptors.request.use(
    (config) => {
        const auth = useAuthStore();
        if (auth.accessToken) { 
            config.headers.Authorization = `Bearer ${auth.accessToken}`; 
        }
        // console.log("[Request Interceptor]: Attached bearer token to header");
        return config;
    }, (error) => { 
        return Promise.reject(error);
    }
);

// Intercept error responses from the server and refresh token if invalid
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // console.log(`[Response Interceptor]: ${error}`);
        // Store the initial request
        const firstRequest = error.config;
        const auth = useAuthStore();
        const alert = useAlertStore();

        // If server returns "unauthorized" and this isn't a retry, refresh token and update header
        if (error.response && error.response.status == 401 && !firstRequest._retry) {
            // console.log("[Response Interceptor]: 401, first");
            firstRequest._retry = true;
            try {
                const newAccessToken = auth.refresh();
                firstRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                // console.log("[Response Interceptor]: Retrying original request with new bearer header");
                return api(firstRequest);
            } catch (error) {
                return Promise.reject(error);
            }
        }
        return Promise.reject(error);
    }
);

export { api, refreshApi };