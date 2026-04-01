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

const positions_endpoint = "/positions";
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
    "Company": {
        name: "company.name",
        filter: false,
        label: "Company",
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
        label: "Min. CGPA \u2265",
        input: {
            type: "number",
            min: "0"
        }
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

const my_applications_endpoint = "/students/me/applications";
const my_applications_route = "application";
const my_applications_fields = {
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
        filter: false
    },    
    "Position": {
        name: "position.role",
        filter: false
    },
    "Company": {
        name: "position.company.name",
        filter: false
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

async function getStats() {
    try {
        const response = await api.get("/students/me/stats");
        stats.value = response.data;
        loading.value = false;
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
        <div class="row d-flex">
            <div class="col">
                <button @click="taskStore.exportCsv" type="button" class="btn btn-sm btn-success mb-3"><i class="bi bi-download me-2"></i>Download Application History</button>
            </div>
        </div>        
    </div>
    <hr class="mb-4">

    <template v-if="!loading">
        <div class="row">
            <div class="col">
                <h3>Scheduled Interviews</h3>
                <ul v-if="stats.upcoming_interviews.length > 0">
                    <li v-for="i in stats.upcoming_interviews">
                        With the company <strong>{{ i.position.company.name }}</strong> on <strong>{{ formatDate(i.interview_date) }}</strong> for the position of <strong>{{ i.position.role }}</strong> <RouterLink :to="{name: 'application', params: { id: i.id } }">(view application)</RouterLink>
                    </li>
                </ul>
                <p v-else>None.</p>
            </div>
        </div>
        <hr class="mb-4">
    </template>

    <div class="row mb-4">
        <div class="col">
            <h4 class="mb-3">Your Applications ({{ stats.num_applications }})</h4>
            <PaginatedTable :url="my_applications_endpoint" :fields="my_applications_fields" :item_route_name="my_applications_route" />
        </div>
    </div>
    <hr class="mb-4">

    <div class="row mb-4">
        <div class="col">
            <h4 class="mb-3">Open Positions</h4>
            <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
        </div>
    </div>
</template>