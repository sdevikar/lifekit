# LifeKit frontend

The LifeKit web app: Next.js 16 (App Router) and Tailwind. It talks to the
feed API on `127.0.0.1:8765` through the `/api/*` rewrites in `next.config.ts`.

- Run the whole app from the repo root with `lifekit ui`. It builds this app
  and serves it on `127.0.0.1:3783`, not `:3000` (see the root `AGENTS.md`).
- Check a change with `npx next build` and `npx eslint src`.
- Read `AGENTS.md` in this folder before you write code: Next.js 16 differs
  from older versions.
- Read `../DESIGN.md` before any UI work.
