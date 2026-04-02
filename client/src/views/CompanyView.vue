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
        const statusModal = document.getElementById("CompanyStatusModal");
        const statusModalInstance = bootstrap.Modal.getInstance(statusModal);
        statusModalInstance.hide();
        alert.addAlert(`Successfully updated Company #${route.params.id}'s status'.`, "success");
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
        input: {
            type: "number",
            min: "0"
        }
    },
    "Max. Salary": {
        name: "salary_max",
        filter: true,
        label: "Max. Salary \u2265",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Min. CGPA": {
        name: "min_cgpa",
        filter: true,
        label: "Min. CGPA \u2265"
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
        filter: false
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
})
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Company</h6>
            <p class="lead text-muted">Company ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button v-if="auth.currentUser.role!='company'" type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "companies" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Companies
                    </button>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">

    <template v-if="!loading">
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

                <Modal :title="'Change Status'" :id="'CompanyStatusModal'" :yes-label="'Change'" @confirm="changeStatus">
                    <template #modal-body>
                        <p v-if="company.status=='pending'">Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>pending</strong> to <strong>whitelisted</strong>?</p>
                        <p v-else-if="company.status=='blacklisted'">Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>blacklisted</strong> to <strong>whitelisted</strong>?</p>
                        <p v-else>Are you sure you want to change Company #{{ $route.params.id }}'s status from <strong>whitelisted</strong> to <strong>blacklisted</strong>?</p>
                    </template>
                </Modal>
            </div>
        </template>
    </template>
    <div class="row mb-4" v-else><p>Loading...</p></div>
    <hr class="mb-4">

    <div class="row mb-4">
        <div class="col">
            <h3 class="mb-3">Positions</h3>
            <div class="col" v-if="!loading">
                <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
            </div>
            <div v-else>Loading...</div>
        </div>
    </div>
</template>