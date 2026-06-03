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
    const container = document.getElementById(id + "-container");
    if (!container) return;

    const ul = container.querySelector(".dropdown-options");
    const trigger = container.querySelector(".dropdown-trigger");
    const hiddenInput = document.getElementById(id);
    const searchInput = container.querySelector(".dropdown-search");
    const currentSearch = searchInput ? searchInput.value.toLowerCase().trim() : "";

    ul.innerHTML = "";
    
    const liAll = document.createElement("li");
    liAll.textContent = "All";
    liAll.dataset.value = "";
    if (!selectedValue) {
        liAll.classList.add("selected");
        trigger.textContent = "All";
        hiddenInput.value = "";
    }
    ul.appendChild(liAll);

    Array.from(values).sort((a, b) => a.localeCompare(b)).forEach(v => {
        const li = document.createElement("li");
        li.textContent = v;
        li.dataset.value = v;
        
        if (v === selectedValue) {
            li.classList.add("selected");
            trigger.textContent = v;
            hiddenInput.value = v;
        }

        if (currentSearch) {
            const exactMatch = v.toLowerCase().includes(currentSearch);
            const fuzzyMatch = getSimilarity(v, currentSearch) > 0.25;
            if (!exactMatch && !fuzzyMatch) {
                li.style.display = "none";
            }
        }

        ul.appendChild(li);
    });
}

function updateFilterOptions() {
    // Read current selection values from hidden inputs
    const study_field = document.getElementById("filter-field").value;
    const country = document.getElementById("filter-country").value;
    const city = document.getElementById("filter-city").value;
    const institution = document.getElementById("filter-institution").value;

    const study_fields = new Set();
    const countries = new Set();
    const cities = new Set();
    const institutions = new Set();

    // Cross-filtering evaluation loop over all database agreements
    allData.forEach(u => {
        // 1. Available Study Fields (affected by country, city, institution)
        const matchForField = 
            (!country || u.countries.has(country)) &&
            (!city || u.cities.has(city)) &&
            (!institution || u.institution === institution);
        if (matchForField) {
            u.study_fields.forEach(v => study_fields.add(v));
        }

        // 2. Available Countries (affected by study_field, city, institution)
        const matchForCountry = 
            (!study_field || u.study_fields.has(study_field)) &&
            (!city || u.cities.has(city)) &&
            (!institution || u.institution === institution);
        if (matchForCountry) {
            u.countries.forEach(v => countries.add(v));
        }

        // 3. Available Cities (affected by study_field, country, institution)
        const matchForCity = 
            (!study_field || u.study_fields.has(study_field)) &&
            (!country || u.countries.has(country)) &&
            (!institution || u.institution === institution);
        if (matchForCity) {
            u.cities.forEach(v => cities.add(v));
        }

        // 4. Available Institutions (affected by study_field, country, city)
        const matchForInstitution = 
            (!study_field || u.study_fields.has(study_field)) &&
            (!country || u.countries.has(country)) &&
            (!city || u.cities.has(city));
        if (matchForInstitution && u.institution) {
            institutions.add(u.institution);
        }
    });

    // Populate each dropdown option list independently
    refillSelect("filter-field", study_fields, study_field);
    refillSelect("filter-country", countries, country);
    refillSelect("filter-city", cities, city);
    refillSelect("filter-institution", institutions, institution);
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

    updateFilterOptions();
    renderCallback(filtered);
}

