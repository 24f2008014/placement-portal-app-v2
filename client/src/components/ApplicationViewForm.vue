<script setup>
import { formatDate } from "@/utils/helpers";
const props = defineProps(["application"]);
</script>

<template>
    <div class="row border rounded border-dark-subtle py-3 px-3 mx-0 mb-4 bg-body-tertiary">
        <div class="col">
            <h3 class="mb-1 display-6 fw-bold">{{ props.application.role }}</h3>
            <p class="lead text-muted"><a href="#">@ {{ props.application.company.name }}</a></p>
            <div class="row row-cols-1 mb-3">
                <div class="col"><p class="lead mb-1"><i class="bi bi-currency-rupee me-2"></i>{{ props.application.salary_min }}&ndash;{{ props.application.salary_max }} <span class="text-muted">(monthly)</span></p></div>
                <div class="col"><p class="lead mb-1"><i class="bi bi-geo-alt-fill me-2"></i>{{ props.application.company.location }}</p></div>
            </div>
            <h4 class="mb-2">Status</h4>
            <p class="lead mb-1" v-if="props.application.status=='open'">
                <i class="bi bi-check-lg me-2 fs-6 text-success"></i><strong>Open</strong>
            </p>
            <p class="lead mb-1" v-else>
                <i class="bi bi-x-lg me-2 fs-6 text-danger"></i><strong>Closed</strong>
            </p>            
        </div>
        
        <div class="col">
            <h4 class="mb-2">Eligibility</h4>
            <p class="lead mb-1"><i class="bi bi-dash me-2 fs-6"></i> <strong>Minimum CGPA:</strong> {{ props.application.min_cgpa }}</p>
            <p class="lead mb-4"><i class="bi bi-dash me-2 fs-6"></i> <strong>Departments:</strong> {{ props.application.departments }}</p>
            <h4 class="mb-2">Created At</h4>
            <p class="lead mb-4"><i class="bi bi-calendar-check fs-6 me-2"></i> <strong>{{ formatDate(props.application.created_at) }}</strong></p>
            <h4 class="mb-2">Deadline</h4>
            <p class="lead mb-1"><i class="bi bi-calendar-check fs-6 me-2"></i> <strong>{{ formatDate(props.application.deadline) }}</strong></p>
        </div>
    </div>
    <hr class="mb-4">

    <!-- <div class="row">
        <h3 class="mb-3">Status: <code>{{ props.application.status }}</code></h3>
        <p>This application is currently accepting new applications.</p>
    </div>
    <hr class="mb-4"> -->

    <div class="row">
        <h3 class="mb-3">Job Description</h3>
        <p>{{ props.application.description }}</p>
    </div>
</template>