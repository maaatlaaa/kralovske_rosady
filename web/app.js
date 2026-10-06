"use strict";

// ------------------------------------------------------------ pomocne

const $ = (vyber) => document.querySelector(vyber);

/** vytvori HTML prvek; text se vklada vzdy jako text (ne HTML) */
function h(znacka, atributy, ...deti) {
  const prvek = document.createElement(znacka);
  for (const [klic, hodnota] of Object.entries(atributy || {})) {
    if (hodnota === null || hodnota === undefined || hodnota === false) continue;
    if (klic === "class") prvek.className = hodnota;
    else if (klic.startsWith("on")) prvek.addEventListener(klic.slice(2), hodnota);
    else prvek.setAttribute(klic, hodnota === true ? "" : hodnota);
  }
  for (const dite of deti.flat()) {
    if (dite === null || dite === undefined || dite === false) continue;
    prvek.append(dite instanceof Node ? dite : String(dite));
  }
  return prvek;
}

function nacti(klic, vychozi) {
  try {
    const hodnota = localStorage.getItem(klic);
    return hodnota === null ? vychozi : JSON.parse(hodnota);
  } catch {
    return vychozi;
  }
}

function uloz(klic, hodnota) {
  try {
    localStorage.setItem(klic, JSON.stringify(hodnota));
  } catch {
    /* prohlizec bez uloziste - hra pujde, jen si nezapamatuje prihlaseni */
  }
}

let casovacHlasky = null;
function hlaska(text) {
  const prvek = $("#hlaska");
  prvek.textContent = text;
  prvek.hidden = false;
  clearTimeout(casovacHlasky);
  casovacHlasky = setTimeout(() => (prvek.hidden = true), 4000);
}

async function api(cesta, telo) {
  const odpoved = await fetch(cesta, {
    method: telo ? "POST" : "GET",
    headers: telo ? { "Content-Type": "application/json" } : {},
    body: telo ? JSON.stringify(telo) : undefined,
  });
  const data = await odpoved.json().catch(() => ({}));
  if (!odpoved.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "Něco se nepovedlo.";
    throw new Error(detail);
  }
  return data;
}

// ------------------------------------------------------------ karty

let katalog = null;
let specialiste = {};   // nazev karty -> kategorie, ve ktere ma bonus

const barvaHrace = (hrac) => katalog.barvy[hrac].hex;

function hodnotaText(hodnota) {
  return hodnota === null ? "–" : String(hodnota).replace(".", ",");
}

function hodnotaNaKarte(nazev) {
  if (nazev === "Dvojník") return "?";
  const hodnota = katalog.karty[nazev].hodnota;
  return hodnota === 9.5 ? "9½" : String(hodnota);
}

const KORUNA = '<svg viewBox="0 0 64 64" aria-hidden="true"><path fill="#e2b85a" stroke="#2c1c0c" ' +
  'stroke-width="2.5" stroke-linejoin="round" d="M8 46 4 18l15 12 13-20 13 20 15-12-4 28z"/>' +
  '<rect x="8" y="48" width="48" height="8" rx="2" fill="#e2b85a" stroke="#2c1c0c" stroke-width="2.5"/>' +
  '<circle cx="32" cy="34" r="4" fill="#9a2015"/><circle cx="18" cy="38" r="3" fill="#23415e"/>' +
  '<circle cx="46" cy="38" r="3" fill="#23415e"/></svg>';

