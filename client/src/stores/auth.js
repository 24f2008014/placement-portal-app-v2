import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { api, refreshApi } from "@/utils/api";
import router from "@/router";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(null);
  const accessExpiresAt = ref(null);

  const isAuthenticated = computed(() => {
    if (!accessToken.value) { return false; }
    return Date.now() < accessExpiresAt.value;
  });

  function setAccessToken(token, exp) {
    console.log(`[setAccessToken]: Start`);
    accessToken.value = token;
    accessExpiresAt.value = Date.now() + exp * 1000;
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    console.log(`[setAccessToken]: ${token}, ${api.defaults.headers.common["Authorization"]}, ${isAuthenticated.value}`);
  };

  async function login(email, password) {
    const response = await api.post("/tokens/new", null,
        { auth: { username: email, password: password } }
    );
    console.log(`Login successful`)
    setAccessToken(response.data.access_token, response.data.expires_in_seconds);
  };

  async function refresh() {
    try {
        const response = await refreshApi.post("/tokens/refresh", null);
        setAccessToken(response.data.access_token, response.data.expires_in_seconds);
    } catch (error) {
        router.replace({ name: "login" });
    }
  };

  return { accessToken, accessExpiresAt, isAuthenticated, setAccessToken, login, refresh };
});
