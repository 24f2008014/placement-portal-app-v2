<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref } from "vue";
import PaginatedTable from "@/components/PaginatedTable.vue";

const loading = ref(true);
const errors = ref({});
const auth = useAuthStore();

const companies_url = "/companies";
const companies_fields = {
    "ID": {name: "id", filter: true, sort: true},
    "Name": {name: "name", filter: false}
};
const company_route = "company";
</script>

<template>
    <div class="row">
        <h6 class="display-6">Active Companies</h6>
        <p class="lead text-muted">A list of all companies currently active on our platform.</p>
    </div>
    <hr>
    <div class="row justify-content-center">
        <div class="col">
            <h4 class="mb-3">Companies</h4>
            <PaginatedTable :url="companies_url" :fields="companies_fields" :item_route_name="company_route" />
        </div>
    </div>
</template>