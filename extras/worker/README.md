# Request relay (Cloudflare Worker)

Free tier is enough. About 10 minutes, once.

1. `cd extras/worker && npx wrangler login`
2. (optional) rate limits: `npx wrangler kv namespace create RL`, then un-comment the `[[kv_namespaces]]` block in `wrangler.toml` and paste the id.
3. Secrets: `npx wrangler secret put GH_TOKEN` (fine-grained token, only this repo, "Contents: Read and write"). Optional: `npx wrangler secret put TURNSTILE_SECRET`.
4. `npx wrangler deploy` -> note the `https://acta-relay.<you>.workers.dev` URL.
5. Put that URL into `docs/request.html` (`WORKER`). If you use Turnstile, add the widget and send its token as `turnstile`.
6. Set `ALLOW_ORIGIN` in `wrangler.toml` to the origin that serves `request.html`.

Limits per UTC day: 3 per email, 10 per IP, 150 global (edit `LIMITS`). Private/loopback links, credentials in URLs and unknown domains are refused before anything is dispatched.