import React, { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import api from "../services/api";
import { Signage, Spinner } from "./primitives";
import { actorLabel, formatStamp, titleCase } from "../lib/domain";

/**
 * The update log for one order — who touched it, when, and what changed.
 * A drawer rather than a modal: the log is a reference you read alongside the
 * record, not a decision you have to dismiss.
 */
export default function OrderLog({ orderId, onClose }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const { data } = await api.get(`/order-history/${orderId}`);
        if (live) setEntries(data.timeline || []);
      } catch {
        if (live) setFailed(true);
      } finally {
        if (live) setLoading(false);
      }
    })();
    return () => {
      live = false;
    };
  }, [orderId]);

  const handleKey = useCallback(
    (e) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  return (
    <AnimatePresence>
      <motion.div
        key="scrim"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-40 bg-desk/70 backdrop-blur-[2px]"
      />
      <motion.aside
        key="drawer"
        role="dialog"
        aria-label={`Update log for order ${orderId}`}
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-[440px] flex-col border-l border-line bg-panel"
      >
        <header className="flex items-start justify-between border-b border-line p-5">
          <div>
            <Signage>Update log</Signage>
            <h2 className="mt-1.5 font-display text-[22px] font-700 leading-none tracking-tightest text-ink">
              {orderId}
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close log"
            className="grid h-9 w-9 place-items-center rounded-card text-muted hover:bg-raised hover:text-ink"
          >
            <X size={17} />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto p-5">
          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted">
              <Spinner /> Loading log
            </div>
          )}

          {!loading && failed && (
            <p className="text-sm text-clay">
              The log didn't load. Close this and open it again.
            </p>
          )}

          {!loading && !failed && entries.length === 0 && (
            <div className="rounded-card border border-dashed border-line p-6 text-center">
              <p className="text-sm text-muted">No updates recorded yet.</p>
              <p className="mt-1 text-[13px] text-faint">
                Changes from drivers, restaurants and support appear here.
              </p>
            </div>
          )}

          {!loading && entries.length > 0 && (
            <ol className="relative space-y-5 pl-5">
              {/* The spine the entries hang from. */}
              <span className="absolute left-[5px] top-2 bottom-2 w-px bg-line" />
              {entries.map((entry, i) => (
                <motion.li
                  key={`${entry.timestamp}-${i}`}
                  initial={{ opacity: 0, x: 6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  className="relative"
                >
                  <span
                    className={`absolute -left-5 top-[5px] h-[11px] w-[11px] rounded-full border-2 ${
                      i === entries.length - 1
                        ? "border-amber bg-panel"
                        : "border-line bg-panel"
                    }`}
                  />
                  <div className="flex items-baseline justify-between gap-3">
                    <h3 className="text-[14px] font-semibold text-ink">
                      {titleCase(entry.update_type)}
                    </h3>
                    <time className="shrink-0 font-mono text-[10.5px] text-faint">
                      {formatStamp(entry.timestamp)}
                    </time>
                  </div>
                  <p className="mt-1 text-[13.5px] leading-snug text-muted">
                    {entry.description}
                  </p>
                  <p className="mt-1.5 font-mono text-[10.5px] uppercase tracking-[0.1em] text-faint">
                    {actorLabel(entry.actor_type)}
                    {entry.actor_username ? ` · ${entry.actor_username}` : ""}
                  </p>
                </motion.li>
              ))}
            </ol>
          )}
        </div>
      </motion.aside>
    </AnimatePresence>
  );
}
