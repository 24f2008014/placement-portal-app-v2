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
const studentCgpa = ref();

const applications_endpoint = `/positions/${route.params.id}/applications`;
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
    "Student ID": {
        name: "student_id",
        filter: false
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

async function changeApproval() {
    try {
        const newStatus = (position.value.is_approved == true) ? false : true;
        const response = await api.patch(`/positions/${route.params.id}`, { status: newStatus });
        position.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("PositionApprovalModal")).hide();
        alert.addAlert(`Successfully updated Position #${route.params.id}'s approval status.`, "success");
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

async function getStudentCgpa() {
    try {
        const response = await api.get("/students/me");
        studentCgpa.value = response.data.cgpa;
    } catch (error) {
        console.error(error);
    }
}

onMounted(() => {
    getPosition();
    if (auth.currentUser.role == "student") {
        getStudentCgpa();
        getStudentApplication();
    }
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Position</h6>
            <p class="lead text-muted">Position ID: #{{ route.params.id }}</p>
            
            <div class="row" v-if="auth.currentUser.role!='company' && !loading">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "positions" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Positions
                    </button>
                </div>
            </div>

            <div class="row" v-if="auth.currentUser.role=='company' && !loading">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-success btn-sm" @click='router.push({ name: "company_dashboard" })'>
                        <i class="bi bi-arrow-left me-2"></i>Dashboard
                    </button>
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
                    <p><RouterLink :to='{ name: "company", params: { "id": position.company_id } }'>Click here to learn more about {{ position.company.name }}.</RouterLink></p>
                </div>
            </div>
        </template>

        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
                <h3>Admin Approved? <code>{{ position.is_approved }}</code></h3>
                <p v-if="position.is_approved==true">This position is <strong>approved</strong>.</p>
                <p v-else>This position <strong>has not yet been approved by an administrator</strong>.</p>
                <template v-if="auth.currentUser.role=='admin' && !position.is_approved">
                    <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#PositionApprovalModal"><i class="bi bi-wrench me-2"></i>Change Approval Status</button>
                    <Modal :title="'Change Approval Status'" :id="'PositionApprovalModal'" :yes-label="'Change'" @confirm="changeApproval">
                        <template #modal-body>
                            <p v-if="position.is_approved==true">Are you sure you want to change Position #{{ $route.params.id }}'s approval status from <strong>approved</strong> to <strong>not approved</strong>?</p>
                            <p v-else>Are you sure you want to change Position #{{ $route.params.id }}'s approval status from <strong>not approved</strong> to <strong>approved</strong>?</p>
                        </template>
                    </Modal>
                </template>
            </div>
        </div>

        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
                <h3>Current Status: <code>{{ position.status }}</code></h3>
                <p v-if="position.status=='closed'">This position is currently <strong>closed</strong>.</p>
                <template v-else>
                    <p>This position is currently <strong>open</strong> (pending admin approval).</p>
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
    
        <template v-if="auth.currentUser.role!='student' && position.is_approved=='true'">
            <hr class="mb-4">
            <div class="row">
                <div class="col">
                    <h3 class="mb-4">Applications Received</h3>
                    <PaginatedTable :url="applications_endpoint" :fields="applications_fields" :item_route_name="applications_route" />
                </div>
            </div>
        </template>

        <template v-if="auth.currentUser.role=='student'">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col" v-if="!applicationLoading">
                    <h3 class="mb-3">Your Application</h3>
                    <template v-if="studentApplication.length == 0 || studentApplication[0].status=='withdrawn'">

                        <template v-if="position.status=='closed'">
                            This position is currently not accepting any new applications.
                        </template>

                        <template v-else>
                            <template v-if="studentCgpa >= position.min_cgpa">
                                <p>You don't have any pending applications for this position. Would you like to submit an application?</p>
                                <button type="button" class="btn btn-sm btn-success" @click="postApplication"><i class="bi bi-plus-lg me-2"></i>Apply</button>
                            </template>

                            <template v-else>
                                <p>Unfortunately, you do not meet the minimum CGPA required for this position ({{ position.min_cgpa }}). You cannot apply.</p>
                                <button type="button" class="btn btn-sm btn-success" disabled><i class="bi bi-plus-lg me-2"></i>Apply</button>
                            </template>
                        </template>

                    </template>

                    <template v-else>
                        <p>You have already applied to this position. Click the button below to view your latest application.</p>
                        <button type="button" class="btn btn-sm btn-primary" @click='router.push({name: "application", params: {"id": studentApplication[0].id}})'>View Application</button>
                    </template>
                </div>
                <div class="col" v-else><p>Loading...</p></div>
            </div>
        </template>
    </template>
    <div v-else><p>Loading...</p></div>
</template>