<script setup>
import { onMounted, ref, computed } from "vue";
import { api } from "@/utils/api";
import { useRouter } from "vue-router";
import { flattenResponse } from "@/utils/helpers";

const props = defineProps(["url", "fields", "item_route_name"]);
const errors = ref({});
const paginatedData = ref();
const pagination = ref({});
const router = useRouter();

const hasPrevious = computed(() => {
    return pagination.value.prev !== null;
})

const hasNext = computed(() => {
    return pagination.value.next !== null;
}) 

const getPrevious = (() => {
    if (pagination.value.prev) {
        getPaginatedData(pagination.value.prev.split("/api")[1]);
    }
})

const getNext = (() => {
    if (pagination.value.next) {
        getPaginatedData(pagination.value.next.split("/api")[1]);
    }
})

const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.limit));
const currentPage = computed(() => (pagination.value.offset / pagination.value.limit) + 1);
const startItem = computed(() => pagination.value.offset + 1);

async function getPaginatedData(url) {
    errors.value = {};
    try {
        const response = await api.get(url);
        paginatedData.value = response.data.data;
        pagination.value = response.data.pagination;
        console.log(response.data.data);
    }
    catch (error) {
        console.log(error)
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
};

onMounted(() => {
    getPaginatedData(props.url);
})
</script>

<template>
    <div class="row mb-2 align-items-center">
        <div class="col">
            <ul class="pagination">
                <li class="page-item" :class="{ disabled: !hasPrevious }"><a class="page-link" href="#" @click="getPrevious">Previous</a></li>
                <li class="page-item"><a class="page-link active" href="#">{{ currentPage }}</a></li>
                <li class="page-item" :class="{ disabled: !hasNext }"><a class="page-link" href="#" @click="getNext">Next</a></li>
            </ul>
        </div>
        <div class="col text-end">
            <p>Showing {{ startItem }}&ndash;{{ startItem + pagination.count - 1 }} of {{ pagination.total }}</p>
        </div>
    </div>
    <table class="border table table-hover">
        <thead>
            <tr>
                <th scope="col" v-for="k in Object.keys(props.fields)">{{ k }}</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="i in paginatedData" :key="i.id" @click='router.push({ name: props.item_route_name, params: { "id": `${i.id}`} })'>
                 <td v-for="v in Object.values(props.fields)">{{ flattenResponse(i)[v] }}</td>
            </tr>
        </tbody>
    </table>
</template>