/** licova strana karty vlivu v barve hrace */
function karta(nazev, hrac) {
  const info = katalog.karty[nazev];
  const kategorie = specialiste[nazev];
  let stitek = null;
  if (kategorie) {
    stitek = h("div", { class: "k-kdy k-kdy-kat", style: `--kat:${katalog.kategorie[kategorie].barva}` }, kategorie);
  } else if (info.kdy) {
    stitek = h("div", { class: `k-kdy k-kdy-${info.kdy}` },
      info.kdy === "otoceni" ? "Po otočení" : "Na konci kola");
  }
  return h("div", { class: "k", style: `--hrac:${barvaHrace(hrac)}` },
    h("div", { class: "k-ram" },
      h("div", { class: "k-obraz" },
        h("img", { src: `/obrazky/ilustrace/${info.soubor}.webp`, alt: "", loading: "lazy", draggable: "false" })),
      h("div", { class: "k-text" }, stitek,
        h("p", { class: info.kdy ? null : "k-citat" }, info.kratky))),
    h("div", { class: "k-nazev" + (nazev.length > 9 ? " dlouhy" : "") }, nazev),
    h("div", {
      class: "medailon k-hodnota" + (hodnotaNaKarte(nazev).includes("½") ? " male" : ""),
      title: `hodnota ${hodnotaText(info.hodnota)}`,
    }, hodnotaNaKarte(nazev)),
    kategorie
      ? h("div", {
          class: "medailon k-bonus",
          style: `--kat:${katalog.kategorie[kategorie].barva}`,
          title: `ve sloupci ${kategorie} má hodnotu ${katalog.bonus_specialisty}`,
        }, h("img", { src: `/obrazky/znaky/${info.soubor}.webp`, alt: "" }),
           h("span", null, katalog.bonus_specialisty))
      : null);
}

/** rub karty - kazdy hrac ma vlastni barvu */
function rubKarty(hrac) {
  const erb = h("div", { class: "k-erb" });
  erb.innerHTML = KORUNA;
  return h("div", { class: "k k-rub", style: `--hrac:${barvaHrace(hrac)}` },
    h("div", { class: "k-ram" }, h("div", { class: "k-pole" }, erb)));
}

/** cilova karta (hodnota + kategorie) */
function cilovaKarta(cilova) {
  const kategorie = katalog.kategorie[cilova.kategorie];
  const znak = katalog.karty[kategorie.specialista].soubor;
  return h("div", { class: "c", style: `--kat:${kategorie.barva}`, title: `${cilova.kategorie} ${cilova.hodnota}` },
    h("div", { class: "c-telo" },
      h("div", { class: "c-hodnota" }, cilova.hodnota),
      h("div", { class: "c-vpravo" },
        h("img", { class: "c-znak", src: `/obrazky/znaky/${znak}.webp`, alt: "" }),
        h("div", { class: "c-nazev" }, cilova.kategorie))));
}

// ------------------------------------------------------- stav aplikace

let mistnost = null;   // posledni stav ze serveru
let kodHry = null;
let soket = null;
let prodlevaPripojeni = 1000;
let casovacPripojeni = null;
let vybranaKarta = null;   // index karty v ruce
let vyberZradce = null;    // sloupec, se kterym Zradce vymeni cilovou kartu

const mojeHry = () => nacti("rosady_hry", {});

function ulozHru(kod, token, jmeno) {
  const hry = mojeHry();
  hry[kod] = { token, jmeno, datum: Date.now() };
  uloz("rosady_hry", hry);
}

function zapomenHru(kod) {
  const hry = mojeHry();
  delete hry[kod];
  uloz("rosady_hry", hry);
}

function ukaz(obrazovka) {
  for (const id of ["domu", "lobby", "hra"]) $("#" + id).hidden = id !== obrazovka;
}

// -------------------------------------------------------------- smerovani

function kodZAdresy() {
  return location.hash.replace("#", "").trim().toUpperCase();
}

function smeruj() {
  const kod = kodZAdresy();
  const hra = kod && mojeHry()[kod];
  if (hra) {
    if (kodHry !== kod) pripojSoket(kod, hra.token);
  } else {
    odpojSoket();
    ukazDomu(kod);
  }
}

// ------------------------------------------------------------ uvodni obrazovka

