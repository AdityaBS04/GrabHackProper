import React from "react";
import { ArrowRight } from "lucide-react";
import { Button, StatusPill, cx } from "../primitives";

/**
 * List2 — a ruled row list.
 *
 * Adapted from the shadcn/21st `list-2` block: same four-column skeleton
 * (mark + title/category · description spanning two · action pushed right,
 * separated by rules), retyped onto this project's tokens instead of shadcn's
 * `bg-muted` / `text-muted-foreground` / `<Separator />` primitives, which the
 * codebase doesn't have. See the note in the PR description for what a real
 * shadcn install would take.
 *
 * Each item:
 *   { id, icon, title, category, description, meta, status, actionLabel,
 *     onAction, secondaryLabel, onSecondary }
 */
export function List2({ heading, items = [], dense = false }) {
  if (items.length === 0) return null;

  return (
    <section className={dense ? "" : "py-2"}>
      {heading && (
        <h2 className="mb-4 font-display text-[22px] font-700 tracking-tightest text-ink">
          {heading}
        </h2>
      )}

      <div className="flex flex-col">
        <Separator />
        {items.map((item, index) => (
          <React.Fragment key={item.id ?? index}>
            <div className="group grid items-center gap-4 px-1 py-5 transition-colors hover:bg-raised sm:px-3 md:grid-cols-4">
              {/* Mark, title, category */}
              <div className="order-2 flex min-w-0 items-center gap-3 md:order-none">
                <span className="flex h-14 w-16 shrink-0 items-center justify-center rounded-card border border-parchment-edge bg-parchment text-parchment-dim">
                  {item.icon}
                </span>
                <div className="flex min-w-0 flex-col gap-1">
                  <h3 className="truncate font-display text-[19px] font-700 leading-none tracking-tightest text-ink">
                    {item.title}
                  </h3>
                  <p className="flex items-center gap-2 truncate font-mono text-[10.5px] uppercase tracking-[0.12em] text-faint">
                    {item.category}
                  </p>
                </div>
              </div>

              {/* What it was */}
              <div className="order-1 min-w-0 md:order-none md:col-span-2">
                <p className="truncate text-[17px] font-semibold leading-snug text-ink">
                  {item.description}
                </p>
                {item.meta && (
                  <p className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[11px] text-faint">
                    {item.meta}
                  </p>
                )}
              </div>

              {/* Status and action */}
              <div className="order-3 flex items-center justify-between gap-3 md:order-none md:justify-end">
                <div className="flex flex-col items-start gap-1.5 md:items-end">
                  {item.status && (
                    <StatusPill tone={item.status.tone}>
                      {item.status.label}
                    </StatusPill>
                  )}
                  {item.secondaryLabel && (
                    <button
                      onClick={item.onSecondary}
                      className="font-mono text-[11px] text-amber-deep underline decoration-dotted underline-offset-2 hover:text-ink"
                    >
                      {item.secondaryLabel}
                    </button>
                  )}
                </div>
                <Button
                  intent="quiet"
                  onClick={item.onAction}
                  className="w-fit shrink-0 group-hover:border-amber-deep/50"
                >
                  <span>{item.actionLabel || "Open"}</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <Separator />
          </React.Fragment>
        ))}
      </div>
    </section>
  );
}

/** The rule between rows. Stands in for shadcn's <Separator />. */
export function Separator({ className = "" }) {
  return (
    <div
      role="separator"
      className={cx("h-px w-full shrink-0 bg-line", className)}
    />
  );
}

export default List2;