function setupFilters(data, renderCallback) {
    allData = groupByAgreement(data);
    updateFilterOptions();

    document.querySelectorAll(".custom-dropdown").forEach(dropdown => {
        const trigger = dropdown.querySelector(".dropdown-trigger");
        const content = dropdown.querySelector(".dropdown-content");
        const searchInput = dropdown.querySelector(".dropdown-search");
        const ul = dropdown.querySelector(".dropdown-options");
        const hiddenInput = dropdown.querySelector("input[type='hidden']");

        function selectOption(li) {
            hiddenInput.value = li.dataset.value;
            trigger.textContent = li.textContent;

            ul.querySelectorAll("li").forEach(l => l.classList.remove("selected", "highlighted"));
            li.classList.add("selected");

            searchInput.value = "";
            ul.querySelectorAll("li").forEach(l => l.style.display = "block");
            content.style.display = "none";

            applyFilters(renderCallback);
        }

        trigger.addEventListener("click", (e) => {
            e.stopPropagation();
            document.querySelectorAll(".dropdown-content").forEach(c => {
                if (c !== content) c.style.display = "none";
            });
            const isHidden = content.style.display === "none" || content.style.display === "";
            content.style.display = isHidden ? "block" : "none";
            
            if (isHidden) {
                searchInput.focus();
                ul.querySelectorAll("li").forEach(l => l.classList.remove("highlighted"));
                const initialActive = ul.querySelector("li.selected") || ul.querySelector("li");
                if (initialActive) initialActive.classList.add("highlighted");
            }
        });

        searchInput.addEventListener("input", () => {
            const term = searchInput.value.toLowerCase().trim();
            let firstVisibleFound = null;

            ul.querySelectorAll("li").forEach(li => {
                const text = li.textContent.toLowerCase();
                li.classList.remove("highlighted");

                if (text === "all" || !term) {
                    li.style.display = "block";
                } else {
                    const exactMatch = text.includes(term);
                    const fuzzyMatch = getSimilarity(text, term) > 0.25;
                    if (exactMatch || fuzzyMatch) {
                        li.style.display = "block";
                    } else {
                        li.style.display = "none";
                    }
                }

                if (li.style.display !== "none" && !firstVisibleFound) {
                    firstVisibleFound = li;
                }
            });

            if (firstVisibleFound) {
                firstVisibleFound.classList.add("highlighted");
                firstVisibleFound.scrollIntoView({ block: "nearest" });
            }
        });

        searchInput.addEventListener("keydown", (e) => {
            const visibleLis = Array.from(ul.querySelectorAll("li")).filter(li => li.style.display !== "none");
            if (visibleLis.length === 0) return;

            const currentHighlighted = ul.querySelector("li.highlighted");
            let currentIndex = visibleLis.indexOf(currentHighlighted);

            if (e.key === "ArrowDown") {
                e.preventDefault();
                if (currentHighlighted) currentHighlighted.classList.remove("highlighted");

                currentIndex = (currentIndex + 1) % visibleLis.length;
                const nextLi = visibleLis[currentIndex];
                nextLi.classList.add("highlighted");
                nextLi.scrollIntoView({ block: "nearest" });

            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                if (currentHighlighted) currentHighlighted.classList.remove("highlighted");

                currentIndex = (currentIndex - 1 + visibleLis.length) % visibleLis.length;
                const prevLi = visibleLis[currentIndex];
                prevLi.classList.add("highlighted");
                prevLi.scrollIntoView({ block: "nearest" });

            } else if (e.key === "Enter") {
                e.preventDefault();
                if (currentHighlighted) {
                    selectOption(currentHighlighted);
                }
            }
        });

        ul.addEventListener("click", (e) => {
            if (e.target.tagName === "LI") {
                selectOption(e.target);
            }
        });
    });

    document.addEventListener("click", () => {
        document.querySelectorAll(".dropdown-content").forEach(c => c.style.display = "none");
    });

    document.getElementById("reset-filters").addEventListener("click", () => {
        document.querySelectorAll(".custom-dropdown").forEach(dropdown => {
            dropdown.querySelector("input[type='hidden']").value = "";
            dropdown.querySelector(".dropdown-trigger").textContent = "All";
            if (dropdown.querySelector(".dropdown-search")) dropdown.querySelector(".dropdown-search").value = "";
        });
        updateFilterOptions();
        renderCallback(allData);
    });
}

function syncTriggerTextFromHidden(id) {
    const val = document.getElementById(id).value;
    const container = document.getElementById(id + "-container");
    if (container) {
        container.querySelector(".dropdown-trigger").textContent = val ? val : "All";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);

    setupFilters(AGREEMENTS_DATA, renderAgreements);

    if (params.get("institution")) document.getElementById("filter-institution").value = params.get("institution");
    if (params.get("field"))       document.getElementById("filter-field").value       = params.get("field");
    if (params.get("country"))     document.getElementById("filter-country").value     = params.get("country");
    if (params.get("city"))        document.getElementById("filter-city").value        = params.get("city");

    syncTriggerTextFromHidden("filter-field");
    syncTriggerTextFromHidden("filter-country");
    syncTriggerTextFromHidden("filter-city");
    syncTriggerTextFromHidden("filter-institution");

    applyFilters(renderAgreements);
});

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