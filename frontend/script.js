// frontend/script.js

const API_URL = "http://localhost:8000";

// --- DOM REFS ---
const form = document.getElementById("campaign-form");
const formTitle = document.getElementById("form-title");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const campaignIdInput = document.getElementById("campaign-id");

const nameInput = document.getElementById("name");
const descriptionInput = document.getElementById("description");
const budgetInput = document.getElementById("budget");
const currencyInput = document.getElementById("currency");
const startDateInput = document.getElementById("start-date");
const endDateInput = document.getElementById("end-date");
const targetAudienceInput = document.getElementById("target-audience");
const statusInput = document.getElementById("status");

const campaignListDiv = document.getElementById("campaign-list");
const statusFilter = document.getElementById("status-filter");
const searchFilter = document.getElementById("search-filter");

const activeBudgetEl = document.getElementById("active-budget");
const totalBudgetEl = document.getElementById("total-budget");

let allCampaigns = [];

// --- API HELPERS ---
async function fetchAPI(endpoint, options = {}) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    if (response.status === 204) return null;
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Something went wrong");
    }
    return response.json();
}

// --- CALCULATION LOGIC ---
function updateDashboardMetrics(campaigns) {
    let activeTotal = 0;
    let absoluteTotal = 0;

    campaigns.forEach(c => {
        const budgetVal = parseFloat(c.budget) || 0;
        absoluteTotal += budgetVal;
        if (c.status === "Active") {
            activeTotal += budgetVal;
        }
    });

    activeBudgetEl.textContent = `$${activeTotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    totalBudgetEl.textContent = `$${absoluteTotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// --- RENDER ---
function renderCampaigns(campaigns, isFilteredView = false) {
    if (!isFilteredView) {
        allCampaigns = campaigns;
        updateDashboardMetrics(campaigns);
    }

    if (!campaigns || campaigns.length === 0) {
        campaignListDiv.innerHTML = `
            <div class="empty-state">
                <span class="emoji">📭</span>
                No strategies match query conditions.
            </div>
        `;
        return;
    }

    let html = "";
    for (const c of campaigns) {
        html += `
            <div class="campaign-item" data-id="${c.id}">
                <div class="campaign-info">
                    <h3>
                        ${c.name}
                        <span class="status-badge status-${c.status}">${c.status}</span>
                    </h3>
                    ${c.description ? `<p class="description">${c.description}</p>` : ""}
                    <div class="meta">
                        <span class="budget">${c.currency} ${Number(c.budget).toFixed(2)}</span>
                        <span>📅 ${formatDate(c.start_date)} ${c.end_date ? `→ ${formatDate(c.end_date)}` : ""}</span>
                        ${c.target_audience ? `<span class="audience">🎯 ${c.target_audience}</span>` : ""}
                    </div>
                </div>
                <div class="campaign-actions">
                    <button class="btn btn-edit" onclick="editCampaign(${c.id})">✏️ Review</button>
                    <button class="btn btn-delete" onclick="deleteCampaign(${c.id})">🗑️ Wipe</button>
                </div>
            </div>
        `;
    }

    campaignListDiv.innerHTML = html;
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

async function loadCampaigns() {
    try {
        const data = await fetchAPI("/campaigns");
        renderCampaigns(data || []);
    } catch (error) {
        campaignListDiv.innerHTML = `
            <div class="empty-state">
                <span class="emoji">❌</span>
                Failed linking backend index grid:<br />${error.message}
            </div>
        `;
    }
}

// --- FILTERS & DEBOUNCE ---
function applyFilters() {
    const status = statusFilter.value;
    const search = searchFilter.value.toLowerCase().trim();

    let filtered = [...allCampaigns];

    if (status) {
        filtered = filtered.filter(c => c.status === status);
    }

    if (search) {
        filtered = filtered.filter(c =>
            c.name.toLowerCase().includes(search) ||
            (c.description && c.description.toLowerCase().includes(search)) ||
            (c.target_audience && c.target_audience.toLowerCase().includes(search))
        );
    }

    renderCampaigns(filtered, true);
}

function debounce(func, delay = 200) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

statusFilter.addEventListener("change", applyFilters);
searchFilter.addEventListener("input", debounce(applyFilters));

// --- MUTATIONS + CHRONOLOGICAL ORDER SAFEGUARD ---
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const startVal = startDateInput.value;
    const endVal = endDateInput.value;

    // Direct UX validation: prevents upside-down system timelines
    if (endVal && new Date(endVal) < new Date(startVal)) {
        alert("❌ Timeline Conflict Error: The Strategy termination date cannot exist before the active deployment date.");
        return;
    }

    const data = {
        name: nameInput.value.trim(),
        description: descriptionInput.value.trim() || null,
        budget: parseFloat(budgetInput.value),
        currency: currencyInput.value,
        start_date: startVal,
        end_date: endVal || null,
        target_audience: targetAudienceInput.value.trim() || null,
        status: statusInput.value
    };

    const isEditing = campaignIdInput.value !== "";
    const id = campaignIdInput.value;

    try {
        if (isEditing) {
            await fetchAPI(`/campaigns/${id}`, {
                method: "PUT",
                body: JSON.stringify(data)
            });
        } else {
            await fetchAPI("/campaigns", {
                method: "POST",
                body: JSON.stringify(data)
            });
        }

        resetForm();
        await loadCampaigns();
    } catch (error) {
        alert(`❌ Strategy Processing Fault: ${error.message}`);
    }
});

// --- ACTIONS ---
async function editCampaign(id) {
    try {
        const c = await fetchAPI(`/campaigns/${id}`);

        campaignIdInput.value = c.id;
        nameInput.value = c.name;
        descriptionInput.value = c.description || "";
        budgetInput.value = c.budget;
        currencyInput.value = c.currency;
        startDateInput.value = c.start_date;
        endDateInput.value = c.end_date || "";
        targetAudienceInput.value = c.target_audience || "";
        statusInput.value = c.status;

        formTitle.textContent = "✏️ Modify System Matrix";
        submitBtn.textContent = "💾 Push System Adjustments";
        cancelBtn.style.display = "inline-block";

        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        alert(`❌ Context Fetch Interruption: ${error.message}`);
    }
}

async function deleteCampaign(id) {
    if (!confirm("Confirm complete tracking annihilation of this system matrix registry?")) return;

    try {
        await fetchAPI(`/campaigns/${id}`, { method: "DELETE" });
        await loadCampaigns();
    } catch (error) {
        alert(`❌ Deletion Fault Error: ${error.message}`);
    }
}

cancelBtn.addEventListener("click", resetForm);

function resetForm() {
    form.reset();
    campaignIdInput.value = "";
    formTitle.textContent = "➕ Create Strategy Matrix";
    submitBtn.textContent = "➕ Deploy Campaign";
    cancelBtn.style.display = "none";

    const today = new Date().toISOString().split("T")[0];
    startDateInput.value = today;
}

// --- INIT ---
const today = new Date().toISOString().split("T")[0];
startDateInput.value = today;
loadCampaigns();