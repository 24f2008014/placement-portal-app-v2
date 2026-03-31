<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { api } from "@/utils/api";
import { useTaskStore } from "@/stores/tasks";

const taskStore = useTaskStore();
const loading = ref(true);
const errors = ref({});
const auth = useAuthStore();
const stats = ref({});

const positions_url = "/positions";
const positions_fields = {
    "ID": {name: "id", label: "ID", filter: true, input: {type: "number", min: "1"}},
    "Role": {name: "role", label: "Role", filter: true, input: {type: "text"}},
    "Company": {name: "name", label: "Company", filter: false, input: {type: "text"}},
    "Min. Salary": {name: "salary_min", filter: true, label: "Min. Salary \u2265", input: {type: "number", min: "0"}},
    "Max. Salary": {name: "salary_max", filter: true, label: "Max. Salary \u2265", input: {type: "number", min: "0"}},
    "Min. CGPA": {name: "min_cgpa", filter: true, label: "Min. CGPA \u2265"},
    "Deadline": {name: "deadline", filter: true, label: "Deadline \u2265", type: "date", input: {type: "datetime-local"}},
    "Status": {name: "status", filter: true, label: "Status", type: "select", input: {type: "select", options: [{label: "Open", value: "open"}, {label: "Closed", value: "closed"}]}},
}
const position_route = "position";

const my_applications_url = "/students/me/applications";
const my_applications_fields = {
    "ID": {name: "id", label: "ID", filter: true, input: {type: "number", min: "1"}},
    "Role": {name: "role", filter: false},
    "Company": {name: "name", filter: false},
    "Date Applied": {name: "created_at", filter: false, type: "date"},
    "Interview Date": {name: "interview_date", filter: false, type: "date"},
    "Status": {name: "status", filter: true, label: "Status", type: "select", input: {type: "select", options: [{label: "Pending", value: "pending"}, {label: "Shortlisted", value: "shortlisted"}, {label: "Selected", value: "selected"}, {label: "Rejected", value: "rejected"}, {label: "Withdrawn", value: "withdrawn"}]}},
}
const my_application_route = "application";

async function getStats() {
    try {
        const response = await api.get("/students/me/stats");
        stats.value = response.data;
    }
    catch (error) {
        console.error(error);
    }
}

onMounted(() => {
    getStats();
})
</script>

<template>
    <div class="row mb-2">
        <h6 class="display-6">Student Dashboard</h6>
        <p class="lead text-muted">Welcome back, {{ auth.currentUser.name }}!</p>
        <p>{{ stats }}</p>
    </div>

    <div class="row d-flex">
        <div class="col">
            <button @click="taskStore.exportCsv" type="button" class="btn btn-sm btn-success mb-3"><i class="bi bi-download me-2"></i>Download Application History</button>
        </div>
    </div>
    <hr>

    <div class="row justify-content-center">
        <div class="col">
            <h4 class="mb-3">Your Applications</h4>
            <PaginatedTable :url="my_applications_url" :fields="my_applications_fields" :item_route_name="my_application_route" />
        </div>
    </div>
    <hr>

    <div class="row justify-content-center">
        <div class="col">
            <h4 class="mb-3">Open Positions</h4>
            <PaginatedTable :url="positions_url" :fields="positions_fields" :item_route_name="position_route" />
        </div>
    </div>
</template>