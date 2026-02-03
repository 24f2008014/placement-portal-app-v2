<script setup>
import { formatDate } from "@/utils/helpers";
const props = defineProps(["position"]);
</script>

<template>
    <div class="row border rounded border-dark-subtle py-3 px-3 mb-4 bg-body-tertiary">
        <div class="col">
            <h3 class="mb-1 display-6 fw-bold">{{ props.position.role }}</h3>
            <p class="lead text-muted"><a href="#">@ {{ props.position.company.name }}</a></p>
            <div class="row row-cols-1 mb-3">
                <div class="col"><p class="lead mb-1"><i class="bi bi-geo-alt-fill me-2"></i>{{ props.position.company.location }}</p></div>
                <div class="col"><p class="lead mb-1"><i class="bi bi-currency-rupee me-2"></i>{{ props.position.salary_min }}&ndash;{{ props.position.salary_max }} <span class="text-muted">(monthly)</span></p></div>
            </div>
            <h4 class="mb-2">Status</h4>
            <p class="lead mb-1"><i class="bi bi-check-lg me-2 fs-6 text-success"></i><strong>Open</strong></p>
        </div>
        <div class="col">
            <h4 class="mb-2">Eligibility</h4>
            <p class="lead mb-1"><i class="bi bi-dash me-2 fs-6"></i> <strong>Minimum CGPA:</strong> {{ props.position.min_cgpa }}</p>
            <p class="lead mb-1"><i class="bi bi-dash me-2 fs-6"></i> <strong>Departments:</strong> Any</p>
            <p class="lead"><i class="bi bi-dash me-2 fs-6"></i> <strong>Branches:</strong> Any</p>
            <h4 class="mb-2">Deadline</h4>
            <p class="lead mb-1"><i class="bi bi-calendar-check fs-6 me-2"></i> <strong>{{ formatDate(props.position.deadline) }}</strong></p>
        </div>
    </div>
    <div class="row">
        <h3 class="mb-3">Job Description</h3>
        <p>{{ props.position.description }}</p>
    </div>
</template>