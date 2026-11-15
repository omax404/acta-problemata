// Cloudflare Worker (free tier): receives the form, validates, triggers the GitHub workflow.
// Secrets: GH_TOKEN (fine-grained PAT, repo omax404/acta-problemata, "Contents: read/write" for dispatch)
// Vars: ALLOW_ORIGIN (your Pages origin), REPO = "omax404/acta-problemata"
const EMAIL = /^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,}$/;
export default {
  async fetch(req, env) {
    const cors = { "Access-Control-Allow-Origin": env.ALLOW_ORIGIN, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "content-type" };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    if (req.method !== "POST") return new Response("POST only", { status: 405, headers: cors });
    let b; try { b = await req.json(); } catch { return new Response("bad json", { status: 400, headers: cors }); }
    let ok = EMAIL.test(b.email || "");
    try { const u = new URL(b.url); ok = ok && /^https?:$/.test(u.protocol); } catch { ok = false; }
    if (!ok) return new Response("invalid link or email", { status: 400, headers: cors });
    const r = await fetch(`https://api.github.com/repos/${env.REPO}/dispatches`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.GH_TOKEN}`, "User-Agent": "acta-worker", Accept: "application/vnd.github+json" },
      body: JSON.stringify({ event_type: "acta-request", client_payload: { url: b.url, email: b.email, domain: b.domain || "" } }),
    });
    return new Response(r.status === 204 ? "queued" : "upstream error", { status: r.status === 204 ? 202 : 502, headers: cors });
  },
};