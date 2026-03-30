import { defineStore } from "pinia";
import { ref } from "vue";

export const useAlertStore = defineStore("alert", () => {
    const alerts = ref([]);
    let nextId = 1;

    function addAlert(message, category) {
        const id = nextId;
        alerts.value.push({
            id: nextId++,
            message: message,
            category: category
        });
        setTimeout(() => { removeAlert(id); }, 5000);
    };

    function removeAlert(id) {
        const index = alerts.value.findIndex((alert) => alert.id === id);
        if (index !== -1) {
            alerts.value.splice(index, 1);
        }
    };

    return { alerts, nextId, addAlert, removeAlert };
});
