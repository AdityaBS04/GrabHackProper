import React from "react";
import { motion } from "framer-motion";
import { ArrowRight, Clock } from "lucide-react";
import { ServiceMark } from "./Marks";
import { StatusPill } from "./primitives";
import {
  formatDate,
  money,
  orderRoute,
  orderSummary,
  serviceFull,
  statusOf,
} from "../lib/domain";

/**
 * An order, rendered as the document it is.
 *
 * The console is ink; records are paper. A waybill has a body and a torn-off
 * filing stub, and the stub is where the actions live — the part a dispatcher
 * keeps.
 */
export default function Waybill({ order, index = 0, onOpenCase, onViewLog }) {
  const status = statusOf(order.status);
  const route = orderRoute(order);
  const amount = money(order.price);
  const date = formatDate(order.date);
  const updates = Number(order.update_count) || 0;

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.45,
        delay: Math.min(index * 0.05, 0.3),
        ease: [0.16, 1, 0.3, 1],
      }}
      className="paper group flex min-w-0 flex-col sm:flex-row"
    >
      {/* Body */}
      <div className="min-w-0 flex-1 px-5 py-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-2.5">
            <span className="text-parchment-dim">
              <ServiceMark service={order.service} width={18} height={18} />
            </span>
            <span className="truncate font-mono text-[11px] uppercase tracking-[0.14em] text-parchment-dim">
              {serviceFull(order.service)}
            </span>
          </div>
          <StatusPill tone={status.tone} onPaper>
            {status.label}
          </StatusPill>
        </div>

        <h3 className="mt-2.5 font-display text-[22px] font-700 leading-none tracking-tightest text-parchment-ink">
          {order.id}
        </h3>

        <p className="mt-1.5 line-clamp-2 text-[14px] leading-snug text-[#4a4232]">
          {orderSummary(order)}
        </p>

        {route && (
          <div className="mt-2.5 flex min-w-0 items-center gap-2 font-mono text-[11px] text-parchment-dim">
            <span className="min-w-0 flex-1 truncate">{route.from}</span>
            <ArrowRight size={12} className="shrink-0" />
            <span className="min-w-0 flex-1 truncate">{route.to}</span>
          </div>
        )}

        {order.current_status_remarks &&
          order.current_status_remarks !== "Order placed" && (
            <p className="mt-3 border-l-2 border-parchment-edge pl-2.5 text-[12.5px] italic text-[#5c5240]">
              {order.current_status_remarks}
            </p>
          )}
      </div>

      {/* Filing stub, torn along the perforation */}
      <div className="relative flex shrink-0 flex-row items-center gap-4 px-5 py-4 sm:w-[176px] sm:flex-col sm:items-stretch sm:justify-between">
        <span
          aria-hidden="true"
          className="perforation-x absolute inset-x-0 top-0 h-px sm:hidden"
        />
        <span
          aria-hidden="true"
          className="perforation-y absolute inset-y-0 left-0 hidden w-px sm:block"
        />
        <div className="flex-1 sm:flex-none">
          {amount && (
            <div className="font-display text-[22px] font-700 leading-none tracking-tightest text-parchment-ink tabular-nums">
              {amount}
            </div>
          )}
          {date && (
            <div className="mt-1.5 font-mono text-[11px] text-parchment-dim">
              {date}
            </div>
          )}
          {updates > 0 && (
            <button
              onClick={() => onViewLog(order.id)}
              className="mt-2.5 inline-flex items-center gap-1.5 font-mono text-[11px] text-[#8a5a11] underline decoration-dotted underline-offset-2 hover:text-parchment-ink"
            >
              <Clock size={11} />
              {updates} update{updates === 1 ? "" : "s"}
            </button>
          )}
        </div>

        <button
          onClick={() => onOpenCase(order)}
          className="inline-flex h-10 items-center justify-center gap-2 rounded-card bg-parchment-ink px-4 text-[13px] font-semibold text-parchment transition-colors hover:bg-[#3b3423]"
        >
          Report issue
          <ArrowRight size={14} />
        </button>
      </div>
    </motion.article>
  );
}
