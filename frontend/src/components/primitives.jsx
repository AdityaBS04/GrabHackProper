import React from "react";

export const cx = (...parts) => parts.filter(Boolean).join(" ");

/**
 * Actions. Three intents only: the one thing to do (signal), the alternative
 * (quiet), and destructive-adjacent exits (bare).
 */
export function Button({
  as: Tag = "button",
  intent = "signal",
  size = "md",
  className = "",
  children,
  ...props
}) {
  const intents = {
    signal:
      "bg-amber text-ink hover:bg-amber-bright active:bg-[#D48D24] font-semibold disabled:bg-sunken disabled:text-faint",
    quiet:
      "bg-raised text-ink hover:bg-sunken border border-line disabled:text-faint",
    bare: "text-muted hover:text-ink hover:bg-raised",
    paper:
      "bg-parchment-ink text-parchment hover:bg-[#3b3423] font-semibold",
  };
  const sizes = {
    sm: "h-8 px-3 text-[13px]",
    md: "h-10 px-4 text-sm",
    lg: "h-12 px-6 text-[15px]",
  };
  return (
    <Tag
      className={cx(
        "inline-flex items-center justify-center gap-2 rounded-card",
        "transition-colors duration-150 disabled:cursor-not-allowed",
        intents[intent],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </Tag>
  );
}

/** A small all-caps label. The console's voice for naming a field. */
export function Signage({ children, className = "" }) {
  return <div className={cx("signage", className)}>{children}</div>;
}

/** Status, in the tone the domain assigns it. */
export function StatusPill({ tone = "slate", children, onPaper = false }) {
  const onSurface = {
    amber: "text-amber-deep border-amber/60 bg-amber-wash",
    jade: "text-jade border-jade/40 bg-jade-wash",
    clay: "text-clay border-clay/40 bg-clay-wash",
    slate: "text-muted border-line bg-raised",
  };
  const onPaperTones = {
    amber: "text-[#6B4207] border-[#c9a45a] bg-[#F0DDB0]",
    jade: "text-[#1f5f4c] border-[#7fae9d] bg-[#c3ddd2]",
    clay: "text-[#8a3d24] border-[#c08a72] bg-[#e5c4b6]",
    slate: "text-parchment-dim border-parchment-edge bg-parchment-deep",
  };
  const palette = onPaper ? onPaperTones : onSurface;
  return (
    <span
      className={cx(
        "inline-flex items-center rounded-[2px] border px-1.5 py-[1px]",
        "font-mono text-[10px] uppercase tracking-[0.12em]",
        palette[tone] || palette.slate
      )}
    >
      {children}
    </span>
  );
}


/** Waiting, with the reason attached. */
export function Spinner({ className = "" }) {
  return (
    <svg
      className={cx("animate-spin", className)}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="12"
        cy="12"
        r="9"
        stroke="currentColor"
        strokeWidth="2.5"
        opacity="0.25"
      />
      <path
        d="M21 12a9 9 0 0 0-9-9"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  );
}
