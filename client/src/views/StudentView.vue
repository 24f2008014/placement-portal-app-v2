<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useRoute, useRouter } from "vue-router";
import { formatDateNoTime } from "@/utils/helpers";
import { useAlertStore } from "@/stores/alert";
import * as bootstrap from "bootstrap";
import Modal from "@/components/Modal.vue";
import { viewResume } from "@/utils/helpers";

const alert = useAlertStore();
const router = useRouter();
const route = useRoute();
const loading = ref(true);
const student = ref(null);
const auth = useAuthStore();
const departments = ref(null);

async function changeStatus() {
    try {
        const newStatus = (student.value.status == "whitelisted") ? "blacklisted" : "whitelisted";
        const response = await api.patch(`/students/${route.params.id}`, { status: newStatus });
        student.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("StudentStatusModal")).hide();
        alert.addAlert(`Successfully updated Student #${route.params.id}'s status.`, "success");
    } catch (error) {
        console.error(error);
        alert.addAlert(error.response.data.description, "error");
    }
}

const applications_endpoint = `/students/${route.params.id}/applications`;
const applications_route = "application";
const applications_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Position ID": {
        name: "position_id",
        filter: true,
        label: "Position ID",
        input: {
            type: "number",
            min: "1"
        }        
    },    
    "Role": {
        name: "position.role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }        
    },
    "Company": {
        name: "position.company.name",
        filter: true,
        label: "Company",
        input: {
            type: "text"
        }
    },
    "Created At": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Updated At": {
        name: "updated_at",
        filter: false,
        type: "date"
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Pending", value: "pending"},
                {label: "Shortlisted", value: "shortlisted"},
                {label: "Selected", value: "selected"},
                {label: "Rejected", value: "rejected"},
                {label: "Withdrawn", value: "withdrawn"}
            ]
        }
    }
};

const placements_endpoint = `/students/${route.params.id}/placements`;
const placements_route = "placement";
const placements_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Application ID": {
        name: "application_id",
        filter: true,
        label: "Application ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Role": {
        name: "application.position.role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }
    },
    "Company": {
        name: "application.position.company.name",
        filter: true,
        label: "Company",
        input: {
            type: "text"
        }
    },
    "Salary": {
        name: "salary",
        filter: true,
        label: "Salary \u2265"
    },
    "Joining Date": {
        name: "joining_date",
        filter: false,
        type: "date"
    },  
    "Created At": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Pending", value: "pending"},
                {label: "Accepted", value: "accepted"},
                {label: "Rejected", value: "rejected"}
            ]
        }
    }
};

const company_applications_endpoint = "/companies/me/applications";
const companyApplicationsFilters = {
    "student_id": route.params.id
};
const company_applications_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Position ID": {
        name: "position_id",
        filter: true,
        label: "Position ID",
        input: {
            type: "number",
            min: "1"
        }        
    },    
    "Role": {
        name: "position.role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }        
    },
    "Created At": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Updated At": {
        name: "updated_at",
        filter: false,
        type: "date"
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Pending", value: "pending"},
                {label: "Shortlisted", value: "shortlisted"},
                {label: "Selected", value: "selected"},
                {label: "Rejected", value: "rejected"}
            ]
        }
    }
};

