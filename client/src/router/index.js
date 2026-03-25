import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import BaseLayout from "@/layouts/BaseLayout.vue";
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import ProfileView from "@/views/ProfileView.vue";
import ProtectedView from "@/views/ProtectedView.vue";
import RegisterView from "@/views/RegisterView.vue";
import AccountView from "@/views/AccountView.vue";
import CompanyDashboardView from "@/views/CompanyDashboardView.vue";
import AdminDashboardView from "@/views/AdminDashboardView.vue";
import CompanyPositionsView from "@/views/CompanyPositionsView.vue";
import PositionView from "@/views/PositionView.vue";
import StudentDashboardView from "@/views/StudentDashboardView.vue";
import StudentPositionView from "@/views/StudentPositionView.vue";
import StudentView from "@/views/StudentView.vue";
import CompanyView from "@/views/CompanyView.vue";
import ApplicationView from "@/views/ApplicationView.vue";

const routes = [
  {
    path: "/",
    component: BaseLayout,
    children: [
      { path: "", name: "home", component: HomeView },
      { path: "/login", name: "login", component: LoginView },
      { path: "/register", name: "register", component: RegisterView },
      { path: "/profile", name: "profile", component: ProfileView, meta: { requiresAuth: true, roleRequired: ["student", "company"] } },
      { path: "/account", name: "account", component: AccountView, meta: { requiresAuth: true } },
      { path: "/protected", name: "protected", component: ProtectedView, meta: { requiresAuth: true } },
      { path: "/company/dashboard", name: "company_dashboard", component: CompanyDashboardView, meta: { requiresAuth: true, roleRequired: ["company"] } },
      { path: "/admin/dashboard", name: "admin_dashboard", component: AdminDashboardView, meta: { requiresAuth: true, roleRequired: ["admin"] } },
      { path: "/student/dashboard", name: "student_dashboard", component: StudentDashboardView, meta: { requiresAuth: true, roleRequired: ["student"] } },
      { path: "/company/positions", name: "company_positions", component: CompanyPositionsView, meta: { requiresAuth: true, roleRequired: ["company"] } },
      { path: "/student/positions/:id", name: "student_position", component: StudentPositionView, meta: { requiresAuth: true } },
      { path: "/positions/:id", name: "position", component: PositionView, meta: { requiresAuth: true } },
      { path: "/companies/:id", name: "company", component: CompanyView, meta: { requiresAuth: true, roleRequired: ["admin", "student"] } },
      { path: "/students/:id", name: "student", component: StudentView, meta: { requiresAuth: true, roleRequired: ["admin", "company"] } },
      { path: "/applications/:id", name: "application", component: ApplicationView, meta: { requiresAuth: true } }
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

  // Role-based guard
  if (to.meta.roleRequired && !to.meta.roleRequired.includes(auth.currentUser.role)) {
    return { name: "home" };
  }

  // Redirect users away from login/register page if already logged in
  if (auth.isAuthenticated && (to.name == "login" || to.name == "register")) {
    return { name: "home" };
  }
});

export default router;