function ukazDomu(kod) {
  ukaz("domu");
  $("#jmeno").value = nacti("rosady_jmeno", "");
  if (kod) $("#kod").value = kod;
  const hry = Object.entries(mojeHry()).sort((a, b) => b[1].datum - a[1].datum);
  $("#moje-hry").hidden = hry.length === 0;
  $("#seznam-her").replaceChildren(
    ...hry.map(([kod, info]) =>
      h("li", null,
        h("span", { class: "roztahni" }, h("b", null, kod), ` – hraješ jako ${info.jmeno}`),
        h("button", { class: "tlacitko", onclick: () => (location.hash = kod) }, "Pokračovat"),
        h("button", {
          class: "tlacitko vedlejsi", title: "Odebrat ze seznamu",
          onclick: () => { zapomenHru(kod); ukazDomu(); },
        }, "✕"))));
}

function chybaDomu(text) {
  const prvek = $("#chyba-domu");
  prvek.textContent = text;
  prvek.hidden = !text;
}

function jmenoHrace() {
  const jmeno = $("#jmeno").value.trim();
  if (!jmeno) {
    chybaDomu("Nejdřív napiš své jméno.");
    $("#jmeno").focus();
    return null;
  }
  uloz("rosady_jmeno", jmeno);
  return jmeno;
}

$("#zalozit").addEventListener("click", async () => {
  const jmeno = jmenoHrace();
  if (!jmeno) return;
  try {
    const odpoved = await api("/api/mistnosti", { jmeno });
    ulozHru(odpoved.kod, odpoved.token, jmeno);
    location.hash = odpoved.kod;
  } catch (chyba) {
    chybaDomu(chyba.message);
  }
});

$("#pripojit").addEventListener("click", async () => {
  const jmeno = jmenoHrace();
  const kod = $("#kod").value.trim().toUpperCase();
  if (!jmeno) return;
  if (kod.length !== 4) {
    chybaDomu("Kód hry má 4 písmena.");
    return;
  }
  try {
    const odpoved = await api(`/api/mistnosti/${kod}/pripojit`, { jmeno });
    ulozHru(odpoved.kod, odpoved.token, jmeno);
    location.hash = odpoved.kod;
    smeruj();
  } catch (chyba) {
    chybaDomu(chyba.message);
  }
});

$("#kod").addEventListener("keydown", (e) => e.key === "Enter" && $("#pripojit").click());

// ---------------------------------------------------------------- spojeni

function pripojSoket(kod, token) {
  odpojSoket();
  kodHry = kod;
  const protokol = location.protocol === "https:" ? "wss" : "ws";
  const novy = new WebSocket(`${protokol}://${location.host}/ws/${kod}?token=${encodeURIComponent(token)}`);
  soket = novy;

  novy.onopen = () => {
    prodlevaPripojeni = 1000;
    $("#odpojeno").hidden = true;
  };
  novy.onmessage = (udalost) => {
    const zprava = JSON.parse(udalost.data);
    if (zprava.typ === "stav") {
      mistnost = zprava.stav;
      vykresli();
    } else if (zprava.typ === "chyba") {
      hlaska(zprava.zprava);
    } else if (zprava.typ === "neplatne") {
      zapomenHru(kod);
      odpojSoket();
      ukazDomu();
      chybaDomu(zprava.zprava);
    }
  };
  novy.onclose = () => {
    if (soket !== novy) return;   // zavreli jsme ho sami
    soket = null;
    if (kodHry !== kod || !mojeHry()[kod]) return;
    $("#odpojeno").hidden = false;
    casovacPripojeni = setTimeout(() => {
      if (kodHry === kod && mojeHry()[kod]) pripojSoket(kod, mojeHry()[kod].token);
    }, prodlevaPripojeni);
    prodlevaPripojeni = Math.min(prodlevaPripojeni * 2, 15000);
  };
}

function odpojSoket() {
  clearTimeout(casovacPripojeni);
  const stary = soket;
  soket = null;
  kodHry = null;
  mistnost = null;
  vybranaKarta = null;
  vyberZradce = null;
  $("#odpojeno").hidden = true;
  if (stary) stary.close();
}

function posli(zprava) {
  if (soket && soket.readyState === WebSocket.OPEN) soket.send(JSON.stringify(zprava));
  else hlaska("Nejsi připojen(a) k serveru.");
}

