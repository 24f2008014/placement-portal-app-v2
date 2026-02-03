<script setup>
import NavBar from "@/components/NavBar.vue";
</script>

<template>
    <NavBar />
    <div class="container-xxl px-5 py-4 shadow rounded border border-dark-subtle my-5">
        <RouterView />
    </div>
</template>