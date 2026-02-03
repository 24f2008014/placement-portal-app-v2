<script setup>
import PaginatedTable from "@/components/PaginatedTable.vue";
const students_url = "/students?limit=2";
const students_fields = {
    "ID": "id",
    "Roll Number": "roll_number",
    "First Name": "first_name",
    "Last Name": "last_name",
}
const companies_url = "/companies"
const companies_fields = {
    "ID": "id",
    "Name": "name",
}
</script>

<template>
    <div class="row">
        <h6 class="display-6">Admin Dashboard</h6>
    </div>
    <hr class="mb-4">
    <div class="row">
        <div class="col">
            <h4 class="mb-3">Students</h4>
            <PaginatedTable :url="students_url" :fields="students_fields" />
        </div>
    </div>
    <div class="row">
        <div class="col">
            <h4 class="mb-3">Companies</h4>
            <PaginatedTable :url="companies_url" :fields="companies_fields" />
        </div>
    </div>
</template>