onMounted(async () => {
    try {
        const [studentRes, departmentsRes] = await Promise.all([
            api.get(`/students/${route.params.id}`),
            api.get("/departments")
        ]);
        student.value = studentRes.data;
        departments.value = departmentsRes.data;
        loading.value = false;
    } catch (error) {
        alert.addAlert(error.response.data.description, "error");
        console.error(error);
    }
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Student</h6>
            <p class="lead text-muted">Student ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button v-if="auth.currentUser.role=='admin'" type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "admin_dashboard" })'><i class="bi bi-arrow-left me-2"></i>Dashboard</button>
                    <button v-else type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "company_dashboard" })'><i class="bi bi-arrow-left me-2"></i>Dashboard</button>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">

    <template v-if="!loading">
        <div class="row mb-3">
            <h3>Student Details</h3>
            <div class="col d-flex mt-2 mb-2">
                <button type="button" v-if="student.resume_url" class="btn btn-sm btn-success" @click="viewResume(student.resume_url)"><i class="bi bi-download me-2"></i>Get Resume</button>
                <button type="button" v-else class="btn btn-sm btn-success" disabled><i class="bi bi-download me-2"></i>Get Resume (N/A)</button>
            </div>
        </div>

        <div class="row mb-4 border rounded mx-0 p-3">
            <div class="col">
                <h6 class="text-primary-emphasis">Name</h6>
                <p>{{ student.first_name }} {{ student.last_name }}</p>
                <h6 class="text-primary-emphasis">Gender</h6>
                <p>{{ student.gender }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Roll No.</h6>
                <p>{{ student.roll_number }}</p>
                <h6 class="text-primary-emphasis">Email</h6>
                <p>{{ student.user.email }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Branch</h6>
                <p>{{ student.branch.name }}</p>
                <h6 class="text-primary-emphasis">Date of Birth</h6>
                <p>{{ formatDateNoTime(student.date_of_birth) }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Graduation Year</h6>
                <p>{{ student.graduation_year }}</p>
                <h6 class="text-primary-emphasis">Signup Date</h6>
                <p>{{ formatDateNoTime(student.user.created_at) }}</p>                
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">CGPA</h6>
                <p>{{ student.cgpa }}</p>
                <h6 class="text-primary-emphasis">Status</h6>
                <p>{{ student.status }}</p>
            </div>
        </div>

        <template v-if="student.bio">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3>Student Bio</h3>
                    <p>{{ student.bio }}</p>
                </div>
            </div>
        </template>

        <template v-if="auth.currentUser.role=='admin'">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ student.status }}</code></h3>
                    <p v-if="student.status=='whitelisted'">This student is <code class="text-success fw-bold">whitelisted</code>. They can freely apply for any open positions.</p>
                    <p v-else>This student is <code class="text-danger fw-bold">blacklisted</code>. They cannot make new job applications.</p>
                    <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#StudentStatusModal"><i class="bi bi-wrench me-2"></i>Change Status</button>
                </div>
                <Modal :title="'Change Status'" :id="'StudentStatusModal'" :yes-label="'Confirm'" @confirm="changeStatus">
                    <template #modal-body>
                        <p v-if="student.status=='whitelisted'">Are you sure you want to change Student #{{ $route.params.id }}'s status from <strong>whitelisted</strong> to <strong>blacklisted</strong>?</p>
                        <p v-else>Are you sure you want to change Student #{{ $route.params.id }}'s status from <strong>blacklisted</strong> to <strong>whitelisted</strong>?</p>                        
                    </template>
                </Modal>
            </div>

            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3 class="mb-3">Applications</h3>
                    <template v-if="!loading">
                        <div class="col mb-4">
                            <PaginatedTable :url="applications_endpoint" :fields="applications_fields" :item_route_name="applications_route" />
                        </div>
                        <hr class="mb-4">

                        <div class="col">
                            <h3 class="mb-3">Placements</h3>
                            <PaginatedTable :url="placements_endpoint" :fields="placements_fields" :item_route_name="placements_route" />
                        </div>
                    </template>
                    <template v-else><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>
                </div>
            </div>
        </template>

        <template v-else>
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3 class="mb-3">Applications to Your Company</h3>
                    <template v-if="!loading">
                        <div class="col">
                            <PaginatedTable :url="company_applications_endpoint" :fields="company_applications_fields" :item_route_name="applications_route" :initial-filters="companyApplicationsFilters" />
                        </div>
                    </template>
                    <template v-else><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>
                </div>
            </div>
        </template>
    </template>

    <template v-else><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>
</template>