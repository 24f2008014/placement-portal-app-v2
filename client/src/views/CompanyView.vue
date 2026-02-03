<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
const loading = ref(true);
const company = ref({});
const errors = ref({});
const auth = useAuthStore();

async function getCompany() {
    try {
        const response = await api.get(`/companies/${route.params.id}`);
        company.value = response.data;
        loading.value = false;
    }
    catch (error) {
        console.log(error);
    }
}

onMounted(() => {
    getCompany();
})
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Company</h6>
            <p class="lead text-muted">Company ID: #{{ route.params.id }}</p>
            <div class="row">
                <div class="col d-flex gap-2">
                    <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "company_positions" })'>
                        <i class="bi bi-arrow-left me-2"></i>All Companies
                    </button>
                    <button type="button" class="btn btn-success btn-sm" @click='router.push({ "name": "student_dashboard" })'>
                        <i class="bi bi-graph-up me-2"></i>Dashboard
                    </button>
                </div>
            </div>
        </div>
    </div>
    <hr class="mb-4">
    <div class="row mb-4">
        <div class="col" v-if="!loading">
            <p>{{ company }}</p>
        </div>
        <div v-else>Loading...</div>
    </div>
    <hr class="mb-4">
    <div class="row mb-4">
        <div class="col">
            <h3 class="mb-3">Open Positions</h3>
            <div class="col" v-if="!loading">
                
            </div>
            <div v-else>Loading...</div>
        </div>
    </div>
</template>