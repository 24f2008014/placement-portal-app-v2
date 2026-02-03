<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";
import PositionCreateForm from "@/components/PositionCreateForm.vue";
import PaginatedTable from "@/components/PaginatedTable.vue";

const loading = ref(true);
const errors = ref({});
const auth = useAuthStore();
const isApproved = ref();
const positions_open_url = "/companies/me/positions";
const positions_closed_url = "/companies/me/positions";
const positions_fields = {
    "ID": "id",
    "Role": "role",
};
const position_route_name = "position";

async function checkApproval() {
    errors.value = {};
    try {
        const response = await api.get("/companies/me");
        isApproved.value = response.data.approval_status;
    }
    catch (error) {
        console.log(error)
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
    finally {
        loading.value = false;
    }
};



onMounted(() => {
    checkApproval();
})

</script>

<template>
    <div class="row">
        <h6 class="display-6">Company Dashboard</h6>
    </div>
    <hr>
    <template v-if="loading"><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>
    <template v-else>
        <template v-if="!isApproved">
            <div class="row">
                <div class="col-6">
                        <h6 class="display-6">Approval Status: <code class="text-danger">Not Approved</code></h6>
                        <p class="lead">Please wait. Your company account is awaiting admin approval before you can list any new positions you're hiring for. Thank you for your patience.</p>
                    <hr>
                </div>
            </div>
        </template>
        <template v-else>
            <div class="col">
                <h4>Approval Status: <code class="text-success">Approved!</code></h4>
                <p class="lead">Your company has been approved, and you're free to list any new positions you're hiring for.</p>
                <hr>
            </div>
        <div class="row justify-content-center">
            <div class="col">
                <h4 class="mb-3">Open Positions</h4>
                <PaginatedTable :url="positions_open_url" :fields="positions_fields" :item_route_name="position_route_name" />
            </div>
        </div>
        </template>
    </template>
</template>