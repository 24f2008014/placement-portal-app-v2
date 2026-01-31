<script setup>
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <ul>
    <li><RouterLink :to="{ name: 'home' }">Home</RouterLink></li>
    <li><RouterLink :to="{ name: 'protected' }">Protected</RouterLink></li>
    <li><RouterLink :to="{ name: 'unprotected' }">Unprotected</RouterLink></li>
    <template v-if="auth.isAuthenticated">
        <li><RouterLink :to="{ name: 'profile' }">Profile</RouterLink></li>
        <li><a href="#" @click.prevent="auth.logout">Log out</a></li>
    </template>
    <template v-else>
        <li><RouterLink :to="{ name: 'login' }">Login</RouterLink></li>
    </template>
    </ul>
</template>