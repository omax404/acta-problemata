// Acta Problemata — request relay (Cloudflare Worker, free tier).
// Form -> validate -> abuse controls -> GitHub repository_dispatch -> workflow builds + emails the PDF.
//
// Bindings / secrets (see wrangler.toml + README.md):
//   GH_TOKEN         secret  fine-grained PAT, only this repo, permission "Contents: write" (for dispatches)
//   TURNSTILE_SECRET secret  optional: Cloudflare Turnstile secret; if unset the check is skipped
//   RL               KV      optional: rate-limit store; if unbound only the per-request checks run
//   REPO, ALLOW_ORIGIN  vars
const EMAIL = /^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,}$/;
const DOMAINS = ["", "Mechanical", "Thermodynamics", "Fluids", "Materials", "Electrical", "Civil"];
const LIMITS = { email: 3, ip: 10, global: 150 };            // per UTC day
const PRIVATE = /^(localhost|.*\.local|.*\.internal|\[?::1\]?|0\.0\.0\.0|127\..*|10\..*|192\.168\..*|169\.254\..*|172\.(1[6-9]|2\d|3[01])\..*)$/i;

const json = (obj, status, cors) =>
  new Response(JSON.stringify(obj), { status, headers: { ...cors, "content-type": "application/json" } });

async function sha(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].slice(0, 12).map((x) => x.toString(16).padStart(2, "0")).join("");
}

// Returns true when the key is still under its daily limit (and counts this hit).
async function under(env, key, limit) {
  if (!env.RL) return true;
  const day = new Date().toISOString().slice(0, 10);
  const k = `${day}:${key}`;
  const n = parseInt((await env.RL.get(k)) || "0", 10);
  if (n >= limit) return false;
  await env.RL.put(k, String(n + 1), { expirationTtl: 90000 });
  return true;
}

async function turnstile(env, token, ip) {
  if (!env.TURNSTILE_SECRET) return true;
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    body: new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token || "", remoteip: ip }),
  });
  return (await r.json()).success === true;
}

export default {
  async fetch(req, env) {
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type",
      Vary: "Origin",
    };
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (req.method !== "POST") return json({ error: "POST only" }, 405, cors);
    if (env.ALLOW_ORIGIN && req.headers.get("Origin") !== env.ALLOW_ORIGIN)
      return json({ error: "origin not allowed" }, 403, cors);

    let b;
    try { b = await req.json(); } catch { return json({ error: "bad json" }, 400, cors); }
    const email = String(b.email || "").trim();
    const domain = String(b.domain || "");
    const reqType = b.type === "solution" ? "acta-solution" : "acta-request";
    let url = null;
    if (b.type !== "solution") {
      try { url = new URL(String(b.url || "").trim()); } catch { return json({ error: "invalid link" }, 400, cors); }
      if (!/^https?:$/.test(url.protocol) || url.username || url.password || PRIVATE.test(url.hostname))
        return json({ error: "the link must be a public http(s) page" }, 400, cors);
      if (url.href.length > 500 || !DOMAINS.includes(domain)) return json({ error: "invalid request" }, 400, cors);
    } else {
      if (!b.problem || typeof b.problem !== "string") return json({ error: "missing problem slug" }, 400, cors);
    }
    if (!EMAIL.test(email)) return json({ error: "invalid email" }, 400, cors);

    const ip = req.headers.get("CF-Connecting-IP") || "0.0.0.0";
    if (!(await turnstile(env, b.turnstile, ip))) return json({ error: "captcha failed" }, 403, cors);
    const [okE, okI, okG] = [
      await under(env, "e:" + (await sha(email.toLowerCase())), LIMITS.email),
      await under(env, "i:" + (await sha(ip)), LIMITS.ip),
      await under(env, "g", LIMITS.global),
    ];
    if (!(okE && okI && okG)) return json({ error: "daily limit reached, try again tomorrow" }, 429, cors);

    const payload = b.type === "solution"
      ? { problem: b.problem, email, name: b.name || "", solution: b.solution || {} }
      : { url: url.href, email, domain };

    const r = await fetch(`https://api.github.com/repos/${env.REPO}/dispatches`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.GH_TOKEN}`, "User-Agent": "acta-relay", Accept: "application/vnd.github+json" },
      body: JSON.stringify({ event_type: reqType, client_payload: payload }),
    });
    return r.status === 204 ? json({ ok: true }, 202, cors) : json({ error: "upstream error" }, 502, cors);
  },
};