<script setup>
import { ref, onMounted } from "vue";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { api } from "@/utils/api";

const industries = ref();

async function getIndustries() {
    try {
        const response = await api.get("/industries");
        industries.value = response.data;
    } catch (error) {
        console.error(error);
    }
}

const companies_endpoint = "/companies";
const companies_route = "company";
const companies_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Name": {
        name: "name",
        filter: true,
        label: "Name",
        input: {
            type: "text"
        }
    },
    "Industry": {
        name: "industry.name",
        filter: true,
        label: "Industry",
        input: {
            type: "text"
        }
    },
    "Location": {
        name: "location",
        filter: true,
        label: "Location",
        input: {
            type: "text"
        }
    },
    "Email": {
        name: "contact_email",
        filter: true,
        label: "Email",
        input: {
            type: "email"
        }
    },
    "Open Positions": {
        name: "open_position_count",
        filter: true,
        label: "Open Positions \u2265",
        input: {
            type: "number",
            min: "0"
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
                {value: "pending", label: "Pending"},
                {value: "whitelisted", label: "Whitelisted"},
                {value: "blacklisted", label: "Blacklisted"}
            ]
        }
    }
};

onMounted(() => {
    getIndustries();
});
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-globe-americas" style="font-size: 3.5rem"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Companies</h6>
            <p class="lead text-muted">A list of all registered companies on this platform.</p>
        </div>
    </div>
    <hr class="mb-4">

    <div class="row justify-content-center">
        <div class="col">
            <PaginatedTable :url="companies_endpoint" :fields="companies_fields" :item_route_name="companies_route" />
        </div>
    </div>
</template>