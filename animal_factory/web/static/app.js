"use strict";
const $ = (id) => document.getElementById(id);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* modo privado */ } },
};
const state = { hero: "auto", style: "cartoon", quality: "final", code: store.get("af_code", ""), jobId: store.get("af_job", ""), timer: null };

function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) el.setAttribute(k, v);
  }
  for (const kid of kids.flat()) el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  return el;
}
const q = (url) => (state.code ? url + (url.includes("?") ? "&" : "?") + "code=" + encodeURIComponent(state.code) : url);

async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json" };
  if (state.code) headers["X-Access-Code"] = state.code;
  const res = await fetch(path, { ...opts, headers });
  let data = null;
  try { data = await res.json(); } catch { /* sin cuerpo */ }
  if (!res.ok) {
    if (res.status === 401) { showGate(); throw new Error("Código de acceso incorrecto."); }
    let d = data && data.detail;
    if (Array.isArray(d)) d = d.map((e) => e.msg).join(" · ");
    throw new Error(d || `Error ${res.status}`);
  }
  return data;
}

function say(text, ok = false) {
  const m = $("msg");
  m.textContent = text || "";
  m.hidden = !text;
  m.className = "msg" + (ok ? " ok" : "");
}
function showGate() { $("gate").hidden = false; $("app").hidden = true; }

function radio(container, items, key, render) {
  container.replaceChildren();
  for (const it of items) {
    const b = h("button", { type: "button", role: "radio", "aria-checked": String(state[key] === it.id), onclick: () => {
      state[key] = it.id;
      for (const s of container.children) s.setAttribute("aria-checked", String(s === b));
    } }, ...render(it));
    container.append(b);
  }
}

async function init() {
  const st = await fetch("/api/status").then((r) => r.json());
  if (!st.ok) {
    const p = $("problems");
    p.hidden = false;
    p.replaceChildren(h("h2", {}, "⚠️ La fábrica no está lista"), ...st.problemas.map((t) => h("p", {}, t)));
    return;
  }
  if (st.requiere_codigo && !state.code) { showGate(); return; }
  try { await loadApp(); } catch (e) { if (!$("gate").hidden) return; say(e.message); }
}

async function loadApp() {
  const o = await api("/api/options");
  $("gate").hidden = true;
  $("app").hidden = false;
  const heroes = $("heroes");
  heroes.replaceChildren(h("button", { type: "button", class: "hero auto", role: "radio", "aria-checked": "true", onclick: pickHero("auto") }, "🎲", h("b", {}, "Automático")));
  for (const c of o.personajes) {
    heroes.append(h("button", { type: "button", class: "hero", role: "radio", "aria-checked": "false", "data-id": c.id, onclick: pickHero(c.id) },
      h("img", { src: `/api/characters/${c.id}.svg`, alt: c.nombre, loading: "lazy" }), h("b", {}, c.nombre), h("small", {}, c.especie)));
  }
  heroes.firstChild.dataset.id = "auto";
  radio($("styles"), o.estilos, "style", (s) => [s.nombre]);
  radio($("qualities"), o.calidades, "quality", (c) => [c.nombre]);
  const ex = $("examples");
  ex.replaceChildren(...o.ejemplos.map((t) => h("button", { type: "button", class: "chip", onclick: () => { $("idea").value = t; count(); } }, t)));
  await refreshHistory();
  if (state.jobId) watch(state.jobId, true);
}
const pickHero = (id) => (ev) => {
  state.hero = id;
  for (const b of $("heroes").children) b.setAttribute("aria-checked", String(b.dataset.id === id));
};
function count() { $("chars").textContent = $("idea").value.length; }

function payload() {
  return JSON.stringify({ idea: $("idea").value, hero: state.hero === "auto" ? null : state.hero, style: state.style, quality: state.quality });
}

function renderScenes(story, thumbs) {
  $("scenesCard").hidden = false;
  $("scenesTitle").textContent = `Panel de escenas — ${story.title}`;
  const u = story.understood || {};
  $("understood").textContent = ["protagonista", "tema", "reparto", "rasgo", "aviso"].filter((k) => u[k]).map((k) => `${k}: ${u[k]}`).join(" · ");
  const names = Object.fromEntries(Object.entries(story.characters).map(([k, c]) => [k, c.name]));
  $("scenes").replaceChildren(...story.scenes.map((s, i) => h("div", { class: "scene" },
    s.miniatura ? h("img", { src: s.miniatura, alt: `Escena ${s.index}` }) : h("div", { class: "ph" }),
    h("div", {}, h("h3", {}, `${s.index}. ${s.title}`), h("div", { class: "meta" }, `${s.location.replace("_", " ")} · ${s.mood}${s.duration ? ` · ${s.duration.toFixed(1)} s` : ""}`),
      ...s.lines.map((l) => h("p", {}, h("span", { class: "who" }, (l.speaker === "narrador" ? "Narrador" : names[l.speaker] || l.speaker) + ": "), l.text))))));
}

async function preview() {
  say("");
  $("previewBtn").disabled = true;
  $("previewBtn").textContent = "Dibujando escenas…";
  try {
    const story = await api("/api/story", { method: "POST", body: payload() });
    renderScenes(story);
    $("scenesCard").scrollIntoView({ behavior: "smooth" });
  } catch (e) { say(e.message); }
  finally { $("previewBtn").disabled = false; $("previewBtn").textContent = "📝 Ver guion y escenas"; }
}

