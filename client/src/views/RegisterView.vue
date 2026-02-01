<script setup>
import { ref } from "vue";
import StudentRegisterForm from "@/components/StudentRegisterForm.vue";

const isStudent = ref(true);
</script>

<template>
    <div class="row justify-content-center">
        <div class="col-6">
            <template v-if="isStudent">
                <a href="#" @click="isStudent = !isStudent">Are you a company? Click here.</a>
                <StudentRegisterForm />
            </template>
            <template v-else>
                <a href="#" @click="isStudent = !isStudent">Are you a student? Click here.</a>
            </template>
        </div>
    </div>
</template>