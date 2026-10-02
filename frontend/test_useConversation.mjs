// Check for the "Talk about this" crash: useConversation must not hit the
// /api/conversations/ *collection* endpoint before the route id resolves —
// that endpoint returns a JSON array, so resp.messages is undefined and
// MessageList throws on `messages.length`.
//
// Also checks the pending-feedback invariant: a failed POST must leave no
// orphan user message. The server replies before it persists, so if the
// request throws nothing was stored and the transcript must match.
//
// Run: node --experimental-strip-types test_useConversation.mjs
//   (needs `lifekit ui` running, which proxies the feed API)
//
// This file drives a hook directly against a React stub, so the calls below
// are intentionally top-level and not inside a component.
/* eslint-disable react-hooks/rules-of-hooks */
import assert from "node:assert";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const BASE = process.env.LIFEKIT_UI ?? "http://127.0.0.1:3783";
const requests = [];

// Minimal React stub: record state writes and effects so we can drive the
// real hook and inspect what it fetched. `apply` runs a queued updater
// against a prior value, which is what the optimistic append/rollback needs.
let state = [];
let effects = [];
const React = {
  useState: (init) => [init, (v) => (state.push(v), v)],
  useCallback: (fn) => fn,
  useEffect: (fn) => effects.push(fn),
};
const apiGet = async (url) => {
  requests.push(url);
  return fetch(BASE + url).then((r) => r.json());
};
// Rewritten per test; defaults to a well-formed reply.
let postImpl = async () => ({ reply: "ok" });

const dir = mkdtempSync(join(tmpdir(), "lk-hook-"));
// Dereferences __React at call time, not import time — cases 3 and 4 swap in
// a stateful stub after the module is already loaded.
writeFileSync(
  join(dir, "react.mjs"),
  "export const useState=(...a)=>globalThis.__React.useState(...a);\nexport const useCallback=(...a)=>globalThis.__React.useCallback(...a);\nexport const useEffect=(...a)=>globalThis.__React.useEffect(...a);\n",
);
writeFileSync(
  join(dir, "api.mjs"),
  "export const apiGet=(...a)=>globalThis.__apiGet(...a);\nexport const apiPost=(...a)=>globalThis.__apiPost(...a);\n",
);

const src = readFileSync("src/hooks/useConversation.ts", "utf8")
  // Park the react import behind a marker: the api pattern below is lazy and
  // would otherwise match starting at this import and swallow it.
  .replace(/^import .*from ["']react["'];$/m, "/*__REACT__*/")
  .replace(/import \{[\s\S]*?\} from ["']@\/types\/api["'];/, 'import { apiGet, apiPost } from "./api.mjs";')
  .replace("/*__REACT__*/", 'import { useCallback, useEffect, useState } from "./react.mjs";');

const mod = join(dir, "useConversation.ts");
writeFileSync(mod, src);

globalThis.__React = React;
globalThis.__apiGet = apiGet;
globalThis.__apiPost = (...a) => postImpl(...a);

const { useConversation } = await import(pathToFileURL(mod).href);

// --- 1. convId "" (route params not yet resolved) must not fetch at all
state = [];
effects = [];
useConversation("");
for (const e of effects) e();
await new Promise((r) => setTimeout(r, 200));
assert.deepEqual(requests, [], "empty convId must not issue a request");

// --- 2. real convId must fetch and expose a usable messages array
state = [];
effects = [];
requests.length = 0;
useConversation("9c2b68edc7b9");
for (const e of effects) e();
await new Promise((r) => setTimeout(r, 500));

assert.deepEqual(requests, ["/api/conversations/9c2b68edc7b9"]);
const messages = state.find((v) => Array.isArray(v));
assert.ok(messages, `messages must be set to an array, got state=${JSON.stringify(state)}`);
assert.doesNotThrow(() => messages.length); // the line that used to throw

console.log("ok - useConversation guards the empty id and returns a messages array");

// --- 3. optimistic append: the user message lands before the reply does
// --- 4. rollback: a rejected POST must leave no orphan user message
//
// Both need the hook's `setMessages(prev => ...)` chain observable, which the
// recording stub above cannot do (it discards the prior value). This stub
// keeps real per-slot state instead. `messages` is the hook's second useState.
const prior = [{ role: "coach", text: "prior", created_at: "2026-10-01T00:00:00Z" }];
const useStore = () => {
  const slots = [];
  let n = 0;
  globalThis.__React = {
    useState: (init) => {
      const i = n++;
      slots[i] = typeof init === "function" ? init() : init;
      return [
        slots[i],
        (v) => {
          slots[i] = typeof v === "function" ? v(slots[i]) : v;
        },
      ];
    },
    useCallback: (fn) => fn,
    useEffect: () => {},
  };
  return {
    // The hook's slot 1 is `messages`. Seeded after construction, standing in
    // for the load() that a real render would have run with prior messages.
    read: () => slots[1],
    seed: (v) => {
      slots[1] = v;
    },
  };
};

// 3. The reply is held on a deferred promise to model a slow local model.
{
  const store = useStore();
  let release;
  postImpl = () => new Promise((r) => (release = () => r({ reply: "the answer" })));

  const hook = useConversation("9c2b68edc7b9");
  store.seed(prior);
  const settled = hook.sendMessage("why does this matter?").catch(() => undefined);

  // Everything up to the first await has already run, so the user message is
  // there while the POST is still in flight.
  let messages = store.read();
  assert.equal(
    messages.length,
    2,
    `user message must appear before the reply, got ${JSON.stringify(messages)}`,
  );
  assert.equal(messages[1].role, "user");
  assert.equal(messages[1].text, "why does this matter?");

  release();
  await settled;
  messages = store.read();
  assert.equal(
    messages.length,
    3,
    `coach reply must be appended, got ${JSON.stringify(messages)}`,
  );
  assert.equal(messages[2].text, "the answer");

  console.log("ok - sendMessage appends the user message before the reply arrives");
}

// 4. A provider 502 is the real failure mode. The server replies before it
//    persists, so a throw means nothing was stored and the optimistic message
//    must come back off the transcript.
{
  const store = useStore();
  postImpl = async () => {
    throw new Error("HTTP 502");
  };

  const hook = useConversation("9c2b68edc7b9");
  store.seed(prior);
  await hook.sendMessage("this one fails").catch(() => undefined);

  assert.deepEqual(
    store.read(),
    prior,
    "transcript must match the server after a failed send",
  );

  console.log("ok - a failed send rolls the optimistic user message back");
}

console.log("all useConversation checks passed");
