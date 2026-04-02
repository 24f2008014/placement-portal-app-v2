<script setup>
import PaginatedTable from "@/components/PaginatedTable.vue";

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
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-envelope" style="font-size: 3.5rem;"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Your Placements</h6>
            <p class="lead text-muted">A list of all position listings made by companies.</p>
        </div>
    </div>
    <hr class="mb-4">
    
    <div class="row justify-content-center">
        <div class="col">
            <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
        </div>
    </div>
</template>