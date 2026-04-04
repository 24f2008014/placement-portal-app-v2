<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { api } from "@/utils/api";
import { useTaskStore } from "@/stores/tasks";
import { formatDate } from "@/utils/helpers";

const taskStore = useTaskStore();
const auth = useAuthStore();
const stats = ref({});
const loading = ref(true);
const studentStatus = ref();

const positions_endpoint = "/students/me/positions/unapplied";
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
    "Company": {
        name: "company.name",
        filter: true,
        label: "Company",
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
    "Created At": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Deadline": {
        name: "deadline",
        filter: true,
        label: "Deadline \u2265",
        type: "date",
        input: {
            type: "datetime-local"
        }
    }
};

const my_applications_endpoint = "/students/me/applications";
const my_applications_route = "application";
const my_applications_fields = {
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
    "Date Applied": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Interview Date": {
        name: "interview_date",
        filter: false,
        type: "date"
    },
    "Last Updated": {
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

const placements_endpoint = "/students/me/placements";
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
        type: "number",
        filter: false
    },
    "Position": {
        name: "application.position.role",
        filter: false
    },
    "Company": {
        name: "application.position.company.name",
        filter: false  
    },
    "Salary": {
        name: "salary",
        type: "number",
        filter: false
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
                {label: "Rejected", value: "rejected"},
                {label: "Withdrawn", value: "withdrawn"}
            ]
        }
    }
};

async function getStats() {
    try {
        const response_status = await api.get("/students/me");
        studentStatus.value = response_status.data.status;
        const response_stats = await api.get("/students/me/stats");
        stats.value = response_stats.data;
        loading.value = false;
    } catch (error) {
        console.error(error);
    }
}

async function getReminder() {
    try {
        const response = await api.get("/students/me/reminder");
        console.log(response.data);
        alert.addAlert("Email reminder sent.", "success");
    } catch (error) {
        console.error(error);
    }
}

onMounted(() => {
    getStats();
});
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-bar-chart-line-fill" style="font-size: 3.5rem"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Student Dashboard</h6>
            <p class="lead text-muted">Welcome back, {{ auth.currentUser.name }}! See everything at a glance here.</p>
        </div>
        <div class="row mb-2">
            <div class="col d-flex gap-3">
                <button @click="taskStore.exportCsv" type="button" class="btn btn-sm btn-success"><i class="bi bi-download me-2"></i>Download Application History</button>
                <button type="button" class="btn btn-sm btn-success" @click="getReminder"><i class="bi bi-envelope-fill me-2"></i>Email Upcoming Interviews</button>
            </div>
        </div>        
    </div>
    <hr class="mb-4">

    <template v-if="!loading">
        <div class="row">
            <div class="col">
                <h4>Scheduled Interviews</h4>
                <ul v-if="stats.upcoming_interviews.length > 0">
                    <li v-for="i in stats.upcoming_interviews">
                        With the company <strong>{{ i.position.company.name }}</strong> on <strong>{{ formatDate(i.interview_date) }}</strong> for the position of <strong>{{ i.position.role }}</strong> <RouterLink :to="{name: 'application', params: { id: i.id } }">(view application)</RouterLink>
                    </li>
                </ul>
                <p v-else>None.</p>
            </div>
        </div>

        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col" v-if="studentStatus=='blacklisted'">
                <h4>Status: <code class="text-danger fw-bold">blacklisted</code></h4>
                <p>Your account has been blacklisted. You cannot apply to new positions.</p>
            </div>
            <div class="col" v-else>
                <h4>Status: <code class="text-success fw-bold">whitelisted</code></h4>
                <p>Your account is whitelisted. You can freely apply to new positions.</p>
            </div>
        </div>
        
        <div class="row">
            <div class="col">
                <ul class="nav nav-tabs" id="myTab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="applications-tab" data-bs-toggle="tab" data-bs-target="#applications-tab-pane" type="button" role="tab" aria-controls="applications-tab-pane" aria-selected="true">Applications ({{ stats.num_applications }})</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="placements-tab" data-bs-toggle="tab" data-bs-target="#placements-tab-pane" type="button" role="tab" aria-controls="placements-tab-pane" aria-selected="false">Placements ({{ stats.num_placements }})</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="positions-tab" data-bs-toggle="tab" data-bs-target="#positions-tab-pane" type="button" role="tab" aria-controls="positions-tab-pane" aria-selected="false">Positions</button>
                    </li>                    
                </ul>
            </div>

            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="applications-tab-pane" role="tabpanel" aria-labelledby="applications-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Your Applications</h4>
                            <PaginatedTable :url="my_applications_endpoint" :fields="my_applications_fields" :item_route_name="my_applications_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="positions-tab-pane" role="tabpanel" aria-labelledby="positions-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Positions</h4>
                            <p>These are open positions you haven't applied for yet.</p>
                            <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="placements-tab-pane" role="tabpanel" aria-labelledby="placements-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Your Placements</h4>
                            <PaginatedTable :url="placements_endpoint" :fields="placements_fields" :item_route_name="placements_route" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </template>
    <template v-else><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>
</template>