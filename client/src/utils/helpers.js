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
            result[key] = obj[key] ;
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

export { markRequiredFields, flattenResponse, formatDate };