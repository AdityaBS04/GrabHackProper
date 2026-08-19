import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { RESOLUTION_STAGES } from "../lib/domain";
import { cx } from "./primitives";

/**
 * The wait, explained.
 *
 * While a case is with the resolution engine it runs a fixed sequence: identify
 * the issue, check it against the record, weigh the account's standing, decide,
 * then write the outcome. Naming those stages turns dead time into the most
 * informative moment in the product — you can watch your case being worked.
 *
 * The engine reports only its finished answer, so this reads as a sequence in
 * progress, never as a claim about what any stage concluded.
 */
export default function ResolutionTrace({ compact = false }) {
  const [reached, setReached] = useState(0);

  useEffect(() => {
    // Advance through the stages and hold on the last until the reply lands.
    const timers = RESOLUTION_STAGES.slice(1).map((_, i) =>
      setTimeout(() => setReached(i + 1), (i + 1) * 620)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div
      className={cx(
        "rounded-card border border-line bg-panel",
        compact ? "p-3" : "p-4"
      )}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2">
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full rounded-full bg-amber opacity-70 animate-blink" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-amber" />
        </span>
        <span className="font-mono text-[10px] uppercase tracking-signage text-amber-deep">
          Working the case
        </span>
      </div>

      <ol className={cx("space-y-1.5", compact ? "mt-2.5" : "mt-3")}>
        {RESOLUTION_STAGES.map((stage, i) => {
          const done = i < reached;
          const active = i === reached;
          return (
            <li key={stage.key} className="flex items-center gap-2.5">
              <span
                className={cx(
                  "grid h-4 w-4 shrink-0 place-items-center rounded-full border transition-colors",
                  done && "border-jade/60 bg-jade-wash text-jade",
                  active && "border-amber bg-amber-wash text-amber-deep",
                  !done && !active && "border-line text-faint"
                )}
              >
                {done ? (
                  <Check size={9} strokeWidth={3.5} />
                ) : (
                  <span
                    className={cx(
                      "h-1 w-1 rounded-full",
                      active ? "bg-amber" : "bg-faint"
                    )}
                  />
                )}
              </span>
              <span
                className={cx(
                  "font-mono text-[11px] transition-colors",
                  done && "text-muted",
                  active && "text-ink",
                  !done && !active && "text-faint"
                )}
              >
                {stage.label}
              </span>
              {active && (
                <span className="ml-auto h-px w-10 overflow-hidden rounded bg-line">
                  <motion.span className="block h-px w-3 bg-amber animate-trace-sweep" />
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
