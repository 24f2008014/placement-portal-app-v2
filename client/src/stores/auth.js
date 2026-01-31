import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { api, refreshApi } from "@/utils/api";
import router from "@/router";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(null);
  const accessExpiresAt = ref(null);
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
  };

  function deleteAccessToken() {
    accessToken.value = null;
    accessExpiresAt.value = null;
    delete api.defaults.headers.common["Authorization"];
    console.log("[deleteAccessToken]: Deleted");
  };

  async function login(email, password) {
    const response = await api.post("/tokens/new", null,
      { auth: { username: email, password: password } }
    );
    console.log(`Login successful: ${response.data}`)
    setAccessToken(response.data.access_token, response.data.expires_in_seconds);
  };

  async function refresh() {
    try {
      console.log("[Refresh]: Fetching new tokens");
      const response = await refreshApi.post("/tokens/refresh", null);
      setAccessToken(response.data.access_token, response.data.expires_in_seconds);
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

  return { accessToken, accessExpiresAt, isInitialized, isAuthenticated, setAccessToken, deleteAccessToken, login, refresh, logout };
});