// ---------------------------------------------------------------- vykresleni

function vykresli() {
  if (!mistnost) return;
  if (mistnost.hra) vykresliHru();
  else vykresliLobby();
}

function vykresliLobby() {
  ukaz("lobby");
  $("#lobby-kod").textContent = mistnost.kod;
  $("#lobby-hraci").replaceChildren(
    ...mistnost.hraci.map((hrac, i) =>
      h("li", null,
        h("span", { class: "barva", style: `background:${barvaHrace(i)}` }),
        h("span", { class: "roztahni" }, hrac.jmeno,
          i === mistnost.ja ? " (ty)" : "", i === 0 ? " 👑" : ""),
        h("span", { class: "pripojeni" + (hrac.pripojen ? " ano" : ""),
                    title: hrac.pripojen ? "připojen(a)" : "nepřipojen(a)" }))));
  const pocet = mistnost.hraci.length;
  const lzeSpustit = pocet >= mistnost.min_hracu;
  $("#spustit").hidden = !mistnost.zakladatel;
  $("#spustit").disabled = !lzeSpustit;
  $("#lobby-info").textContent = mistnost.zakladatel
    ? (lzeSpustit ? `Až budou všichni tady, spusť hru (max. ${mistnost.max_hracu} hráčů).`
                  : "Čekáme, až se připojí aspoň jeden další hráč.")
    : "Čekáme, až zakladatel hru spustí.";
}

$("#spustit").addEventListener("click", () => posli({ akce: "start" }));
$("#opustit").addEventListener("click", () => {
  const kod = kodHry;
  posli({ akce: "opustit" });
  zapomenHru(kod);
  location.hash = "";
});
$("#kopirovat").addEventListener("click", async () => {
  const odkaz = `${location.origin}/#${mistnost.kod}`;
  try {
    await navigator.clipboard.writeText(odkaz);
    hlaska("Odkaz zkopírován – pošli ho ostatním.");
  } catch {
    hlaska(odkaz);
  }
});

function vykresliHru() {
  ukaz("hra");
  const hra = mistnost.hra;
  const ja = hra.ja;
  const mujTah = hra.faze === "tah" && hra.na_tahu === ja;
  if (vybranaKarta >= hra.ruka.length) vybranaKarta = null;
  const volimZradce = hra.faze === "volba" && hra.volba.hrac === ja && hra.volba.typ === "zradce";
  if (!volimZradce) vyberZradce = null;

  $("#kolo").textContent = `Kolo ${Math.min(hra.kolo + 1, hra.pocet_kol)}/${hra.pocet_kol}`;
  vykresliStav(hra, mujTah);
  vykresliKonec(hra);
  vykresliPlochu(hra, mujTah, volimZradce);
  vykresliRozhodnuti(hra, volimZradce);
  vykresliRuku(hra, mujTah);
  vykresliVysledky(hra);
  vykresliHrace(hra);
  $("#zaznamy").replaceChildren(...hra.zaznamy.slice().reverse().map((z) => h("li", null, z)));
}

function vykresliStav(hra, mujTah) {
  const jmeno = (i) => hra.hraci[i].jmeno;
  const prvek = $("#stav-tahu");
  let text;
  let ja = false;
  if (hra.faze === "tah") {
    ja = mujTah;
    text = mujTah ? "Jsi na tahu – vyber kartu z ruky a pak sloupec."
                  : `Na tahu je ${jmeno(hra.na_tahu)}.`;
  } else if (hra.faze === "volba") {
    const karta = hra.volba.typ === "prevlek" ? "Převleku" : "Zrádci";
    ja = hra.volba.hrac === hra.ja;
    text = ja ? `Otočila se tvoje karta – rozhodni o ${karta}.`
              : `${jmeno(hra.volba.hrac)} rozhoduje o ${karta}…`;
  } else if (hra.faze === "vyhodnoceni") {
    text = "Kolo je vyhodnocené.";
  } else {
    text = "Konec hry!";
  }
  prvek.textContent = text;
  prvek.classList.toggle("ja", ja);
  document.title = (ja ? "● " : "") + "Královské rošády";
}

