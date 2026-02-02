import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { api, refreshApi } from "@/utils/api";
import { jwtDecode } from "jwt-decode";
import router from "@/router";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(null);
  const accessExpiresAt = ref(null);
  const currentUser = ref({
    id: "",
    role: "",
    name: ""
  });
  const isInitialized = ref(false);

  const isAuthenticated = computed(() => {
    if (!accessToken.value) { return false; }
    return Date.now() < accessExpiresAt.value;
  });

  function setAccessToken(token, exp) {
    console.log("[setAccessToken]: Start");
    accessToken.value = token;
    accessExpiresAt.value = Date.now() + exp * 1000;
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    console.log(`[setAccessToken]: Header set, isAuthenticated: ${isAuthenticated.value}`);
    const decoded = jwtDecode(token);
    currentUser.value.id = decoded.sub;
    currentUser.value.role = decoded.roles[0];
  };

  function deleteAccessToken() {
    accessToken.value = null;
    accessExpiresAt.value = null;
    currentUser.value = null;
    delete api.defaults.headers.common["Authorization"];
    console.log("[deleteAccessToken]: Deleted");
  };

  async function login(email, password) {
    try {
      const response = await refreshApi.post("/tokens/new", null,
        { auth: { username: email, password: password } }
      );
      console.log(`Login successful: ${response.data}`);
      setAccessToken(response.data.access_token, response.data.expires_in_seconds);
      currentUser.value.name = response.data.username;
      console.log(response.data);
    }
    catch (error) {
      console.log("login caught");
      return Promise.reject(error);
    }
  };

  async function refresh() {
    try {
      console.log("[Refresh]: Fetching new tokens");
      const response = await refreshApi.post("/tokens/refresh", null);
      setAccessToken(response.data.access_token, response.data.expires_in_seconds);
      currentUser.value.name = response.data.username;
      isInitialized.value = true;
      console.log("[Refresh]: Set new tokens");
      return response.data.access_token;
    } catch (error) {
      console.log(`[Refresh]: ${error}`);
      isInitialized.value = true;
    }
  };

  async function logout() {
    try {
      await api.post("/tokens/revoke", null);
      deleteAccessToken();
      router.replace({ name: "home" });
      console.log(`[Logout]: Success`);
    }
    catch (error) {
      console.log(`[Logout]: ${error}`);
      return Promise.reject(error);
    }
  };

  return { accessToken, accessExpiresAt, currentUser, isInitialized, isAuthenticated, setAccessToken, deleteAccessToken, login, refresh, logout };
});
