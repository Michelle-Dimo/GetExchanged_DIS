let allData = [];

function renderReports(data) {
    const container = document.getElementById("reports-container");

    container.innerHTML = data.map(report => `
        <div class="card-container">
            <a href="/reports/${report.report_id}" class="agreement-card card">
                <h3>${report.institution}</h3>
                <p>${report.study_field}</p>
                <p>Academic year: ${report.academic_year}</p>
            </a>
        </div>
    `).join("");
}

function refillSelect(id, values, selectedValue) {
    const select = document.getElementById(id);

    select.innerHTML = '<option value="">All</option>';

    Array.from(values).sort().forEach(v => {
        const option = document.createElement("option");

        option.value = v;
        option.textContent = v;

        if (v === selectedValue) {
            option.selected = true;
        }

        select.appendChild(option);
    });
}

function updateFilterOptions(filteredData) {
    const studyFields = new Set();
    const institutions = new Set();
    const academicYears = new Set();

    filteredData.forEach(report => {
        if (report.study_field) {
            studyFields.add(report.study_field);
        }

        if (report.institution) {
            institutions.add(report.institution);
        }

        if (report.academic_year) {
            academicYears.add(report.academic_year);
        }
    });

    refillSelect(
        "filter-field",
        studyFields,
        document.getElementById("filter-field").value
    );

    refillSelect(
        "filter-institution",
        institutions,
        document.getElementById("filter-institution").value
    );

    refillSelect(
        "filter-year",
        academicYears,
        document.getElementById("filter-year").value
    );
}

function applyFilters() {
    const studyField = document.getElementById("filter-field").value;
    const institution = document.getElementById("filter-institution").value;
    const academicYear = document.getElementById("filter-year").value;

    let filtered = allData;

    if (studyField) {
        filtered = filtered.filter(
            report => report.study_field === studyField
        );
    }

    if (institution) {
        filtered = filtered.filter(
            report => report.institution === institution
        );
    }

    if (academicYear) {
        filtered = filtered.filter(
            report => String(report.academic_year) === academicYear
        );
    }

    setupFilters(REPORTS_DATA);
}

function setupFilters(data) {
    allData = data;

    updateFilterOptions(allData);

    document.querySelectorAll(".filter-panel select").forEach(el => {
        el.addEventListener("change", applyFilters);
    });

    document.getElementById("reset-filters").addEventListener("click", () => {

        document.querySelectorAll(".filter-panel select").forEach(el => {
            el.value = "";
        });

        updateFilterOptions(allData);
        renderReports(allData);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupFilters(REPORTS_DATA);
    renderReports(allData);
});