<script setup>
import { onMounted, ref, computed, reactive, watch, useId } from "vue";
import { api } from "@/utils/api";
import { useRouter } from "vue-router";
import { flattenResponse, flattenResponsePrefixed } from "@/utils/helpers";
import { formatDate } from "@/utils/helpers";

const props = defineProps(["url", "fields", "item_route_name"]);
const errors = ref({});
const paginatedData = ref();
const pagination = ref({});
const router = useRouter();
const filterDropdownId = useId();

const hasPrevious = computed(() => {
    return pagination.value.prev !== null;
});

const hasNext = computed(() => {
    return pagination.value.next !== null;
});

const getPrevious = (() => {
    if (pagination.value.prev) {
        getPaginatedData(pagination.value.prev.split("/api")[1]);
    }
});

const getNext = (() => {
    if (pagination.value.next) {
        getPaginatedData(pagination.value.next.split("/api")[1]);
    }
});

const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.limit));
const currentPage = computed(() => (pagination.value.offset / pagination.value.limit) + 1);
const startItem = computed(() => pagination.value.offset + 1);

const tableState = reactive({
    sort_by: "id",
    sort_dir: "desc"
});

function clearFilters() {
    Object.keys(filters).forEach(k => filters[k] = "");
    getPaginatedData(props.url, tableState, filters);
}

const filters = reactive({
    id: "",
});

async function getPaginatedData(url, params=null, filters=null) {
    errors.value = {};
    let fetchUrl = url;
    if (params) {
        fetchUrl = `${url}?sort_by=${params.sort_by}&sort_dir=${params.sort_dir}`;
        if (Object.keys(filters).length!=0) {
            fetchUrl += `&filters=${JSON.stringify(filters)}`;
        }
    }
    try {
        const response = await api.get(fetchUrl);
        paginatedData.value = response.data.data;
        pagination.value = response.data.pagination;
    } catch (error) {
        console.error(error);
        if ("errors" in error.response.data) {
            errors.value = flattenResponse(error.response.data.errors.json);
        }
    }
};

watch(tableState, async (newState) => {
    getPaginatedData(props.url, newState, filters);
});

function sort(col) {
    if (col == tableState.sort_by) {
        tableState.sort_dir = tableState.sort_dir == "asc" ? "desc" : "asc";
    } else {
        tableState.sort_by = col;
        tableState.sort_dir = "asc";
    }
}

function sortClasses(col) {
    return {
        "active-sort": tableState.sort_by == col,
        "asc": tableState.sort_by == col && tableState.sort_dir == "asc",
        "desc": tableState.sort_by == col && tableState.sort_dir == "desc"
    };
}

onMounted(() => {
    getPaginatedData(props.url, tableState, filters);
});
</script>

<template>
    <div class="row mb-2 align-items-center">
        <div class="col d-flex gap-3">
            <ul class="pagination pagination-sm">
                <li class="page-item" :class="{ disabled: !hasPrevious }"><a class="page-link" href="#" @click="getPrevious">Prev</a></li>
                <li class="page-item active"><a class="page-link" href="#">{{ currentPage }}</a></li>
                <li class="page-item" :class="{ disabled: !hasNext }"><a class="page-link" href="#" @click="getNext">Next</a></li>
            </ul>
            <button class="btn btn-success btn-sm mb-3" data-bs-toggle="collapse" :data-bs-target="'#' + filterDropdownId"><i class="bi bi-filter me-2"></i>Filter</button>
        </div>

        <div class="col text-end">
            <p>Showing {{ startItem }}&ndash;{{ startItem + pagination.count - 1 }} of {{ pagination.total }}</p>
        </div>        
    </div>

    <div class="row mb-3 collapse" :id="filterDropdownId">
        <div class="col">
            <form class="p-3 border rounded shadow-sm" @submit.prevent="getPaginatedData(props.url, tableState, filters)">
                <div class="row mb-3">
                    <template v-for="f in Object.values(props.fields)">
                        <div class="col" v-if="f.filter==true">
                            <label :for="f.name" class="form-label">{{ f.label }}</label>
                            <template v-if="f.type=='select'">
                                <select class="form-select" :id="f.name" v-model="filters[f.name]">
                                    <option value="" selected>...</option>
                                    <template v-for="o in f.input.options">
                                        <option :value="o.value">{{ o.label }}</option>
                                    </template>
                                </select>
                            </template>
                            <input v-else v-bind="f.input" class="form-control" :id="f.name" v-model="filters[f.name]">
                        </div>
                    </template>
                </div>

                <div class="row">
                    <div class="col d-flex gap-3">
                        <button type="submit" class="btn btn-primary btn-sm"><i class="bi bi-check-lg me-2"></i>Apply</button>
                        <button type="button" class="btn btn-secondary btn-sm" @click="clearFilters"><i class="bi bi-arrow-counterclockwise me-2"></i>Reset</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

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
                 <td v-for="f in Object.values(props.fields)">
                    <template v-if="f.type=='date'">
                        {{ i[f.name] ? formatDate(flattenResponsePrefixed(i)[f.name]) : "N/A" }}
                    </template>
                    <template v-else>
                        {{ flattenResponsePrefixed(i)[f.name] }}
                    </template>
                </td>
            </tr>
        </tbody>
    </table>
</template>