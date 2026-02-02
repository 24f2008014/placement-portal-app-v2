<script setup>
import StudentEditForm from "@/components/StudentEditForm.vue";
import CompanyEditForm from "@/components/CompanyEditForm.vue";
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
</script>

<template>
    <div class="row justify-content-center">
        <div class="col-6">
            <StudentEditForm v-if="auth.currentUser.role == 'student'"/>
            <CompanyEditForm v-else />
        </div>
    </div>
</template>