"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ExerciseCard } from "@/components/feed/ExerciseCard";
import { FadingIdeasCard } from "@/components/feed/FadingIdeasCard";
import { MasterComposer } from "@/components/feed/MasterComposer";
import { ResurfacedIdeaCard } from "@/components/feed/ResurfacedIdeaCard";
import { ConversationsList } from "@/components/feed/ConversationsList";
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

  const handleComposerSubmit = async (text: string) => {
    setActionPending(true);
    try {
      const convId = await createConversation("composer", undefined, text.slice(0, 80));
      router.push(`/c/${convId}`);
    } finally {
      setActionPending(false);
    }
  };

  const handleOpenConversation = (id: string) => {
    router.push(`/c/${id}`);
  };

  const handleStillWithMe = async (remembered: boolean) => {
    if (!briefing) return;
    await signalIdea(briefing.resurfaced_idea.id, remembered);
  };

  if (loading) {
    return (
      <div className="pb-24">
        <div className="animate-pulse space-y-4 p-6">
          <div className="h-5 bg-lk-muted/20 rounded w-3/4" />
          <div className="h-4 bg-lk-muted/20 rounded w-1/2" />
          <div className="lk-card" />
          <div className="lk-card" />
          <div className="lk-card" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-lk-primary">Failed to load feed: {error}</p>
        <button
          className="lk-btn lk-btn-sm mt-3"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!briefing) {
    return (
      <div className="p-6">
        <p className="text-sm text-lk-muted">No briefing available.</p>
      </div>
    );
  }

  return (
    <div className="pb-24">
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

      {/* 5. Conversations list */}
      <ConversationsList
        conversations={[]}
        onOpen={handleOpenConversation}
      />

      {/* 6. Master composer */}
      <MasterComposer
        onSubmit={handleComposerSubmit}
        submitting={actionPending}
      />
    </div>
  );
}