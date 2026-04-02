<script setup>
import StudentEditForm from "@/components/StudentEditForm.vue";
import CompanyEditForm from "@/components/CompanyEditForm.vue";
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <div class="row align-items-center justify-content-center">
        <div class="col-6">
            <div class="row">
                <div class="col-auto">
                    <i class="bi bi-person-circle" style="font-size: 3.5rem"></i>
                </div>
                <div class="col">
                    <h6 class="display-6">Your Profile</h6>
                    <p class="lead text-muted">You can view and edit your profile details here.</p>
                </div>
            </div>
            <hr class="mb-4">
        </div>
    </div>
    <div class="row justify-content-center">
        <div class="col-6">
            <StudentEditForm v-if="auth.currentUser.role == 'student'"/>
            <CompanyEditForm v-else />
        </div>
    </div>
</template>