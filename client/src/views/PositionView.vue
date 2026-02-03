<script setup>
import { onMounted, ref, computed } from "vue";
import { api } from "@/utils/api";
import { useRouter, useRoute } from "vue-router";
import PaginatedTable from "@/components/PaginatedTable.vue";
import PositionViewForm from "@/components/PositionViewForm.vue";

const router = useRouter();
const route = useRoute();
const errors = ref({});
const applications_url = `/positions/${route.params.id}/applications`;
const applications_fields = {
    "ID": "id",
};
const application_item_route = "";
</script>

<template>
    <div class="row justify-content-center mb-4">
        <div class="col">
            <h3 class="display-6 mb-3">Position #{{ route.params.id }}</h3>
            <button type="button" class="btn btn-primary btn-sm" @click='router.push({ "name": "company_positions" })'>
                <i class="bi bi-arrow-left me-2"></i>All Positions
            </button>
        </div>
    </div>
    <hr class="mb-4">
    <div class="row mb-4">
        <div class="col-6">
            <h3 class="mb-4">Details</h3>
            <PositionViewForm />
        </div>
    </div>
    <hr class="mb-4">
    <div class="row">
        <div class="col">
            <h3 class="mb-4">Applications Received</h3>
            <PaginatedTable :url="applications_url" :fields="applications_fields" :item_route_name="application_item_route"></PaginatedTable>
        </div>
    </div>
</template>