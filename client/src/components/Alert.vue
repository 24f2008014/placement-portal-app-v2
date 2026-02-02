<script setup>
import { useAlertStore } from "@/stores/alert";
const alerts = useAlertStore();
</script>

<template>
    <div class="toast-container p-3 start-50 translate-middle-x top-0 position-fixed">
        <div class="toast align-items-center p-2 show" role="alert" v-for="alert in alerts.alerts" :key="alert.id" @click="alerts.removeAlert(alert.id)">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center">
                    <div class="me-3">
                        <i class="bi bi-exclamation-square-fill text-warning" v-if="alert.category == 'warning'"></i>
                        <i class="bi text-danger bi-x-square-fill" v-else-if="alert.category == 'error'"></i>
                        <i class="bi bi-info-square-fill text-primary" v-else></i>
                    </div>
                    <div>{{ alert.message }}</div>
                </div>
            </div>
        </div>
    </div>
</template>