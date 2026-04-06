<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { formatDate } from "@/utils/helpers";
import router from "@/router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const loading = ref(true);
const errors = ref({});
const status = ref();
const stats = ref({});

const positions_endpoint = "/companies/me/positions";
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
        filter: true,
        label: "Min. CGPA \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0",
            max: "10"
        }
    },
    "Deadline": {
        name: "deadline",
        filter: false,
        label: "Deadline \u2265",
        type: "date",
        input: {
            type: "datetime-local"
        }
    },
    "Applications": {
        name: "application_count",
        filter: true,
        label: "Applications \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
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

const placements_endpoint = "/companies/me/placements";
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
    "Position": {
        name: "application.position.role",
        filter: true,
        label: "Position",
        input: {
            type: "text"
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

const applications_endpoint = "/companies/me/applications";
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
    "Position ID": {
        name: "position_id",
        filter: true,
        label: "Position ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },    
    "Position": {
        name: "position.role",
        filter: false,
        label: "Position",
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

async function checkStatus() {
    errors.value = {};
    try {
        const response = await api.get("/companies/me");
        status.value = response.data.status;
    } catch (error) {
        console.error(error);
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json);
        }
    }
}

async function getStats() {
    try {
        const response = await api.get("/companies/me/stats");
        stats.value = response.data;
        loading.value = false;
    } catch (error) {
        console.error(error.response.data);
    }
}

onMounted(() => {
    checkStatus();
    getStats();
});
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-bar-chart-line-fill" style="font-size: 3.5rem"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Company Dashboard</h6>
            <p class="lead text-muted">Welcome back, {{ auth.currentUser.name }}! See everything at a glance here.</p>
        </div>
    </div>
    <hr class="mb-4">

    <template v-if="loading"><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>

    <template v-else>
        <div class="row">
            <div class="col">
                <h3>Scheduled Interviews</h3>
                <ul v-if="stats.upcoming_interviews.length > 0">
                    <li v-for="i in stats.upcoming_interviews">
                        {{ i.student.first_name + " " + i.student.last_name }} on <strong>{{ formatDate(i.interview_date) }}</strong> for the position of <strong>{{ i.position.role }}</strong> <RouterLink :to="{name: 'application', params: { id: i.id } }">(view application)</RouterLink>
                    </li>
                </ul>
                <p v-else>None.</p>
            </div>
        </div>
        <hr class="mb-4">

        <div class="row">
            <div class="col">
                <template v-if="status=='pending'">
                    <h4>Status: <code class="text-warning">Pending</code></h4>
                    <p>Your company account requires admin approval before you can list any new positions. Please wait. Thank you for your patience.</p>
                    <div class="col">
                        <button type="button" class="btn btn-sm btn-success mb-3" disabled><i class="bi bi-plus-lg me-2"></i>New Position</button>
                    </div>
                </template>
                <template v-else-if="status=='blacklisted'">
                    <h4>Status: <code class="text-danger">Blacklisted</code></h4>
                    <p>Your company account has been blacklisted, and you cannot list any new positions. Please contact an administrator for further details.</p>
                    <div class="col">
                        <button type="button" class="btn btn-sm btn-success mb-3" disabled><i class="bi bi-plus-lg me-2"></i>New Position</button>
                    </div>
                </template>
                <template v-else>
                    <h4>Status: <code class="text-success">Whitelisted</code></h4>
                    <p>Your company has been approved, and you're free to list any new positions you're hiring for.</p>
                    <div class="col">
                        <button @click="router.push({ name: 'company_positions' })" type="button" class="btn btn-sm btn-success mb-3"><i class="bi bi-plus-lg me-2"></i>New Position</button>
                    </div>
                </template>
            </div>
        </div>
        <hr class="mb-4">

        <div class="row">
            <div class="col">
            <ul class="nav nav-tabs" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="positions-tab" data-bs-toggle="tab" data-bs-target="#positions-tab-pane" type="button" role="tab" aria-controls="positions-tab-pane" aria-selected="true">Positions ({{ stats.num_positions }})</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="applications-tab" data-bs-toggle="tab" data-bs-target="#applications-tab-pane" type="button" role="tab" aria-controls="applications-tab-pane" aria-selected="false">Applications ({{ stats.num_applications }})</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="placements-tab" data-bs-toggle="tab" data-bs-target="#placements-tab-pane" type="button" role="tab" aria-controls="placements-tab-pane" aria-selected="false">Placements ({{ stats.num_placements }})</button>
                </li>
            </ul>
            </div>

            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="positions-tab-pane" role="tabpanel" aria-labelledby="positions-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Your Positions</h4>
                            <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="applications-tab-pane" role="tabpanel" aria-labelledby="applications-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Applications Received</h4>
                            <PaginatedTable :url="applications_endpoint" :fields="applications_fields" :item_route_name="applications_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="placements-tab-pane" role="tabpanel" aria-labelledby="placements-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Your Placement Offers</h4>
                            <PaginatedTable :url="placements_endpoint" :fields="placements_fields" :item_route_name="placements_route" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </template>
</template>