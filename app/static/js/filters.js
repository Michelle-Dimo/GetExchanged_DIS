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

function populateFilters(data) {
    const fields = new Set();
    const countries = new Set();
    const cities = new Set();
    const institutions = new Set();

    data.forEach(u => {
        if (u.field) fields.add(u.field);
        if (u.country) countries.add(u.country);
        if (u.city) cities.add(u.city);
        if (u.institution) institutions.add(u.institution);
    });

    fillSelect("filter-field", fields);
    fillSelect("filter-country", countries);
    fillSelect("filter-city", cities);
    fillSelect("filter-institution", institutions);
}

function fillSelect(id, values) {
    const select = document.getElementById(id);
    Array.from(values).sort().forEach(v => {
        const option = document.createElement("option");
        option.value = v;
        option.textContent = v;
        select.appendChild(option);
    });
}

function applyFilters(renderCallback) {
    const field = document.getElementById("filter-field").value;
    const country = document.getElementById("filter-country").value;
    const city = document.getElementById("filter-city").value;
    const institution = document.getElementById("filter-institution").value;

    let filtered = allData;
    if (field) filtered = filtered.filter(u => u.field === field);
    if (country) filtered = filtered.filter(u => u.country === country);
    if (city) filtered = filtered.filter(u => u.city === city);
    if (institution) filtered = filtered.filter(u => u.institution === institution);

    renderCallback(filtered);
}

function setupFilters(data, renderCallback) {
    allData = data;
    populateFilters(allData);

    document.querySelectorAll(".filter-panel select").forEach(el => {
        el.addEventListener("change", () => applyFilters(renderCallback));
    });

    document.getElementById("reset-filters").addEventListener("click", () => {
        document.querySelectorAll(".filter-panel select").forEach(el => el.value = "");
        renderCallback(allData);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupFilters(AGREEMENTS_DATA, renderAgreements);
    renderAgreements(AGREEMENTS_DATA);
});