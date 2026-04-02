<script setup>
import { onMounted, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { markRequiredFields } from "@/utils/helpers";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const errors = ref({});
const loading = ref(false);
const inputEmail = ref();
const inputPassword = ref();

async function submitForm() {
    errors.value = {};
    loading.value = true;
    try {
        const response = await auth.login(inputEmail.value, inputPassword.value);
        router.push(route.query.next || "/");
    } catch (error) {
        console.error(error.response.data);
        errors.value = error.response.data;
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    markRequiredFields();
});
</script>

<template>
    <form class="border px-3 py-3 needs-validation" @submit.prevent="submitForm">
        <div class="mb-3">
            <label for="inputEmail" class="form-label">Email Address</label>
            <input type="email" class="form-control" :class="{ 'is-invalid': errors.email }" id="inputEmail" v-model="inputEmail" required aria-describedby="inputEmailValidation">
            <div v-if="errors.email" class="invalid-feedback" id="inputEmailValidation">{{ errors.email[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputPassword" class="form-label">Password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.password }" id="inputPassword" v-model="inputPassword" required aria-describedby="inputPasswordValidation">
            <div v-if="errors.password" class="invalid-feedback" id="inputPasswordValidation">{{ errors.password[0] }}</div>
        </div>

        <button type="submit" class="btn btn-sm btn-primary mb-2">Login
            <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
        </button>

        <div v-if="errors.code == '401'" class="mt-2 mb-2 text-danger">
            Please check your login details and try again.
        </div>
    </form>
</template>