import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/utils/api";

export const useTaskStore = defineStore("tasks", () => {
    const tasks = ref({});

    function startTask(id) {
        tasks.value[id] = { status: "PENDING", result: null };

        const interval = setInterval(async () => {
            try {
                const response = await api.get(`/result/${id}`);
                tasks.value[id].status = response.data.task_status;

                if (response.data.status == "SUCCESS") {
                    tasks.value[id].result = response.data.result;
                    clearInterval(interval);
                } else if (response.data.status == "FAILURE") {
                    clearInterval(interval);
                    console.error(`Task ${id} failed.`);
                }
            } catch (error) {
                console.error(error);
                clearInterval(interval);
            }
        }, 2000);
    };

    async function exportCsv() {
        try {
            const response = await api.get("/celery_test");
            startTask(response.data.result_id);
        } catch (error) {
            console.error(error);
        }
    };

    return { tasks, exportCsv };
});