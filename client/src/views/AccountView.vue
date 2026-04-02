<script setup>
import AccountEditForm from "@/components/AccountEditForm.vue";
</script>

<template>
    <div class="row align-items-center justify-content-center">
        <div class="col-6">
            <div class="row">
                <div class="col-auto">
                    <i class="bi bi-gear-wide-connected" style="font-size: 3.5rem"></i>
                </div>
                <div class="col">
                    <h6 class="display-6">Your Account</h6>
                    <p class="lead text-muted">You can update your email and password here.</p>
                </div>
            </div>
            <hr class="mb-4">
        </div>
    </div>

    <div class="row justify-content-center">
        <div class="col-6">
            <AccountEditForm />
        </div>
    </div>
</template>