function vykresliKonec(hra) {
  const panel = $("#konec");
  panel.hidden = hra.faze !== "konec";
  if (panel.hidden) return;
  panel.replaceChildren(
    h("h2", null, "Konečné pořadí"),
    h("ol", { class: "poradi" },
      hra.poradi.map((p) =>
        h("li", null,
          h("span", { class: "barva", style: `background:${barvaHrace(p.hrac)};display:inline-block;vertical-align:middle;margin-right:6px` }),
          h("b", null, hra.hraci[p.hrac].jmeno), ` – ${p.body} bodů`))),
    h("button", {
      class: "tlacitko hlavni",
      onclick: () => { zapomenHru(mistnost.kod); location.hash = ""; },
    }, "Zpět na úvod"));
}

function vykresliPlochu(hra, mujTah, volimZradce) {
  const n = hra.hraci.length;
  const plocha = $("#plocha");
  plocha.style.gridTemplateColumns = `repeat(${n}, minmax(0, 1fr))`;
  plocha.style.maxWidth = `${n * 150 + 20}px`;
  const konecKola = hra.faze === "vyhodnoceni" || hra.faze === "konec";
  const vitezove = {};
  const odstranene = new Set();
  for (const v of hra.vysledky_kola) {
    vitezove[v.sloupec] = v.vitez;
    for (const k of v.karty) if (k.odstranena) odstranene.add(`${k.index}:${v.sloupec}`);
  }

  const sloupce = [];
  for (let s = 0; s < n; s++) {
    const karty = hra.sloupce[s];
    const uzavreny = hra.uzavrene[s];
    const cilova = hra.hlavicka[s];
    const lze = mujTah && vybranaKarta !== null && !uzavreny;
    const volitelna = volimZradce && s !== hra.volba.sloupec;
    const vlastniZradce = volimZradce && s === hra.volba.sloupec;

    const hlavicka = h("div", {
      class: "cilova" + (volitelna ? " volitelna" : "") +
        (vyberZradce === s || vlastniZradce ? " vybrana" : ""),
      title: `${cilova.kategorie} ${cilova.hodnota}`,
      onclick: volitelna ? () => { vyberZradce = s; vykresli(); } : null,
    }, cilovaKarta(cilova));

    let stav;
    if (konecKola && s in vitezove) {
      stav = vitezove[s] === null ? "nikdo nevyhrál" : `🏆 ${hra.hraci[vitezove[s]].jmeno}`;
    } else if (uzavreny) stav = "⛈ uzavřeno";
    else if (karty.length >= cilova.hodnota) stav = `✓ ${karty.length}/${cilova.hodnota}`;
    else stav = `${karty.length}/${cilova.hodnota}`;
    const info = h("div", {
      class: "stav-sloupce" + (uzavreny || karty.length >= cilova.hodnota ? " splneny" : ""),
      title: "vyložené karty / kolik jich sloupec potřebuje",
    }, stav);

    const bunky = karty.map((pole, i) => vykresliPole(hra, pole, odstranene.has(`${i}:${s}`)));
    // prazdna mista do poctu, ktery sloupec potrebuje; pri tahu misto pro novou kartu
    const chybi = uzavreny ? 0 : Math.max(0, cilova.hodnota - karty.length);
    for (let i = 0; i < Math.max(chybi, lze ? 1 : 0); i++) {
      bunky.push(h("div", { class: "pole volne" + (lze && i === 0 ? " cil" : "") }));
    }
    sloupce.push(h("div", {
      class: "sloupec" + (lze ? " lze" : "") + (uzavreny ? " uzavreny" : ""),
      onclick: lze ? () => vyloz(s) : null,
    }, hlavicka, info, h("div", { class: "karty" + (karty.length > 3 ? " husty" : "") }, bunky)));
  }
  plocha.replaceChildren(...sloupce);
}

