import React from "react";
import { motion } from "framer-motion";
import { ServiceMark } from "./Marks";
import { Signage, StatusPill, cx } from "./primitives";
import ResolutionTrace from "./ResolutionTrace";
import {
  actorLabel,
  formatDate,
  money,
  orderRoute,
  orderSummary,
  serviceFull,
  statusOf,
  titleCase,
} from "../lib/domain";

/**
 * The case, as an instrument panel.
 *
 * It carries what the person can see and check for themselves — which service,
 * which order, what was in it, what it cost — and fills in as they narrow the
 * problem. How the engine weighs an account is its own business and stays on
 * the server; showing a score here only invites arguing with the number.
 */
export default function CaseConsole({
  service,
  userType,
  order,
  orderId,
  category,
  subIssue,
  working,
}) {
  const fields = [
    { label: "Service", value: serviceFull(service) },
    { label: "Reporting as", value: actorLabel(userType) },
    { label: "Category", value: category?.name },
    { label: "Issue", value: subIssue?.name },
  ];

  const status = order ? statusOf(order.status) : null;
  const route = order ? orderRoute(order) : null;
  const amount = order ? money(order.price) : null;
  const date = order ? formatDate(order.date) : null;

  return (
    <div className="flex h-full flex-col gap-5">
      <div className="panel p-5">
        <div className="flex items-center justify-between">
          <Signage>Case</Signage>
          <span className="text-amber-deep">
            <ServiceMark service={service} width={18} height={18} />
          </span>
        </div>

        <dl className="mt-4 space-y-3">
          {fields.map((field) => (
            <div key={field.label}>
              <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-faint">
                {field.label}
              </dt>
              <dd
                className={cx(
                  "mt-0.5 text-[13.5px] leading-snug transition-colors",
                  field.value ? "text-ink" : "text-faint"
                )}
              >
                {field.value || <span className="text-faint">Not set yet</span>}
              </dd>
            </div>
          ))}
        </dl>
      </div>

      {/* The record this case is about, on its own stock. */}
      {(order || orderId) && (
        <div className="paper p-5">
          <div className="flex items-center justify-between border-b border-parchment-edge pb-3">
            <span className="font-mono text-[10px] uppercase tracking-signage text-parchment-dim">
              Order
            </span>
            {status && <StatusPill tone={status.tone} onPaper>{status.label}</StatusPill>}
          </div>

          <h3 className="mt-3 font-display text-[22px] font-700 leading-none tracking-tightest text-parchment-ink">
            {order?.id || orderId}
          </h3>

          {order && (
            <>
              <p className="mt-2 text-[13.5px] leading-snug text-[#4a4232]">
                {orderSummary(order)}
              </p>

              <dl className="mt-4 space-y-2.5 border-t border-parchment-edge pt-3 font-mono text-[11px]">
                {amount && (
                  <Row label="Total">
                    <span className="font-semibold text-parchment-ink">
                      {amount}
                    </span>
                  </Row>
                )}
                {date && <Row label="Placed">{date}</Row>}
                {order.payment_method && (
                  <Row label="Paid by">{paymentLabel(order.payment_method)}</Row>
                )}
                {order.restaurant_name && (
                  <Row label="From">{order.restaurant_name}</Row>
                )}
                {route && (
                  <div>
                    <dt className="text-parchment-dim">Route</dt>
                    <dd className="mt-1 leading-snug text-parchment-ink">
                      {route.from}
                      <br />
                      <span className="text-parchment-dim">&darr;</span>
                      <br />
                      {route.to}
                    </dd>
                  </div>
                )}
              </dl>
            </>
          )}
        </div>
      )}

      {working && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <ResolutionTrace />
        </motion.div>
      )}
    </div>
  );
}

/** "cod" is an initialism; everything else reads as a word. */
function paymentLabel(method) {
  const value = String(method).trim();
  return /^cod$/i.test(value) ? "COD" : titleCase(value);
}

function Row({ label, children }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="shrink-0 text-parchment-dim">{label}</dt>
      <dd className="truncate text-right text-parchment-ink">{children}</dd>
    </div>
  );
}
