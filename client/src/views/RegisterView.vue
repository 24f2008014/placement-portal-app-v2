<script setup>
import { ref } from "vue";
import StudentRegisterForm from "@/components/StudentRegisterForm.vue";
import CompanyRegisterForm from "@/components/CompanyRegisterForm.vue";

const role = ref(null);
</script>

<template>
    <div class="row align-items-center justify-content-center">
        <div class="col-6">
            <div class="row">
                <div class="col-auto">
                    <i class="bi bi-person-add" style="font-size: 3.5rem"></i>
                </div>
                <div class="col">
                    <h6 class="display-6">Register</h6>
                    <p class="lead text-muted">Already have an account? <RouterLink :to="{ name: 'login' }">Login here.</RouterLink></p>
                </div>
            </div>
            <hr class="mb-4">
        </div>
    </div>

    <div v-if="!role" class="row justify-content-center text-center">
        <div class="col-3">
            <div class="card shadow">
                <div class="card-body">
                    <h6 class="card-title display-6">Student</h6>
                    <p><i class="bi bi-book" style="font-size: 2rem;"></i></p>
                    <p class="card-text lead">As a student, you can apply to open position listings.</p>
                    <a href="#" class="stretched-link" @click="role='student'"></a>
                </div>
            </div>
        </div>
        <div class="col-3">
            <div class="card shadow">
                <div class="card-body">
                    <h6 class="card-title display-6">Company</h6>
                    <p><i class="bi bi-briefcase" style="font-size: 2rem;"></i></p>
                    <p class="card-text lead">As a company, you can create listings and recruit students.</p>
                    <a href="#" class="stretched-link" @click="role='company'"></a>
                </div>
            </div>
        </div>
    </div>

    <div class="row justify-content-center">
        <div class="col-6">
            <template v-if="role=='student'">
                <div class="mb-2">
                    <a href="#" @click="role='company'">Are you a company? Click here.</a>
                </div>
                <StudentRegisterForm />
            </template>
            <template v-else-if="role=='company'">
                <a href="#" @click="role='student'">Are you a student? Click here.</a>
                <CompanyRegisterForm />
            </template>
        </div>
    </div>
</template>