const STEPS = [["guion", "Guion"], ["voces", "Voces"], ["audio", "Música y efectos"], ["animacion", "Animación"], ["montaje", "Montaje y MP4"]];
function renderStatus(j) {
  $("statusCard").hidden = false;
  $("barFill").style.width = Math.round(j.progress * 100) + "%";
  $("statusText").textContent = j.status === "error" ? "❌ " + (j.error || "Error") : `${Math.round(j.progress * 100)} % · ${j.message}${j.elapsed ? ` · ${Math.round(j.elapsed)} s` : ""}`;
  const idx = STEPS.findIndex(([k]) => k === j.stage);
  $("steps").replaceChildren(...STEPS.map(([k, label], i) => {
    const done = j.status === "done" || i < idx;
    const now = j.status === "running" && i === idx;
    return h("li", { class: done ? "done" : now ? "now" : "" }, h("span", {}, done ? "✅" : now ? "⏳" : "○"), h("span", {}, label));
  }));
}

function showResult(j) {
  $("resultCard").hidden = false;
  $("resultTitle").textContent = j.title || "Vista previa";
  const v = $("video");
  const src = q(`/api/jobs/${j.id}/video`);
  if (v.dataset.src !== src) { v.dataset.src = src; v.src = src; v.poster = q(`/api/jobs/${j.id}/poster`); }
  $("downloadBtn").href = q(`/api/jobs/${j.id}/video?download=1`);
  $("srtBtn").href = q(`/api/jobs/${j.id}/subtitles`);
  const mb = j.stats && j.stats.probe ? (j.stats.probe.bytes / 1e6).toFixed(1) + " MB · " : "";
  $("resultInfo").textContent = `${mb}${j.duration || ""} s · render en ${j.stats && j.stats.segundos_de_render ? j.stats.segundos_de_render : "?"} s` +
    (j.warnings && j.warnings.length ? " · Avisos: " + j.warnings.join(" ") : "");
}

function watch(id, silent = false) {
  state.jobId = id;
  store.set("af_job", id);
  clearInterval(state.timer);
  const tick = async () => {
    let j;
    try { j = await api(`/api/jobs/${id}`); } catch (e) { if (!silent) say(e.message); clearInterval(state.timer); return; }
    renderStatus(j);
    if (j.story) renderScenes(j.story);
    if (j.status === "done") { clearInterval(state.timer); showResult(j); say("¡Tu video está listo!", true); refreshHistory(); $("goBtn").disabled = false; }
    else if (j.status === "error") { clearInterval(state.timer); say(j.error || "Falló la generación"); refreshHistory(); $("goBtn").disabled = false; }
    else { $("resultCard").hidden = true; $("goBtn").disabled = true; }
  };
  tick();
  state.timer = setInterval(tick, 1500);
}

async function generate() {
  say("");
  try {
    const j = await api("/api/jobs", { method: "POST", body: payload() });
    $("goBtn").disabled = true;
    watch(j.id);
    $("statusCard").scrollIntoView({ behavior: "smooth" });
    refreshHistory();
  } catch (e) { say(e.message); }
}

async function refreshHistory() {
  let jobs;
  try { jobs = await api("/api/jobs"); } catch { return; }
  const box = $("history");
  if (!jobs.length) { box.replaceChildren(h("p", { class: "hint" }, "Todavía no hay producciones.")); return; }
  box.replaceChildren(...jobs.slice(0, 20).map((j) => {
    const label = { done: "listo", error: "error", queued: "en cola", running: "generando" }[j.status] || j.status;
    const item = h("div", { class: "item", role: "button", tabindex: "0", onclick: () => open(j) },
      j.has_video ? h("img", { src: q(`/api/jobs/${j.id}/poster`), alt: "" }) : h("div", { class: "ph" }),
      h("div", {}, h("b", {}, j.title || j.idea.slice(0, 50)), h("small", {}, new Date(j.created * 1000).toLocaleString("es")), " ", h("span", { class: "badge " + j.status }, label)),
      h("button", { class: "del", "aria-label": "Borrar", onclick: async (ev) => { ev.stopPropagation(); if (!confirm("¿Borrar este video?")) return;
        try { await api(`/api/jobs/${j.id}`, { method: "DELETE" }); } catch (e) { say(e.message); } refreshHistory(); } }, "🗑"));
    return item;
  }));
}
function open(j) {
  $("idea").value = j.idea; count();
  watch(j.id);
  $("statusCard").scrollIntoView({ behavior: "smooth" });
}

$("idea").addEventListener("input", count);
$("previewBtn").addEventListener("click", preview);
$("goBtn").addEventListener("click", generate);
$("codeBtn").addEventListener("click", async () => {
  state.code = $("code").value.trim();
  store.set("af_code", state.code);
  const gm = $("gateMsg");
  gm.hidden = true;
  try { await loadApp(); } catch (e) { $("gate").hidden = false; gm.textContent = e.message.includes("código") ? "Código incorrecto." : e.message; gm.hidden = false; }
});
init().catch((e) => say(e.message));
