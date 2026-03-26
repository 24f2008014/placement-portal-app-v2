<script setup>
const props = defineProps(["title", "id", "yesLabel"]);
</script>

<template>
    <div class="modal fade" tabindex="-1" :id="props.id">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{ props.title }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <slot name="modal-body"></slot>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary btn-sm" @click="$emit('confirm')">{{ props.yesLabel }}</button>
                </div>
            </div>
        </div>
    </div>
</template>