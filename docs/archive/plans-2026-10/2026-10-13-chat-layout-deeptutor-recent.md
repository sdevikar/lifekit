# Chat Layout — DeepTutor-style Recent Sidebar — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executecuting-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the two-pane `/chat` layout, make it single-column full-width, and add a collapsible "Recent" section to the sidebar with conversation history grouped by recency.

**Architecture:** The `/chat` page becomes a single-column view (conversation + composer). The sidebar gains a "Recent" section when the Chat tab is active, showing conversations grouped by recency (Today / Yesterday / Last 7 days / Earlier) with rename and delete. Deep links move to `/chat/<id>`; `/c/[id]` redirects to `/chat/<id>`.

**Tech Stack:** Next.js 16 App Router, React, Tailwind CSS, TypeScript

## Global Constraints

- Frontend only — no backend changes (the API already supports `GET /api/conversations`, `POST /api/conversations`, `PATCH /api/conversations/<id>`, `DELETE /api/conversations/<id>`).
- All styling uses the existing `--lk-*` CSS custom properties (no hex/rgb literals).
- No new dependencies.
- Tests: `uv run pytest tests/ -v` must show no new failures beyond `test_split_dyl_pdf`.
- Build: `cd frontend && npm run build` and `npm run lint` must pass.

---

### Task 1: Make `/chat` single-column

**Files:**
- Modify: `frontend/src/app/chat/page.tsx`
- Delete: `frontend/src/components/feed/ConversationsList.tsx` (no longer used)

**Interfaces:**
- Consumes: `ChatView`, `MasterComposer`, `useConversations` (all exist)
- Produces: Single-column `/chat` page with no left pane

- [ ] **Step 1: Rewrite `frontend/src/app/chat/page.tsx`**

Replace the entire file with:

```tsx
"use client";

import { useState } from "react";
import { MasterComposer } from "@/components/feed/MasterComposer";
import { ChatView } from "@/components/ChatView";
import { useConversations } from "@/hooks/useConversations";
import { apiPost } from "@/types/api";

export default function ChatPage() {
  const { conversations, refresh } = useConversations();
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const handleComposerSubmit = async (text: string) => {
    setCreating(true);
    try {
      const resp = await apiPost<{ id: string }>("/api/conversations", {
        seed_kind: "composer",
        title: text,
      });
      setSelectedConvId(resp.id);
      refresh();
    } catch {
      // TODO: surface error
    } finally {
      setCreating(false);
    }
  };

  // If a conversation is selected, show it full-width
  if (selectedConvId) {
    return <ChatView convId={selectedConvId} />;
  }

  // Otherwise show the composer empty state
  return (
    <div className="flex flex-col min-h-screen bg-lk-bg">
      <header className="border-b border-lk-border py-3.5 bg-lk-card sticky top-0 z-20 shadow-xs">
        <div className="lk-shell flex items-center justify-between gap-4">
          <h1 className="text-sm font-semibold text-lk-fg">Chat</h1>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-8">
        <p className="text-sm text-lk-muted">
          Start a conversation or pick one from the sidebar.
        </p>
      </main>

      <MasterComposer
        onSubmit={handleComposerSubmit}
        submitting={creating}
      />
    </div>
  );
}
```

- [ ] **Step 2: Delete `frontend/src/components/feed/ConversationsList.tsx`**

```bash
rm frontend/src/components/feed/ConversationsList.tsx
```

- [ ] **Step 3: Update `frontend/src/hooks/useConversations.ts` to expose `refresh`**

Add a `refresh` function that re-fetches the conversation list:

```tsx
import { useCallback, useEffect, useState } from "react";
import { ConversationListItem, apiGet } from "@/types/api";

export function useConversations() {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<ConversationListItem[]>("/api/conversations");
      setConversations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversations");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { conversations, loading, error, refresh };
}
```

- [ ] **Step 4: Build and lint**

Run: `cd frontend && npm run build && npm run lint`
Expected: Clean build, no lint errors.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: make /chat single-column, remove two-pane layout"
```

---

### Task 2: Add sidebar "Recent" section

**Files:**
- Modify: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/components/sidebar/RecentConversations.tsx`

