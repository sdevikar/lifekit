// Type definitions for the 13a Feed API contract.
// Source: openspec/changes/step-13-ui-feed-conversations/proposal.md

export interface BookInfo {
  id: string;
  title: string;
}

export interface StageStrip {
  seen: number;
  retained: number;
  lived: number;
}

export interface ExerciseCard {
  id: number;
  title: string;
  text: string;
  chapter_title?: string;
  source_quote?: string;
}

export interface ResurfacedIdea {
  id: number;
  text: string;
  why: string;
}

export interface FadingIdea {
  id: number;
  text: string;
}

export interface BriefingResponse {
  book: BookInfo;
  day: string;
  stages: StageStrip;
  exercise: ExerciseCard;
  resurfaced_idea: ResurfacedIdea;
  fading_ideas: FadingIdea[];
}

export interface ConversationListItem {
  id: string;
  title: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string;
  book_id: string;
  seed_kind: "card" | "composer";
  seed_ref: string | null;
}

export interface Message {
  role: "user" | "coach";
  text: string;
  created_at: string;
}

export interface ConversationResponse {
  conversation: ConversationDetail;
  messages: Message[];
}

export interface ApiOk {
  ok: true;
}

export interface ApiError {
  ok: false;
  error: string;
}

// Request types
export interface CompletionRequest {
  exercise_id: number;
}

export interface IdeaSignalRequest {
  idea_id: number;
  remembered: boolean;
}

export interface CreateConversationRequest {
  seed_kind: "card" | "composer";
  seed_ref?: string;
  title?: string;
}

export interface SendMessageRequest {
  text: string;
}

// Helper: fetch wrapper with error handling
export async function apiGet<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function apiPost<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}