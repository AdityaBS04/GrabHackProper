import React, { useRef, useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, ImagePlus, X } from "lucide-react";
import RichText from "./RichText";
import { Signage, cx } from "./primitives";
import { formatTime } from "../lib/domain";

/** What the person said. Quiet, right-aligned, no ornament. */
export function OperatorMessage({ text, at }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
      className="flex justify-end"
    >
      {/* Cool and white, so the only warm surface in the transcript stays the
          record itself. Alignment is what marks this as yours. */}
      <div className="max-w-[82%] rounded-card border border-line bg-white px-4 py-3 shadow-panel">
        <p className="text-[14.5px] leading-relaxed text-ink">{text}</p>
        <time className="mt-1.5 block text-right font-mono text-[10px] text-faint">
          {formatTime(at)}
        </time>
      </div>
    </motion.div>
  );
}

/**
 * What the engine said.
 *
 * A resolution — the reply that carries the decision — lands on paper, because
 * it is the outcome on the case file. Everything before it is console chatter.
 */
export function EngineMessage({ text, at, resolution = false, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
      className="flex justify-start"
    >
      <div className={cx("w-full", resolution ? "max-w-[92%]" : "max-w-[88%]")}>
        {resolution ? (
          <div className="paper p-5">
            <div className="flex items-center justify-between border-b border-parchment-edge pb-3">
              <span className="font-mono text-[10px] uppercase tracking-signage text-parchment-dim">
                Resolution
              </span>
              <time className="font-mono text-[10px] text-parchment-dim">
                {formatTime(at)}
              </time>
            </div>
            <div className="mt-3.5 text-[14.5px] text-[#3a3324]">
              <RichText text={text} tone="paper" />
            </div>
            {children}
          </div>
        ) : (
          <div className="rounded-card border border-line bg-panel px-4 py-3">
            <div className="text-[14.5px] text-ink">
              <RichText text={text} />
            </div>
            {children}
            <time className="mt-2 block font-mono text-[10px] text-faint">
              {formatTime(at)}
            </time>
          </div>
        )}
      </div>
    </motion.div>
  );
}

/** Narrowing the case: pick one. */
export function ChoiceList({ label, options, onPick, disabled }) {
  return (
    <div className="mt-3.5">
      <Signage>{label}</Signage>
      <div className="mt-2.5 grid gap-1.5">
        {options.map((option, i) => (
          <motion.button
            key={option.id}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04, duration: 0.3 }}
            onClick={() => onPick(option)}
            disabled={disabled}
            className="group flex items-center justify-between gap-3 rounded-card border border-line bg-white px-3.5 py-2.5 text-left transition-colors hover:border-amber-deep/50 hover:bg-raised disabled:cursor-not-allowed disabled:opacity-50"
          >
            <span className="min-w-0">
              <span className="block text-[14px] text-ink">{option.name}</span>
              {option.description && (
                <span className="mt-0.5 block text-[12.5px] leading-snug text-muted">
                  {option.description}
                </span>
              )}
            </span>
            <ArrowRight
              size={15}
              className="shrink-0 text-faint transition-colors group-hover:text-amber-deep"
            />
          </motion.button>
        ))}
      </div>
    </div>
  );
}

/**
 * Evidence. Some outcomes need a photo before the engine can authorise them,
 * so when it asks, the attachment control appears in the reply that asked.
 */
export function EvidencePicker({ onAttach, disabled }) {
  const inputRef = useRef(null);
  const [error, setError] = useState("");

  function handleFile(file) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError("Choose an image file.");
      return;
    }
    if (file.size > 6 * 1024 * 1024) {
      setError("That image is over 6 MB. Choose a smaller one.");
      return;
    }
    setError("");
    const reader = new FileReader();
    reader.onload = () => onAttach(String(reader.result), file.name);
    reader.onerror = () => setError("That file couldn't be read. Try another.");
    reader.readAsDataURL(file);
  }

  return (
    <div className="mt-3.5">
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={disabled}
        className="flex w-full items-center justify-center gap-2 rounded-card border border-dashed border-amber/40 bg-amber-wash px-4 py-3.5 text-[13.5px] text-amber-deep transition-colors hover:border-amber/70 hover:bg-amber-wash disabled:cursor-not-allowed disabled:opacity-50"
      >
        <ImagePlus size={16} />
        Attach a photo
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="sr-only"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      {error && <p className="mt-2 text-[12.5px] text-clay">{error}</p>}
    </div>
  );
}

/** A photo the person attached, shown in the transcript as sent. */
export function EvidenceMessage({ src, name, at, onRemove }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-end"
    >
      <div className="max-w-[62%] overflow-hidden rounded-card border border-line bg-white shadow-panel">
        <img
          src={src}
          alt={name || "Attached evidence"}
          className="block max-h-64 w-full object-cover"
        />
        <div className="flex items-center justify-between gap-2 px-3 py-2">
          <span className="truncate font-mono text-[10.5px] text-muted">
            {name || "photo"}
          </span>
          <span className="flex items-center gap-2">
            <time className="font-mono text-[10px] text-faint">
              {formatTime(at)}
            </time>
            {onRemove && (
              <button
                onClick={onRemove}
                aria-label="Remove attachment"
                className="text-faint hover:text-ink"
              >
                <X size={13} />
              </button>
            )}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
