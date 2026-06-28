const API_URL =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://localhost:8000"
        : window.location.origin.replace(/\/$/, "");

const form             = document.getElementById("campaign-form");
const formTitle        = document.getElementById("form-title");
const submitBtn        = document.getElementById("submit-btn");
const cancelBtn        = document.getElementById("cancel-btn");
const campaignIdInput  = document.getElementById("campaign-id");

const nameInput        = document.getElementById("name");
const ownerInput       = document.getElementById("owner");
const descriptionInput = document.getElementById("description");
const budgetInput      = document.getElementById("budget");
const spentInput       = document.getElementById("spent");
const currencyInput    = document.getElementById("currency");
const startDateInput   = document.getElementById("start-date");
const endDateInput     = document.getElementById("end-date");
const targetAudienceInput = document.getElementById("target-audience");
const statusInput      = document.getElementById("status");
const tagsInput        = document.getElementById("tags");
const assetsInput      = document.getElementById("assets");
const notesInput       = document.getElementById("notes");

const campaignListDiv  = document.getElementById("campaign-list");
const statusFilter     = document.getElementById("status-filter");
const searchFilter     = document.getElementById("search-filter");

const activeBudgetEl   = document.getElementById("active-budget");
const totalBudgetEl    = document.getElementById("total-budget");
const totalSpentEl     = document.getElementById("total-spent");
const expiredWarning   = document.getElementById("expired-warning");
const expiredText      = document.getElementById("expired-text");

const toastEl = document.getElementById("toast");
let toastTimer;
let allCampaigns = [];

async function fetchAPI(endpoint, options = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    });
    if (res.status === 204) return null;
    if (!res.ok) {
        let msg = "Request failed";
        try {
            const err = await res.json();
            if (err.detail) msg = err.detail;
            else if (err.errors && Array.isArray(err.errors)) {
                msg = err.errors.map(e => e.msg).join(", ");
            }
        } catch (_) {}
        throw new Error(msg);
    }
    return res.json();
}

function showToast(msg, isError = false) {
    clearTimeout(toastTimer);
    toastEl.textContent = msg;
    toastEl.className = "toast show" + (isError ? " toast-error" : "");
    toastTimer = setTimeout(() => { toastEl.className = "toast"; }, 3000);
}

async function loadStats() {
    try {
        const stats = await fetchAPI("/campaigns/stats");

        activeBudgetEl.textContent = formatUSD(stats.active_budget_usd);
        totalBudgetEl.textContent  = formatUSD(stats.total_budget_usd);
        totalSpentEl.textContent   = formatUSD(stats.total_spent_usd);

        ["Draft", "Active", "Paused", "Completed"].forEach(s => {
            const el = document.getElementById(`count-${s}`);
            if (el) el.textContent = stats.counts_by_status[s] ?? 0;
        });

        if (stats.expired_count > 0) {
            expiredWarning.style.display = "flex";
            expiredText.textContent = `${stats.expired_count} campaign${stats.expired_count > 1 ? "s" : ""} may have expired`;
        } else {
            expiredWarning.style.display = "none";
        }
    } catch (_) {}
}

// ---------- AI: BRIEF GENERATOR ----------
async function generateBrief() {
    const name = nameInput.value.trim();
    if (!name) {
        showToast("Enter a campaign name first.", true);
        return;
    }

    const btn = document.getElementById("btn-generate-brief");
    const statusEl = document.getElementById("ai-brief-status");

    btn.disabled = true;
    btn.textContent = "Generating...";
    statusEl.style.display = "block";
    statusEl.className = "ai-brief-status ai-brief-loading";
    statusEl.textContent = "AI is writing your brief…";

    try {
        const result = await fetchAPI("/ai/brief", {
            method: "POST",
            body: JSON.stringify({
                name,
                target_audience: targetAudienceInput.value.trim() || null,
                budget: budgetInput.value ? parseFloat(budgetInput.value) : null,
                currency: currencyInput.value,
            }),
        });

        if (result.description) descriptionInput.value = result.description;
        if (result.tags && result.tags.length) tagsInput.value = result.tags.join(", ");
        if (result.notes) notesInput.value = result.notes;

        statusEl.className = "ai-brief-status ai-brief-success";
        statusEl.textContent = "✓ Brief generated — review and adjust as needed.";
        setTimeout(() => { statusEl.style.display = "none"; }, 4000);
    } catch (err) {
        statusEl.className = "ai-brief-status ai-brief-error";
        statusEl.textContent = `⚠ ${err.message}. Is Ollama running?`;
    } finally {
        btn.disabled = false;
        btn.textContent = "Generate";
    }
}

