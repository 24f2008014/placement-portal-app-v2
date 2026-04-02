<script setup>
import LoginForm from "@/components/LoginForm.vue";
</script>

<template>
    <div class="row align-items-center justify-content-center">
        <div class="col-6">
            <div class="row">
                <div class="col-auto">
                    <i class="bi bi-box-arrow-in-right" style="font-size: 3.5rem"></i>
                </div>
                <div class="col">
                    <h6 class="display-6">Login</h6>
                    <p class="lead text-muted">Don't have an account? <RouterLink :to="{ name: 'register' }">Register here.</RouterLink></p>
                </div>
            </div>
            <hr class="mb-4">
        </div>
    </div>

    <div class="row justify-content-center mb-4">
        <div class="col-6">
            <LoginForm />
        </div>
    </div>
</template>