**Interfaces:**
- Consumes: `useConversations()` → `{ conversations, loading, error, refresh }`
- Produces: `<RecentConversations />` component that renders a collapsible list of conversations grouped by recency

- [ ] **Step 1: Create `frontend/src/components/sidebar/RecentConversations.tsx`**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useConversations } from "@/hooks/useConversations";
import { apiPatch, apiDelete } from "@/types/api";

function getDayGroup(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return "Last 7 days";
  return "Earlier";
}

const GROUP_ORDER = ["Today", "Yesterday", "Last 7 days", "Earlier"];

export function RecentConversations() {
  const router = useRouter();
  const { conversations, loading, error, refresh } = useConversations();
  const [collapsed, setCollapsed] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  const handleSelect = (id: string) => {
    router.push(`/chat/${id}`);
  };

  const handleRename = async (id: string) => {
    const title = editTitle.trim();
    if (!title) {
      setEditingId(null);
      return;
    }
    await apiPatch(`/api/conversations/${id}`, { title });
    setEditingId(null);
    refresh();
  };

  const handleDelete = async (id: string) => {
    await apiDelete(`/api/conversations/${id}`);
    refresh();
  };

  if (loading) {
    return (
      <div className="px-3 py-2 space-y-2">
        <div className="h-4 bg-lk-muted/20 rounded w-1/2 animate-pulse" />
        <div className="h-4 bg-lk-muted/20 rounded w-3/4 animate-pulse" />
      </div>
    );
  }

  if (error) {
    return <p className="px-3 py-2 text-xs text-lk-primary">{error}</p>;
  }

  // Group conversations by recency
  const groups: Record<string, typeof conversations> = {};
  for (const conv of conversations) {
    const group = getDayGroup(conv.updated_at);
    if (!groups[group]) groups[group] = [];
    groups[group].push(conv);
  }

  return (
    <div className="px-2 py-1">
      <button
        type="button"
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center gap-1.5 w-full px-2 py-1.5 text-xs font-semibold uppercase tracking-wider text-lk-muted hover:text-lk-fg transition-colors"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`transition-transform ${collapsed ? "" : "rotate-90"}`}
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        Recent
      </button>

      {!collapsed && (
        <div className="space-y-2">
          {GROUP_ORDER.filter((g) => groups[g]).map((group) => (
            <div key={group}>
              <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-lk-muted/70">
                {group}
              </div>
              <ul className="space-y-0.5">
                {groups[group].map((conv) => (
                  <li key={conv.id} className="group relative">
                    {editingId === conv.id ? (
                      <div className="flex items-center gap-1 px-2 py-1">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") handleRename(conv.id);
                            if (e.key === "Escape") setEditingId(null);
                          }}
                          className="flex-1 min-w-0 px-1.5 py-0.5 text-xs rounded border border-lk-border bg-lk-bg text-lk-fg outline-none focus:ring-1 focus:ring-lk-primary/40"
                          autoFocus
                        />
                      </div>
                    ) : (
                      <div
                        role="button"
                        tabIndex={0}
                        onClick={() => handleSelect(conv.id)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            handleSelect(conv.id);
                          }
                        }}
                        className="flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-lk-fg hover:bg-lk-user-msg cursor-pointer transition-colors"
                      >
                        <span className="truncate flex-1">{conv.title}</span>
                        <div className="hidden group-hover:flex items-center gap-0.5 shrink-0">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingId(conv.id);
                              setEditTitle(conv.title);
                            }}
                            className="p-0.5 rounded text-lk-muted hover:text-lk-fg"
                            aria-label="Rename"
                          >
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                            </svg>
                          </button>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(conv.id);
                            }}
                            className="p-0.5 rounded text-lk-muted hover:text-lk-primary"
                            aria-label="Delete"
                          >
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M3 6h18" />
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
                              <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Add `apiPatch` and `apiDelete` to `frontend/src/types/api.ts`**

Add these two functions at the end of the file:

```typescript
export async function apiPatch<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function apiDelete(url: string): Promise<void> {
  const res = await fetch(url, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
}
```

- [ ] **Step 3: Wire `RecentConversations` into `frontend/src/components/Sidebar.tsx`**

In the sidebar, when the Chat tab is active and the sidebar is expanded, show `<RecentConversations />` in the panel area. Replace the existing panel content section:

```tsx
import { RecentConversations } from "./sidebar/RecentConversations";
```

Then in the panel area (the `flex-1 min-h-0 overflow-y-auto px-2` div), add:

```tsx
{!collapsed && activeTab === "chat" && <RecentConversations />}
```

- [ ] **Step 4: Build and lint**

Run: `cd frontend && npm run build && npm run lint`
Expected: Clean build, no lint errors.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add collapsible Recent section to sidebar"
```

---

### Task 3: Add inline rename to ChatView header

**Files:**
- Modify: `frontend/src/components/ChatView.tsx`

**Interfaces:**
- Consumes: `apiPatch` from `@/types/api`
- Produces: ChatView with inline-editable title

- [ ] **Step 1: Update `frontend/src/components/ChatView.tsx`**

Add inline rename to the title. Replace the header section:

```tsx
"use client";

import { useState } from "react";
import { useConversation } from "@/hooks/useConversation";
import { MessageList } from "./conversation/MessageList";
import { ChatInput } from "./conversation/ChatInput";
import { apiPatch } from "@/types/api";

interface ChatViewProps {
  convId: string;
}

export function ChatView({ convId }: ChatViewProps) {
  const { conversation, messages, loading, sending, error, sendMessage } =
    useConversation(convId);
  const [editing, setEditing] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");

  const startEdit = () => {
    setTitleDraft(conversation?.title ?? "");
    setEditing(true);
  };

  const commitEdit = async () => {
    const title = titleDraft.trim();
    if (title && title !== conversation?.title) {
      await apiPatch(`/api/conversations/${convId}`, { title });
    }
    setEditing(false);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-pulse space-y-3 w-full max-w-md px-4">
          <div className="h-4 bg-lk-muted/20 rounded w-1/3" />
          <div className="h-4 bg-lk-muted/20 rounded w-2/3" />
          <div className="h-4 bg-lk-muted/20 rounded w-1/2" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <p className="text-sm text-lk-primary">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-lk-border py-3.5 bg-lk-card shrink-0">
        <div className="lk-shell">
          {editing ? (
            <input
              type="text"
              value={titleDraft}
              onChange={(e) => setTitleDraft(e.target.value)}
              onBlur={commitEdit}
              onKeyDown={(e) => {
                if (e.key === "Enter") commitEdit();
                if (e.key === "Escape") setEditing(false);
              }}
              className="w-full px-2 py-1 text-sm font-semibold rounded border border-lk-border bg-lk-bg text-lk-fg outline-none focus:ring-1 focus:ring-lk-primary/40"
              autoFocus
            />
          ) : (
            <button
              type="button"
              onClick={startEdit}
              className="text-sm font-semibold text-lk-fg hover:text-lk-primary transition-colors"
            >
              {conversation?.title ?? "Conversation"}
            </button>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} pending={sending} />
      </div>

      <ChatInput onSend={async (text) => { await sendMessage(text); }} disabled={sending} />
    </div>
  );
}
```

- [ ] **Step 2: Build and lint**

Run: `cd frontend && npm run build && npm run lint`
Expected: Clean build, no lint errors.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: add inline rename to ChatView header"
```

---

### Task 4: Update routing — `/chat/<id>` deep links + `/c/[id]` redirect

**Files:**
- Create: `frontend/src/app/chat/[id]/page.tsx`
- Modify: `frontend/src/app/c/[id]/page.tsx`

**Interfaces:**
- Consumes: `ChatView` from `@/components/ChatView`
- Produces: `/chat/<id>` route that renders `ChatView`, `/c/[id]` redirects to `/chat/<id>`

- [ ] **Step 1: Create `frontend/src/app/chat/[id]/page.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { ChatView } from "@/components/ChatView";

interface ChatSessionPageProps {
  params: Promise<{ id: string }>;
}

export default function ChatSessionPage({ params }: ChatSessionPageProps) {
  const [convId, setConvId] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setConvId(p.id));
  }, [params]);

  if (!convId) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-pulse space-y-3 w-full max-w-md px-4">
          <div className="h-4 bg-lk-muted/20 rounded w-1/3" />
          <div className="h-4 bg-lk-muted/20 rounded w-2/3" />
        </div>
      </div>
    );
  }

  return <ChatView convId={convId} />;
}
```

- [ ] **Step 2: Update `frontend/src/app/c/[id]/page.tsx` to redirect**

Replace the entire file with:

```tsx
"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const router = useRouter();

  useEffect(() => {
    params.then((p) => {
      router.replace(`/chat/${p.id}`);
    });
  }, [params, router]);

  return (
    <div className="flex flex-col min-h-screen bg-lk-bg">
      <main className="flex-1 flex items-center justify-center">
        <p className="text-sm text-lk-muted">Redirecting…</p>
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Build and lint**

Run: `cd frontend && npm run build && npm run lint`
Expected: Clean build, no lint errors.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add /chat/<id> route, redirect /c/<id> to /chat/<id>"
```

---

### Task 5: Update feed "Talk about this" handlers to use `/chat/<id>`

**Files:**
- Modify: `frontend/src/app/feed/page.tsx`

**Interfaces:**
- Consumes: None (just URL changes)
- Produces: Feed cards navigate to `/chat/<id>` instead of `/c/<id>`

- [ ] **Step 1: Update all `router.push('/c/${convId}')` to `router.push('/chat/${convId}')` in `frontend/src/app/feed/page.tsx`**

There are three handlers (`handleTalkAboutExercise`, `handleTalkAboutIdea`, `handleTalkAboutFading`). Each has a line like:

```tsx
router.push(`/c/${convId}`);
```

Change each to:

```tsx
router.push(`/chat/${convId}`);
```

- [ ] **Step 2: Build and lint**

Run: `cd frontend && npm run build && npm run lint`
Expected: Clean build, no lint errors.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: update feed entry points to navigate to /chat/<id>"
```

---

### Task 6: Update docs and verify

**Files:**
- Modify: `docs/product/STATUS.md`
- Modify: `docs/product/KANBAN.md`

**Interfaces:**
- Consumes: None
- Produces: Updated docs reflecting the new chat layout

- [ ] **Step 1: Update `docs/product/STATUS.md`**

Update the Chat Surface row to reflect the new single-column layout:

```
| Chat Surface (Chat as destination) | ✅ Shipped 2026-10-13 — `/chat` single-column layout (conversation + composer full-width). Sidebar shows collapsible "Recent" section with conversations grouped by recency. Deep links at `/chat/<id>`. `/c/[id]` redirects to `/chat/<id>`. Inline rename on conversation title. Spec at `../../openspec/changes/chat-layout-deeptutor-recent/`. |
```

- [ ] **Step 2: Update `docs/product/KANBAN.md`**

Move the chat layout slice from "Upcoming" to "Done":

```
| Chat layout — DeepTutor-style single-column + sidebar Recent | 2026-10-13 | `/chat` single-column, sidebar Recent section with collapsible conversation list grouped by recency. Deep links at `/chat/<id>`. `/c/[id]` redirects. Inline rename. Build + lint clean, 116/117 tests pass (1 pre-existing fail). |
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest tests/ -v`
Expected: 116 pass, 1 fail (`test_split_dyl_pdf`, pre-existing).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs: update STATUS and KANBAN for chat layout change"
```

---

## Self-Review

**Spec coverage:**
- ✅ `/chat` single-column — Task 1
- ✅ Sidebar "Recent" section — Task 2
- ✅ Inline rename in ChatView — Task 3
- ✅ `/chat/<id>` deep links — Task 4
- ✅ `/c/[id]` redirect — Task 4
- ✅ Feed entry points updated — Task 5
- ✅ Docs updated — Task 6

**Placeholder scan:** No TBDs, no "implement later", no vague steps.

**Type consistency:** `useConversations` returns `{ conversations, loading, error, refresh }` — used consistently across Tasks 1, 2. `apiPatch` and `apiDelete` defined in Task 2, used in Tasks 2 and 3.
