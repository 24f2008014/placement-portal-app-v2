<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue";
import { api } from "@/utils/api";

const errors = ref({});
const auth = useAuthStore();
const isApproved = ref();

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
        <div class="col-6">
            
        </div>
    </div>
    </template>
</template>