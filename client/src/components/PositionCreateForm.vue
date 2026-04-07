<script setup>
import { onMounted, ref, computed } from "vue";
import { api } from "@/utils/api";
import { useRouter } from "vue-router";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";
import { useAlertStore } from "@/stores/alert";

const alert = useAlertStore();
const router = useRouter();
const errors = ref({});
const loading = ref(true);

const inputRole = ref();
const inputSalaryMin = ref();
const inputSalaryMax = ref();
const inputDescription = ref();
const inputDeadline = ref();
const inputMinCgpa = ref();
const inputDepartments = ref([]);
const departments = ref("");
const inputDepartmentsValid = computed(() => inputDepartments.value.length > 0);

async function submitForm() {
    errors.value = {};
    loading.value = true;
    try {
        const formData = {
            role: inputRole.value,
            salary_min: inputSalaryMin.value,
            salary_max: inputSalaryMax.value,
            description: inputDescription.value,
            deadline: inputDeadline.value,
            min_cgpa: inputMinCgpa.value,
            department_ids: inputDepartments.value.map(Number)
        };
        const response = await api.post("/positions", formData);
        const position_id = response.data.id;
        alert.addAlert("Successfully created a new position.", "success");
        router.push({ name: "position", params: { id: position_id } });
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
        const response = await api.get("/departments");
        departments.value = response.data;
        for (const d of departments.value) {
            inputDepartments.value.push(d.id);
        }
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
            <label for="inputRole" class="form-label">Role</label>
            <input type="text" class="form-control" :class="{ 'is-invalid': errors.role }" id="inputRole" v-model="inputRole" required aria-describedby="inputRoleValidation" placeholder="Ex. Engineer">
            <div v-if="errors.role" class="invalid-feedback" id="inputRoleValidation">{{ errors.role[0] }}</div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputSalaryMin" class="form-label">Min. Salary (monthly)</label>
                <input type="number" class="form-control" id="inputSalaryMin" :class="{ 'is-invalid': errors.salary_min }" v-model="inputSalaryMin" min="0" required aria-describedby="inputSalaryMinValidation">
                <div v-if="errors.salary_min" class="invalid-feedback" id="inputSalaryMinValidation">{{ errors.salary_min[0] }}</div>
            </div>
            <div class="col">
                <label for="inputSalaryMax" class="form-label">Max. Salary (monthly)</label>
                <input type="number" class="form-control" id="inputSalaryMax" :class="{ 'is-invalid': errors.salary_max }" v-model="inputSalaryMax" min="0" required aria-describedby="inputSalaryMaxValidation">
                <div v-if="errors.salary_max" class="invalid-feedback" id="inputSalaryMaxValidation">{{ errors.salary_max[0] }}</div>
            </div>
        </div>

        <div class="mb-3">
            <label for="inputDescription" class="form-label">Job Description</label>
            <textarea class="form-control" :class="{ 'is-invalid': errors.description }" id="inputDescription" v-model="inputDescription" required style="height:100px;" aria-describedby="inputDescriptionValidation" placeholder="A brief description of what the job might entail - duties, required skills, etc." />
            <div v-if="errors.description" class="invalid-feedback" id="inputDescriptionValidation">{{ errors.description[0] }}</div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputMinCgpa" class="form-label">Minimum CGPA</label>
                <input type="number" step="0.01" class="form-control" id="inputMinCgpa" :class="{ 'is-invalid': errors.min_cgpa }" v-model="inputMinCgpa" min="0" max="10" required aria-describedby="inputMinCgpaValidation">
                <div v-if="errors.min_cgpa" class="invalid-feedback" id="inputMinCgpaValidation">{{ errors.min_cgpa[0] }}</div>
            </div>
            <div class="col">
                <label for="inputDeadline" class="form-label">Deadline</label>
                <input class="form-control" type="datetime-local" :class="{ 'is-invalid': errors.deadline }"id="inputDeadline" v-model="inputDeadline" required aria-describedby="inputDeadlineValidation" :min="new Date().toISOString().slice(0, 16)">
                <div v-if="errors.deadline" class="invalid-feedback" id="inputDeadlineValidation">{{ errors.deadline[0] }}</div>
            </div>
        </div>

        <div class="mb-3">
            <p class="mb-2">Eligible Departments</p>
            <hr>
            <template v-if="!loading">
                <template v-for="d in departments">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" :value="d.id" :id="`d-${d.id}`" v-model="inputDepartments">
                        <label class="form-check-label" :for="`d-${d.id}`">{{ d.name }}</label>
                    </div>
                </template>
                <div v-if="!inputDepartmentsValid">
                    <p class="text-danger">Please select at least one eligible department.</p>
                </div>
            </template>
            <div v-else><div class="spinner-border spinner-border-sm text-center ms-1"></div></div>
        </div>

        <button type="submit" class="btn btn-primary mb-3" :disabled="loading || !inputDepartmentsValid">Submit</button>
    </form>
</template>