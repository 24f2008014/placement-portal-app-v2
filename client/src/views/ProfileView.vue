<script setup>
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/utils/api";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const error = ref(null);
const loading = ref(false);
const profile = ref(null);

async function getProfile() {
    loading.value = true;
    try {
        const response = await api.get("/user");
        profile.value = response.data;
    }
    catch (error) {
        console.log(error);
    }
    finally {
        loading.value = false;
    }
}

onMounted(() => getProfile());
</script>

<template>
    <p>Hi!</p>
    <p>{{ profile }}</p>
</template>