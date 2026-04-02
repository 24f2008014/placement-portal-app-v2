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

async function getDetails() {
    try {
        const response = await api.get("/users/me");
        inputEmail.value = response.data.email;
    } catch (error) {
        console.error(error);
    }
};

async function submitForm() {
    errors.value = {};
    try {
        const formData = {
            email: inputEmail.value,
            old_password: inputOldPassword.value,
            password: inputPassword.value,
        };
        const response = await api.put("/users/me", formData);
        alert.addAlert("Account info updated.", "success");
        inputOldPassword.value = null;
        inputPassword.value = null;
    } catch (error) {
        console.error(error.response.data);
        // alert.addAlert(error.response.data, "error");
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json);
        }
    }
}

onMounted(() => {
    getDetails();
    markRequiredFields();
});
</script>

<template>
    <form class="border px-3 py-3 needs-validation body-bg-tertiary" @submit.prevent="submitForm">
        <div class="mb-3">
            <label for="inputEmail" class="form-label">Email Address</label>
            <input type="email" class="form-control" :class="{ 'is-invalid': errors.email }" id="inputEmail" v-model="inputEmail" required aria-describedby="inputEmailValidation">
            <div v-if="errors.email" class="invalid-feedback" id="inputEmailValidation">{{ errors.email[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputOldPassword" class="form-label">Old Password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.old_password }" id="inputOldPassword" v-model="inputOldPassword" required aria-describedby="inputOldPasswordValidation">
            <div v-if="errors.old_password" class="invalid-feedback" id="inputOldPasswordValidation">{{ errors.old_password[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputPassword" class="form-label">New Password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.password }" id="inputPassword" v-model="inputPassword" required aria-describedby="inputPasswordValidation" minlength="6">
            <div id="PasswordHelp" class="form-text">Must have at least 6 characters.</div>
            <div v-if="errors.password" class="invalid-feedback" id="inputPasswordValidation">{{ errors.password[0] }}</div>
        </div>
        <button type="submit" class="btn btn-sm btn-primary mb-2">Update</button>
    </form>
</template>