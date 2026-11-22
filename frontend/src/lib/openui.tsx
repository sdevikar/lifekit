import { defineComponent, createLibrary } from "@openuidev/react-lang";
import { openuiLibrary } from "@openuidev/react-ui";
import Markdown from "react-markdown";
import remarkBreaks from "remark-breaks";
import remarkGfm from "remark-gfm";
import { z } from "zod/v4";

// Pull a few chart components out of the built-in library so the coach can
// emit diagrams/charts when asked, without importing the whole 82-component
// catalog into the prompt.
const { BarChart, LineChart, PieChart, RadarChart } = openuiLibrary.components;

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
      <Markdown remarkPlugins={[remarkGfm, remarkBreaks]}>
        {props.text.replace(/\\n/g, "\n")}
      </Markdown>
    </div>
  ),
});

export const library = createLibrary({
  root: "Card",
  components: [Card, TextContent, BarChart, LineChart, PieChart, RadarChart],
});