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
import { viewResume } from "@/utils/helpers";

const alert = useAlertStore();
const auth = useAuthStore();
const loading = ref(true);
const application = ref(null);
const router = useRouter();
const route = useRoute();
const errors = ref({});
const shortlistInterviewDate = ref(null);
const selectJoiningDate = ref(null);
const selectSalary = ref(null);
const now = new Date();
const minDate = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
const rejectFeedback = ref(null);

async function getApplication() {
    try {
        loading.value = true;
        const response = await api.get(`/applications/${route.params.id}`);
        application.value = response.data;
        loading.value = false;
    } catch (error) {
        console.error(error);
    }
}

async function withdrawApplication() {
    try {
        const response = await api.post(`/applications/${route.params.id}/withdraw`);
        application.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("withdrawApplicationModal")).hide();
        alert.addAlert(`Successfully withdrew your application (#${route.params.id}).`, "success");
    } catch (error) {
        console.error(error);
        // errors.value = flattenResponse(error.response.data.json.errors);
    }
}

async function shortlistApplication() {
    try {
        const response = await api.post(`/applications/${route.params.id}/shortlist`, { interview_date: shortlistInterviewDate.value });
        application.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("shortlistModal")).hide();
        alert.addAlert(`Successfully shortlisted application (#${route.params.id}).`, "success");
    } catch (error) {
        console.error(error);
        errors.value = flattenResponse(error.response.data);
    }
}

async function rejectApplication() {
    try {
        const response = await api.post(`/applications/${route.params.id}/reject`, { feedback: rejectFeedback.value });
        application.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("rejectModal")).hide();
        alert.addAlert(`Successfully rejected application (#${route.params.id}).`, "success");
    } catch (error) {
        console.error(error);
        errors.value = flattenResponse(error.response.data);
    }
}

