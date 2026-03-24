<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useRoute, useRouter } from "vue-router";
import { flattenResponse } from "@/utils/helpers";
import { formatDate } from "@/utils/helpers";

const router = useRouter();
const route = useRoute();
const loading = ref(true);
const student = ref(null);
const errors = ref({});
const auth = useAuthStore();
const departments = ref(null);

async function getDepartments() {
    try {
        const response = await api.get("/departments");
        departments.value = response.data;
        console.log(departments.value);
    }
    catch (error) {
        console.log(error);
    }
};

async function getStudent() {
    try {
        const response = await api.get(`/students/${route.params.id}`);
        student.value = response.data;
        loading.value = false;
    }
    catch (error) {
        console.log(error);
    }
}

const applications_url = `/students/${route.params.id}/applications`
const applications_route_name = "application"
const applications_fields = {
    "ID": "id",
    "Status": "status"
}

onMounted(() => {
    getDepartments();
    getStudent();
})
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Student</h6>
            <p class="lead text-muted">Student ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "company_positions" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Students
                    </button>
                    <button type="button" class="btn btn-success btn-sm" @click='router.push({ "name": "student_dashboard" })'>
                        <i class="bi bi-graph-up me-2"></i>Dashboard
                    </button>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">

    <div class="row mb-4" v-if="!loading">
        <div class="col">
            <h6 class="text-primary-emphasis">First Name</h6>
            <p>{{ student.first_name }}</p>
            <h6 class="text-primary-emphasis">Last Name</h6>
            <p>{{ student.last_name }}</p>
        </div>
        <div class="col">
            <h6 class="text-primary-emphasis">Roll No.</h6>
            <p>{{ student.roll_number }}</p>
            <h6 class="text-primary-emphasis">Email</h6>
            <p>{{ student.user.email }}</p>
        </div>
        <div class="col">
            <h6 class="text-primary-emphasis">Date of Birth</h6>
            <p>{{ formatDate(student.date_of_birth) }}</p>
            <h6 class="text-primary-emphasis">Gender</h6>
            <p>{{ student.gender }}</p>
        </div>
        <div class="col">
            <h6 class="text-primary-emphasis">CGPA</h6>
            <p>{{ student.cgpa }}</p>
            <h6 class="text-primary-emphasis">Graduation Year</h6>
            <p>{{ student.graduation_year }}</p>
        </div>
        <div class="col">
            <h6 class="text-primary-emphasis">Branch</h6>
            <p>{{ student.branch.name }}</p>
            <h6 class="text-primary-emphasis">Resume</h6>
            <p>{{ student.resume_url ? student.resume_url : "N/A" }}</p>
        </div>
    </div>    
    <div class="row mb-4" v-else><p>Loading...</p></div>
    <div class="row" v-if="auth.currentUser.role=='admin'"">
        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#StudentStatusModal">
            Launch demo modal
        </button>
        <div class="col">
            <div class="modal fade" tabindex="-1" id="StudentStatusModal" aria-labelledby="StudentStatusModalTitle">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="StudentStatusModalTitle">Change Student's Status</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to change student #{{ $route.params.id }}'s status?</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary">Save changes</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">

    <div class="row mb-4" v-if="auth.currentUser.role=='admin'"">
        <div class="col">
            <h3 class="mb-3">Applications Made</h3>
            <div class="col" v-if="!loading">
                <PaginatedTable :url="applications_url" :fields="applications_fields" :item_route_name="applications_route_name" />
            </div>
            <div v-else>Loading...</div>
        </div>
    </div>
</template>