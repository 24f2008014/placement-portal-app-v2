<script setup>
import PaginatedTable from "@/components/PaginatedTable.vue";
const students_url = '/students?filters={"status":"whitelisted"}';
const students_route_name = "student"
const students_fields = {
    "ID": "id",
    "Roll No.": "roll_number",
    "Email": "email",
    "First Name": "first_name",
    "Last Name": "last_name",
    "Status": "status"
}
const companies_url = "/companies"
const companies_route_name = "company"
const companies_fields = {
    "ID": "id",
    "Name": "name",
    "Email": "email",
    "Status": "status"
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
            <!-- <button class="btn btn-primary btn-sm" data-bs-toggle="collapse" data-bs-target="#searchCollapse">Filter</button>
            <div class="row mb-3 collapse" id="searchCollapse">
                <div class="col">
                    <form class="p-3 border rounded shadow-sm" @submit.prevent="filterData">
                        <div class="row mb-3">
                            <div class="col-2">
                                <label for="ID" class="form-label">ID</label>
                                <input type="number" class="form-control" id="inputID" v-model="inputID" min="0">
                            </div>
                            <div class="col-2">
                                <label for="inputRollNumber" class="form-label">Roll No.</label>
                                <input type="number" class="form-control" id="inputRollNumber" v-model="inputRollNumber" min="0">
                            </div>
                        </div>
                        <button class="btn btn-success btn-sm">Submit</button>
                    </form>
                </div>
            </div> -->
            <PaginatedTable :url="students_url" :fields="students_fields" :item_route_name="students_route_name" />
        </div>
    </div>
    <!-- <div class="row">
        <div class="col">
            <h4 class="mb-3">Companies</h4>
            <PaginatedTable :url="companies_url" :fields="companies_fields" :item_route_name="companies_route_name" />
        </div>
    </div> -->
</template>