// node --test extras/worker/worker.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import worker from "./worker.js";

const kv = () => { const m = new Map(); return { get: async (k) => m.get(k) ?? null, put: async (k, v) => void m.set(k, v) }; };
const mk = (body, env = {}, ip = "1.2.3.4") =>
  worker.fetch(new Request("https://r.example/", { method: "POST", headers: { Origin: "https://o.example", "CF-Connecting-IP": ip }, body: JSON.stringify(body) }),
    { ALLOW_ORIGIN: "https://o.example", REPO: "o/r", GH_TOKEN: "t", ...env });
const ok = { url: "https://example.org/p", email: "a@b.co" };
let calls = 0;
globalThis.fetch = async () => { calls++; return new Response(null, { status: 204 }); };

test("valid request is dispatched", async () => { const r = await mk(ok); assert.equal(r.status, 202); assert.equal(calls, 1); });
test("bad email / private url / odd domain refused before dispatch", async () => {
  const before = calls;
  for (const b of [{ ...ok, email: "x" }, { ...ok, url: "http://127.0.0.1/x" }, { ...ok, url: "http://10.1.1.1/" },
                   { ...ok, url: "https://u:p@example.org/" }, { ...ok, url: "ftp://example.org" }, { ...ok, domain: "Hacking" }])
    assert.equal((await mk(b)).status, 400);
  assert.equal(calls, before);
});
test("wrong origin refused", async () => {
  const r = await worker.fetch(new Request("https://r.example/", { method: "POST", headers: { Origin: "https://evil.example" }, body: "{}" }), { ALLOW_ORIGIN: "https://o.example" });
  assert.equal(r.status, 403);
});
test("per-email limit is 3 per day", async () => {
  const RL = kv();
  const s = [];
  for (let i = 0; i < 4; i++) s.push((await mk(ok, { RL }, `9.9.9.${i}`)).status);
  assert.deepEqual(s, [202, 202, 202, 429]);
});
test("per-IP limit is 10 per day", async () => {
  const RL = kv();
  const s = [];
  for (let i = 0; i < 11; i++) s.push((await mk({ ...ok, email: `u${i}@b.co` }, { RL }, "7.7.7.7")).status);
  assert.equal(s.filter((x) => x === 202).length, 10);
  assert.equal(s[10], 429);
});
test("turnstile failure blocks", async () => {
  const f = globalThis.fetch;
  globalThis.fetch = async (u) => (String(u).includes("turnstile") ? new Response(JSON.stringify({ success: false })) : f(u));
  assert.equal((await mk(ok, { TURNSTILE_SECRET: "s" })).status, 403);
  globalThis.fetch = f;
});