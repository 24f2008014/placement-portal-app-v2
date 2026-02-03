<script setup>
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <nav class="navbar navbar-expand-lg py-2 shadow bg-body-tertiary">
        <div class="container align-items-center">
            <a class="navbar-brand fw-bold" href="#">Placer</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav">
                    <li class="nav-item"><RouterLink :to="{ name: 'home' }" class="nav-link">Home</RouterLink></li>
                    <li class="nav-item" v-if="auth.currentUser.role=='company'"><RouterLink :to="{ name: 'company_dashboard' }" class="nav-link">Dashboard</RouterLink></li>
                    <li class="nav-item" v-if="auth.currentUser.role=='admin'"><RouterLink :to="{ name: 'admin_dashboard' }" class="nav-link">Dashboard</RouterLink></li>
                    <li class="nav-item" v-if="auth.currentUser.role=='student'"><RouterLink :to="{ name: 'student_dashboard' }" class="nav-link">Dashboard</RouterLink></li>
                    <li class="nav-item" v-if="auth.currentUser.role=='company'"><RouterLink :to="{ name: 'company_positions' }" class="nav-link">Positions</RouterLink></li>
                </ul>
                <ul class="ms-auto navbar-nav">
                    <template v-if="auth.isAuthenticated">
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"><i class="bi bi-person-circle fs-4 pe-1"></i></a>
                            <ul class="dropdown-menu">
                                <li><RouterLink :to="{ name: 'profile' }" class="dropdown-item">Profile</RouterLink></li>
                                <li><RouterLink :to="{ name: 'account' }" class="dropdown-item">Account</RouterLink></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a href="#" @click.prevent="auth.logout" class="dropdown-item">Log out</a></li>
                            </ul>
                        </li>
                    </template>
                    <template v-else>
                        <li class="nav-item"><RouterLink :to="{ name: 'register' }" class="nav-link">Register</RouterLink></li>
                        <li class="nav-item"><RouterLink :to="{ name: 'login' }" class="nav-link">Login</RouterLink></li>
                    </template>
                </ul>
            </div>
        </div>
    </nav>
</template>