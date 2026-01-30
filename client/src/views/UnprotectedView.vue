<script setup>
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
const isAuthenticated = auth.isAuthenticated;
</script>

<template>
    <p>Unprotected</p>
</template>