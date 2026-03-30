import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useAlertStore } from "@/stores/alert";
import BaseLayout from "@/layouts/BaseLayout.vue";
import HomeView from "@/views/HomeView.vue";
import RegisterView from "@/views/RegisterView.vue";
import LoginView from "@/views/LoginView.vue";
import AccountView from "@/views/AccountView.vue";
import ProfileView from "@/views/ProfileView.vue";
import AdminDashboardView from "@/views/AdminDashboardView.vue";
import CompanyDashboardView from "@/views/CompanyDashboardView.vue";
import StudentDashboardView from "@/views/StudentDashboardView.vue";
import CompanyPositionsView from "@/views/CompanyPositionsView.vue";
import CompaniesView from "@/views/CompaniesView.vue";
import CompanyView from "@/views/CompanyView.vue";
import PositionView from "@/views/PositionView.vue";
import StudentView from "@/views/StudentView.vue";
import ApplicationView from "@/views/ApplicationView.vue";
import PlacementView from "@/views/PlacementView.vue";

const routes = [
  {
    path: "/",
    component: BaseLayout,
    children: [
      { 
        path: "",
        name: "home",
        component: HomeView,
        meta: { title: "Home" }
      },
      { 
        path: "/login",
        name: "login",
        component: LoginView,
        meta: { title: "Login" }
      },
      { 
        path: "/register",
        name: "register",
        component: RegisterView,
        meta: { title: "Register" }
      },
      {
        path: "/profile",
        name: "profile",
        component: ProfileView,
        meta: { title: "Profile", requiresAuth: true, roleRequired: ["company", "student"] }
      },
      {
        path: "/account",
        name: "account",
        component: AccountView,
        meta: { requiresAuth: true, title: "Account" }
      },
      {
        path: "/company/dashboard",
        name: "company_dashboard",
        component: CompanyDashboardView,
        meta: { title: "Dashboard", requiresAuth: true, roleRequired: ["company"] }
      },
      {
        path: "/admin/dashboard",
        name: "admin_dashboard",
        component: AdminDashboardView,
        meta: { title: "Dashboard", requiresAuth: true, roleRequired: ["admin"] }
      },
      {
        path: "/student/dashboard",
        name: "student_dashboard",
        component: StudentDashboardView,
        meta: { title: "Dashboard", requiresAuth: true, roleRequired: ["student"] }
      },
      {
        path: "/company/positions",
        name: "company_positions",
        component: CompanyPositionsView,
        meta: { title: "Your Positions", requiresAuth: true, roleRequired: ["company"] }
      },
      {
        path: "/positions/:id",
        name: "position",
        component: PositionView,
        meta: { title: "View Position", requiresAuth: true }
      },
      {
        path: "/companies/:id",
        name: "company",
        component: CompanyView,
        meta: { title: "Company", requiresAuth: true, roleRequired: ["admin", "student"] } },
      {
        path: "/students/:id",
        name: "student",
        component: StudentView,
        meta: { title: "Student", requiresAuth: true, roleRequired: ["admin", "company"] } },
      {
        path: "/applications/:id",
        name: "application",
        component: ApplicationView,
        meta: { title: "Application", requiresAuth: true }
      },
      {
        path: "/companies",
        name: "companies",
        component: CompaniesView,
        meta: { title: "Companies", requiresAuth: true, roleRequired: ["admin", "student"] }
      },
      {
        path: "/placements/:id",
        name: "placement",
        component: PlacementView,
        meta: { title: "Placement", requiresAuth: true }
      },
      {
        path: "/:pathMatch(.*)*",
        redirect: "/"
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

router.beforeEach(async (to, from) => {
  const auth = useAuthStore();
  const alert = useAlertStore();

  // Initialize auth store on startup
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
    alert.addAlert("You are not authorized to view that page.", "error");
    return { name: "home" };
  }

  // Redirect users away from login/register page if already logged in
  if (auth.isAuthenticated && (to.name == "login" || to.name == "register")) {
    return { name: "home" };
  }
});

// Dynamic page titles
router.afterEach((to, from) => {
  const id = to.params.id;
  if (id) {
    document.title = to.meta.title ? `${to.meta.title} #${id} | Placer` : "Placer";
  } else {
    document.title = to.meta.title ? `${to.meta.title} | Placer` : "Placer";
  }
});

export default router;
