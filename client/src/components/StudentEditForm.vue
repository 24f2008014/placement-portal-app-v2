<script setup>
import { onMounted, ref, computed, handleError } from "vue";
import { api } from "@/utils/api";
import { useAlertStore } from "@/stores/alert";
import { markRequiredFields, flattenResponse } from "@/utils/helpers";

const alert = useAlertStore();
const errors = ref({});
const inputRollNumber = ref();
const inputFirstName = ref();
const inputLastName = ref();
const inputDateOfBirth = ref();
const inputGender = ref();
const inputDepartment = ref();
const inputBranch = ref();
const inputGraduationYear = ref();
const inputCgpa = ref();
const inputResume = ref();
const resumeUrl = ref();
const departments = ref("");
const branches = ref("");
const updateSuccessful = ref(false);

const available_branches = computed(() => {
    if (inputDepartment.value != "" && branches.value != "") {
        return branches.value.filter((b) => b.department_id == inputDepartment.value);
    }
    return "";
});

const inputBranchDisabled = computed(() => {
    return inputDepartment.value == "";
});

async function getDepartments() {
    try {
        const response = await api.get("/departments");
        departments.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
};

async function getBranches() {
    try {
        const response = await api.get("/branches");
        branches.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
};

async function getDetails() {
    try {
        const response = await api.get("/students/me");
        console.log(response.data);
        inputRollNumber.value = response.data.roll_number;
        inputFirstName.value = response.data.first_name;
        inputLastName.value = response.data.last_name;
        inputDateOfBirth.value = response.data.date_of_birth.split("T")[0];
        inputGender.value = response.data.gender;
        inputDepartment.value = response.data.branch.department_id;
        inputBranch.value = response.data.branch_id;
        inputGraduationYear.value = response.data.graduation_year;
        inputCgpa.value = response.data.cgpa;
        resumeUrl.value = response.data.resume_url;
    }
    catch (error) {
        console.log(error);
    }
}

async function submitForm() {
    errors.value = {};
    try {
        const formData = new FormData();
        formData.append("roll_number", inputRollNumber.value);
        formData.append("first_name", inputFirstName.value);
        formData.append("last_name", inputLastName.value);
        formData.append("date_of_birth", inputDateOfBirth.value);
        formData.append("gender", inputGender.value);
        formData.append("branch_id", inputBranch.value);
        formData.append("graduation_year", inputGraduationYear.value);
        formData.append("cgpa", inputCgpa.value);
        if (inputResume.value) {
            formData.append("resume", inputResume.value);
        }
        const response = await api.put("/students/me", formData, { headers: { "Content-Type": "multipart/form-data" } });
        updateSuccessful.value = true;
        alert.addAlert("Successfully updated your profile.", "success");
    }
    catch (error) {
        console.log(error.response.data)
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
};

function handleFileUpload(event) {
    inputResume.value = event.target.files[0];
};

async function viewResume() {
    try {
        const response = await api.get(`/uploads/resumes/${resumeUrl.value}`, {responseType: "blob"});
        const blob = new Blob([response.data], {type: "application/pdf"})
        const objectURL = URL.createObjectURL(blob);
        window.open(objectURL, "_blank");
    }
    catch (error) {
        console.log(error);
    }
};

onMounted(() => {
    getDepartments();
    getBranches();
    getDetails();
    markRequiredFields();
});
</script>

<template>
    <h3 class="display-6">Your Profile</h3>
    <hr class="mb-4">
    <p v-if="updateSuccessful" class="text-success">Successfully updated your profile.</p>
    <form class="border px-3 py-3 needs-validation" @submit.prevent="submitForm">
        <div class="mb-3">
            <label for="inputRollNumber" class="form-label">Roll number</label>
            <input type="text" class="form-control" :class="{ 'is-invalid': errors.roll_number }" id="inputRollNumber" v-model="inputRollNumber" required aria-describedby="inputRollNumberValidation">
            <div v-if="errors.roll_number" class="invalid-feedback" id="inputRollNumberValidation">{{ errors.roll_number[0] }}</div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputFirstName" class="form-label">First name</label>
                <input type="text" class="form-control" :class="{ 'is-invalid': errors.first_name }" id="inputFirstName" v-model="inputFirstName" required aria-describedby="inputFirstNameValidation">
                <div v-if="errors.first_name" class="invalid-feedback" id="inputFirstNameValidation">{{ errors.first_name[0] }}</div>
            </div>
            <div class="col">
                <label for="inputLastName" class="form-label">Last name</label>
                <input type="text" class="form-control" :class="{ 'is-invalid': errors.last_name }" id="inputLastName" v-model="inputLastName" required aria-describedby="inputFirstNameValidation">
                <div v-if="errors.last_name" class="invalid-feedback" id="inputLastNameValidation">{{ errors.last_name[0] }}</div>
            </div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputDateOfBirth" class="form-label">Date of birth</label>
                <input type="date" class="form-control" :class="{ 'is-invalid': errors.date_of_birth }" id="inputDateOfBirth" v-model="inputDateOfBirth" min="1900-01-01" max="2026-01-01" aria-describedby="inputDateOfBirthValidation">
                <div v-if="errors.date_of_birth" class="invalid-feedback" id="inputDateOfBirthValidation">{{ errors.date_of_birth[0] }}</div>
            </div>
            <div class="col">
                <label for="inputGender" class="form-label">Gender</label>
                <select id="inputGender" class="form-select" :class="{ 'is-invalid': errors.gender }" v-model="inputGender" required aria-describedby="inputGenderValidation">
                    <option value="" selected>Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                </select>
                <div v-if="errors.gender" class="invalid-feedback" id="inputGenderValidation">{{ errors.gender[0] }}</div>
            </div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputDepartment" class="form-label">Department</label>
                <select id="inputDepartment" class="form-select" v-model="inputDepartment" required :class="{ 'is-invalid': errors.department_id }" aria-describedby="inputDepartmentValidation">
                    <option value="" selected>Select</option>
                    <template v-for="d in departments">
                        <option :value="d.id">{{ d.name }}</option>
                    </template>
                </select>
                <div v-if="errors.department_id" class="invalid-feedback" id="inputDepartmentValidation">{{ errors.department_id[0] }}</div>
            </div>
            <div class="col">
                <label for="inputBranch" class="form-label">Branch</label>
                <select id="inputBranch" class="form-select" v-model="inputBranch" required :disabled="inputBranchDisabled" :class="{ 'is-invalid': errors.branch_id }" aria-describedby="inputBranchValidation">
                    <option value="" selected>Select</option>
                    <template v-for="b in available_branches">
                        <option :value="b.id">{{ b.name }}</option>
                    </template>
                </select>
                <div v-if="errors.branch_id" class="invalid-feedback" id="inputBranchValidation">{{ errors.branch_id[0] }}</div>
            </div>
        </div>

        <div class="row mb-3">
            <div class="col">
                <label for="inputGraduationYear" class="form-label">Graduation year</label>
                <input class="form-control" type="number" min="2000" max="2099" :class="{ 'is-invalid': errors.graduation_year }"id="inputGraduationYear" v-model="inputGraduationYear" required aria-describedby="inputGraduationYearValidation">
                <div v-if="errors.graduation_year" class="invalid-feedback" id="inputGraduationYearValidation">{{ errors.graduation_year[0] }}</div>
            </div>
            <div class="col">
                <label for="inputCgpa" class="form-label">Current CGPA</label>
                <input type="number" class="form-control" id="inputCgpa" :class="{ 'is-invalid': errors.cgpa }" v-model="inputCgpa" min="0" max="10" required aria-describedby="inputCgpaValidation">
                <div v-if="errors.cgpa" class="invalid-feedback" id="inputCgpaValidation">{{ errors.cgpa[0] }}</div>
            </div>
        </div>

        <div class="mb-3">
            <label for="inputResume" class="form-label">Upload resume (PDF)
            </label>
            <p v-if="resumeUrl"><a @click="viewResume" style="color: lightblue; cursor: pointer">View Existing ({{ resumeUrl }})</a></p>
            <input class="form-control" type="file" id="inputResume" accept=".pdf" @change="handleFileUpload">
        </div>

        <button type="submit" class="btn btn-primary mb-3">Submit</button>
    </form>
</template>