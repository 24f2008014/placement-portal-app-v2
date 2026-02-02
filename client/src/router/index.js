import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import BaseLayout from "@/layouts/BaseLayout.vue";
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import ProfileView from "@/views/ProfileView.vue";
import ProtectedView from "@/views/ProtectedView.vue";
import UnprotectedView from "@/views/UnprotectedView.vue";
import RegisterView from "@/views/RegisterView.vue";
import AccountView from "@/views/AccountView.vue";

const routes = [
  {
    path: "/",
    component: BaseLayout,
    children: [
      { path: "", name: "home", component: HomeView },
      { path: "/login", name: "login", component: LoginView },
      { path: "/register", name: "register", component: RegisterView },
      { path: "/profile", name: "profile", component: ProfileView, meta: { requiresAuth: true } },
      { path: "/account", name: "account", component: AccountView, meta: { requiresAuth: true } },
      { path: "/protected", name: "protected", component: ProtectedView, meta: { requiresAuth: true } },
      { path: "/unprotected", name: "unprotected", component: UnprotectedView, },
    ]
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

// Navigation guards
router.beforeEach(async (to, from) => {
  const auth = useAuthStore();

  // Initialize Pinia auth store on startup
  if (!auth.isInitialized) {
    await auth.refresh();
  }

  // Redirect non-logged-in users away from protected pages to login page
  if (!auth.isAuthenticated && to.meta.requiresAuth) {
    return {
      name: "login",
      query: { redirect: to.fullPath }
    };
  }

  // Redirect users away from login/register page if already logged in
  if (auth.isAuthenticated && (to.name == "login" || to.name == "register")) {
    return { name: "home" };
  }
});

export default router;
