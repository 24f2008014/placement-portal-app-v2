<script setup>
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
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
</template>