function vykresliPole(hra, pole, odstranena) {
  const vlastnik = hra.hraci[pole.hrac].jmeno;
  const tridy = ["pole", "karta"];
  if (odstranena) tridy.push("odstranena");
  let odznak = null;
  if (!pole.odkryta && pole.karta) {
    tridy.push("zakryta-moje");
    odznak = h("span", { class: "odznak" }, "zakrytá");
  }
  let prevlek = null;
  if (pole.ma_prevlek) {
    prevlek = h("span", { class: "odznak prevlek" },
      pole.pod_prevlekem ? `🎭 ${pole.pod_prevlekem}` : "🎭 skrytá karta");
  }
  return h("div", {
    class: tridy.join(" "),
    title: pole.karta ? `${pole.karta} (${vlastnik})` : `zakrytá karta (${vlastnik})`,
    onclick: (udalost) => {
      if (udalost.currentTarget.closest(".sloupec.lze")) return;
      ukazDetail(pole, vlastnik);
    },
  }, pole.karta ? karta(pole.karta, pole.hrac) : rubKarty(pole.hrac), odznak, prevlek);
}

function ukazDetail(pole, vlastnik) {
  const obsah = $("#detail-obsah");
  if (!pole.karta) {
    obsah.replaceChildren(
      h("div", { class: "detail-karta" }, rubKarty(pole.hrac)),
      h("p", null, `Zakrytá karta hráče ${vlastnik}.`));
  } else {
    const info = katalog.karty[pole.karta];
    obsah.replaceChildren(
      h("div", { class: "detail-karta" }, karta(pole.karta, pole.hrac)),
      h("p", null, info.popis),
      h("p", { class: "napoveda" }, `Patří hráči ${vlastnik}.`),
      pole.pod_prevlekem ? h("p", null, `🎭 Pod Převlekem: ${pole.pod_prevlekem}`) : null);
  }
  $("#detail").showModal();
}

function vyloz(sloupec) {
  posli({ akce: "vyloz", karta: vybranaKarta, sloupec });
  vybranaKarta = null;
}

function kartaVRuce(hra, nazev, index, vybrana, onclick) {
  return h("button", {
    class: "karta-ruka" + (vybrana ? " vybrana" : ""),
    title: `${nazev} – ${katalog.karty[nazev].popis}`,
    onclick,
    disabled: onclick ? null : true,
  }, karta(nazev, hra.ja));
}

function vykresliRuku(hra, mujTah) {
  const skryt = hra.faze === "konec" || (hra.faze === "volba" && hra.volba.hrac === hra.ja);
  $("#ruka-obal").hidden = skryt;
  if (skryt) return;
  $("#ruka").replaceChildren(...hra.ruka.map((nazev, i) =>
    kartaVRuce(hra, nazev, i, i === vybranaKarta, () => {
      vybranaKarta = vybranaKarta === i ? null : i;
      vykresli();
    })));
  const popis = $("#popis-karty");
  if (vybranaKarta !== null) {
    const nazev = hra.ruka[vybranaKarta];
    const info = katalog.karty[nazev];
    popis.textContent = `${nazev} (${hodnotaText(info.hodnota)}): ${info.popis}` +
      (mujTah ? " Teď klikni na sloupec." : "");
  } else {
    popis.textContent = mujTah ? "Vyber kartu, kterou chceš vyložit." : "Klepnutím na kartu zobrazíš její popis.";
  }
}

