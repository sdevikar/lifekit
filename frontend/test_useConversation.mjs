// Check for the "Talk about this" crash: useConversation must not hit the
// /api/conversations/ *collection* endpoint before the route id resolves —
// that endpoint returns a JSON array, so resp.messages is undefined and
// MessageList throws on `messages.length`.
//
// Run: node --experimental-strip-types test_useConversation.mjs
//   (needs Next.js :3000 running, which proxies the feed API)
import assert from "node:assert";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const BASE = "http://127.0.0.1:3000";
const requests = [];

// Minimal React stub: record state writes and effects so we can drive the
// real hook and inspect what it fetched.
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

const dir = mkdtempSync(join(tmpdir(), "lk-hook-"));
writeFileSync(join(dir, "react.mjs"), "export const R = globalThis.__React;\nexport const useState=(...a)=>R.useState(...a);\nexport const useCallback=(...a)=>R.useCallback(...a);\nexport const useEffect=(...a)=>R.useEffect(...a);\n");
writeFileSync(join(dir, "api.mjs"), "export const apiGet=(...a)=>globalThis.__apiGet(...a);\nexport const apiPost=async()=>({ok:true});\n");

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
