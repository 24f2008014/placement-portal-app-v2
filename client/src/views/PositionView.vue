<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import PaginatedTable from "@/components/PaginatedTable.vue";
import PositionViewForm from "@/components/PositionViewForm.vue";
import { useAuthStore } from "@/stores/auth";
import * as bootstrap from "bootstrap";
import { useAlertStore } from "@/stores/alert";
import Modal from "@/components/Modal.vue";

const alert = useAlertStore();
const auth = useAuthStore();
const loading = ref(true);
const applicationLoading = ref(true);
const position = ref(null);
const router = useRouter();
const route = useRoute();
const errors = ref({});
const studentApplication = ref([]);
const student = ref({});

const applications_endpoint = `/positions/${route.params.id}/applications`;
const applications_route = "application";
const applications_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Student ID": {
        name: "student_id",
        filter: true,
        label: "Student ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
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

const placements_endpoint = `/positions/${route.params.id}/placements`;
const placements_route = "placement";
const placements_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Application ID": {
        name: "application_id",
        filter: true,
        label: "Application ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Student ID": {
        name: "application.student.id",
        filter: true,
        label: "Student ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }        
    },
    "Salary": {
        name: "salary",
        filter: true,
        label: "Salary \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
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

async function getPosition() {
    try {
        loading.value = true;
        const response = await api.get(`/positions/${route.params.id}`);
        position.value = response.data;
        loading.value = false;
    } catch (error) {
        console.error(error);
    }
}

async function whitelistPosition() {
    try {
        const response = await api.post(`/positions/${route.params.id}/whitelist`, null);
        position.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("PositionApprovalModal")).hide();
        alert.addAlert(`Successfully whitelisted Position #${route.params.id}.`, "success");
    } catch (error) {
        console.error(error);
    }
}

async function changeStatus() {
    try {
        const newStatus = (position.value.status == "open") ? "closed" : "open";
        const response = await api.patch(`/positions/${route.params.id}`, { status: newStatus });
        position.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("PositionStatusModal")).hide();
        alert.addAlert(`Successfully updated Position #${route.params.id}'s status.`, "success");
    } catch (error) {
        console.error(error);
    }
}

async function getStudentApplication() {
    try {
        applicationLoading.value = true;
        const response = await api.get(`/students/me/applications?sort_by=created_at&sort_dir=desc&filters={"position_id":"${route.params.id}"}`);
        studentApplication.value = response.data.data;
        applicationLoading.value = false;
    } catch (error) {
        console.error(error);
    }
}

async function postApplication() {
    try {
        const response = await api.post(`/positions/${route.params.id}/applications`, null);
        const application_id = response.data.id;
        alert.addAlert("Application created!", "success");
        router.push({ name: "application", params: { id: application_id } });
    } catch (error) {
        console.error(error);
        alert.addAlert(error, "error");
    }
}

async function getStudent() {
    try {
        applicationLoading.value = true;
        const response = await api.get("/students/me");
        student.value = response.data;
        applicationLoading.value = false;
    } catch (error) {
        console.error(error);
    }
}

