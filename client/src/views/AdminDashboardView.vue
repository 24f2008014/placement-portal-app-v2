<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/utils/api";
import PaginatedTable from "@/components/PaginatedTable.vue";
import { useAlertStore } from "@/stores/alert";

const alert = useAlertStore();
const loading = ref(true);
const stats = ref({});

const students_endpoint = "/students";
const students_route = "student"
const students_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Roll No.": {
        name: "roll_number",
        filter: true,
        label: "Roll No.",
        type: "number",
        input: {
            type: "text"
        }
    },
    "Email": {
        name: "user.email",
        filter: true,
        label: "Email",
        input: {
            type: "email"
        }
    },
    "First Name": {
        name: "first_name",
        filter: true,
        label: "First Name",
        input: {
            type: "text"
        }
    },
    "Last Name": {
        name: "last_name",
        filter: true,
        label: "Last Name",
        input: {
            type: "text"
        }
    },
    "CGPA": {
        name: "cgpa",
        filter: true,
        label: "CGPA",
        type: "number",
        input: {
            type: "number",
            min: "0",
            max: "10"
        }
    },
    "Gender": {
        name: "gender",
        filter: true,
        label: "Gender",
        type: "select",
        input: {
            type: "select",
            options: [
                {value: "male", label: "Male"},
                {value: "female", label: "Female"},
                {value: "other", label: "Other"}
            ]
        }
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {value: "whitelisted", label: "Whitelisted"},
                {value: "blacklisted", label: "Blacklisted"}
            ]
        }
    }
};

const companies_endpoint = "/companies";
const companies_route = "company";
const companies_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Name": {
        name: "name",
        filter: true,
        label: "Name",
        input: {
            type: "text"
        }
    },
    "Industry": {
        name: "industry.name",
        filter: true,
        label: "Industry",
        input: {
            type: "text"
        }
    },
    "Location": {
        name: "location",
        filter: true,
        label: "Location",
        input: {
            type: "text"
        }
    },
    "Email": {
        name: "user.email",
        filter: true,
        label: "Email",
        input: {
            type: "email"
        }
    },
    "Open Positions": {
        name: "open_position_count",
        filter: true,
        label: "Open Positions \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {value: "pending", label: "Pending"},
                {value: "whitelisted", label: "Whitelisted"},
                {value: "blacklisted", label: "Blacklisted"}
            ]
        }
    }
};

const positions_endpoint = "/positions";
const positions_route = "position";
const positions_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Role": {
        name: "role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }
    },
    "Company": {
        name: "company.name",
        filter: true,
        label: "Company",
        input: {
            type: "text"
        }
    },
    "Min. Salary": {
        name: "salary_min",
        filter: true,
        label: "Min. Salary \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Max. Salary": {
        name: "salary_max",
        filter: true,
        label: "Max. Salary \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Min. CGPA": {
        name: "min_cgpa",
        type: "number",
        filter: false
    },
    "Deadline": {
        name: "deadline",
        filter: true,
        label: "Deadline \u2265",
        type: "date",
        input: {
            type: "datetime-local"
        }
    },
    "Approved": {
        name: "is_approved",
        filter: true,
        label: "Approved",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "True", value: true},
                {label: "False", value: false}
            ]
        }
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Open", value: "open"},
                {label: "Closed", value: "closed"}
            ]
        }
    }
};

const applications_endpoint = `/applications`;
const applications_route = "application";
const applications_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Student ID": {
        name: "student_id",
        filter: true,
        label: "Student ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Position ID": {
        name: "position_id",
        filter: true,
        label: "Position ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },    
    "Role": {
        name: "position.role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }        
    },
    "Company": {
        name: "position.company.name",
        filter: true,
        label: "Company",
        input: {
            type: "text"
        }
    },
    "Created At": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Updated At": {
        name: "updated_at",
        filter: false,
        type: "date"
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Pending", value: "pending"},
                {label: "Shortlisted", value: "shortlisted"},
                {label: "Selected", value: "selected"},
                {label: "Rejected", value: "rejected"},
                {label: "Withdrawn", value: "withdrawn"}
            ]
        }
    }
};

