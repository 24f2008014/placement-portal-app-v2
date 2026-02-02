<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";

const errors = ref({});
const students = ref();
const studentsPagination = ref();

async function getStudents() {
    errors.value = {};
    try {
        // const filters = JSON.stringify({ last_name: "e", first_name: "e", });
        // const response = await api.get(`/students?filters=${encodeURIComponent(filters)}`);
        // const response = await api.get(`/students?filters={"first_name":"e"}`);
        const response = await api.get(`/students?limit=2`);
        students.value = response.data.data;
        studentsPagination.value = response.data.pagination;
    }
    catch (error) {
        console.log(error)
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
};

onMounted(() => {
    getStudents();
})
</script>

<template>
    <div class="row justify-content-center">
        <div class="col">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th scope="col">ID</th>
                        <th scope="col">Roll No.</th>
                        <th scope="col">First Name</th>
                        <th scope="col">Last Name</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="s in students" :key="s.id">
                        <td>{{ s.id }}</td>
                        <td>{{ s.roll_number }}</td>
                        <td>{{ s.first_name }}</td>
                        <td>{{ s.last_name }}</td>
                    </tr>
                </tbody>
            </table>
            <p>{{ studentsPagination }}</p>
            <ul v-for="s in students" :key="s.id">
                <li>{{ s }}</li>
            </ul>
        </div>
    </div>
</template>