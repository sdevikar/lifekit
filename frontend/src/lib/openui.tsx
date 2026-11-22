import { defineComponent, createLibrary } from "@openuidev/react-lang";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { z } from "zod/v4";

const Card = defineComponent({
  name: "Card",
  description: "Vertical container for a coach reply. Root component.",
  props: z.object({
    children: z.array(z.any()).optional(),
  }),
  component: ({ props, renderNode }) => (
    <div className="space-y-2">{renderNode(props.children ?? [])}</div>
  ),
});

const TextContent = defineComponent({
  name: "TextContent",
  description:
    "Text block. ONE text string (use \\n for new lines). Supports markdown (bold, lists, paragraphs). Optional size: small/default/large/small-heavy/large-heavy.",
  props: z.object({
    text: z.string(),
    size: z
      .enum(["small", "default", "large", "small-heavy", "large-heavy"])
      .optional(),
  }),
  component: ({ props }) => (
    <div className="text-sm leading-relaxed lk-prose">
      <Markdown remarkPlugins={[remarkGfm]}>{props.text}</Markdown>
    </div>
  ),
});

export const library = createLibrary({
  root: "Card",
  components: [Card, TextContent],
});