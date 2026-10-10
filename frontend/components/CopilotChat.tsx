"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type Message = { role: "user" | "assistant"; text: string };

const SUGGESTIONS = [
  "Why is operating cost high?",
  "Which zone should we prioritize?",
  "What maintenance is most urgent?",
  "What if segregation increased to 60%?",
];

export function CopilotChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Ask me about operating costs, zone priorities, maintenance risk, recommended interventions, or a segregation what-if scenario. Every answer is computed from the live dataset — no external AI model, no guessing.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(question: string) {
    if (!question.trim()) return;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.askCopilot(question);
      setMessages((m) => [...m, { role: "assistant", text: res.answer }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Couldn't reach the backend — is it running?" }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto scrollbar-thin flex flex-col gap-3 pr-1 mb-3 max-h-80">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-sm rounded-lg px-3 py-2 max-w-[90%] ${
              m.role === "user" ? "self-end bg-accent-soft text-foreground" : "self-start bg-surface-raised text-muted"
            }`}
          >
            {m.text}
          </div>
        ))}
        {loading && <div className="text-xs text-muted self-start">thinking…</div>}
      </div>
      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            className="text-xs border border-border rounded-full px-3 py-1 text-muted hover:text-foreground hover:border-accent"
          >
            {s}
          </button>
        ))}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the copilot…"
          className="flex-1 bg-surface-raised border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-accent"
        />
        <button type="submit" className="bg-accent text-background rounded-lg px-4 py-2 text-sm font-medium">
          Ask
        </button>
      </form>
    </div>
  );
}
