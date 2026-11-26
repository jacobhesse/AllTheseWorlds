# All These Worlds — static site

A static rebuild of alltheseworlds.us, moved off GoDaddy Managed WordPress. Every page keeps the same URL it had on WordPress.

```
public/               ← the website (this is what gets deployed)
  index.html          ← home page
  <slug>/index.html   ← one folder per page, e.g. public/about/index.html
  assets/theme.css    ← the WordPress theme's look (colours, fonts, layout) + your Additional CSS
  assets/site.css     ← small extras for generated pages (blog list)
  assets/fonts/       ← Manrope & Fira Code, self-hosted
  wp-content/uploads/ ← images & downloads (same paths as WordPress)
  _redirects          ← old/broken URLs → new ones (Cloudflare Pages format)
  sitemap.xml, robots.txt, 404.html
partials/header.html  ← the Stargazer nav bar (edit the menu HERE)
partials/footer.html  ← the site footer
tools/apply_partials.py   ← copies the header/footer into every page after you edit them
tools/import_theme.py     ← one-time: captured theme CSS/header/footer from WordPress (already run)
tools/import_wordpress.py ← one-time importer (already run; re-running overwrites pages)
wp-export/            ← raw JSON pulled from the WordPress API (backup of the content)
```

## Editing in VS Code

1. `code ~/alltheseworlds`
2. Install the recommended **Live Server** extension when VS Code prompts you.
3. Right-click `public/index.html` → **Open with Live Server**. The page reloads every time you save.
   (Or, without an extension: `python3 -m http.server 8000 -d public` and open http://localhost:8000.)

- **Edit a page:** open `public/<slug>/index.html`. Each page is a self-contained HTML file with its own `<style>`, the same HTML you pasted into WordPress.
- **Add a page:** copy an existing folder, rename it, and edit what's between the header and footer. Keep the `theme.css` link and the `<!-- site-header -->` / `<!-- site-footer -->` markers.
- **Change the menu or footer:** edit `partials/header.html` or `partials/footer.html`, then run `python3 tools/apply_partials.py` to update every page.
- **Add a blog post:** copy `public/stellar-classification/`, edit it, then add an entry to `public/blog/index.html`, `sitemap.xml` and `site-map/index.html`.
- Claude Code works well here: ask it things like "add a new Space page about pulsars styled like stellar-classes".

## Going live without GoDaddy

Recommended setup: **GitHub** (stores the code) → **Cloudflare Pages** (free hosting, deploys on every push) → **Cloudflare Registrar** (domain at cost, ~$10/yr). Do the steps **in this order** so the site and email never go down.

### 1. Put the code on GitHub
```bash
cd ~/alltheseworlds
git add -A && git commit -m "Static site migrated from WordPress"
gh repo create alltheseworlds --private --source=. --push
```

### 2. Host on Cloudflare Pages
Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick the repo.
- Framework preset: **None** · Build command: *(empty)* · Output directory: **`public`**

You get a preview URL (`alltheseworlds.pages.dev`). Click through the site there before going further.

### 3. Move DNS to Cloudflare (website switches over; email must keep working)
1. Cloudflare → **Add a domain** → `alltheseworlds.us` → Free plan. It scans and imports your GoDaddy DNS records.
2. **Compare against GoDaddy's DNS page** (GoDaddy → Domain → DNS) and make sure *every email record* came across exactly. Today these are:

   | Type | Name | Value |
   |---|---|---|
   | MX | @ | `alltheseworlds-us.mail.protection.outlook.com` (priority 0) |
   | TXT | @ | `v=spf1 include:secureserver.net -all` |
   | TXT | @ | `NETORGFT12253031.onmicrosoft.com` |
   | CNAME | autodiscover | `autodiscover.outlook.com` |
   | CNAME | lyncdiscover | `webdir.online.lync.com` |
   | CNAME | sip | `sipdir.online.lync.com` |
   | SRV | _sip._tls / _sipfederationtls._tcp | *(copy from GoDaddy if present)* |

   Set all of these to **DNS only (grey cloud)**, not proxied.
3. Delete the imported `A` record for `@` (GoDaddy's 160.153.0.45) and the `www` record. Then in **Pages → your project → Custom domains**, add `alltheseworlds.us` and `www.alltheseworlds.us`. Cloudflare creates the right records.
4. At GoDaddy: **Domain → Nameservers → Change → "I'll use my own"** → enter the two nameservers Cloudflare gives you.
5. Within a few hours: check that https://alltheseworlds.us loads from Cloudflare, and **send and receive a test email**.

### 4. Transfer the domain registration to Cloudflare
At GoDaddy: turn off **Domain lock**, then request the **authorization (EPP) code**. In Cloudflare → **Domain Registration → Transfer**, paste the code and pay (this adds a year). The transfer takes up to 5 days, and the site stays up throughout.

### 5. Email: the last GoDaddy dependency ⚠️
Your Microsoft 365 was bought **through GoDaddy** (that's what the `NETORGFT…` tenant and `secureserver.net` SPF mean). It keeps working after steps 1–4, but you're still paying GoDaddy for it. To leave GoDaddy completely, either:
- **Defederate** the tenant from GoDaddy and buy M365 directly from Microsoft (keeps the mailboxes; Microsoft-partner and migration tools such as a defederation service can do this), or
- Move to a new provider (Microsoft direct, Google Workspace, Fastmail…) and migrate mail.

After that, change SPF to `v=spf1 include:spf.protection.outlook.com -all` (for M365 direct) and set up DKIM and DMARC.

### 6. Cancel GoDaddy hosting
Only after the site has run from Cloudflare for a week or so: export a full WordPress backup (WP Admin → Tools → Export, plus the `wp-export/` folder here), then cancel the Managed WordPress plan.

## Things changed vs. the WordPress site
- WooCommerce shop/cart/checkout removed (it had one free product). `/shop/` and `/product/*` redirect to `/hipaa-kit/`.
- Empty or test pages dropped: change-readiness, security, cybersecurity, project-management-2, test-page, navigation-test-page.
- Same Stargazer nav, theme, fonts and footer as WordPress. Menu changes: "Guides & Resources" (was a 404) and "Change Readiness" (empty page) removed; "Digital Transformation" and "Marketplace" now link to real pages.
- Footer: dead "FAQs" / "Events" links removed, "Terms" and "Site Map" added, "Designed with WordPress" replaced with a copyright line.
- Previously broken links (`/site-map.html`, `/contact/`, `/virtual-ciso/`, `/iso-27001-2022/`…) now work: there are new Site Map and Contact pages, plus redirects.
- **Still needs your attention:** two forms have placeholder targets on the old site too:
  `public/fractional-ciso/index.html` (`action="#"`) and `public/digital-transformation/index.html` (`formspree.io/f/your-id`). Point them at real Formspree form IDs.
- Privacy policy is branded "Stargazer Consulting", while the rest of the site is "All These Worlds". Worth a look.
