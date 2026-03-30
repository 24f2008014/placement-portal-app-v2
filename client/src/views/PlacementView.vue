<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import * as bootstrap from "bootstrap";
import { useAlertStore } from "@/stores/alert";
import { formatDate } from "@/utils/helpers";
import Modal from "@/components/Modal.vue";
import { flattenResponse } from "@/utils/helpers";

const alert = useAlertStore();
const auth = useAuthStore();
const loading = ref(true);
const placement = ref(null);
const router = useRouter();
const route = useRoute();
const errors = ref({});

async function getPlacement() {
    try {
        loading.value = true;
        const response = await api.get(`/placements/${route.params.id}`);
        placement.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
    finally {
        loading.value = false;
    }
};

async function withdrawPlacement() {
    try {
        const response = await api.post(`/placements/${route.params.id}/withdraw`, null);
        placement.value = response.data;
        const withdrawPlacementModal = document.getElementById("withdrawPlacementModal");
        const withdrawPlacementModalInstance = bootstrap.Modal.getInstance(withdrawPlacementModal);
        withdrawPlacementModalInstance.hide();
        alert.addAlert(`Successfully withdrawn your placement offer (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data.json.errors);
    }
};

async function acceptPlacement() {
    try {
        const response = await api.post(`/placements/${route.params.id}/accept`, null);
        placement.value = response.data;
        const acceptPlacementModal = document.getElementById("acceptModal");
        const acceptPlacementModalInstance = bootstrap.Modal.getInstance(acceptPlacementModal);
        acceptPlacementModalInstance.hide();
        alert.addAlert(`Successfully accepted placement offer (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data.json.errors);
    }
};

async function rejectPlacement() {
    try {
        const response = await api.post(`/placements/${route.params.id}/reject`, null);
        placement.value = response.data;
        const rejectPlacementModal = document.getElementById("rejectModal");
        const rejectPlacementModalInstance = bootstrap.Modal.getInstance(rejectPlacementModal);
        rejectPlacementModalInstance.hide();
        alert.addAlert(`Successfully rejected placement offer (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data.json.errors);
    }
};

onMounted(() => {
    getPlacement();
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Placement</h6>
            <p class="lead text-muted">Placement ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "application", params: {"id": placement.application_id} })'>
                        <i class="bi bi-arrow-left me-2"></i>Application
                    </button>
                    <button type="button" class="btn btn-success btn-sm" @click='router.push({ "name": "student_dashboard" })'>
                        <i class="bi bi-graph-up me-2"></i>Dashboard
                    </button>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">

    <p v-if="Object.keys(errors).length > 0" class="text-danger">{{ errors }}</p>

    <template v-if="!loading">
        <div class="row mb-4">
            <h3>Placement Details</h3>
        </div>
        <div class="row mb-4">
            <div class="col">
                <h6 class="text-primary-emphasis">Student Name</h6>
                <p>
                    {{ placement.application.student.first_name + " " + placement.application.student.last_name }}
                    <RouterLink v-if="auth.currentUser.role!='student'" :to="{name: 'student', params: {'id': placement.application.student.id}}">(click to view)</RouterLink>
                </p>
                <h6 class="text-primary-emphasis">Student Roll No.</h6>
                <p>{{ placement.application.student.roll_number }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Role</h6>
                <p>{{ placement.application.position.role }}</p>
                <h6 class="text-primary-emphasis">Company</h6>
                <p>{{ placement.application.position.company.name }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Salary</h6>
                <p>{{ placement.salary }}</p>
                <h6 class="text-primary-emphasis">Joining Date</h6>
                <p>{{ formatDate(placement.joining_date) }}</p>
            </div>
        </div>
        <hr class="mb-4">

        <template v-if="auth.currentUser.role=='student'">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ placement.status }}</code></h3>
                    <template v-if="placement.status=='pending'">
                        <p>This placement offer is <strong>pending</strong> your decision.</p>
                        <div class="row">
                            <div class="col d-flex gap-3">
                                <button type="button" class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#acceptModal"><i class="bi bi-check-lg me-2"></i>Accept</button>
                                <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#rejectModal"><i class="bi bi-x-lg me-2"></i>Reject</button>
                            </div>
                        </div>
                    </template>
                    <p v-else-if="placement.status=='accepted'">You have <strong>accepted</strong> this placement offer. Congratulations!</p>
                    <p v-else-if="placement.status=='accepted'">You have <strong>rejected</strong> this placement offer.</p>
                    <p v-else-if="placement.status=='withdrawn'">The placement offer has been <strong>withdrawn</strong> by the company.</p>
                </div>                

                <Modal :title="'Accept Placement Offer'" :id="'acceptModal'" :yesLabel="'Accept'" @confirm="acceptPlacement">
                    <template #modal-body>
                        <p>Are you sure you want to <strong>accept</strong> this company's placement offer? This cannot be undone.</p>
                    </template>
                </Modal>
                
                <Modal :title="'Reject Placement Offer'" :id="'rejectModal'" :yesLabel="'Reject'" @confirm="rejectPlacement">
                    <template #modal-body>
                        <p>Are you sure you want to <strong>reject</strong> this company's placement offer? This cannot be undone.</p>
                    </template>
                </Modal>                
            </div>
            <hr class="mb-4">
        </template>

        <template v-else-if="auth.currentUser.role=='company'">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ placement.status }}</code></h3>
                    <template v-if="placement.status=='pending'">
                        <p>This placement offer is <strong>pending</strong> the student's decision.</p>
                        <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#withdrawModal"><i class="bi bi-x-lg me-2"></i>Withdraw</button>
                    </template>
                    <p v-else-if="placement.status=='accepted'">This placement offer has been <strong>accepted</strong> by the student.</p>
                    <p v-else-if="placement.status=='rejected'">This placement offer has been<strong>rejected</strong> by the student.</p>
                    <p v-else-if="placement.status=='withdrawn'">The placement offer has been <strong>withdrawn</strong> by the company.</p>
                </div>

                 <Modal :title="'Withdraw Placement Offer'" :id="'withdrawModal'" :yesLabel="'Withdraw'" @confirm="withdrawPlacement">
                    <template #modal-body>
                        <p>Are you sure you want to <strong>withdraw</strong> your placement offer? This cannot be undone.</p>
                    </template>
                </Modal>
            </div>
            <hr class="mb-4">
        </template>

    </template>
</template>