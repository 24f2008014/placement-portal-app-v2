<script setup>
import PositionCreateForm from "@/components/PositionCreateForm.vue";
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";

const status = ref(null);
const loading = ref(true);

async function checkStatus() {
    try {
        const response = await api.get("/companies/me");
        status.value = response.data.status;
    } catch (error) {
        console.error(error);
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    checkStatus();
})
</script>

<template>
    <div class="row align-items-center justify-content-center">
        <div class="col-6">
            <div class="row">
                <div class="col-auto">
                    <i class="bi bi-clipboard-plus-fill" style="font-size: 3.5rem"></i>
                </div>
                <div class="col">
                    <h6 class="display-6">New Position</h6>
                    <p class="lead text-muted">List any new openings you're hiring for here.</p>
                </div>
            </div>
            <hr class="mb-4">
        </div>
    </div>

    <div v-if="!loading" class="row justify-content-center">
            <div class="col-6">
                <PositionCreateForm v-if="status=='whitelisted'" />
                <p v-else-if="status=='pending'">Your company's registration status is <code class="text-warning fw-bold">pending</code>. Please wait for an administrator to approve your account before listing new positions.</p>
                <p v-else>Your company has been <code class="text-danger fw-bold">blacklisted</code>, and you can't list new positions right now.</p>
            </div>
    </div>
    <div v-else>Loading...</div>
</template>