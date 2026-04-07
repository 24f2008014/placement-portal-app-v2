<script setup>
import { useAlertStore } from "@/stores/alert";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/utils/api";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const alert = useAlertStore();
const stats = ref({});
const loading = ref(true);

onMounted(async () => {
    try {
        const response = await api.get("/home/stats");
        stats.value = response.data;
        loading.value = false;
    } catch (error) {
        console.error(error);
        alert.addAlert(error.response.data.description);
    }
});
</script>

<template>
    <div class="row align-items-center justify-content-center py-4 g-5 mb-4">
        <div class="col-6">
            <h6 class="display-4 fw-bold mb-3">Welcome to Placer.</h6>
            <p class="lead mb-4">Whether you're a student looking to find the job of your dreams, or a company looking to recruit the best and brightest, we have something for you. What are you waiting for? Sign up today!</p>
            <div class="row">
                <div class="col d-flex gap-3">
                    <template v-if="!auth.currentUser.role">
                        <button type="button" class="btn btn-primary btn-lg" @click="router.push({ name: 'register' })">Register</button>
                        <button type="button" class="btn btn-outline-secondary btn-lg" @click="router.push({ name: 'login' })">Login</button>
                    </template>
                    <template v-else>
                        <button type="button" class="btn btn-success btn-lg" @click="router.push({ name: 'admin_dashboard' })"><i class="bi bi-arrow-right me-2"></i>Dashboard</button>
                    </template>
                </div>
            </div>
        </div>
        <div class="col-5">
            <img src="@/assets/home_hero.jpg" class="img-fluid">
        </div>
    </div>

    <hr class="mb-4">
    <div class="row text-center gap-2 mb-4">
        <div class="col">
            <div class="card shadow">
                <div class="card-body">
                    <h3 class="card-title">Registered Students</h3>
                    <p><i class="bi bi-book" style="font-size: 2rem;"></i></p>
                    <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
                    <p v-else class="card-text lead fs-3 fw-bold">{{ stats.num_students }}</p>
                </div>
            </div>
        </div>

        <div class="col">
            <div class="card shadow">
                <div class="card-body">
                    <h3 class="card-title">Registered Companies</h3>
                    <p><i class="bi bi-briefcase-fill" style="font-size: 2rem;"></i></p>
                    <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
                    <p v-else class="card-text lead fs-3 fw-bold">{{ stats.num_companies }}</p>
                </div>
            </div>
        </div>

        <div class="col">
            <div class="card shadow">
                <div class="card-body">
                    <h3 class="card-title">Positions Created</h3>
                    <p><i class="bi bi-card-text" style="font-size: 2rem;"></i></p>
                    <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
                    <p v-else class="card-text lead fs-3 fw-bold">{{ stats.num_positions }}</p>
                </div>
            </div>
        </div>

        <div class="col">
            <div class="card shadow">
                <div class="card-body">
                    <h3 class="card-title">Students Placed</h3>
                    <p><i class="bi bi-rocket-takeoff-fill" style="font-size: 2rem;"></i></p>
                    <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
                    <p v-else class="card-text lead fs-3 fw-bold">{{ stats.num_placements }}</p>
                </div>
            </div>
        </div>

        <div class="col">
            <div class="card shadow">
                <div class="card-body">
                    <h3 class="card-title">Average Placement</h3>
                    <p><i class="bi bi-piggy-bank-fill" style="font-size: 2rem;"></i></p>
                    <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
                    <p v-else class="card-text lead fs-3 fw-bold">&#8377;{{ stats.avg_placement_salary ? stats.avg_placement_salary.toLocaleString("en-US") : 0 }}</p>
                </div>
            </div>
        </div>
    </div>
</template>