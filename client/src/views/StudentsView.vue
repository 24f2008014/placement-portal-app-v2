<script setup>
import PaginatedTable from "@/components/PaginatedTable.vue";

const students_endpoint = "/students";
const students_route = "student";
const students_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Roll No.": {
        name: "roll_number",
        filter: true,
        label: "Roll No.",
        input: {
            type: "text"
        }
    },
    "Email": {
        name: "user.email",
        filter: false
    },
    "First Name": {
        name: "first_name",
        filter: true,
        label: "First Name",
        input: {
            type: "text"
        }
    },
    "Last Name": {
        name: "last_name",
        filter: true,
        label: "Last Name",
        input: {
            type: "text"
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
                {value: "whitelisted", label: "Whitelisted"},
                {value: "blacklisted", label: "Blacklisted"}
            ]
        }
    }
};
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-book" style="font-size: 3.5rem"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Students</h6>
            <p class="lead text-muted">A list of all registered students on this platform.</p>
        </div>
    </div>
    <hr class="mb-4">

    <div class="row justify-content-center">
        <div class="col">
            <PaginatedTable :url="students_endpoint" :fields="students_fields" :item_route_name="students_route" />
        </div>
    </div>
</template>