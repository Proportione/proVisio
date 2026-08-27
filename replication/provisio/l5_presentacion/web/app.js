"use strict";
// L5 — render vanilla del board /api/board. Sin framework, sin build. FR-11: la UI
// solo PINTA hechos ya calculados; el brazo L (narrativa IA) va en su propia cinta,
// separado de las cifras, y se oculta si está ausente (degradación).

const $ = (id) => document.getElementById(id);
const pct = (x) => (x == null ? "—" : (x * 100).toFixed(0) + "%");

async function tick() {
  let b;
  try {
    b = await (await fetch("/api/board", { cache: "no-store" })).json();
  } catch (e) { return; }

  $("generated").textContent = b.generatedAt || "—";
  $("mode").textContent = (b.tenant || "proportione");

  const fa1 = (b.fusion && b.fusion.fa1) || {};
  const r = fa1.brazo_R || {};
  $("fusion-lectura").textContent = r.lectura || "—";

  // brazo L (narrativa IA): cinta aparte, oculta si no hay
  const l = fa1.brazo_L || {};
  const nar = $("fusion-narrativa");
  if (l.sintesis) { nar.textContent = "IA · " + l.sintesis; nar.style.display = ""; }
  else { nar.style.display = "none"; }

  // citación-por-afirmación: cada afirmación con sus anclas de fuente
  const citas = $("fusion-citas");
  citas.innerHTML = "";
  (r.afirmaciones || []).forEach((a) => {
    const li = document.createElement("li");
    const src = (a.citas || []).map((c) => `<code>${c}</code>`).join(" ");
    li.innerHTML = `${a.texto} <span class="cite">${src}</span>`;
    citas.appendChild(li);
  });

  // K1 tiles (census real)
  const k1 = (b.screens && b.screens.k1) || {};
  $("k1-fuerza").textContent = "señal " + (k1.fuerza_senal || "—");
  const tiles = [
    ["Contactos", k1.contactos], ["Clientes", k1.clientes], ["Leads", k1.leads],
    ["Deals", k1.deals], ["Follow-ups vencidos", k1.follow_ups_vencidos],
  ];
  const pipe = k1.pipeline || {};
  tiles.push(["Pipeline (fixture)", pipe.valor_pipeline], ["Ponderado", pipe.ponderado]);
  $("k1-tiles").innerHTML = tiles.map(([lab, v]) =>
    `<div class="tile"><div class="v">${v == null ? "—" : v}</div><div class="l">${lab}</div></div>`
  ).join("");
  $("k1-accion").textContent = k1.accion || "—";

  // señales
  const s1 = (b.signals && b.signals.s1) || {};
  const br = s1.branded || {};
  $("sig-s1").querySelector(".sig-body").innerHTML =
    `${s1.queries_total || 0} queries · marca "${br.query || "—"}" ${br.impressions || 0} impr · CTR ${br.ctr == null ? "—" : (br.ctr * 100).toFixed(2) + "%"}`;

  const s2 = (b.signals && b.signals.s2) || {};
  const mix = s2.channel_mix || {};
  $("sig-s2").querySelector(".sig-body").innerHTML =
    `${s2.sessions || 0} sesiones · Direct ${pct(mix.Direct)} · Organic ${pct(mix.Organic)} · newUsers ${pct(s2.newuser_ratio)}`;

  const s3 = (b.signals && b.signals.s3) || {};
  $("sig-s3").querySelector(".sig-body").innerHTML =
    s3.estado === "na_estructural"
      ? `<strong>N/A estructural</strong><br><small>${s3.razon || ""}</small>`
      : "—";

  // alertas (brazo R en vivo)
  $("alerts").innerHTML = (b.alerts || []).map((a) =>
    `<div class="alert ${a.severity}"><b>${a.severity}</b> ${a.title} — ${a.detail}</div>`
  ).join("") || `<div class="alert ok">Sin condiciones activas</div>`;
}

tick();
setInterval(tick, 5000);
