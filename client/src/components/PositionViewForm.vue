<script setup>
import { formatDate, formatDateNoTime } from "@/utils/helpers";
import { useAuthStore } from "@/stores/auth";

const props = defineProps(["position"]);
const auth = useAuthStore();

function getDaysUntil(d) {
    const today = new Date();
    const target = new Date(d);
    if (today > target) {
        return 0;
    }
    const diff = target.getTime() - today.getTime();
    return Math.round(diff / (1000 * 60 * 60 * 24));
}
</script>

<template>
    <div class="row border rounded border-dark-subtle py-3 px-3 mx-0 mb-4 bg-body-tertiary">
        <div class="col">
            <h3 class="mb-1 display-6 fw-bold">{{ props.position.role }}</h3>
            
            <p v-if="auth.currentUser.role!='company'" class="lead text-muted"><RouterLink :to="{ name: 'company', params: { id: props.position.company_id } }">@ {{ props.position.company.name }}</RouterLink></p>
            <p v-else class="lead text-muted">@ {{ props.position.company.name }}</p>

            <div class="row row-cols-1 mb-3">
                <div class="col"><p class="lead mb-1"><i class="bi bi-currency-rupee me-2"></i>{{ props.position.salary_min.toLocaleString("en-US") }}&ndash;{{ props.position.salary_max.toLocaleString("en-US") }} <span class="text-muted">(monthly)</span></p></div>
                <div class="col"><p class="lead mb-1"><i class="bi bi-geo-alt-fill me-2"></i>{{ props.position.company.location }}</p></div>
            </div>

            <h5 class="mb-2">Status</h5>
            <p class="mb-4" v-if="props.position.status=='open'"><i class="bi bi-check-lg me-2 fs-6 text-success"></i><strong>Open</strong></p>
            <p class="mb-4" v-else><i class="bi bi-x-lg me-2 fs-6 text-danger"></i><strong>Closed</strong></p>

            <h5 class="mb-2">Applications Received</h5>
            <p class="mb-1">{{ props.position.application_count }}</p>
        </div>

        <div class="col">
            <h5 class="mb-2">Eligibility</h5>
            <ul>
                <li>Minimum CGPA: {{ props.position.min_cgpa }}</li>
                <li>
                    Departments:
                    <ul>
                        <li v-for="d in props.position.departments" :id="d.id">{{ d.name }}</li>
                    </ul>
                </li>
            </ul>
            <h5 class="mb-2">Posted On</h5>
            <p class="mb-4"><i class="bi bi-calendar-check fs-6 me-2"></i>{{ formatDateNoTime(props.position.created_at) }}</p>
            <h5 class="mb-2">Deadline</h5>
            <p class="mb-1"><i class="bi bi-calendar-check fs-6 me-2"></i>{{ formatDate(props.position.deadline) }} ({{ getDaysUntil(props.position.deadline) }} days left)</p>
        </div>
    </div>
    <hr class="mb-4">

    <div class="row">
        <h3 class="mb-3">Job Description</h3>
        <p>{{ props.position.description }}</p>
    </div>
</template>