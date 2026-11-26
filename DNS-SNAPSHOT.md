# DNS records at GoDaddy before the move (captured 2026-11-25)

Nameservers: `ns73.domaincontrol.com`, `ns74.domaincontrol.com` · DNSSEC: off

| Type | Name | Value | In Cloudflare |
|---|---|---|---|
| A | @ | 160.153.0.45 | **Delete** (old GoDaddy website) → replaced by Pages custom domain |
| CNAME | www | alltheseworlds.us | **Delete** → replaced by Pages custom domain |
| MX | @ | alltheseworlds-us.mail.protection.outlook.com (priority 0) | Keep (email) |
| TXT | @ | NETORGFT12253031.onmicrosoft.com | Keep (M365 domain verification) |
| TXT | @ | v=spf1 include:secureserver.net -all | Keep exactly (email sending) |
| CNAME | autodiscover | autodiscover.outlook.com | Keep, DNS only (Outlook setup) |
| CNAME | msoid | clientconfig.microsoftonline-p.net | Keep, DNS only (M365 sign-in) |
| CNAME | lyncdiscover | webdir.online.lync.com | Keep, DNS only |
| CNAME | sip | sipdir.online.lync.com | Keep, DNS only |
| SRV | _sip._tls | 100 1 443 sipdir.online.lync.com | Keep |
| SRV | _sipfederationtls._tcp | 100 1 5061 sipfed.online.lync.com | Keep |
| CNAME | email | email.secureserver.net | Keep, DNS only (GoDaddy webmail shortcut) |
| CNAME | _domainconnect | _domainconnect.gd.domaincontrol.com | Optional: GoDaddy-only, safe to delete |

Records found by querying common names. GoDaddy's DNS page is the authoritative list;
compare against it too in case there's something here that couldn't be discovered.
