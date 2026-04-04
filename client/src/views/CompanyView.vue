<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useRoute, useRouter } from "vue-router";
import { useAlertStore } from "@/stores/alert";
import * as bootstrap from "bootstrap";
import Modal from "@/components/Modal.vue";
import { formatDateNoTime } from "@/utils/helpers";

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
    } catch (error) {
        console.error(error);
    }
}

async function changeStatus() {
    try {
        const newStatus = (company.value.status == "whitelisted") ? "blacklisted" : "whitelisted";
        const response = await api.patch(`/companies/${route.params.id}`, { status: newStatus });
        company.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("CompanyStatusModal")).hide();
        alert.addAlert(`Successfully updated Company #${route.params.id}'s status.`, "success");
    } catch (error) {
        console.error(error);
    }
};

const positions_endpoint = `/companies/${route.params.id}/positions`;
const positions_route = "position";
const positions_fields = {
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
    "Role": {
        name: "role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }
    },
    "Min. Salary": {
        name: "salary_min",
        filter: true,
        label: "Min. Salary \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Max. Salary": {
        name: "salary_max",
        filter: true,
        label: "Max. Salary \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Min. CGPA": {
        name: "min_cgpa",
        filter: false,
        type: "number"
    },
    "Deadline": {
        name: "deadline",
        filter: true,
        label: "Deadline \u2265",
        type: "date",
        input: {
            type: "datetime-local"
        }
    },
    "Application Count": {
        name: "application_count",
        filter: false,
        type: "number"
    },
    "Approved": {
        name: "is_approved",
        filter: true,
        label: "Approved",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "True", value: true},
                {label: "False", value: false}
            ]
        }
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Open", value: "open"},
                {label: "Closed", value: "closed"}
            ]
        }
    }
};

onMounted(() => {
    getCompany();
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Company</h6>
            <p class="lead text-muted">Company ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button v-if="auth.currentUser.role=='admin'" type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "admin_dashboard" })'><i class="bi bi-arrow-left me-2"></i>Dashboard</button>
                    <button v-else type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "student_dashboard" })'><i class="bi bi-arrow-left me-2"></i>Dashboard</button>
                </div>
            </div>
        </div>
    </div>

    <template v-if="!loading">
        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
                <h6 class="text-primary-emphasis">Name</h6>
                <p>{{ company.name }}</p>
                <h6 class="text-primary-emphasis">Contact Email</h6>
                <p>{{ company.contact_email }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Industry</h6>
                <p>{{ company.industry.name }}</p>
                <h6 class="text-primary-emphasis">Contact Phone No.</h6>
                <p>{{ company.contact_phone_number ? company.contact_phone_number : "N/A" }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Location</h6>
                <p>{{ company.location }}</p>
                <h6 class="text-primary-emphasis">Joining Date</h6>
                <p>{{ formatDateNoTime(company.user.created_at) }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Website</h6>
                <p>{{ company.website }}</p>
                <h6 class="text-primary-emphasis">Status</h6>
                <p>{{ company.status }}</p>
            </div>     
        </div>

        <template v-if="company.description">
            <hr class="mb-4">
            <div class="row mb-4">
                <h3 class="mb-3">Description</h3>
                <p>{{ company.description }}</p>
            </div>
        </template>

        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
                <h3>Current Status: <code>{{ company.status }}</code></h3>
                <p v-if="company.status=='pending'">This company's status is <code class="text-warning fw-bold">pending</code>. They need admin approval before they can list new positions.</p>
                <p v-else-if="company.status=='blacklisted'">This company is <code class="text-danger fw-bold">blacklisted</code>. They cannot list new positions.</p>
                <p v-else>This company is <code class="text-success fw-bold">whitelisted</code>. They can freely list new positions.</p>

                <template v-if="auth.currentUser.role=='admin'">
                    <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#CompanyStatusModal"><i class="bi bi-gear-fill me-2"></i>Change Status</button>
                    <Modal :title="'Change Status'" :id="'CompanyStatusModal'" :yes-label="'Change'" @confirm="changeStatus">
                        <template #modal-body>
                            <p v-if="company.status=='pending'">Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>pending</strong> to <strong>whitelisted</strong>? They will be able to list new positions they're hiring for.</p>
                            <p v-else-if="company.status=='blacklisted'">Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>blacklisted</strong> to <strong>whitelisted</strong>? They will again be able to list new positions they're hiring for.</p>
                            <p v-else>Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>whitelisted</strong> to <strong>blacklisted</strong>? This will not close their existing positions, but will prevent them from opening new ones.</p>
                        </template>
                    </Modal>
                </template>
            </div>
        </div>

        <template v-if="company.status=='whitelisted' || auth.currentUser.role=='admin'">
            <hr class="mb-4">
            <div class="row-mb-4">
                <div class="col">
                    <h3 class="mb-3">Positions</h3>
                    <div class="col">
                        <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
                    </div>
                </div>
            </div>
        </template>
    </template>

    <div class="row mb-4" v-else><p>Loading...</p></div>
</template>