async function selectApplication() {
    try {
        const formData = {
            joining_date: selectJoiningDate.value,
            salary: selectSalary.value
        };
        const response = await api.post(`/applications/${route.params.id}/select`, formData);
        application.value = response.data;
        bootstrap.Modal.getInstance(document.getElementById("selectModal")).hide();
        alert.addAlert(`Successfully selected application (#${route.params.id}).`, "success");
    } catch (error) {
        console.error(error);
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
            <div v-if="!loading" class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ name: "position", params: { id: application.position_id } })'><i class="bi bi-arrow-left me-2"></i>Position</button>
                </div>
            </div>
        </div>
    </div>

    <template v-if="!loading">
        <hr class="mb-4">
        <div class="row mb-4">
            <div class="col">
            <h3>Application Details</h3>
            <template v-if="auth.currentUser.role!='student'">
                <div class="row">
                    <div class="col d-flex mt-2 gap-2">
                        <button type="button" class="btn btn-sm btn-primary" @click="router.push({ name: 'student', params: { id: application.student_id } })"><i class="bi bi-box-arrow-up-right me-2"></i>View Student</button>
                        <button v-if="application.student.resume_url" type="button" class="btn btn-sm btn-success" @click="viewResume(application.student.resume_url)"><i class="bi bi-download me-2"></i>Get Resume</button>
                    </div>
                </div>
            </template>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col">
                <h6 class="text-primary-emphasis">Student Name</h6>
                <p>{{ application.student.first_name + " " + application.student.last_name }}</p>
                <h6 class="text-primary-emphasis">Student Roll No.</h6>
                <p>{{ application.student.roll_number }}</p>
            </div>
            <div class="col">
                <h6 class="text-primary-emphasis">Position</h6>
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
        <div class="row mb-4">
            <div class="col">
                <h3>Current Status: <code>{{ application.status }}</code></h3>
                <template v-if="application.status=='pending'">
                    <p>This application is currently <code class="text-warning fw-bold">pending</code> company review. The company may either shortlist the candidate for an interview, or reject the application.</p>
                    <button v-if="auth.currentUser.role=='student'" type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#withdrawApplicationModal"><i class="bi bi-x-lg me-2"></i>Withdraw Application</button>
                    <template v-else-if="auth.currentUser.role=='company'">
                        <div class="row">
                            <div class="col d-flex gap-2">
                                <button type="button" class="btn btn-sm btn-success me-2" data-bs-toggle="modal" data-bs-target="#shortlistModal"><i class="bi bi-check-lg me-2"></i>Shortlist</button>
                                <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#rejectModal"><i class="bi bi-x-lg me-2"></i>Reject</button>
                            </div>
                        </div>
                    </template>
                </template>

                <template v-else-if="application.status=='shortlisted'">
                    <p>This application has been <code class="text-primary fw-bold">shortlisted</code>, and an interview has been scheduled. The company will get in touch with the applicant via email soon to organize the interview. In case of any further questions, here is the company's email address.</p>
                    <p class="mb-0"><strong>Interview Date: </strong>{{ formatDate(application.interview_date) }}</p>
                    <p class="mb-3"><strong>Company Email: </strong>{{ application.position.company.contact_email }}</p>
                    <template v-if="auth.currentUser.role=='company'">
                        <div class="row">
                            <div class="col d-flex gap-3">
                                <button type="button" class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#selectModal"><i class="bi bi-check-lg me-2"></i>Select</button>
                                <button type="button" class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#rejectModal"><i class="bi bi-x-lg me-2"></i>Reject</button>
                            </div>
                        </div>
                    </template>
                </template>

                <template v-else-if="application.status=='selected'">
                    <p>This application has been <code class="text-success fw-bold">selected</code>. <RouterLink :to="{ name: 'placement', params: { 'id': application.placements[0].id } }">Click here</RouterLink> to view the linked placement offer.</p>
                </template>

                <template v-else-if="application.status=='rejected'">
                    <p class="mb-2">This application has been <code class="text-danger fw-bold">rejected</code> by the company.</p>
                    <p><strong>Feedback: </strong>{{ application.feedback ? application.feedback : "N/A" }}</p>
                </template>

                <p v-else-if="application.status=='withdrawn'">This application has been <code class="text-danger fw-bold">withdrawn</code> by the student.</p>
            </div>

            <Modal :title="'Change Status'" :id="'withdrawApplicationModal'" :yes-label="'Withdraw'" @confirm="withdrawApplication">
                <template #modal-body>
                    <p>Are you sure you want to <strong>withdraw</strong> your application (#{{ $route.params.id }})? This cannot be undone.</p>
                </template>
            </Modal>

            <Modal :title="'Shortlist Application'" :id="'shortlistModal'" :yesLabel="'Shortlist'" @confirm="shortlistApplication">
                <template #modal-body>
                    <p>Would you like to <strong>shortlist</strong> this student's application (#{{ $route.params.id }}) for an interview?</p>
                    <form>
                        <div class="row mb-3">
                            <div class="col">
                                <label for="shortlistInterviewDate" class="form-label"><strong>Interview date</strong></label>
                                <input class="form-control" type="datetime-local" :class="{ 'is-invalid': errors.interview_date } "id="shortlistInterviewDate" v-model="shortlistInterviewDate" required aria-describedby="inputDeadlineValidation" :min="minDate">
                                <div v-if="errors.interview_date" class="invalid-feedback" id="shortlistInterviewDateValidation">{{ errors.interview_date[0] }}</div>
                            </div>
                        </div>
                    </form>
                </template>
            </Modal>

            <Modal :title="'Reject Application'" :id="'rejectModal'" :yesLabel="'Reject'" @confirm="rejectApplication">
                <template #modal-body>
                    <p>Are you sure you want to <strong>reject</strong> this student's application (#{{ $route.params.id }})? This cannot be undone.</p>
                    <form>
                        <div class="row mb-3">
                            <div class="col">
                                <label for="rejectFeedback" class="form-label"><strong>Your Feedback</strong></label>
                                <input class="form-control" type="text" :class="{ 'is-invalid': errors.feedback }" id="rejectFeedback" v-model="rejectFeedback" required aria-describedby="rejectFeedbackValidation">
                                <div v-if="errors.feedback" class="invalid-feedback" id="rejectFeedbackValidation">{{ errors.feedback[0] }}</div>
                            </div>
                        </div>
                    </form>                    
                </template>
            </Modal>

            <Modal :title="'Select Application'" :id="'selectModal'" :yesLabel="'Select'" @confirm="selectApplication">
                <template #modal-body>
                    <p>Would you like to <strong>select</strong> this student's application (#{{ $route.params.id }}) and make them a placement offer?</p>
                    <form>
                        <div class="row mb-3">
                            <div class="col">
                                <label for="selectJoiningDate" class="form-label"><strong>Joining Date</strong></label>
                                <input class="form-control" type="date" :class="{ 'is-invalid': errors.joining_date }"id="selectJoiningDate" v-model="selectJoiningDate" required aria-describedby="selectJoiningDateValidation" :min="minDate">
                                <div v-if="errors.joining_date" class="invalid-feedback" id="selectJoiningDateValidation">{{ errors.joining_date[0] }}</div>
                            </div>
                            <div class="col">
                                <label for="selectSalary" class="form-label"><strong>Salary Offer</strong></label>
                                <input class="form-control" type="number" :class="{ 'is-invalid': errors.salary }"id="selectSalary" v-model="selectSalary" required aria-describedby="selectSalaryValidation" min=0>
                                <div v-if="errors.salary" class="invalid-feedback" id="selectSalaryValidation">{{ errors.salary[0] }}</div>
                            </div>
                        </div>
                    </form>
                </template>
            </Modal>
        </div>
    </template>
</template>