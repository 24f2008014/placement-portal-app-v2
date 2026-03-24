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
    "ID": "id",
    "Role": "role",
};
const position_route_name = "student_position";
const companies_url = `/companies?filters={"status":"whitelisted"}`;
const companies_fields = {
    "ID": "id",
    "Name": "name",
};
const company_route_name = "student_position";

onMounted(() => {

});
</script>

<template>
    <div class="row">
        <h6 class="display-6">Student Dashboard</h6>
    </div>
    <hr>
    <div class="row justify-content-center">
        <div class="col">
            <h4 class="mb-3">Open Positions</h4>
            <PaginatedTable :url="positions_url" :fields="positions_fields" :item_route_name="position_route_name" />
        </div>
    </div>
    <hr>
    <div class="row justify-content-center">
        <div class="col">
            <h4 class="mb-3">Companies</h4>
            <PaginatedTable :url="companies_url" :fields="companies_fields" :item_route_name="company_route_name" />
        </div>
    </div>
</template>