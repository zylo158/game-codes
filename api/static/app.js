const GAMES = ["wuwa", "nte", "bluearchive", "endfield"];
const GAME_LABELS = { wuwa: "Wuthering Waves", nte: "Neverness to Everness", bluearchive: "Blue Archive", endfield: "Arknights: Endfield" };
const GAME_LOGOS = { wuwa: "wuwa.svg", nte: "nte.png", bluearchive: "bluearchive.svg", endfield: "endfield.svg" };
const GAME_COLORS = { wuwa: "#eab308", nte: "#3b82f6", bluearchive: "#a855f7", endfield: "#ef4444" };

let currentGame = "wuwa";

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

const GAME_SHORT_LABELS = { wuwa: "WuWa", nte: "NTE", bluearchive: "BA", endfield: "Endfield" };

function updateStats(stats) {
  const row = document.getElementById("statsRow");
  const isMobile = window.innerWidth < 500;
  row.innerHTML = GAMES.map(slug => {
    const g = stats[slug] || { codes: 0, unverified: 0 };
    const label = isMobile ? GAME_SHORT_LABELS[slug] : GAME_LABELS[slug];
    return `<span class="stat-badge" style="color:${GAME_COLORS[slug]}">${label}: ${g.codes}</span>`;
  }).join("");
}

function renderCodes(slug, data) {
  const grid = document.getElementById("codesGrid");
  const codes = data.codes || [];
  if (!codes.length) {
    grid.innerHTML = '<div class="loading">No active codes for this game.</div>';
    return;
  }
  grid.innerHTML = codes.map(c => {
    const rewards = c.rewards ? `<div class="rewards-text">${escapeHTML(c.rewards)}</div>` : "";
    const source = c.source ? `<div class="source-text">${escapeHTML(c.source)}</div>` : "";
    return `
      <div class="code-card">
        <div class="code-row">
          <span class="code-text">${escapeHTML(c.code)}</span>
          <button class="copy-btn" data-code="${escapeHTML(c.code)}" title="Copy code">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
        </div>
        ${rewards}
        ${source}
      </div>`;
  }).join("");
  document.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", handleCopy);
  });
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function handleCopy(e) {
  const btn = e.currentTarget;
  const code = btn.dataset.code;
  try {
    await navigator.clipboard.writeText(code);
    btn.classList.add("copied");
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
    setTimeout(() => {
      btn.classList.remove("copied");
      btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
    }, 2000);
  } catch {}
}

function renderDropdown() {
  const trigger = document.getElementById("dropdownTrigger");
  const menu = document.getElementById("dropdownMenu");

  function renderTrigger(slug) {
    trigger.innerHTML = `<img class="logo-img" src="/static/logos/${GAME_LOGOS[slug]}" alt="">${GAME_LABELS[slug]}`;
  }

  function renderOptions() {
    menu.innerHTML = GAMES.map(slug =>
      `<button class="dropdown-option${slug === currentGame ? " selected" : ""}" data-game="${slug}">
        <img class="logo-img" src="/static/logos/${GAME_LOGOS[slug]}" alt="">
        ${GAME_LABELS[slug]}
      </button>`
    ).join("");
  }

  function open() { menu.classList.add("open"); trigger.classList.add("open"); }
  function close() { menu.classList.remove("open"); trigger.classList.remove("open"); }

  renderTrigger(currentGame);
  renderOptions();

  trigger.addEventListener("click", e => {
    e.stopPropagation();
    menu.classList.contains("open") ? close() : open();
  });

  menu.addEventListener("click", e => {
    const opt = e.target.closest(".dropdown-option");
    if (!opt) return;
    currentGame = opt.dataset.game;
    renderTrigger(currentGame);
    renderOptions();
    close();
    loadCodes(currentGame);
  });

  document.addEventListener("click", close);
}

async function loadCodes(slug) {
  const grid = document.getElementById("codesGrid");
  grid.innerHTML = '<div class="loading">Loading...</div>';
  try {
    const data = await fetchJSON(`/codes?game=${slug}`);
    renderCodes(slug, data);
  } catch {
    grid.innerHTML = '<div class="error">Failed to load codes. Try again later.</div>';
  }
}

async function loadAll() {
  try {
    const stats = await fetchJSON("/stats");
    updateStats(stats);
  } catch {}
  const now = new Date();
  document.getElementById("lastUpdate").textContent = `Updated ${now.toLocaleTimeString()}`;
  renderDropdown();
  loadCodes(currentGame);
}

document.addEventListener("DOMContentLoaded", loadAll);
setInterval(loadAll, 3600000);
