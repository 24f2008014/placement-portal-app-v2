<script setup>
import NavBar from "@/components/NavBar.vue";
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <p>Route: {{ $route.fullPath }}</p>
    <NavBar />
    <RouterView />
</template>