<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRoute, useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const error = ref(null);
const loading = ref(false);
const email = ref(null)
const password = ref(null);

async function sendLoginForm() {
    loading.value = true;
    try {
        auth.login(email.value, password.value);
        const next = route.query.next || "/";
        router.push(next);
    }
    catch (error) {
        alert("oops.");
    }
    finally {
        loading.value = false;
    }
}

</script>

<template>
    <h2>Login</h2>
    <form @submit.prevent="sendLoginForm">
        <label for="email">Email </label>
        <input type="email" id="email" v-model="email" required>
        <br>
        <label for="password">Password </label>
        <input type="password" id="password" v-model="password" required>
        <br>
        <button type="submit">Submit</button>
    </form>
</template>