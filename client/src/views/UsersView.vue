<script setup>
import { ref, onMounted } from "vue";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { api } from "@/utils/api";

const users_endpoint = "/users";
const users_route = "company";
const users_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Email": {
        name: "email",
        filter: true,
        label: "Email",
        input: {
            type: "email"
        }
    },
    "Role(s)": {
        name: "roles",
        filter: false
    },
    "Created At": {
        name: "created_at",
        filter: true,
        label: "Created At",
        type: "date",
        input: {
            type: "date"
        }
    }
};
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-globe-americas" style="font-size: 3.5rem"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Users</h6>
            <p class="lead text-muted">A list of all registered users on this platform.</p>
        </div>
    </div>
    <hr class="mb-4">

    <div class="row justify-content-center">
        <div class="col">
            <PaginatedTable :url="users_endpoint" :fields="users_fields" :item_route_name="users_route" />
        </div>
    </div>
</template>