/*
 * Shared site header + footer for All These Worlds.
 * Edit MENU / FOOTER_LINKS below to change navigation on every page at once.
 * Uses Shadow DOM so these styles never clash with each page's own CSS.
 */
const SITE_NAME = "All These Worlds";

const MENU = [
  { label: "Home", href: "/" },
  { label: "Project Management", href: "/project-management-3/", children: [
    { label: "Phases of Project Management", href: "/phases-of-project-management/" },
    { label: "AI in Project Management", href: "/ai-in-project-management/" },
    { label: "Modern Trends in PM", href: "/modern-trends-in-project-management/" },
    { label: "Project Management Services", href: "/project-management/" },
    { label: "PM Formulas", href: "/project-management-formulas/" },
  ]},
  { label: "Space", href: "/space/", children: [
    { label: "Spaceflight", href: "/spaceflight/" },
    { label: "50 Nearest Stars", href: "/the-nearest-50-stars/" },
    { label: "Habitable Zones", href: "/habitable-zone-calculator/" },
    { label: "Lets Go to Mars", href: "/lets-go-to-mars/" },
    { label: "Stellar Classifications", href: "/stellar-classes/" },
    { label: "Solar Wind", href: "/solar-wind/" },
    { label: "Space Engines", href: "/space-engines/" },
    { label: "Layers of the Sun", href: "/layers-of-the-sun/" },
    { label: "Terraforming Venus", href: "/terraforming-venus/" },
  ]},
  { label: "Compliance & Infosec", href: "/compliance/", children: [
    { label: "AI Governance", href: "/ai-governance/" },
    { label: "Throughline Starter", href: "/839-2/" },
    { label: "Throughline Assessment", href: "/842-2/" },
    { label: "Email Retention", href: "/how-long-will-they-keep-my-emails/" },
    { label: "Cyber Roles and AI", href: "/cybersecurity-roles-and-ai/" },
  ]},
  { label: "Digital Transformation", href: "/digital-transformation/", children: [
    { label: "When DT Fails", href: "/when-dt-fails/" },
    { label: "Cultural Misalignment", href: "/good-leadership-is-not-universally-interpreted/" },
  ]},
  { label: "Courses", href: "/courses/", children: [
    { label: "Intro to Business", href: "/introduction-to-business-management/" },
    { label: "Intro to Operations", href: "/intro-to-operations-management/" },
    { label: "Calculus I", href: "/calculus-i/" },
    { label: "Thermodynamics", href: "/thermodynamics/" },
    { label: "Intro to Flight", href: "/flight/" },
  ]},
  { label: "Marketplace", href: "/846-2/", children: [
    { label: "Solar Slider App", href: "/846-2/" },
  ]},
];

const FOOTER_LINKS = [
  { label: "Blog", href: "/blog/" },
  { label: "About", href: "/about/" },
  { label: "Privacy Policy", href: "/privacy/" },
  { label: "Terms", href: "/terms/" },
];

const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const here = location.pathname.replace(/index\.html$/, "");

const SHARED_CSS = `
  :host { all: initial; display: block; font-family: Manrope, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.4; }
  * { box-sizing: border-box; }
  a { color: inherit; text-decoration: none; }
  .inner { max-width: 1200px; margin: 0 auto; padding: 0 16px; }
`;

