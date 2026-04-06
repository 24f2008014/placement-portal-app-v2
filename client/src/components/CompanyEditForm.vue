<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";
import { useAlertStore } from "@/stores/alert";

const alert = useAlertStore();
const errors = ref({});
const loading = ref(true);
const industries = ref("");

const inputName = ref();
const inputIndustry = ref("");
const inputWebsite = ref();
const inputDescription = ref();
const inputContactEmail = ref();
const inputContactPhoneNumber = ref();
const inputLocation = ref();

async function submitForm() {
    errors.value = {};
    loading.value = true;
    try {
        const formData = {
            name: inputName.value,
            industry_id: inputIndustry.value,
            website: inputWebsite.value,
            description: inputDescription.value,
            contact_email: inputContactEmail.value,
            contact_phone_number: inputContactPhoneNumber.value,
            location: inputLocation.value,
        };
        const response = await api.put("/companies/me", formData);

        inputName.value = response.data.name;
        inputIndustry.value = response.data.industry_id;
        inputWebsite.value = response.data.website;
        inputDescription.value = response.data.description;
        inputContactEmail.value = response.data.contact_email;
        inputContactPhoneNumber.value = response.data.contact_phone_number;
        inputLocation.value = response.data.location;

        alert.addAlert("Company profile updated.", "success");
    } catch (error) {
        console.error(error.response.data);
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json);
        }
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    try {
        markRequiredFields();
        const [industriesRes, companyRes] = await Promise.all([
            api.get("/industries"),
            api.get("/companies/me")
        ]);

        industries.value = industriesRes.data;
        inputName.value = companyRes.data.name;
        inputIndustry.value = companyRes.data.industry_id;
        inputWebsite.value = companyRes.data.website;
        inputDescription.value = companyRes.data.description;
        inputContactEmail.value = companyRes.data.contact_email;
        inputContactPhoneNumber.value = companyRes.data.contact_phone_number;
        inputLocation.value = companyRes.data.location;
        loading.value = false;
    } catch (error) {
        alert.addAlert(error.response.data.description, "error");
        console.error(error);
    }
});
</script>

<template>
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
            <textarea class="form-control" :class="{ 'is-invalid': errors.description }" id="inputDescription" v-model="inputDescription" aria-describedby="inputDescriptionValidation" required style="height:100px;" />
            <div id="descriptionHelp" class="form-text">Please provide a brief description of what your company does.</div>
            <div v-if="errors.description" class="invalid-feedback" id="inputDescriptionValidation">{{ errors.description[0] }}</div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputContactEmail" class="form-label">Contact Email</label>
                <input type="email" class="form-control" :class="{ 'is-invalid': errors.contact_email }" id="inputContactEmail" v-model="inputContactEmail" required aria-describedby="inputContactEmailValidation">
                <div id="contactEmailHelp" class="form-text">This will be provided to students who want to get in touch with your company.</div>
                <div v-if="errors.contact_email" class="invalid-feedback" id="inputContactEmailValidation">{{ errors.contact_email[0] }}</div>
            </div>
            <div class="col">
                <label for="inputContactPhoneNumber" class="form-label">Contact Phone Number</label>
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

        <div class="row">
            <div class="col d-flex">
                <button type="submit" class="btn btn-sm btn-primary mb-2" :disabled="loading">Update</button>
            </div>
        </div>
    </form>
</template>