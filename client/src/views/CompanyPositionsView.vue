<script setup>
import { ref } from "vue";
import PositionCreateForm from "@/components/PositionCreateForm.vue";
import PaginatedTable from "@/components/PaginatedTable.vue";
const positions_url = "/companies/me/positions";
const positions_fields = {
    "ID": {name: "id", filter: true, sort: true},
    "Role": {name: "role", filter: false}
};
const position_route_name = "position";
</script>

<template>
    <div class="row">
        <h6 class="display-6">Positions</h6>
    </div>
    <hr>
    <div class="row justify-content-center">
        <div class="col-6">
            <PaginatedTable :url="positions_url" :fields="positions_fields" :item_route_name="position_route_name" />
        </div>
    </div>
    <div class="row justify-content-center">
        <div class="col-6">
            <PositionCreateForm />
        </div>
    </div>
</template>