function vykresliRozhodnuti(hra, volimZradce) {
  const panel = $("#rozhodnuti");
  const volimPrevlek = hra.faze === "volba" && hra.volba.hrac === hra.ja && hra.volba.typ === "prevlek";
  panel.hidden = !(volimPrevlek || volimZradce);
  if (volimPrevlek) {
    panel.replaceChildren(
      h("h2", null, "🎭 Převlek"),
      h("p", null, `Tvůj Převlek ve sloupci ${hra.volba.sloupec + 1} se otočil. ` +
        "Můžeš pod něj skrytě vložit jednu kartu z ruky – při vyhodnocení se v ni promění."),
      h("div", { class: "ruka" }, hra.ruka.map((nazev, i) =>
        kartaVRuce(hra, nazev, i, false, () => posli({ akce: "prevlek", karta: i })))),
      h("button", { class: "tlacitko", onclick: () => posli({ akce: "prevlek", karta: null }) },
        "Nic nevkládat"));
  } else if (volimZradce) {
    const vlastni = hra.volba.sloupec;
    panel.replaceChildren(
      h("h2", null, "🗡 Zrádce"),
      h("p", null, `Tvůj Zrádce ve sloupci ${vlastni + 1} se otočil. Klepni nahoře na cílovou kartu ` +
        "jiného sloupce – vymění se s cílovou kartou Zrádcova sloupce."),
      h("div", { class: "radek-tlacitek" },
        h("button", {
          class: "tlacitko hlavni",
          disabled: vyberZradce === null ? true : null,
          onclick: () => posli({ akce: "zradce", sloupec: vyberZradce }),
        }, vyberZradce === null ? "Vyměnit" : `Vyměnit sloupce ${vlastni + 1} a ${vyberZradce + 1}`),
        h("button", {
          class: "tlacitko",
          onclick: () => posli({ akce: "zradce", sloupec: null }),
        }, "Nic neměnit")));
  }
}

function vykresliVysledky(hra) {
  const panel = $("#vysledky");
  panel.hidden = hra.vysledky_kola.length === 0;
  if (panel.hidden) return;
  const jmeno = (i) => hra.hraci[i].jmeno;
  const karty = hra.vysledky_kola.map((v) => {
    const cilova = hra.hlavicka[v.sloupec];
    const soucty = Object.entries(v.soucty).sort((x, y) =>
      v.nejnizsi_vyhrava ? x[1] - y[1] : y[1] - x[1]);
    return h("div", { class: "panel vysledek" },
      h("h3", null, `Sloupec ${v.sloupec + 1}: ${cilova.kategorie} ${cilova.hodnota}`),
      h("table", null, v.karty.map((k) =>
        h("tr", { class: k.odstranena ? "odstranena" : null },
          h("td", null, h("span", { class: "barva", style: `background:${barvaHrace(k.hrac)};display:inline-block;width:12px;height:12px;vertical-align:middle` })),
          h("td", null, k.prevlek ? `🎭 ${k.nazev}` : k.nazev),
          h("td", { class: "cislo" }, hodnotaText(k.hodnota))))),
      v.poznamky.map((p) => h("p", { class: "poznamka" }, p)),
      soucty.length
        ? h("p", { class: "poznamka" }, "Součty: " + soucty.map(([i, s]) => `${jmeno(i)} ${hodnotaText(s)}`).join(", "))
        : null,
      h("p", { class: "vitez" }, v.vitez === null ? "Nikdo nevyhrál." : `🏆 ${jmeno(v.vitez)}`));
  });

  const hlavicka = [];
  if (hra.faze === "vyhodnoceni") {
    const potvrdil = hra.potvrdili.includes(hra.ja);
    const cekame = hra.hraci.map((_, i) => i).filter((i) => !hra.potvrdili.includes(i)).map(jmeno);
    hlavicka.push(h("div", { class: "panel hlavicka-vysledku" },
      h("h2", null, `Výsledky ${hra.kolo + 1}. kola`),
      h("div", { class: "radek-tlacitek" },
        h("button", {
          class: "tlacitko hlavni", disabled: potvrdil ? true : null,
          onclick: () => posli({ akce: "pokracovat" }),
        }, potvrdil ? "Čekám na ostatní…" : "Pokračovat do dalšího kola"),
        mistnost.zakladatel && cekame.length
          ? h("button", { class: "tlacitko", onclick: () => posli({ akce: "pokracovat", za_vsechny: true }) },
              "Pokračovat za všechny")
          : null),
      cekame.length ? h("p", { class: "napoveda" }, `Čeká se na: ${cekame.join(", ")}`) : null));
  } else {
    hlavicka.push(h("div", { class: "panel hlavicka-vysledku" }, h("h2", null, "Výsledky posledního kola")));
  }
  panel.replaceChildren(...hlavicka, ...karty);
}

