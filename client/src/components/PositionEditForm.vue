<script setup>
import { onMounted, ref, computed } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";

const router = useRouter();
const route = useRoute();
const errors = ref({});

const positionId = ref();
const inputRole = ref();
const inputSalaryMin = ref();
const inputSalaryMax = ref();
const inputDescription = ref();
const inputDeadline = ref();
const inputMinCgpa = ref();

async function getDetails() {
    try {
        const response = await api.get(`/positions/${route.params.id}`);
        inputRole.value = response.data.role;
        inputSalaryMin.value = response.data.salary_min;
        inputSalaryMax.value = response.data.salary_max;
        inputDescription.value = response.data.description;
        inputDeadline.value = response.data.deadline;
        inputMinCgpa.value = response.data.min_cgpa;
        positionId.value = response.data.id;
    }
    catch (error) {
        console.log(error);
    }
};

async function submitForm() {
    // errors.value = {};
    // try {
    //     const formData = {
    //         role: inputRole.value,
    //         salary_min: inputSalaryMin.value,
    //         salary_max: inputSalaryMax.value,
    //         description: inputDescription.value,
    //         deadline: inputDeadline.value,
    //         min_cgpa: inputMinCgpa.value
    //     }
    //     const response = await api.post("/positions", formData);
    //     const position_id = response.data.id;
    //     router.push({ name: `/position/${position_id}` });
    // }
    // catch (error) {
    //     console.log(error.response.data)
    //     if ("errors" in error.response.data) {
    //         errors.value = flattenResponse(error.response.data.errors.json)
    //     }
    // }
};

onMounted(() => {
    // markRequiredFields();
    getDetails();
});
</script>

<template>
    <div class="row">
        <div class="col">
            <h3 class="display-6 mb-2">Position #{{ positionId }}</h3>
            <button type="button" class="btn btn-primary btn-sm mb-3" @click='router.push({ "name": "company_positions" })'>
                <i class="bi bi-arrow-left me-2"></i>All Positions
            </button>
            <hr class="mb-4">
            <form class="border px-3 py-3 needs-validation" @submit.prevent="submitForm">
                <div class="mb-3">
                    <label for="inputRole" class="form-label">Job role (title)</label>
                    <input type="text" class="form-control" :class="{ 'is-invalid': errors.role }" id="inputRole" v-model="inputRole" required aria-describedby="inputRoleValidation" disabled>
                    <div v-if="errors.role" class="invalid-feedback" id="inputRoleValidation">{{ errors.role[0] }}</div>
                </div>

                <div class="row mb-3">
                    <div class="col">
                        <label for="inputSalaryMin" class="form-label">Minimum salary</label>
                        <input type="number" class="form-control" id="inputSalaryMin" :class="{ 'is-invalid': errors.salary_min }" v-model="inputSalaryMin" min="0" required aria-describedby="inputSalaryMinValidation" disabled>
                        <div v-if="errors.salary_min" class="invalid-feedback" id="inputSalaryMinValidation">{{ errors.salary_min[0] }}</div>
                    </div>
                    <div class="col">
                        <label for="inputSalaryMax" class="form-label">Maximum salary</label>
                        <input type="number" class="form-control" id="inputSalaryMax" :class="{ 'is-invalid': errors.salary_max }" v-model="inputSalaryMax" min="0" required aria-describedby="inputSalaryMaxValidation" disabled>
                        <div v-if="errors.salary_max" class="invalid-feedback" id="inputSalaryMaxValidation">{{ errors.salary_max[0] }}</div>
                    </div>
                </div>

                <div class="mb-3">
                    <label for="inputDescription" class="form-label">Job description</label>
                    <input type="text" class="form-control" :class="{ 'is-invalid': errors.description }" id="inputDescription" v-model="inputDescription" required aria-describedby="inputDescriptionValidation" disabled>
                    <div v-if="errors.description" class="invalid-feedback" id="inputDescriptionValidation">{{ errors.description[0] }}</div>
                </div>

                <div class="row mb-3">
                    <div class="col">
                        <label for="inputDeadline" class="form-label">Application deadline</label>
                        <input class="form-control" type="datetime-local" :class="{ 'is-invalid': errors.deadline }"id="inputDeadline" v-model="inputDeadline" required aria-describedby="inputDeadlineValidation" disabled>
                        <div v-if="errors.deadline" class="invalid-feedback" id="inputDeadlineValidation">{{ errors.deadline[0] }}</div>
                    </div>
                    <div class="col">
                        <label for="inputMinCgpa" class="form-label">Minimum CGPA</label>
                        <input type="number" class="form-control" id="inputMinCgpa" :class="{ 'is-invalid': errors.min_cgpa }" v-model="inputMinCgpa" min="0" max="10" required aria-describedby="inputMinCgpaValidation" disabled>
                        <div v-if="errors.min_cgpa" class="invalid-feedback" id="inputMinCgpaValidation">{{ errors.min_cgpa[0] }}</div>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary mb-3" disabled>Submit</button>
            </form>
        </div>
    </div>
</template>