class AtwHeader extends HTMLElement {
  connectedCallback() {
    const root = this.attachShadow({ mode: "open" });
    const items = MENU.map((m, i) => {
      const active = (m.href === "/" ? here === "/" : here.startsWith(m.href)) ? " active" : "";
      if (!m.children) return `<li><a class="top${active}" href="${m.href}">${esc(m.label)}</a></li>`;
      return `<li class="has-sub">
        <div class="row"><a class="top${active}" href="${m.href}">${esc(m.label)}</a>
          <button class="caret" aria-expanded="false" aria-controls="sub${i}" aria-label="Show ${esc(m.label)} pages">▾</button></div>
        <ul class="sub" id="sub${i}">${m.children.map((c) => `<li><a href="${c.href}">${esc(c.label)}</a></li>`).join("")}</ul>
      </li>`;
    }).join("");

    root.innerHTML = `<style>${SHARED_CSS}
      header { background: #0b1220; color: #e8edf7; border-bottom: 1px solid rgba(255,255,255,.12); position: relative; z-index: 1000; }
      .bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 60px; }
      .brand { font-weight: 800; font-size: 17px; letter-spacing: .2px; white-space: nowrap; }
      .menu-btn { display: none; background: none; border: 1px solid rgba(255,255,255,.25); color: inherit; border-radius: 8px; padding: 6px 10px; font: inherit; cursor: pointer; }
      nav > ul { list-style: none; margin: 0; padding: 0; display: flex; gap: 2px; flex-wrap: wrap; }
      li { position: relative; list-style: none; }
      .row { display: flex; align-items: center; }
      a.top { display: block; padding: 8px 10px; border-radius: 8px; color: #c9d3e6; }
      a.top:hover, a.top.active { color: #fff; background: rgba(255,255,255,.08); }
      .caret { background: none; border: 0; color: #8fa0bf; cursor: pointer; padding: 8px 4px; margin-left: -6px; font-size: 12px; }
      .sub { display: none; position: absolute; top: 100%; left: 0; min-width: 240px; margin: 0; padding: 6px; background: #121b2e; border: 1px solid rgba(255,255,255,.14); border-radius: 10px; box-shadow: 0 12px 30px rgba(0,0,0,.4); }
      .sub a { display: block; padding: 8px 10px; border-radius: 6px; color: #c9d3e6; }
      .sub a:hover { background: rgba(255,255,255,.08); color: #fff; }
      .has-sub:hover > .sub, .has-sub:focus-within > .sub, .has-sub.open > .sub { display: block; }
      a:focus-visible, button:focus-visible { outline: 2px solid #7dd3fc; outline-offset: 2px; }
      @media (max-width: 960px) {
        .menu-btn { display: block; }
        nav { display: none; width: 100%; padding-bottom: 12px; }
        nav.open { display: block; }
        .bar { flex-wrap: wrap; }
        nav > ul { flex-direction: column; }
        .row { justify-content: space-between; }
        .caret { padding: 8px 12px; font-size: 14px; }
        .sub { position: static; box-shadow: none; border: 0; background: transparent; padding: 0 0 0 14px; }
        .has-sub:hover > .sub, .has-sub:focus-within > .sub { display: none; }
        .has-sub.open > .sub { display: block; }
      }
    </style>
    <header><div class="inner bar">
      <a class="brand" href="/">${esc(SITE_NAME)}</a>
      <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
      <nav id="nav" aria-label="Main"><ul>${items}</ul></nav>
    </div></header>`;

    const nav = root.getElementById("nav");
    const menuBtn = root.querySelector(".menu-btn");
    menuBtn.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open);
    });
    root.querySelectorAll(".caret").forEach((b) => b.addEventListener("click", () => {
      const li = b.closest("li");
      const open = li.classList.toggle("open");
      b.setAttribute("aria-expanded", open);
    }));
  }
}

class AtwFooter extends HTMLElement {
  connectedCallback() {
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `<style>${SHARED_CSS}
      footer { background: #0b1220; color: #8fa0bf; border-top: 1px solid rgba(255,255,255,.12); padding: 28px 0; margin-top: 48px; }
      .f { display: flex; flex-wrap: wrap; gap: 12px 24px; align-items: center; justify-content: space-between; }
      ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 18px; }
      a:hover { color: #fff; }
    </style>
    <footer><div class="inner f">
      <ul>${FOOTER_LINKS.map((l) => `<li><a href="${l.href}">${esc(l.label)}</a></li>`).join("")}</ul>
      <div>© ${new Date().getFullYear()} ${esc(SITE_NAME)}. All rights reserved.</div>
    </div></footer>`;
  }
}

customElements.define("atw-header", AtwHeader);
customElements.define("atw-footer", AtwFooter);
