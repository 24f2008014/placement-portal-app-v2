import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/utils/api";
import { useAlertStore } from "./alert";

export const useTaskStore = defineStore("tasks", () => {
    const tasks = ref({});
    const alert = useAlertStore();

    function startTask(id, download, filename) {
        tasks.value[id] = { status: "PENDING", result: null };

        // Poll every 2s
        const interval = setInterval(async () => {
            try {
                // Fetch task status from server
                const response = await api.get(`/result/${id}`);
                tasks.value[id].status = response.data.task_status;

                if (response.data.status == "SUCCESS") {
                    // Stop polling if task is done
                    tasks.value[id].result = response.data.result;
                    clearInterval(interval);
                    alert.addAlert(`Task ${id} completed.`, "success");

                    if (download) {
                        downloadFile(tasks.value[id].result, filename);
                    }
                } else if (response.data.status == "FAILURE") {
                    clearInterval(interval);
                    console.error(`Task ${id} failed.`);
                    alert.addAlert(`Task ${id} failed.`, "error");
                }
            } catch (error) {
                console.error(error);
                clearInterval(interval);
            }
        }, 2000);
    }

    // Download a file in a new tab
    async function downloadFile(id, filename) {
        try {
            const response = await api.get(`/temp/${id}`, {responseType: "blob"});
            const blob = new Blob([response.data], {type: "text/csv;charset=utf-8;" });
            const objectURL = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = objectURL;
            link.download = filename;
            link.click();

            URL.revokeObjectURL(link.href);
        } catch (error) {
            console.error(error);
        }
    }

    async function exportCsv() {
        try {
            const response = await api.get("/student/me/applications/export");
            startTask(response.data.result_id, true, "my_applications.csv");
        } catch (error) {
            console.error(error);
        }
    }

    return { tasks, exportCsv };
});