const placements_endpoint = "/placements";
const placements_route = "placement";
const placements_fields = {
    "ID": {
        name: "id",
        filter: true,
        label: "ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Application ID": {
        name: "application_id",
        filter: true,
        label: "Application ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Student ID": {
        name: "application.student.id",
        filter: true,
        label: "Student ID",
        type: "number",
        input: {
            type: "number",
            min: "1"
        }
    },
    "Role": {
        name: "application.position.role",
        filter: true,
        label: "Role",
        input: {
            type: "text"
        }
    },
    "Company": {
        name: "application.position.company.name",
        filter: true,
        label: "Company",
        input: {
            type: "text"
        }
    },
    "Salary": {
        name: "salary",
        filter: true,
        label: "Salary \u2265",
        type: "number",
        input: {
            type: "number",
            min: "0"
        }
    },
    "Joining Date": {
        name: "joining_date",
        filter: false,
        type: "date"
    },  
    "Created At": {
        name: "created_at",
        filter: false,
        type: "date"
    },
    "Status": {
        name: "status",
        filter: true,
        label: "Status",
        type: "select",
        input: {
            type: "select",
            options: [
                {label: "Pending", value: "pending"},
                {label: "Accepted", value: "accepted"},
                {label: "Rejected", value: "rejected"}
            ]
        }
    }
};

async function getMonthlyReport() {
    try {
        const response = await api.get("/admin/monthly_report");
        alert.addAlert("Email sent.", "success");
        console.log(response.data);
    } catch (error) {
        alert.addAlert(error.response.data.description, "error");
        console.error(error);
    }
}

onMounted(async () => {
    try {
        const response = await api.get("/stats");
        stats.value = response.data;
        loading.value = false;        
    } catch (error) {
        alert.addAlert(error.response.data.description, "error");
        console.error(error)
    }
});
</script>

<template>
    <div class="row align-items-center">
        <div class="col-auto">
            <i class="bi bi-bar-chart-line-fill" style="font-size: 3.5rem"></i>
        </div>
        <div class="col">
            <h6 class="display-6">Admin Dashboard</h6>
            <p class="lead text-muted">See everything at a glance here.</p>
        </div>
    </div>
    <div class="row mb-4">
        <div class="col">
            <button type="button" class="btn btn-sm btn-success" @click="getMonthlyReport"><i class="bi bi-envelope-fill me-2"></i>Get Email Report</button>
        </div>
    </div>
    <hr class="mb-4">


    <template v-if="!loading">
        <div class="row">
            <div class="col">
                <ul v-if="stats.num_companies_pending > 0">
                    <li><strong>Companies pending approval</strong> ({{ stats.num_companies_pending }}):</li>
                    <ul>
                        <li v-for="c in stats.companies_pending.slice(0, 10)">
                            <RouterLink :to="{ name: 'company', params: { id: c.id } }">{{ c.name }} (#{{ c.id }})</RouterLink>
                        </li>
                    </ul>
                </ul>
                <ul v-if="stats.num_positions_pending > 0">
                    <li><strong>Positions pending approval</strong> ({{ stats.num_positions_pending }}):</li>
                    <ul>
                        <li v-for="p in stats.positions_pending.slice(0, 10)">
                            <RouterLink :to="{ name: 'position', params: { id: p.id } }">{{ p.role }} (#{{ p.id }})</RouterLink>
                        </li>
                    </ul>
                </ul>
            </div>
        </div>

        <div class="row">
            <div class="col">
                <ul class="nav nav-tabs" id="myTab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="students-tab" data-bs-toggle="tab" data-bs-target="#students-tab-pane" type="button" role="tab" aria-controls="students-tab-pane" aria-selected="true">Students ({{ stats.num_students }})</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="companies-tab" data-bs-toggle="tab" data-bs-target="#companies-tab-pane" type="button" role="tab" aria-controls="companies-tab-pane" aria-selected="false">Companies ({{ stats.num_companies }})</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="positions-tab" data-bs-toggle="tab" data-bs-target="#positions-tab-pane" type="button" role="tab" aria-controls="positions-tab-pane" aria-selected="false">Positions ({{ stats.num_positions }})</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="applications-tab" data-bs-toggle="tab" data-bs-target="#applications-tab-pane" type="button" role="tab" aria-controls="applications-tab-pane" aria-selected="false">Applications ({{ stats.num_applications }})</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="placements-tab" data-bs-toggle="tab" data-bs-target="#placements-tab-pane" type="button" role="tab" aria-controls="placements-tab-pane" aria-selected="false">Placements ({{ stats.num_placements }})</button>
                    </li>
                </ul>
            </div>

            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="students-tab-pane" role="tabpanel" aria-labelledby="students-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Students</h4>
                            <PaginatedTable :url="students_endpoint" :fields="students_fields" :item_route_name="students_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="companies-tab-pane" role="tabpanel" aria-labelledby="companies-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Companies</h4>
                            <PaginatedTable :url="companies_endpoint" :fields="companies_fields" :item_route_name="companies_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="positions-tab-pane" role="tabpanel" aria-labelledby="positions-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Positions</h4>
                            <PaginatedTable :url="positions_endpoint" :fields="positions_fields" :item_route_name="positions_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="applications-tab-pane" role="tabpanel" aria-labelledby="applications-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Applications</h4>
                            <PaginatedTable :url="applications_endpoint" :fields="applications_fields" :item_route_name="applications_route" />
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="placements-tab-pane" role="tabpanel" aria-labelledby="placements-tab" tabindex="0">
                    <div class="row mt-3">
                        <div class="col">
                            <h4 class="mb-3">Placements</h4>
                            <PaginatedTable :url="placements_endpoint" :fields="placements_fields" :item_route_name="placements_route" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </template>

    <template v-else><div class="spinner-border spinner-border-sm text-center ms-1"></div></template>
</template>