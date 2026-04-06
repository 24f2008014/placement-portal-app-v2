<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { useRouter } from "vue-router";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";
import { useAlertStore } from "@/stores/alert";

const alert = useAlertStore();
const router = useRouter();
const errors = ref({});
const inputEmail = ref();
const inputPassword = ref();
const inputName = ref();
const inputIndustry = ref("");
const inputDescription = ref();
const inputContactEmail = ref();
const inputContactPhoneNumber = ref();
const inputWebsite = ref();
const inputLocation = ref();
const industries = ref("");
const loading = ref(true);

async function submitForm() {
    errors.value = {};
    loading.value = true;
    try {
        const formData = {
            email: inputEmail.value,
            password: inputPassword.value,
            profile: {
                type: "company",
                name: inputName.value,
                industry_id: inputIndustry.value,
                description: inputDescription.value,
                contact_email: inputContactEmail.value,
                contact_phone_number: inputContactPhoneNumber.value,
                website: inputWebsite.value,
                location: inputLocation.value,
            }
        };
        await api.post("/register", formData);
        alert.addAlert("Account successfully created.", "success");
        router.push({ name: "login" });
    } catch (error) {
        console.error(error.response.data);
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    try {
        markRequiredFields();
        const response = await api.get("/industries");
        industries.value = response.data;
        loading.value = false;
    } catch (error) {
        alert.addAlert(error.response.data.description, "error");
        console.error(error);
    }
});
</script>

<template>
    <h3 class="display-6">Company Registration</h3>
    <hr class="mb-4">
    <form class="border px-3 py-3 needs-validation" @submit.prevent="submitForm">
        <div class="mb-3">
            <label for="inputEmail" class="form-label">Email address</label>
            <input type="email" class="form-control" :class="{ 'is-invalid': errors.email }" id="inputEmail" v-model="inputEmail" required aria-describedby="inputEmailValidation">
            <div v-if="errors.email" class="invalid-feedback" id="inputEmailValidation">{{ errors.email[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputPassword" class="form-label">Password</label>
            <input type="password" class="form-control" :class="{ 'is-invalid': errors.password }" id="inputPassword" v-model="inputPassword" required aria-describedby="inputPasswordValidation" minlength="6">
            <div id="passwordHelp" class="form-text">Must be at least 6 characters.</div>
            <div v-if="errors.password" class="invalid-feedback" id="inputPasswordValidation">{{ errors.password[0] }}</div>
        </div>

        <div class="mb-3">
            <label for="inputName" class="form-label">Company Name</label>
            <input type="text" class="form-control" :class="{ 'is-invalid': errors.name }" id="inputName" v-model="inputName" required aria-describedby="inputNameValidation">
            <div v-if="errors.name" class="invalid-feedback" id="inputNameValidation">{{ errors.name[0] }}</div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputIndustry" class="form-label">Industry</label>
                <select id="inputIndustry" class="form-select" v-model="inputIndustry" required :class="{ 'is-invalid': errors.industry_id }" aria-describedby="inputIndustryValidation">
                    <option value="" selected>Select</option>
                    <template v-for="i in industries">
                        <option :value="i.id">{{ i.name }}</option>
                    </template>
                </select>
                <div v-if="errors.industry_id" class="invalid-feedback" id="inputIndustryValidation">{{ errors.industry_id[0] }}</div>
            </div>
            <div class="col">
                <label for="inputWebsite" class="form-label">Website</label>
                <input type="text" class="form-control" :class="{ 'is-invalid': errors.website }" id="inputWebsite" v-model="inputWebsite" required aria-describedby="inputWebsiteValidation">
                <div v-if="errors.website" class="invalid-feedback" id="inputWebsiteValidation">{{ errors.website[0] }}</div>
            </div>
        </div>

        <div class="mb-3">
            <label for="inputDescription" class="form-label">Description</label>
            <textarea class="form-control" :class="{ 'is-invalid': errors.description }" id="inputDescription" v-model="inputDescription" aria-describedby="inputDescriptionValidation" required style="height:100px;" />
            <div id="descriptionHelp" class="form-text">Please provide a brief description of what your company does.</div>
            <div v-if="errors.description" class="invalid-feedback" id="inputDescriptionValidation">{{ errors.description[0] }}</div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputContactEmail" class="form-label">Contact email</label>
                <input type="email" class="form-control" :class="{ 'is-invalid': errors.contact_email }" id="inputContactEmail" v-model="inputContactEmail" required aria-describedby="inputContactEmailValidation">
                <div id="contactEmailHelp" class="form-text">This will be provided to students who want to get in touch with your company.</div>
                <div v-if="errors.contact_email" class="invalid-feedback" id="inputContactEmailValidation">{{ errors.contact_email[0] }}</div>
            </div>
            <div class="col">
                <label for="inputContactPhoneNumber" class="form-label">Contact phone number</label>
                <input type="tel" class="form-control" :class="{ 'is-invalid': errors.contact_phone_number }" id="inputContactPhoneNumber" v-model="inputContactPhoneNumber" aria-describedby="inputContactPhoneNumberValidation" placeholder="+91 ..." pattern="[0-9]{10}">
                <div id="contactPhoneNumberHelp" class="form-text">This will be provided to students who want to get in touch with your company.</div>
                <div v-if="errors.contact_phone_number" class="invalid-feedback" id="inputContactPhoneNumberValidation">{{ errors.contact_phone_number[0] }}</div>
            </div>
        </div>

        <div class="mb-3">
            <label for="inputLocation" class="form-label">Location</label>
            <input type="text" class="form-control" :class="{ 'is-invalid': errors.location }" id="inputLocation" v-model="inputLocation" aria-describedby="inputLocationValidation" placeholder="Ex. Chennai" required>
            <div v-if="errors.location" class="invalid-feedback" id="inputLocationValidation">{{ errors.location[0] }}</div>
        </div>

        <button type="submit" class="btn btn-primary mb-3" :disabled="loading">Submit</button>
    </form>
</template>