<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useTaskStore } from "@/stores/tasks";

const taskStore = useTaskStore();
const stats = ref({});

const students_endpoint = "/students";
const students_route = "student"
const students_fields = {
    "ID": {
        name: "id",
        filter: true
    },
    "Roll No.": {
        name: "roll_number",
        filter: true
    },
    "Email": {
        name: "email"
    },
    "First Name": {
        name: "first_name"
    },
    "Last Name": {
        name: "last_name"
    },
    "Status": {
        name: "status"
    }
};

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
            type: "name"
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

async function getStats() {
    try {
        const response = await api.get("/stats");
        stats.value = response.data;
    } catch (error) {
        console.error(error.response.data);
    }
};

onMounted(() => {
    getStats();
});
</script>

<template>
    <div class="row">
        <h6 class="display-6">Admin Dashboard</h6>
    </div>
    <hr class="mb-4">

    <p>{{ stats }}</p>

    <button @click="taskStore.exportCsv" type="button" class="btn btn-sm btn-success mb-3">Start Task</button>
    <template v-if="Object.keys(taskStore.tasks).length>0">
        <div v-for="(task, id) in taskStore.tasks" :key="id">
            {{ task, id }}
        </div>
    </template>

    <div class="row">
        <div class="col">
            <h4 class="mb-3">Students</h4>
            <PaginatedTable :url="students_endpoint" :fields="students_fields" :item_route_name="students_route" />
        </div>
    </div>

    <div class="row">
        <div class="col">
            <h4 class="mb-3">Companies</h4>
            <PaginatedTable :url="companies_endpoint" :fields="companies_fields" :item_route_name="companies_route" />
        </div>
    </div>
</template>