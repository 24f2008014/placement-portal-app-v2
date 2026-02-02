<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { useAlertStore } from "@/stores/alert";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";

const alert = useAlertStore();
const errors = ref({});
const inputEmail = ref();
const inputOldPassword = ref();
const inputPassword = ref();
const updateSuccessful = ref(false);

async function getDetails() {
    try {
        const response = await api.get("/users/me");
        inputEmail.value = response.data.email;
    }
    catch (error) {
        console.log(error);
    }
}

async function submitForm() {
    errors.value = {};
    try {
        const formData = {
            email: inputEmail.value,
            old_password: inputOldPassword.value,
            password: inputPassword.value,
        }
        const response = await api.put("/users/me", formData);
        updateSuccessful.value = true;
        alert.addAlert("Account info updated.", "success");
        inputOldPassword.value = null;
        inputPassword.value = null;
    }
    catch (error) {
        console.log(error.response.data)
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
};

onMounted(() => {
    getDetails();
    markRequiredFields();
});
</script>

<template>
    <h3 class="display-6">Account Details</h3>
    <hr class="mb-4">
    <p v-if="updateSuccessful" class="text-success">Successfully updated your account info.</p>
    <form class="border px-3 py-3 needs-validation body-bg-tertiary" @submit.prevent="submitForm">
        <div class="mb-3">
            <label for="inputEmail" class="form-label">Email address</label>
            <input type="email" class="form-control" :class="{ 'is-invalid': errors.email }" id="inputEmail" v-model="inputEmail" required aria-describedby="inputEmailValidation">
            <div v-if="errors.email" class="invalid-feedback" id="inputEmailValidation">{{ errors.email[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputOldPassword" class="form-label">Old password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.old_password }" id="inputOldPassword" v-model="inputOldPassword" required aria-describedby="inputOldPasswordValidation">
            <div v-if="errors.old_password" class="invalid-feedback" id="inputOldPasswordValidation">{{ errors.old_password[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputPassword" class="form-label">New password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.password }" id="inputPassword" v-model="inputPassword" required aria-describedby="inputPasswordValidation" minlength="6">
            <div id="PasswordHelp" class="form-text">Must be at least 6 characters.</div>
            <div v-if="errors.password" class="invalid-feedback" id="inputPasswordValidation">{{ errors.password[0] }}</div>
        </div>
        <button type="submit" class="btn btn-primary mb-3">Submit</button>
    </form>
</template>