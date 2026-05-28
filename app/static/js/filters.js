let allData = [];

function populateFilters(data) {
    const fields = new Set();
    const countries = new Set();
    const cities = new Set();
    const institutions = new Set();

    data.forEach(u => {
        if (u["Study field"]) fields.add(u["Study field"]);
        if (u.Country) countries.add(u.Country);
        if (u.City) cities.add(u.City);
        if (u.Institution) institutions.add(u.Institution);
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

    if (field) filtered = filtered.filter(u => u["Study field"] === field);
    if (country) filtered = filtered.filter(u => u.Country === country);
    if (city) filtered = filtered.filter(u => u.City === city);
    if (institution) filtered = filtered.filter(u => u.Institution === institution);

    renderCallback(filtered);
}

function setupFilters(data, renderCallback) {
    allData = data;

    populateFilters(allData);

    document.querySelectorAll(".filter-panel select").forEach(el => {
        el.addEventListener("change", () => {
            applyFilters(renderCallback);
        });
    });

    document.getElementById("reset-filters").addEventListener("click", () => {

        document.querySelectorAll(".filter-panel select").forEach(el => {
            el.value = "";
        });

        renderCallback(allData);
    });
}