function vykresliHrace(hra) {
  const pripojeni = mistnost.hraci;
  $("#hraci").replaceChildren(...hra.hraci.map((hrac, i) =>
    h("li", { class: hra.faze === "tah" && hra.na_tahu === i ? "na-tahu" : null },
      h("span", { class: "barva", style: `background:${barvaHrace(i)}` }),
      h("div", { class: "roztahni" },
        h("div", null, hrac.jmeno, i === hra.ja ? " (ty)" : ""),
        h("div", { class: "cilove-mini" },
          hrac.cilove_karty.map((k) => h("span", { title: k.kategorie }, `${k.kategorie} ${k.hodnota}`)))),
      h("span", { class: "skore", title: "body za cílové karty" }, hrac.skore),
      h("span", {
        class: "pripojeni" + (pripojeni[i] && pripojeni[i].pripojen ? " ano" : ""),
        title: pripojeni[i] && pripojeni[i].pripojen ? "připojen(a)" : "nepřipojen(a)",
      }))));
}

// ----------------------------------------------------------- dialogy

function vykresliKatalog() {
  $("#seznam-karet").replaceChildren(...Object.entries(katalog.karty).map(([nazev, info]) =>
    h("div", { class: "karta-info" },
      karta(nazev, 3),
      h("div", null, h("b", null, nazev), h("small", null, `hodnota ${hodnotaText(info.hodnota)}`),
        h("div", null, info.popis)))));
}

for (const tlacitko of document.querySelectorAll("[data-otevri]")) {
  tlacitko.addEventListener("click", () => $("#" + tlacitko.dataset.otevri).showModal());
}

$("#otevri-sal").addEventListener("click", async () => {
  const obsah = $("#sal-obsah");
  obsah.replaceChildren(h("p", null, "Načítám…"));
  $("#sal").showModal();
  try {
    const hry = await api("/api/sal-slavy");
    if (!hry.length) {
      obsah.replaceChildren(h("p", null, "Zatím se nedohrála žádná hra."));
      return;
    }
    const vitezstvi = {};
    for (const hra of hry) {
      const nejvic = hra.poradi[0].body;
      for (const p of hra.poradi) if (p.body === nejvic) vitezstvi[p.jmeno] = (vitezstvi[p.jmeno] || 0) + 1;
    }
    obsah.replaceChildren(
      h("h3", null, "Počet vítězství"),
      h("ol", { class: "poradi" }, Object.entries(vitezstvi).sort((a, b) => b[1] - a[1])
        .map(([jmeno, pocet]) => h("li", null, h("b", null, jmeno), ` – ${pocet}×`))),
      h("h3", null, "Odehrané hry"),
      h("ul", { class: "seznam" }, hry.slice().reverse().map((hra) =>
        h("li", null, h("span", { class: "roztahni" },
          h("small", null, hra.datum), h("br"),
          hra.poradi.map((p) => `${p.jmeno} ${p.body}`).join(" · "))))));
  } catch (chyba) {
    obsah.replaceChildren(h("p", { class: "chyba" }, chyba.message));
  }
});

// zavreni dialogu kliknutim mimo nej
for (const dialog of document.querySelectorAll("dialog")) {
  dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
}

// ------------------------------------------------------------------ start

window.addEventListener("hashchange", smeruj);

(async function start() {
  try {
    katalog = await api("/api/katalog");
    for (const [kategorie, info] of Object.entries(katalog.kategorie)) specialiste[info.specialista] = kategorie;
  } catch {
    document.body.textContent = "Server neodpovídá. Zkus stránku načíst znovu.";
    return;
  }
  vykresliKatalog();
  smeruj();
})();
