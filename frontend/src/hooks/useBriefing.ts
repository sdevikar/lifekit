import { useEffect, useState } from "react";
import { BriefingResponse, apiGet, apiPost } from "@/types/api";

const BRIEFING_URL = "/api/briefing/today";

export function useBriefing() {
  const [data, setData] = useState<BriefingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    // Allow parent to refresh by re-calling loadData
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiGet<BriefingResponse>(BRIEFING_URL);
      setData(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load briefing");
    } finally {
      setLoading(false);
    }
  };

  const markDone = async (exerciseId: number) => {
    const resp = await apiPost<{ ok: boolean; completion_id?: number }>(
      "/api/completions",
      { exercise_id: exerciseId },
    );
    if (resp.ok) {
      // Refresh briefing to get next exercise
      await loadData();
    }
    return resp;
  };

  const signalIdea = async (ideaId: number, remembered: boolean) => {
    const resp = await apiPost<{ ok: boolean }>(
      "/api/idea-signals",
      { idea_id: ideaId, remembered },
    );
    if (resp.ok) {
      await loadData();
    }
    return resp;
  };

  const createConversation = async (seedKind: "card" | "composer", seedRef?: string, title?: string) => {
    const resp = await apiPost<{ id: string }>("/api/conversations", {
      seed_kind: seedKind,
      seed_ref: seedRef,
      title: title,
    });
    return resp.id;
  };

  return {
    briefing: data,
    loading,
    error,
    refresh: loadData,
    markDone,
    signalIdea,
    createConversation,
  };
}