// ---------- AI: INSIGHTS ----------
async function runInsights() {
    const btn = document.getElementById("btn-ai-insights");
    const body = document.getElementById("ai-insights-body");

    if (!allCampaigns.length) {
        showToast("No campaigns to analyze.", true);
        return;
    }

    btn.disabled = true;
    btn.textContent = "Analyzing...";
    body.innerHTML = `<span class="ai-insights-loading">Analyzing your portfolio…</span>`;

    try {
        const result = await fetchAPI("/ai/insights", {
            method: "POST",
            body: JSON.stringify({ campaigns: allCampaigns }),
        });

        body.innerHTML = `<p class="ai-insights-text">${escapeHtml(result.insights)}</p>`;
    } catch (err) {
        body.innerHTML = `<span class="ai-brief-error">⚠ ${escapeHtml(err.message)}. Is Ollama running?</span>`;
    } finally {
        btn.disabled = false;
        btn.textContent = "Analyze campaigns";
    }
}

// ---------- RENDER ----------
function renderCampaigns(campaigns, filtered = false) {
    if (!filtered) allCampaigns = campaigns;

    if (!campaigns.length) {
        campaignListDiv.innerHTML = `
            <div class="empty-state">
                <span class="empty-state-icon">📭</span>
                ${filtered ? "No campaigns match your filters." : "No campaigns yet. Create one to get started."}
            </div>`;
        return;
    }

    campaignListDiv.innerHTML = campaigns.map(c => {
        const currencySymbol = { USD: "$", EUR: "€", GBP: "£" }[c.currency] || c.currency;
        const isNonUSD = c.currency !== "USD";
        const usdNote = isNonUSD
            ? `<span class="meta-usd-note">(≈ ${formatUSD(c.budget_usd)} USD)</span>`
            : "";
        const expiredTag = c.is_expired && c.status !== "Completed"
            ? `<span class="expired-tag">Expired</span>`
            : "";
        const dateRange = c.start_date
            ? `${formatDate(c.start_date)}${c.end_date ? ` → ${formatDate(c.end_date)}` : ""}`
            : "";
        const notesHtml = c.notes
            ? `<div class="card-notes">${escapeHtml(c.notes)}</div>`
            : "";
        const descHtml = c.description
            ? `<p class="card-description">${escapeHtml(c.description)}</p>`
            : "";
        const audienceHtml = c.target_audience
            ? `<span>🎯 ${escapeHtml(c.target_audience)}</span>`
            : "";
        const ownerHtml = c.owner
            ? `<span>👤 ${escapeHtml(c.owner)}</span>`
            : "";
        const tagsHtml = c.tags && c.tags.length
            ? `<div class="card-tags">${c.tags.map(t => `<span class="tag-pill">${escapeHtml(t)}</span>`).join("")}</div>`
            : "";
        const assetsHtml = c.assets
            ? `<div class="card-assets">${escapeHtml(c.assets)}</div>`
            : "";

        const spent = Number(c.spent || 0);
        const remaining = Number(c.remaining || 0);
        const progress = Number(c.progress_pct || 0);

        const budgetLine = `${currencySymbol}${Number(c.budget).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        const spentLine = `${currencySymbol}${spent.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        const remainingLine = `${currencySymbol}${remaining.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

        return `
            <div class="campaign-card status-${c.status}" data-id="${c.id}">
                <div class="card-top">
                    <span class="card-name">${escapeHtml(c.name)}${expiredTag}</span>
                    <span class="status-badge badge-${c.status}">${c.status}</span>
                </div>
                ${descHtml}
                <div class="card-meta">
                    <span class="meta-budget">Budget: ${budgetLine}</span>
                    <span class="meta-spent">Spent: ${spentLine}</span>
                    <span class="meta-remaining">Remaining: ${remainingLine}</span>
                    ${usdNote}
                    ${dateRange ? `<span>📅 ${dateRange}</span>` : ""}
                    ${audienceHtml}
                    ${ownerHtml}
                </div>
                <div class="progress-row">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:${progress}%"></div>
                    </div>
                    <span class="progress-label">${progress.toFixed(1)}%</span>
                </div>
                ${tagsHtml}
                ${assetsHtml}
                ${notesHtml}
                <div class="card-actions">
                    <button class="btn-action btn-edit"  onclick="editCampaign(${c.id})">Edit</button>
                    <button class="btn-action btn-clone" onclick="cloneCampaign(${c.id})">Duplicate</button>
                    <button class="btn-action btn-delete" onclick="deleteCampaign(${c.id})">Delete</button>
                </div>
            </div>`;
    }).join("");
}

async function loadCampaigns() {
    try {
        const data = await fetchAPI("/campaigns");
        renderCampaigns(data || []);
        applyFilters();
    } catch (err) {
        campaignListDiv.innerHTML = `
            <div class="empty-state">
                <span class="empty-state-icon">⚠️</span>
                Couldn't reach the backend.<br><small>${escapeHtml(err.message)}</small>
            </div>`;
    }
}

async function refreshAll() {
    await Promise.all([loadCampaigns(), loadStats()]);
}

function applyFilters() {
    const status = statusFilter.value;
    const search = searchFilter.value.toLowerCase().trim();

    let result = [...allCampaigns];
    if (status) result = result.filter(c => c.status === status);
    if (search) result = result.filter(c =>
        c.name.toLowerCase().includes(search) ||
        (c.description && c.description.toLowerCase().includes(search)) ||
        (c.target_audience && c.target_audience.toLowerCase().includes(search)) ||
        (c.notes && c.notes.toLowerCase().includes(search)) ||
        (c.owner && c.owner.toLowerCase().includes(search)) ||
        (c.tags && c.tags.join(" ").toLowerCase().includes(search))
    );

    renderCampaigns(result, true);
}

function debounce(fn, ms = 200) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

statusFilter.addEventListener("change", applyFilters);
searchFilter.addEventListener("input", debounce(applyFilters));

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const startVal = startDateInput.value;
    const endVal   = endDateInput.value;

    if (endVal && new Date(endVal) < new Date(startVal)) {
        showToast("End date cannot be before start date.", true);
        return;
    }

    const tags = tagsInput.value
        ? tagsInput.value.split(",").map(t => t.trim()).filter(Boolean)
        : [];

    const payload = {
        name:            nameInput.value.trim(),
        owner:           ownerInput.value.trim() || null,
        description:     descriptionInput.value.trim() || null,
        budget:          parseFloat(budgetInput.value),
        spent:           spentInput.value ? parseFloat(spentInput.value) : 0,
        currency:        currencyInput.value,
        start_date:      startVal,
        end_date:        endVal || null,
        target_audience: targetAudienceInput.value.trim() || null,
        status:          statusInput.value,
        tags:            tags.length ? tags : null,
        assets:          assetsInput.value.trim() || null,
        notes:           notesInput.value.trim() || null,
    };

    const isEditing = campaignIdInput.value !== "";
    const id        = campaignIdInput.value;

    submitBtn.disabled = true;
    submitBtn.textContent = isEditing ? "Saving..." : "Creating...";

    try {
        if (isEditing) {
            await fetchAPI(`/campaigns/${id}`, { method: "PUT", body: JSON.stringify(payload) });
            showToast("Campaign updated.");
        } else {
            await fetchAPI("/campaigns", { method: "POST", body: JSON.stringify(payload) });
            showToast("Campaign created.");
        }
        resetForm();
        await refreshAll();
    } catch (err) {
        showToast(err.message, true);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = isEditing ? "Save changes" : "Create campaign";
    }
});

async function editCampaign(id) {
    try {
        const c = await fetchAPI(`/campaigns/${id}`);
        campaignIdInput.value      = c.id;
        nameInput.value            = c.name;
        ownerInput.value           = c.owner || "";
        descriptionInput.value     = c.description || "";
        budgetInput.value          = c.budget;
        spentInput.value           = c.spent || "";
        currencyInput.value        = c.currency;
        startDateInput.value       = c.start_date;
        endDateInput.value         = c.end_date || "";
        targetAudienceInput.value  = c.target_audience || "";
        statusInput.value          = c.status;
        tagsInput.value            = c.tags && c.tags.length ? c.tags.join(", ") : "";
        assetsInput.value          = c.assets || "";
        notesInput.value           = c.notes || "";

        formTitle.textContent      = "Edit campaign";
        submitBtn.textContent      = "Save changes";
        cancelBtn.style.display    = "inline-block";

        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
        showToast(err.message, true);
    }
}

async function cloneCampaign(id) {
    try {
        await fetchAPI(`/campaigns/${id}/duplicate`, { method: "POST" });
        showToast("Campaign duplicated as Draft.");
        await refreshAll();
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
        showToast(err.message, true);
    }
}

async function deleteCampaign(id) {
    if (!confirm("Delete this campaign? This cannot be undone.")) return;
    try {
        await fetchAPI(`/campaigns/${id}`, { method: "DELETE" });
        showToast("Campaign deleted.");
        await refreshAll();
    } catch (err) {
        showToast(err.message, true);
    }
}

function exportCSV() {
    const a = document.createElement("a");
    a.href = `${API_URL}/campaigns/export`;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast("Downloading CSV...");
}

function resetForm() {
    form.reset();
    campaignIdInput.value   = "";
    formTitle.textContent   = "New campaign";
    submitBtn.textContent   = "Create campaign";
    cancelBtn.style.display = "none";
    startDateInput.value    = todayISO();

    const statusEl = document.getElementById("ai-brief-status");
    if (statusEl) statusEl.style.display = "none";
}

cancelBtn.addEventListener("click", resetForm);

function todayISO() {
    return new Date().toISOString().split("T")[0];
}

function formatDate(str) {
    if (!str) return "";
    const d = new Date(str + "T00:00:00");
    return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function formatUSD(val) {
    return "$" + Number(val).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
}

startDateInput.value = todayISO();
refreshAll();