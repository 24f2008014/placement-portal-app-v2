<script setup>
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <h2 class="display-5">Welcome, {{ auth.currentUser }}!</h2>
</template>