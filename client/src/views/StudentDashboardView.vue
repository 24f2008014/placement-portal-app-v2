<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";

const loading = ref(true);
const errors = ref({});
const auth = useAuthStore();

const positions_url = "/positions";
const positions_fields = {
    "ID": {name: "id", filter: true, input_type: "number", sort: true},
    "Role": {name: "role", filter: true, input_type: "text"},
    "Company": {name: "name", filter: false},
    "Salary (Min.)": {name: "salary_min", filter: false},
    "Salary (Max.)": {name: "salary_max", filter: false},
    "Min. CGPA": {name: "min_cgpa", filter: false},
    "Deadline": {name: "deadline", filter: false},
    "Status": {name: "status", filter: false},
}
const position_route = "position";

const my_applications_url = "/students/me/applications";
const my_applications_fields = {
    "ID": {name: "id", filter: true, sort: true},
    "Status": {name: "status", filter: true}
}
const my_application_route = "application";

const companies_url = "/companies";
const companies_fields = {
    "ID": {name: "id", filter: true, sort: true},
    "Name": {name: "name", filter: false}
};
const company_route = "company";

onMounted(() => {

});
</script>

<template>
    <div class="row">
        <h6 class="display-6">Student Dashboard</h6>
        <p class="lead text-muted">Welcome back, {{ auth.currentUser.name }}!</p>
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
    <hr>
    <div class="row justify-content-center">
        <div class="col">
            <h4 class="mb-3">Companies</h4>
            <PaginatedTable :url="companies_url" :fields="companies_fields" :item_route_name="company_route" />
        </div>
    </div>
</template>