onMounted(() => {
    getPosition();
    if (auth.currentUser.role == "student") {
        getStudent();
        getStudentApplication();
    }
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Position</h6>
            <p class="lead text-muted">Position ID: #{{ route.params.id }}</p>

            <div class="row" v-if="!loading">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "company_dashboard" })'><i class="bi bi-arrow-left me-2"></i>Dashboard</button>
                </div>
            </div>          
        </div>
    </div>

    <template v-if="!loading">
        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
                <h3 class="mb-4">Position Details</h3>
                <PositionViewForm :position="position" />
            </div>
        </div>

        <template v-if="auth.currentUser.role!='company'">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3 class="mb-3">About the Company</h3>                    
                    <p>{{ position.company.description }}</p>
                    <div class="col d-flex gap-2">
                        <button type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "company", params: { id: position.company_id } })'><i class="bi bi-box-arrow-up-right me-2"></i>View Company</button>
                    </div>                    
                </div>
            </div>
        </template>

        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
                <h3>Admin Approved? <code>{{ position.is_approved }}</code></h3>
                <p v-if="position.is_approved==true">This position is <code class="text-success fw-bold">approved</code>.</p>
                <p v-else>This position has <code class="text-danger fw-bold">not been approved</code> by an administrator.</p>

                <template v-if="auth.currentUser.role=='admin' && !position.is_approved">
                    <button type="button" class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#PositionApprovalModal"><i class="bi bi-check-lg me-2"></i>Whitelist</button>
                    <Modal :title="'Whitelist Position'" :id="'PositionApprovalModal'" :yes-label="'Confirm'" @confirm="whitelistPosition">
                        <template #modal-body>
                            <p>Are you sure you want to whitelist <strong>Position #{{ $route.params.id }}</strong>?</p>
                        </template>
                    </Modal>
                </template>
            </div>

            <div class="col">
                <h3>Current Status: <code>{{ position.status }}</code></h3>
                <p v-if="position.status=='closed'">This position is currently <code class="text-danger fw-bold">closed</code>.</p>

                <template v-else>
                    <p>This position is currently <code class="text-success fw-bold">open</code> (pending admin approval).</p>
                    <template v-if="auth.currentUser.role=='company'">
                        <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#PositionStatusModal"><i class="bi bi-x-lg me-2"></i>Close Position</button>
                        <Modal :title="'Change Status'" :id="'PositionStatusModal'" :yes-label="'Change'" @confirm="changeStatus">
                            <template #modal-body>
                                <p>Are you sure you want to <strong>close</strong> Position #{{ $route.params.id }}? This cannot be undone.</p>
                            </template>
                        </Modal>
                    </template>
                </template>
            </div>            
        </div>
    
        <template v-if="auth.currentUser.role!='student' && position.is_approved==true">
            <hr class="mb-4">
            <div class="row">
                <div class="col">
                    <h3 class="mb-4">Applications Received</h3>
                    <PaginatedTable :url="applications_endpoint" :fields="applications_fields" :item_route_name="applications_route" />
                </div>
            </div>
            <hr class="mb-4">
            <div class="row">
                <div class="col">
                    <h3 class="mb-4">Placements Made</h3>
                    <PaginatedTable :url="placements_endpoint" :fields="placements_fields" :item_route_name="placements_route" />
                </div>
            </div>
        </template>

        <template v-if="auth.currentUser.role=='student'">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col" v-if="!applicationLoading">
                    <h3 class="mb-3">Your Application</h3>
                    <template v-if="studentApplication.length == 0 || studentApplication[0].status=='withdrawn'">

                        <template v-if="position.status=='closed' || position.is_approved == false">
                            This position is currently not accepting any new applications.
                        </template>

                        <template v-else>
                            <template v-if="student.status=='blacklisted'">
                                <p>Your account is currently <code class="text-danger fw-bold">blacklisted</code>. You cannot make new applications.</p>
                            </template>

                            <template v-else>
                                <p class="mb-1">
                                    <strong>Your CGPA:</strong> {{ student.cgpa }}
                                    <i v-if="student.cgpa >= position.min_cgpa" class="bi bi-check-lg text-success"></i>
                                    <i v-else class="bi bi-x-lg text-danger"></i>
                                </p>
                                <p>
                                    <strong>Your Department:</strong> {{ student.branch.department.name }}
                                    <i v-if="position.departments.some(d => d.id == student.branch.department_id)" class="bi bi-check-lg text-success"></i>
                                    <i v-else class="bi bi-x-lg text-danger"></i>                                    
                                </p>
                                <template v-if="(student.cgpa >= position.min_cgpa) && position.departments.some(d => d.id == student.branch.department_id)">
                                    <p>You're eligible to apply, and you don't have any pending applications for this position. Would you like to submit an application?</p>
                                    <button type="button" class="btn btn-sm btn-success" @click="postApplication"><i class="bi bi-plus-lg me-2"></i>Apply</button>
                                </template>

                                <template v-else>
                                    <p>Unfortunately, you do not meet the eligibility requirements for this application. You cannot apply.</p>
                                    <button type="button" class="btn btn-sm btn-success" disabled><i class="bi bi-plus-lg me-2"></i>Apply</button>
                                </template>
                            </template>
                        </template>

                    </template>

                    <template v-else>
                        <p>You have already applied to this position. Click the button to view the status of your latest application.</p>
                        <button type="button" class="btn btn-sm btn-primary" @click='router.push({name: "application", params: {"id": studentApplication[0].id}})'><i class="bi bi-box-arrow-up-right me-2"></i>View Application</button>
                    </template>
                </div>
                <div class="col" v-else><p>Loading...</p></div>
            </div>
        </template>
    </template>
    <div v-else><p>Loading...</p></div>
</template>