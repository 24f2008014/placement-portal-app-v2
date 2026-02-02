<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";
import { useAlertStore } from "@/stores/alert";

const alert = useAlertStore();
const updated = ref(false);
const errors = ref({});
const inputName = ref();
const inputIndustry = ref("");
const inputDescription = ref();
const inputContactEmail = ref();
const inputContactPhoneNumber = ref();
const inputWebsite = ref();
const inputLocation = ref();
const industries = ref("");

async function getIndustries() {
    try {
        const response = await api.get("/industries");
        industries.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
};

async function getDetails() {
    try {
        const response = await api.get("/companies/me");
        inputName.value = response.data.name;
        inputIndustry.value = response.data.industry_id;
        inputDescription.value = response.data.description;
        inputContactEmail.value = response.data.contact_email;
        inputContactPhoneNumber.value = response.data.contact_phone_number;
        inputWebsite.value = response.data.website;
        inputLocation.value = response.data.location;
    }
    catch (error) {
        console.log(error);
    }
}

async function submitForm() {
    errors.value = {};
    try {
        const formData = {
            name: inputName.value,
            industry_id: inputIndustry.value,
            website: inputWebsite.value,
            description: inputDescription.value,
            contact_email: inputContactEmail.value,
            contact_phone_number: inputContactPhoneNumber.value,
            location: inputLocation.value,
        }
        const response = await api.put("/companies/me", formData);
        updated.value = true;
        alert.addAlert("Company profile updated.", "success");
    }
    catch (error) {
        console.log(error.response.data)
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
};

onMounted(() => {
    getIndustries();
    getDetails();
    markRequiredFields();
});
</script>

<template>
    <h3 class="display-6">Company Profile</h3>
    <hr class="mb-4">
    <p v-if="updated" class="text-success">Updated profile.</p>
    <form class="border px-3 py-3 needs-validation" @submit.prevent="submitForm">
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
            <input type="text" class="form-control" :class="{ 'is-invalid': errors.description }" id="inputDescription" v-model="inputDescription" aria-describedby="inputDescriptionValidation" required>
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
                <input type="url" class="form-control" :class="{ 'is-invalid': errors.contact_phone_number }" id="inputContactPhoneNumber" v-model="inputContactPhoneNumber" aria-describedby="inputContactPhoneNumberValidation" placeholder="+91 ...">
                <div id="contactPhoneNumberHelp" class="form-text">This will be provided to students who want to get in touch with your company.</div>
                <div v-if="errors.contact_phone_number" class="invalid-feedback" id="inputContactPhoneNumberValidation">{{ errors.contact_phone_number[0] }}</div>
            </div>
        </div>

        <div class="mb-3">
            <label for="inputLocation" class="form-label">Location</label>
            <input type="text" class="form-control" :class="{ 'is-invalid': errors.location }" id="inputLocation" v-model="inputLocation" aria-describedby="inputLocationValidation" placeholder="Ex. Chennai" required>
            <div v-if="errors.location" class="invalid-feedback" id="inputLocationValidation">{{ errors.location[0] }}</div>
        </div>

        <button type="submit" class="btn btn-primary mb-3">Submit</button>
    </form>
</template>