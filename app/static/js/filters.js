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
    Array.from(values).sort((a, b) => a.localeCompare(b)).forEach(v => {
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
    
    // NEW: Read values from the new quick search panel text box
    const searchText = document.getElementById("filter-search-input").value.toLowerCase().trim();

    let filtered = allData;
    if (study_field) filtered = filtered.filter(u => u.study_fields.has(study_field));
    if (country) filtered = filtered.filter(u => u.countries.has(country));
    if (city) filtered = filtered.filter(u => u.cities.has(city));
    if (institution) filtered = filtered.filter(u => u.institution === institution);

    // NEW: Client-side keyword and typo-tolerant fuzzy validation
    if (searchText) {
        filtered = filtered.filter(u => {
            // A. Check for standard substring matches first (fast and exact)
            if (u.institution.toLowerCase().includes(searchText)) return true;
            for (let c of u.countries) if (c.toLowerCase().includes(searchText)) return true;
            for (let c of u.cities) if (c.toLowerCase().includes(searchText)) return true;
            for (let f of u.study_fields) if (f.toLowerCase().includes(searchText)) return true;

            // B. If no direct match, check fuzzy similarity threshold (catches typos like "aple" -> "apple")
            // 0.25 is our matching threshold (0.0 is completely different, 1.0 is identical)
            if (getSimilarity(u.institution, searchText) > 0.25) return true;
            for (let c of u.countries) if (getSimilarity(c, searchText) > 0.25) return true;
            for (let c of u.cities) if (getSimilarity(c, searchText) > 0.25) return true;
            for (let f of u.study_fields) if (getSimilarity(f, searchText) > 0.25) return true;

            return false;
        });
    }

    updateFilterOptions(filtered);
    renderCallback(filtered);
}

function setupFilters(data, renderCallback) {
    allData = groupByAgreement(data);
    updateFilterOptions(allData);

    document.querySelectorAll(".filter-panel select").forEach(el => {
        el.addEventListener("change", () => applyFilters(renderCallback));
    });

    // NEW: Filter the system live on every keypress inside the input box
    document.getElementById("filter-search-input").addEventListener("input", () => {
        applyFilters(renderCallback);
    });

    document.getElementById("reset-filters").addEventListener("click", () => {
        document.querySelectorAll(".filter-panel select").forEach(el => el.value = "");
        
        // NEW: Clear the text box input on reset
        document.getElementById("filter-search-input").value = "";
        
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


// NEW: Add text matching utility algorithms to the very bottom of the file
// This uses a Sørensen–Dice Coefficient algorithm to perform fast, typo-tolerant checks in JavaScript
function getSimilarity(str1, str2) {
    str1 = str1.toLowerCase().trim();
    str2 = str2.toLowerCase().trim();
    if (!str1 || !str2) return 0;
    if (str1 === str2) return 1;

    const pairs1 = getBigrams(str1);
    const pairs2 = getBigrams(str2);
    let intersection = 0;

    for (const pair of pairs1) {
        if (pairs2.includes(pair)) {
            intersection++;
        }
    }
    return intersection > 0 ? (2.0 * intersection) / (pairs1.length + pairs2.length) : 0;
}

function getBigrams(str) {
    const bigrams = [];
    for (let i = 0; i < str.length - 1; i++) {
        bigrams.push(str.slice(i, i + 2));
    }
    return bigrams;
}