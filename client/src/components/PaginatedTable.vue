<script setup>
import { onMounted, ref, computed, reactive, watch } from "vue";
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

async function getPaginatedData(url, params=null) {
    errors.value = {};
    let fetchUrl = url;
    if (params) {
        let fetchParams = new URLSearchParams(params).toString();
        fetchUrl = `${url}?${fetchParams}`;
    }
    try {
        const response = await api.get(fetchUrl);
        paginatedData.value = response.data.data;
        pagination.value = response.data.pagination;
    }
    catch (error) {
        console.log(error);
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json)
        }
    }
};

const tableState = reactive({
    sort_by: "id",
    sort_dir: "asc"
});

watch(tableState, async (newState, oldState) => {
    getPaginatedData(props.url, newState);
});

function sort(col) {
    if (col == tableState.sort_by) {
        tableState.sort_dir = tableState.sort_dir == "asc" ? "desc" : "asc";
    } else {
        tableState.sort_by = col;
        tableState.sort_dir = "asc";
    }
};

function sortClasses(col) {
    return {
        "active-sort": tableState.sort_by == col,
        "asc": tableState.sort_by == col && tableState.sort_dir == "asc",
        "desc": tableState.sort_by == col && tableState.sort_dir == "desc"
    }
}

onMounted(() => {
    getPaginatedData(props.url, tableState);
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

    <!-- <button class="btn btn-primary btn-sm mb-3" data-bs-toggle="collapse" data-bs-target="#searchCollapse">Filter</button>
    <div class="row mb-3 collapse" id="searchCollapse">
        <div class="col">
            <form class="p-3 border rounded shadow-sm" @submit.prevent="filterData">
                <div class="row mb-3">
                    <template v-for="v in Object.values(props.fields)">
                        <div class="col" v-if="v.filter==true">
                            <label :for="v.name" class="form-label">{{ v.name }}</label>
                            <input :type="v.input_type" class="form-control" :id="v.name" v-model="v.name">
                        </div>
                    </template>
                </div>
                <button class="btn btn-success btn-sm">Submit</button>
            </form>
        </div>
    </div> -->

    <table class="border table table-hover">
        <thead>
            <tr>
                <th scope="col" v-for="k in Object.keys(props.fields)" @click="sort(props.fields[k].name)" :class="sortClasses(props.fields[k].name)">{{ k }}</th>
            </tr>
        </thead>
        <tbody>
            <tr 
                v-for="i in paginatedData"
                :key="i.id"
                @click='router.push({ name: props.item_route_name, params: { "id": `${i.id}`} })'
            >
                 <td v-for="v in Object.values(props.fields)">{{ flattenResponse(i)[v.name] }}</td>
            </tr>
        </tbody>
    </table>
</template>