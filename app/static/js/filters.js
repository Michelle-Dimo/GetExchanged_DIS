let allData = [];

function renderAgreements(data) {
    const container = document.getElementById("agreements-container");
    container.innerHTML = data.map(agreement => `
        <div class="card-container">
            <a href="/agreements/${agreement.id}" class="agreement-card card">
                <h3>${agreement.institution}</h3>
                <p>ID: ${agreement.id}</p>
            </a>
        </div>
    `).join("");
}

function groupByAgreement(data) {
    const grouped = new Map();
    data.forEach(u => {
        if (!grouped.has(u.id)) {
            grouped.set(u.id, {
                id: u.id,
                institution: u.institution,
                study_fields: new Set(),
                cities: new Set(),
                countries: new Set(),
            });
        }
        const entry = grouped.get(u.id);
        if (u.study_field) entry.study_fields.add(u.study_field);
        if (u.city) entry.cities.add(u.city);
        if (u.country) entry.countries.add(u.country);
    });
    return [...grouped.values()];
}

function refillSelect(id, values, selectedValue) {
    const select = document.getElementById(id);
    select.innerHTML = '<option value="">All</option>';
    Array.from(values).sort().forEach(v => {
        const option = document.createElement("option");
        option.value = v;
        option.textContent = v;
        if (v === selectedValue) option.selected = true;
        select.appendChild(option);
    });
}

function updateFilterOptions(filteredData) {
    const study_fields = new Set();
    const countries = new Set();
    const cities = new Set();
    const institutions = new Set();

    filteredData.forEach(u => {
        u.study_fields.forEach(v => study_fields.add(v));
        u.countries.forEach(v => countries.add(v));
        u.cities.forEach(v => cities.add(v));
        if (u.institution) institutions.add(u.institution);
    });

    refillSelect("filter-field", study_fields, document.getElementById("filter-field").value);
    refillSelect("filter-country", countries, document.getElementById("filter-country").value);
    refillSelect("filter-city", cities, document.getElementById("filter-city").value);
    refillSelect("filter-institution", institutions, document.getElementById("filter-institution").value);
}

function applyFilters(renderCallback) {
    const study_field = document.getElementById("filter-field").value;
    const country = document.getElementById("filter-country").value;
    const city = document.getElementById("filter-city").value;
    const institution = document.getElementById("filter-institution").value;

    let filtered = allData;
    if (study_field) filtered = filtered.filter(u => u.study_fields.has(study_field));
    if (country) filtered = filtered.filter(u => u.countries.has(country));
    if (city) filtered = filtered.filter(u => u.cities.has(city));
    if (institution) filtered = filtered.filter(u => u.institution === institution);

    updateFilterOptions(filtered);
    renderCallback(filtered);
}

function setupFilters(data, renderCallback) {
    allData = groupByAgreement(data);
    updateFilterOptions(allData);

    document.querySelectorAll(".filter-panel select").forEach(el => {
        el.addEventListener("change", () => applyFilters(renderCallback));
    });

    document.getElementById("reset-filters").addEventListener("click", () => {
        document.querySelectorAll(".filter-panel select").forEach(el => el.value = "");
        updateFilterOptions(allData);
        renderCallback(allData);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);

    setupFilters(AGREEMENTS_DATA, renderAgreements);

    if (params.get("institution")) document.getElementById("filter-institution").value = params.get("institution");
    if (params.get("field"))       document.getElementById("filter-field").value       = params.get("field");
    if (params.get("country"))     document.getElementById("filter-country").value     = params.get("country");
    if (params.get("city"))        document.getElementById("filter-city").value        = params.get("city");

    applyFilters(renderAgreements);
});