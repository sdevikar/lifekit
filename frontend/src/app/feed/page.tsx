"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ExerciseCard } from "@/components/feed/ExerciseCard";
import { FadingIdeasCard } from "@/components/feed/FadingIdeasCard";
import { ResurfacedIdeaCard } from "@/components/feed/ResurfacedIdeaCard";
import { TodayHeader } from "@/components/feed/TodayHeader";
import { useBriefing } from "@/hooks/useBriefing";

export default function FeedPage() {
  const router = useRouter();
  const {
    briefing,
    loading,
    error,
    markDone,
    signalIdea,
    createConversation,
  } = useBriefing();

  const [actionPending, setActionPending] = useState(false);

  const handleTalkAboutExercise = async () => {
    if (!briefing) return;
    setActionPending(true);
    try {
      const convId = await createConversation("card", String(briefing.exercise.id));
      router.push(`/c/${convId}`);
    } finally {
      setActionPending(false);
    }
  };

  const handleTalkAboutIdea = async (ideaId: number) => {
    setActionPending(true);
    try {
      const convId = await createConversation("card", String(ideaId));
      router.push(`/c/${convId}`);
    } finally {
      setActionPending(false);
    }
  };

  const handleTalkAboutResurfaced = async () => {
    if (!briefing) return;
    setActionPending(true);
    try {
      const convId = await createConversation(
        "card",
        String(briefing.resurfaced_idea.id),
      );
      router.push(`/c/${convId}`);
    } finally {
      setActionPending(false);
    }
  };

  const handleStillWithMe = async (remembered: boolean) => {
    if (!briefing) return;
    await signalIdea(briefing.resurfaced_idea.id, remembered);
  };

  if (loading) {
    return (
      <div className="lk-shell py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-lk-muted/20 rounded-md w-1/3" />
          <div className="h-12 bg-lk-muted/20 rounded-md w-full" />
          <div className="h-32 bg-lk-muted/20 rounded-lg w-full" />
          <div className="h-32 bg-lk-muted/20 rounded-lg w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lk-shell py-12">
        <div className="lk-card border-lk-primary/30">
          <p className="text-sm text-lk-primary font-medium">Failed to load briefing feed: {error}</p>
          <button
            className="lk-btn lk-btn-sm mt-3"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!briefing) {
    return (
      <div className="lk-shell py-12">
        <p className="text-sm text-lk-muted">No briefing available.</p>
      </div>
    );
  }

  return (
    <div className="lk-shell">
      {/* 1. Today header + stage strip */}
      <TodayHeader
        book={briefing.book}
        day={briefing.day}
        stages={briefing.stages}
      />

      {/* 2. Today's exercise card */}
      <ExerciseCard
        exercise={briefing.exercise}
        onMarkDone={async () => {
          await markDone(briefing.exercise.id);
        }}
        onTalkAbout={handleTalkAboutExercise}
        markingDone={actionPending}
      />

      {/* 3. Resurfaced idea card */}
      <ResurfacedIdeaCard
        idea={briefing.resurfaced_idea}
        onStillWithMe={handleStillWithMe}
        onTalkAbout={handleTalkAboutResurfaced}
        signaling={actionPending}
      />

      {/* 4. Fading ideas card */}
      <FadingIdeasCard
        ideas={briefing.fading_ideas}
        onTalkAbout={handleTalkAboutIdea}
      />

    </div>
  );
}
