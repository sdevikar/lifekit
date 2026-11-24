"use client";

import { useState } from "react";
import { ExerciseCard } from "@/components/feed/ExerciseCard";
import { FadingIdeasCard } from "@/components/feed/FadingIdeasCard";
import { ResurfacedIdeaCard } from "@/components/feed/ResurfacedIdeaCard";
import { TodayHeader } from "@/components/feed/TodayHeader";
import { useBriefing } from "@/hooks/useBriefing";
import { ActivityDrawer, DrawerCard } from "@/components/ActivityDrawer";

export default function FeedPage() {
  const {
    briefing,
    loading,
    error,
    markDone,
    signalIdea,
  } = useBriefing();

  const [actionPending, setActionPending] = useState(false);
  const [drawerCard, setDrawerCard] = useState<DrawerCard | null>(null);

  const handleTalkAboutExercise = () => {
    if (!briefing) return;
    setDrawerCard({
      kind: "exercise",
      id: briefing.exercise.id,
      title: briefing.exercise.title,
      text: briefing.exercise.text,
    });
  };

  const handleTalkAboutIdea = (ideaId: number, text: string) => {
    setDrawerCard({ kind: "idea", id: ideaId, title: "", text });
  };

  const handleTalkAboutResurfaced = () => {
    if (!briefing) return;
    setDrawerCard({
      kind: "resurfaced",
      id: briefing.resurfaced_idea.id,
      title: "",
      text: briefing.resurfaced_idea.text,
    });
  };

  const handleMarkDone = async (exerciseId: number) => {
    setActionPending(true);
    try {
      await markDone(exerciseId);
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
    <>
    <div className="lk-shell">
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
        onTalkAbout={(id) => {
          const idea = briefing.fading_ideas.find((i) => i.id === id);
          handleTalkAboutIdea(id, idea?.text ?? "");
        }}
      />

    </div>

    <ActivityDrawer
      card={drawerCard}
      onClose={() => setDrawerCard(null)}
      onMarkDone={handleMarkDone}
      markingDone={actionPending}
    />
    </>
  );
}
