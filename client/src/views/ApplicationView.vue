<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import PaginatedTable from "@/components/PaginatedTable.vue";
import PositionViewForm from "@/components/PositionViewForm.vue";
import { useAuthStore } from "@/stores/auth";
import * as bootstrap from "bootstrap";
import { useAlertStore } from "@/stores/alert";
import { formatDate } from "@/utils/helpers";
import Modal from "@/components/Modal.vue";
import { flattenResponse } from "@/utils/helpers";

const alert = useAlertStore();
const auth = useAuthStore();
const loading = ref(true);
const application = ref(null);
const router = useRouter();
const route = useRoute();
const errors = ref({});
const shortlistInterviewDate = ref(null);
const now = new Date();
const minDate = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);

async function getApplication() {
    try {
        loading.value = true;
        const response = await api.get(`/applications/${route.params.id}`);
        application.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
    finally {
        loading.value = false;
    }
};

async function withdrawApplication() {
    try {
        const formData = { status: "withdrawn" };
        const response = await api.patch(`/positions/${route.params.id}`, formData);
        application.value = response.data;
        const withdrawApplicationModal = document.getElementById("withdrawApplicationModal");
        const withdrawApplicationModalInstance = bootstrap.Modal.getInstance(withdrawApplicationModal);
        withdrawApplicationModalInstance.hide();
        alert.addAlert(`Successfully withdrew your application (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data.json.errors);
    }
};

async function shortlistApplication() {
    try {
        const response = await api.post(`/applications/${route.params.id}/shortlist`, { interview_date: shortlistInterviewDate.value });
        application.value = response.data;
        console.log(response.data)
        const statusModal = document.getElementById("shortlistModal");
        const statusModalInstance = bootstrap.Modal.getInstance(statusModal);
        statusModalInstance.hide();
        alert.addAlert(`Successfully shortlisted application (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data);
    }
}

async function rejectApplication() {
    try {
        const response = await api.post(`/applications/${route.params.id}/reject`);
        application.value = response.data;
        const statusModal = document.getElementById("rejectModal");
        const statusModalInstance = bootstrap.Modal.getInstance(statusModal);
        statusModalInstance.hide();
        alert.addAlert(`Successfully rejected application (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data);
    }
}

async function selectApplication() {
    try {
        const response = await api.post(`/applications/${route.params.id}/select`);
        application.value = response.data;
        const statusModal = document.getElementById("selectModal");
        const statusModalInstance = bootstrap.Modal.getInstance(statusModal);
        statusModalInstance.hide();
        alert.addAlert(`Successfully selected application (#${route.params.id}).`, "success");
    }
    catch (error) {
        console.log(error);
        errors.value = flattenResponse(error.response.data);
    }
}

onMounted(() => {
    getApplication();
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Application</h6>
            <p class="lead text-muted">Application ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "company_positions" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Positions
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
        <p>{{ application }}</p>
        <div class="row mb-4">
            <div class="col">
                <h6 class="text-primary-emphasis">Student Name</h6>
                <p>
                    {{ application.student.first_name + " " + application.student.last_name }}
                    <RouterLink v-if="auth.currentUser.role!='student'" :to="{name: 'student', params: {'id': application.student_id}}">(click to view)</RouterLink>
                </p>
                <h6 class="text-primary-emphasis">Student Roll No.</h6>
                <p>{{ application.student.roll_number }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Role</h6>
                <p>{{ application.position.role }}</p>
                <h6 class="text-primary-emphasis">Company</h6>
                <p>{{ application.position.company.name }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Date Submitted</h6>
                <p>{{ formatDate(application.created_at) }}</p>
                <h6 class="text-primary-emphasis">Status</h6>
                <p>{{ application.status }}</p>
            </div>
        </div>
        <hr class="mb-4">

        <template v-if="auth.currentUser.role=='student'">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ application.status }}</code></h3>
                    <p v-if="application.status=='pending'">Your application is currently <strong>pending</strong>. Please wait for the company to take a look at it.</p>
                    <template v-else-if="application.status=='shortlisted'">
                        <p>Your application has been shortlisted, and you have an interview scheduled. The company will get in touch with you via email soon to organize the interview. In case you have any further questions, here is their email address.</p>
                        <p class="mb-0"><strong>Interview Date: </strong>{{ formatDate(application.interview_date) }}</p>
                        <p class="mb-3"><strong>Company Email: </strong>{{ application.position.company.contact_email }}</p>
                    </template>
                    <p v-else-if="application.status=='selected'">Your application has been <strong>selected</strong>! Congratulations!</p>
                    <p v-else-if="application.status=='rejected'">Unfortunately, your application has been<strong>rejected</strong>. Thank you for applying.</p>
                    <p v-else-if="application.status=='withdrawn'">You have <strong>withdrawn</strong> your application.</p>
                    <button v-if="application.status!='withdrawn'" type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#withdrawApplicationModal"><i class="bi bi-x-lg me-2"></i>Withdraw Application</button>
                </div>

                <div>
                    <div class="modal fade" tabindex="-1" id="withdrawApplicationModal" aria-labelledby="withdrawApplicationModalTitle">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="withdrawApplicationModalTitle">Change Status</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <p>Are you sure you want to <strong>withdraw</strong> your application (#{{ $route.params.id }})? This cannot be undone.</p>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
                                    <button type="button" class="btn btn-danger btn-sm" @click="withdrawApplication">Withdraw</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <hr class="mb-4">
        </template>

        <template v-else-if="auth.currentUser.role=='company'">
            <div class="row mb-4">
                <div class="col">
                    <h3>Current Status: <code>{{ application.status }}</code></h3>
                    <template v-if="application.status=='pending'">
                        <p>This application is <strong>pending</strong> further review. You can either shortlist the applicant for an interview, or reject their application.</p>
                        <button type="button" class="btn btn-sm btn-success me-2" data-bs-toggle="modal" data-bs-target="#shortlistModal"><i class="bi bi-check-lg me-2"></i>Shortlist</button>
                        <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#rejectModal"><i class="bi bi-x-lg me-2"></i>Reject</button>
                    </template>
                    <template v-else-if="application.status=='shortlisted'">
                        <p>This application has been <strong>shortlisted</strong>. You can either make them a placement offer, or reject their application.</p>
                        <button type="button" class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#selectModal"><i class="bi bi-check-lg me-2"></i>Select</button>
                        <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#rejectModal"><i class="bi bi-x-lg me-2"></i>Reject</button>
                    </template>
                    <p v-else-if="application.status=='selected'">This application has been <strong>selected</strong>.</p>
                    <p v-else-if="application.status=='rejected'">This application has been<strong>rejected</strong>.</p>
                    <p v-else-if="application.status=='withdrawn'">The candidate has <strong>withdrawn</strong> their application.</p>
                </div>

                <Modal :title="'Shortlist Application'" :id="'shortlistModal'" :yesLabel="'Shortlist'" @confirm="shortlistApplication">
                    <template #modal-body>
                        <p>Would you like to <strong>shortlist</strong> this student's application (#{{ $route.params.id }}) for an interview?</p>
                        <form>
                            <div class="row mb-3">
                                <div class="col">
                                    <label for="shortlistInterviewDate" class="form-label"><strong>Interview date</strong></label>
                                    <input class="form-control" type="datetime-local" :class="{ 'is-invalid': errors.interview_date }"id="shortlistInterviewDate" v-model="shortlistInterviewDate" required aria-describedby="inputDeadlineValidation" :min="minDate">
                                    <div v-if="errors.interview_date" class="invalid-feedback" id="shortlistInterviewDateValidation">{{ errors.interview_date[0] }}</div>
                                </div>
                            </div>
                        </form>
                    </template>
                </Modal>

                <Modal :title="'Reject Application'" :id="'rejectModal'" :yesLabel="'Reject'" @confirm="rejectApplication">
                    <template #modal-body>
                        <p>Are you sure you want to <strong>reject</strong> this student's application (#{{ $route.params.id }})? This cannot be undone.</p>
                    </template>
                </Modal>

                <Modal :title="'Select Application'" :id="'selectModal'" :yesLabel="'Select'" @confirm="selectApplication">
                    <template #modal-body>
                        <p>Are you sure you want to <strong>select</strong> this student's application (#{{ $route.params.id }})?</p>
                    </template>
                </Modal>
            </div>
            <hr class="mb-4">
        </template>

    </template>
</template>