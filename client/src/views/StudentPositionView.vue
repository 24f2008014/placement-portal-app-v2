<script setup>
import { onMounted, ref, computed } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import PositionViewForm from "@/components/PositionViewForm.vue";

const router = useRouter();
const route = useRoute();
const errors = ref({});
const position = ref({});
const loading = ref(true);

async function getDetails() {
    try {
        const response = await api.get(`/positions/${route.params.id}`);
        position.value = response.data;
        loading.value = false;
    }
    catch (error) {
        console.log(error);
    }
};

onMounted(() => {
    getDetails();
});
</script>

<template>
    <div class="row">
        <div class="col mb-3">
            <h6 class="display-6">View Position</h6>
            <p class="lead text-muted">Position ID: #{{ route.params.id }}</p>
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
    <div class="row mb-4">
        <div class="col" v-if="!loading">
            <PositionViewForm :position="position"/>
        </div>
        <div v-else>Loading...</div>
    </div>
    <hr class="mb-4">
    <div class="row mb-4">
        <div class="col">
            <h3 class="mb-3">About the Company</h3>
            <div class="col" v-if="!loading">
                <p><RouterLink :to='{ "name": "company", "params": { "id": position.company_id } }'>Click here to learn more about {{ position.company.name }}</RouterLink></p>
                <p>{{ position.company.description }}</p>
            </div>
            <div v-else>Loading...</div>
        </div>
    </div>
    <hr class="mb-4">
    <div class="row">
        <div class="col">
            <h3 class="mb-4">Application Status</h3>
        </div>
    </div>
</template>