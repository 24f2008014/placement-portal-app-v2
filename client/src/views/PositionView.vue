<script setup>
import { onMounted, ref, computed } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import PaginatedTable from "@/components/PaginatedTable.vue";
import PositionViewForm from "@/components/PositionViewForm.vue";
import { useAuthStore } from "@/stores/auth";
import * as bootstrap from "bootstrap";
import { useAlertStore } from "@/stores/alert";

const alert = useAlertStore();
const auth = useAuthStore();
const loading = ref(true);
const applicationLoading = ref(true);
const position = ref(null);
const router = useRouter();
const route = useRoute();
const errors = ref({});
const studentApplication = ref([]);
const applications_url = `/positions/${route.params.id}/applications`;
const applications_fields = {
    "ID": {name: "id", filter: true, sort: true},
    "Roll No.": {name: "roll_number", filter: false},
    "First Name": {name: "first_name", filter: false},
    "Last Name": {name: "last_name", filter: false},
    "Created At": {name: "created_at", filter: false, type: "date"},
    "Status": {name: "status", filter: false}
};
const application_item_route = "application";

async function getPosition() {
    try {
        loading.value = true;
        const response = await api.get(`/positions/${route.params.id}`);
        position.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
    finally {
        loading.value = false;
    }
};

async function changeApproval() {
    try {
        const newStatus = (position.value.is_approved == true) ? false : true;
        const formData = {
            status: newStatus
        };
        const response = await api.patch(`/positions/${route.params.id}`, formData);
        position.value = response.data;
        const approvalModal = document.getElementById("PositionApprovalModal");
        const approvalModalInstance = bootstrap.Modal.getInstance(approvalModal);
        approvalModalInstance.hide();
        alert.addAlert(`Successfully updated Position #${route.params.id}'s approval status.`, "success");
    }
    catch (error) {
        console.log(error);
    }
};

async function changeStatus() {
    try {
        const newStatus = (position.value.status == "open") ? "closed" : "open";
        const formData = {
            status: newStatus
        };
        const response = await api.patch(`/positions/${route.params.id}`, formData);
        position.value = response.data;
        const statusModal = document.getElementById("PositionStatusModal");
        const statusModalInstance = bootstrap.Modal.getInstance(statusModal);
        statusModalInstance.hide();
        alert.addAlert(`Successfully updated Position #${route.params.id}'s status.`, "success");
    }
    catch (error) {
        console.log(error);
    }
};

async function getStudentApplication() {
    try {
        applicationLoading.value = true;
        const response = await api.get(`/students/me/applications?filters={"position_id":"${route.params.id}"}`)
        studentApplication.value = response.data.data;
        console.log(response.data.data);
    }
    catch (error) {
        console.log(error);
    }
    finally {
        applicationLoading.value = false;
    }
};

async function postApplication() {
    try {
        const response = await api.post(`/positions/${route.params.id}/applications`, null);
        const application_id = response.data.id;
        alert.addAlert("Application created!", "success");
        router.push({ name: `/applications/${application_id}` });
    }
    catch (error) {
        console.log(error);
    }
}

onMounted(() => {
    getPosition();
    if (auth.currentUser.role == "student") {
        getStudentApplication();
    }
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Position</h6>
            <p class="lead text-muted">Position ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "company_positions" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Positions
                    </button>
                    <button type="button" class="btn btn-success btn-sm" @click='router.push({ "name": "student_dashboard" })'>
                        <i class="bi bi-graph-up me-2"></i>Dashboard
                    </button>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">

    <template v-if="!loading">
        <div class="row mb-4">
            <div class="col">
                <h3 class="mb-4">Details</h3>
                <PositionViewForm :position="position" />
            </div>
        </div>
        <hr class="mb-4">

        <template v-if="auth.currentUser.role=='company'">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ position.status }}</code></h3>
                    <p v-if="position.status=='open'">This position is currently <strong>open</strong>.</p>
                    <p v-else>This position is currently <strong>closed</strong>.</p>
                    <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#PositionStatusModal"><i class="bi bi-wrench me-2"></i>Change Status</button>
                </div>
                <div>
                    <div class="modal fade" tabindex="-1" id="PositionStatusModal" aria-labelledby="PositionStatusModalTitle">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="PositionStatusModalTitle">Change Status</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <p v-if="position.status=='open'">Are you sure you want to <strong>close</strong> Position #{{ $route.params.id }}?</p>
                                    <p v-else>Are you sure you want to <strong>open</strong> Position #{{ $route.params.id }}?</p>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
                                    <button type="button" class="btn btn-primary btn-sm" @click="changeStatus">Change Status</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <hr class="mb-4">
        </template>

        <template v-if="auth.currentUser.role=='admin'">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3>Approval Status: <code>{{ position.is_approved }}</code></h3>
                    <p v-if="position.is_approved==true">This position is <strong>approved</strong>.</p>
                    <p v-else>This position is not <strong>approved</strong>, and requires admin approval.</p>
                    <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#PositionApprovalModal"><i class="bi bi-wrench me-2"></i>Change Approval Status</button>
                </div>
                <div>
                    <div class="modal fade" tabindex="-1" id="PositionApprovalModal" aria-labelledby="PositionApprovalModalTitle">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="PositionApprovalModalTitle">Change Approval Status</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <p v-if="position.is_approved==true">Are you sure you want to change Position #{{ $route.params.id }}'s approval status from <strong>approved</strong> to <strong>not approved</strong>?</p>
                                    <p v-else>Are you sure you want to change Position #{{ $route.params.id }}'s approval status from <strong>not approved</strong> to <strong>approved</strong>?</p>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
                                    <button type="button" class="btn btn-primary btn-sm" @click="changeApproval">Change Status</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </template>
    <div v-else><p>Loading...</p></div>

    <div class="row mb-4">
        <div class="col">
            <h3 class="mb-3">About the Company</h3>
            <div class="col" v-if="!loading">
                <p>{{ position.company.description }}</p>
                <p><RouterLink :to='{ "name": "company", "params": { "id": position.company_id } }'>Click here to learn more about {{ position.company.name }}</RouterLink></p>
            </div>
            <div v-else>Loading...</div>
        </div>
    </div>
    <hr class="mb-4">

    <template v-if="auth.currentUser.role!='student'">
        <div class="row">
            <div class="col">
                <h3 class="mb-4">Applications Received</h3>
                <PaginatedTable :url="applications_url" :fields="applications_fields" :item_route_name="application_item_route"></PaginatedTable>
            </div>
        </div>
        <hr class="mb-4">
    </template>

    <template v-if="auth.currentUser.role=='student'">
        <div class="row mb-4" v-if="auth.currentUser.role=='student'">
            <div class="col" v-if="!applicationLoading">
                <h3 class="mb-4">Your Application</h3>
                <template v-if="!studentApplication">
                    <p class="lead">You haven't applied for this role yet. Would you like to submit an application?</p>
                    <button type="button" class="btn btn-sm btn-success" @click="postApplication">Apply</button>
                </template>
                <template v-else>
                    <p>You have already applied to this position. Click the button below to view your application.</p>
                    <button type="button" class="btn btn-sm btn-primary" @click='router.push({name: "application", params: {"id": studentApplication[0].id}})'>View Application</button>
                </template>
            </div>
            <div class="col" v-else><p>Loading...</p></div>
        </div>
        <hr class="mb-4">
    </template>
</template>