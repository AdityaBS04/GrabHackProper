"use client";

import * as React from "react";
import { SendIcon } from "lucide-react";
import { format } from "date-fns";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ChatEntry = {
  id: string;
  sender: string;
  initials: string;
  isOwn: boolean;
  at: Date;
  /** Rendered body. Attachments and choice lists come through here. */
  body: React.ReactNode;
  /** The reply that carries the decision is shown on the record's stock. */
  resolution?: boolean;
};

export interface CaseChatProps {
  entries: ChatEntry[];
  draft: string;
  onDraftChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  busy?: boolean;
  placeholder?: string;
  /** Shown under the transcript while the engine works the case. */
  footer?: React.ReactNode;
}

function formatMessageTime(date: Date): string {
  return format(date, "h:mm a");
}

/**
 * The case transcript.
 *
 * Built on the shadcn scroll-area chat pattern: an avatar rail, sender and
 * time above each bubble, own messages mirrored to the right, a fade at the
 * foot of the scroller and a fixed composer beneath it.
 */
export function CaseChat({
  entries,
  draft,
  onDraftChange,
  onSend,
  disabled = false,
  busy = false,
  placeholder = "Type a message...",
  footer,
}: CaseChatProps) {
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = React.useCallback(() => {
    const viewport = scrollAreaRef.current?.querySelector(
      '[data-slot="scroll-area-viewport"]'
    ) as HTMLElement | null;
    if (viewport) viewport.scrollTop = viewport.scrollHeight;
  }, []);

  React.useEffect(() => {
    scrollToBottom();
    const timeout = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeout);
  }, [entries, busy, scrollToBottom]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && draft.trim()) onSend();
    }
  };

  return (
    <div className="relative flex min-h-0 w-full flex-1 flex-col overflow-hidden">
      <div className="relative min-h-0 flex-1">
        <div ref={scrollAreaRef} className="h-full">
          <ScrollArea className="h-full">
            <div className="flex min-h-full flex-col justify-end space-y-5 py-6 pr-4">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className={cn(
                    "flex gap-3",
                    entry.isOwn ? "flex-row-reverse" : "flex-row"
                  )}
                >
                  <Avatar className="h-8 w-8 shrink-0 border border-line">
                    <AvatarFallback
                      className={cn(
                        "font-mono text-[10px] font-semibold uppercase",
                        entry.isOwn
                          ? "bg-white text-muted"
                          : "bg-parchment text-parchment-dim"
                      )}
                    >
                      {entry.initials}
                    </AvatarFallback>
                  </Avatar>

                  <div
                    className={cn(
                      "flex max-w-[78%] flex-col gap-1.5",
                      entry.isOwn ? "items-end" : "items-start"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-[12px] font-semibold text-ink">
                        {entry.sender}
                      </span>
                      <span className="font-mono text-[10px] text-faint">
                        {formatMessageTime(entry.at)}
                      </span>
                    </div>

                    <div
                      className={cn(
                        "w-full rounded-card px-4 py-3 text-[14.5px] leading-relaxed",
                        entry.resolution
                          ? "paper"
                          : entry.isOwn
                            ? "border border-line bg-white text-ink shadow-panel"
                            : "border border-line bg-panel text-ink"
                      )}
                    >
                      {entry.body}
                    </div>
                  </div>
                </div>
              ))}

              {footer}
            </div>
          </ScrollArea>
        </div>

        {/* Softens the cut where the transcript meets the composer. */}
        <div className="pointer-events-none absolute bottom-0 left-0 right-0 z-10 h-12 bg-gradient-to-t from-desk to-transparent" />
      </div>

      <div className="relative z-20 shrink-0 border-t border-line py-4">
        <div className="flex gap-2">
          <Input
            placeholder={placeholder}
            value={draft}
            onChange={(e) => onDraftChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            className="h-11 flex-1 rounded-card text-[14.5px]"
          />
          <Button
            onClick={onSend}
            size="icon"
            aria-label="Send"
            disabled={disabled || busy || !draft.trim()}
            className="h-11 w-11 shrink-0 rounded-card"
          >
            <SendIcon className="h-4 w-4" />
          </Button>
        </div>
        <p className="mt-2 px-1 font-mono text-[10.5px] text-faint">
          Enter sends
        </p>
      </div>
    </div>
  );
}

export default CaseChat;
