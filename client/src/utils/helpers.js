import { api } from "./api";

const markRequiredFields = () => {
    document.querySelectorAll("input[required], select[required]").forEach((e) => {
        document.querySelector(`label[for=${e.id}]`).classList.add("required");
    });
};

const flattenResponse = (obj) => {
    let result = {};
    for (const key in obj) {
        if (typeof obj[key] === "object" && !Array.isArray(obj[key])) {
            Object.assign(result, flattenResponse(obj[key]));
        } 
        else { 
            result[key] = obj[key];
        }
    }
    return result;
}

function flattenResponsePrefixed(obj, prefix="") {
    let result = {};
    for (const key in obj) {
        const newKey = prefix ? `${prefix}.${key}` : key; // Prefix + dot + current key
        if (typeof obj[key] === "object" && !Array.isArray(obj[key])) {
            Object.assign(result, flattenResponsePrefixed(obj[key], newKey));
        } else { 
            result[newKey] = obj[key];
        }
    }
    return result;
}

const dateOptions = { 
    year: "numeric",
    month: "long",
    day: "numeric",
    hour12: true,
    hour: "numeric",
    minute: "2-digit"
};
const formatDate = ((d) => new Intl.DateTimeFormat("en-GB", dateOptions).format(new Date(d)));

const dateNoTimeOptions = { 
    year: "numeric",
    month: "long",
    day: "numeric"
};
const formatDateNoTime = ((d) => new Intl.DateTimeFormat("en-GB", dateNoTimeOptions).format(new Date(d)));

async function viewResume(url) {
    try {
        const response = await api.get(`/uploads/resumes/${url}`, {responseType: "blob"});
        const blob = new Blob([response.data], {type: "application/pdf"})
        const objectURL = URL.createObjectURL(blob);
        window.open(objectURL, "_blank");
    }
    catch (error) {
        console.log(error);
    }
};

export { markRequiredFields, flattenResponse, flattenResponsePrefixed, formatDate, formatDateNoTime, viewResume };