<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useRoute, useRouter } from "vue-router";
import { useAlertStore } from "@/stores/alert";
import * as bootstrap from "bootstrap";

const alert = useAlertStore();
const router = useRouter();
const route = useRoute();
const loading = ref(true);
const company = ref({});
const errors = ref({});
const auth = useAuthStore();

async function getCompany() {
    try {
        const response = await api.get(`/companies/${route.params.id}`);
        company.value = response.data;
        loading.value = false;
    }
    catch (error) {
        console.log(error);
    }
}

async function changeStatus() {
    try {
        const newStatus = (company.value.status == "whitelisted") ? "blacklisted" : "whitelisted";
        const formData = {
            status: newStatus
        };
        const response = await api.patch(`/companies/${route.params.id}`, formData);
        company.value = response.data;
        const statusModal = document.getElementById("CompanyStatusModal");
        const statusModalInstance = bootstrap.Modal.getInstance(statusModal);
        statusModalInstance.hide();
        alert.addAlert(`Successfully updated Company #${route.params.id}'s status'.`, "success");
    }
    catch (error) {
        console.log(error);
    }
};

const positions_url = `/companies/${route.params.id}/positions`
const positions_route_name = "position"
const positions_fields = {
    "ID": {name: "id", filter: true, sort: true},
    "Role": {name: "role", filter: true},
    "Status": {name: "status", filter: false}
}

onMounted(() => {
    getCompany();
})
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Company</h6>
            <p class="lead text-muted">Company ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "company_positions" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Companies
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
                <h6 class="text-primary-emphasis">Company Name</h6>
                <p>{{ company.name }}</p>
                <h6 class="text-primary-emphasis">Industry</h6>
                <p>{{ company.industry.name }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Website</h6>
                <p>{{ company.website }}</p>
                <h6 class="text-primary-emphasis">Location</h6>
                <p>{{ company.location }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Email</h6>
                <p>{{ company.contact_email }}</p>
                <h6 class="text-primary-emphasis">Phone No.</h6>
                <p>{{ company.contact_phone_number ? company.contact_phone_number : "N/A" }}</p>
            </div>
        </div>
        <template v-if="auth.currentUser.role=='admin'">
            <hr class="mb-4">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ company.status }}</code></h3>
                    <p v-if="company.status=='pending'">This company's status is <strong>pending</strong>. They need admin approval before they can list new positions.</p>
                    <p v-else-if="company.status=='blacklisted'">This company is <strong>blacklisted</strong>. They cannot make new job listings.</p>
                    <p v-else>This company is <strong>whitelisted</strong>. They can freely list new positions.</p>
                    <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#CompanyStatusModal"><i class="bi bi-wrench me-2"></i>Change Status</button>
                </div>
                <div>
                    <div class="modal fade" tabindex="-1" id="CompanyStatusModal" aria-labelledby="CompanyStatusModalTitle">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="CompanyStatusModalTitle">Change Status</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <p v-if="company.status=='pending'">Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>pending</strong> to <strong>whitelisted</strong>?</p>
                                    <p v-else-if="company.status=='blacklisted'">Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>blacklisted</strong> to <strong>whitelisted</strong>?</p>
                                    <p v-else>Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>whitelisted</strong> to <strong>blacklisted</strong>?</p>
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
        </template>
    </template>
    <div class="row mb-4" v-else><p>Loading...</p></div>
    <hr class="mb-4">

    <div class="row mb-4">
        <div class="col">
            <h3 class="mb-3">Positions</h3>
            <div class="col" v-if="!loading">
                <PaginatedTable :url="positions_url" :fields="positions_fields" :item_route_name="positions_route_name" />
            </div>
            <div v-else>Loading...</div>
        </div>
    </div>
</template>