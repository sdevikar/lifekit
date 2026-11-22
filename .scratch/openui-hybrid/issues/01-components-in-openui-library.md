Type: grilling
Status: resolved

## Question

Which components belong in the OpenUI library for the chat surface, beyond the built-in `openuiChatLibrary`? And how do they map to LifeKit's existing design tokens and coach reply shapes (cards, key terms, lists of steps)?

## Blocked by

(none)

## Answer

**Minimal custom library.** The chat slice uses a small custom library
(`frontend/src/lib/openui.tsx`: Card root + TextContent) instead of the built-in
`openuiChatLibrary`, whose 53k-char prompt (105 components) starves context on
local models. Coach replies are prose; LifeKit-specific widgets arrive with the
exercise surfaces via `library.extend`.

**OpenUI replaces the bubble.** The existing card bubble (`max-w-[85%]`, bg-lk-card, border, font-serif) is replaced by OpenUI's Card. OpenUI owns the visual container; no custom wrapper. This principle applies to every similar decision in this effort.

**Emphasis via OpenUI.** Bold key terms use OpenUI's text emphasis props, not inline markdown. One rendering path, no markdown parser in the chat.

**User messages stay plain text.** Typed prose is never generated; only coach replies render OpenUI Lang.

Unblocks tickets 02 and 03.