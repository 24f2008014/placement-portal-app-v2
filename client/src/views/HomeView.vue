<script setup>
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <h2 class="display-5" v-if="auth.currentUser">Welcome, {{ auth.currentUser }}!</h2>
    <h2 class="display-5" v-else>Welcome!</h2>
</template>