<script setup>
import { onMounted, ref, computed } from "vue";
import { api, refreshApi } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

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
        const response = await auth.login(inputEmail.value, inputPassword.value)
        const next = route.query.next || "/";
        router.push(next);
    }
    catch (error) {
        console.log("comp caught");
        console.log(error.response.data);
        errors.value = error.response.data;
    }
    finally {
        loading.value = false;
    }
};

onMounted(() => {
    document.querySelectorAll("input[required], select[required]").forEach((e) => {
        document.querySelector(`label[for=${e.id}]`).classList.add("required");
    });
});
</script>

<template>
    <h3 class="display-6">Login</h3>
    <hr class="mb-4">
    <form class="border px-3 py-3 needs-validation" @submit.prevent="submitForm">
        <div class="mb-3">
            <label for="inputEmail" class="form-label">Email address</label>
            <input type="email" class="form-control" :class="{ 'is-invalid': errors.email }" id="inputEmail" v-model="inputEmail" required aria-describedby="inputEmailValidation">
            <div v-if="errors.email" class="invalid-feedback" id="inputEmailValidation">{{ errors.email[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputPassword" class="form-label">Password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.password }" id="inputPassword" v-model="inputPassword" required aria-describedby="inputPasswordValidation">
            <div v-if="errors.password" class="invalid-feedback" id="inputPasswordValidation">{{ errors.password[0] }}</div>
        </div>

        <button type="submit" class="btn btn-primary mb-3">Submit
            <div v-if="loading" class="spinner-border spinner-border-sm text-center ms-1"></div>
        </button>
        <div v-if="errors.code == '401'" class="mb-3 text-danger">Please check your login details and try again.</div>
    </form>
</template>