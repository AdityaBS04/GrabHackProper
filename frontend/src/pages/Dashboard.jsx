import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api, { currentUser } from "../services/api";
import AppShell from "../components/AppShell";
import OrderLog from "../components/OrderLog";
import { List2 } from "../components/ui/list-2";
import { ServiceMark } from "../components/Marks";
import { Button, Signage, Spinner, cx } from "../components/primitives";
import {
  actorLabel,
  formatDate,
  isLive,
  isSettled,
  money,
  orderRoute,
  orderSummary,
  serviceFull,
  serviceLabel,
  statusOf,
} from "../lib/domain";

export default function Dashboard() {
  const navigate = useNavigate();
  const [user] = useState(currentUser);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);
  const [filter, setFilter] = useState("all");
  const [logOrderId, setLogOrderId] = useState(null);

  useEffect(() => {
    if (!user) navigate("/signin", { replace: true });
  }, [user, navigate]);

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setLoadFailed(false);
    try {
      let data;
      try {
        ({ data } = await api.get(
          `/orders/${user.type}/${user.username}/with-updates`
        ));
      } catch {
        ({ data } = await api.get(`/orders/${user.type}/${user.username}`));
      }
      setOrders(data.orders || []);
    } catch {
      setLoadFailed(true);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    load();
  }, [load]);

  const counts = useMemo(
    () => ({
      total: orders.length,
      live: orders.filter((o) => isLive(o.status)).length,
      settled: orders.filter((o) => isSettled(o.status)).length,
    }),
    [orders]
  );

  const services = useMemo(() => {
    const present = new Set(orders.map((o) => o.service));
    return (user?.services || []).filter((s) => present.has(s));
  }, [orders, user]);

  const visible = useMemo(
    () => (filter === "all" ? orders : orders.filter((o) => o.service === filter)),
    [orders, filter]
  );

  // Anything still moving comes first — that's where a problem is urgent.
  const [running, past] = useMemo(
    () => [
      visible.filter((o) => isLive(o.status)),
      visible.filter((o) => !isLive(o.status)),
    ],
    [visible]
  );

  function openCase(order) {
    navigate("/case", {
      state: {
        service: order.service,
        userType: user.type,
        orderId: order.id,
        order,
      },
    });
  }

  /** An order, as a row: what it was, what it cost, and the way in. */
  function toRow(order) {
    const status = statusOf(order.status);
    const route = orderRoute(order);
    const amount = money(order.price);
    const date = formatDate(order.date);
    const updates = Number(order.update_count) || 0;

    return {
      id: order.id,
      icon: <ServiceMark service={order.service} width={22} height={22} />,
      title: order.id,
      category: serviceFull(order.service),
      description: orderSummary(order),
      meta: (
        <>
          {amount && (
            <span className="font-semibold text-ink">{amount}</span>
          )}
          {date && (
            <>
              <Dot />
              <span>{date}</span>
            </>
          )}
          {route && (
            <>
              <Dot />
              <span className="truncate">
                {route.from} &rarr; {route.to}
              </span>
            </>
          )}
        </>
      ),
      status,
      actionLabel: "Report issue",
      onAction: () => openCase(order),
      secondaryLabel: updates > 0 ? `${updates} update${updates === 1 ? "" : "s"}` : null,
      onSecondary: () => setLogOrderId(order.id),
    };
  }

  if (!user) return null;

  return (
    <AppShell user={user}>
      <div className="w-full px-5 py-8 sm:px-8 lg:px-10 lg:py-12">
        {/* Masthead */}
        <motion.header
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-wrap items-end justify-between gap-6 border-b border-line pb-7"
        >
          <div>
            <Signage>{actorLabel(user.type)} console</Signage>
            <h1 className="mt-2 font-display text-[clamp(2rem,4vw,2.8rem)] font-800 leading-[0.95] tracking-tightest text-ink">
              {user.username}
            </h1>
            <p className="mt-2.5 max-w-md text-[14.5px] text-muted">
              Pick the order that went wrong. The resolution engine works the
              case and decides the outcome.
            </p>
          </div>
        </motion.header>

        {/* Counts */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
          className="grid grid-cols-3 divide-x divide-line border-b border-line"
        >
          <Tally label="Orders" value={counts.total} />
          <Tally label="In progress" value={counts.live} tone="amber" />
          <Tally label="Completed" value={counts.settled} tone="jade" />
        </motion.div>

        {/* Filter */}
        {services.length > 1 && (
          <div className="mt-7 flex flex-wrap items-center gap-2">
            <FilterChip
              active={filter === "all"}
              onClick={() => setFilter("all")}
            >
              All
            </FilterChip>
            {services.map((service) => (
              <FilterChip
                key={service}
                active={filter === service}
                onClick={() => setFilter(service)}
              >
                <ServiceMark service={service} width={15} height={15} />
                {serviceLabel(service)}
              </FilterChip>
            ))}
          </div>
        )}

        {/* Records */}
        <section className="mt-7" aria-label="Orders">
          {loading && (
            <div className="flex items-center gap-2.5 py-16 text-sm text-muted">
              <Spinner /> Loading your orders
            </div>
          )}

          {!loading && loadFailed && (
            <div className="panel p-8 text-center">
              <h2 className="font-display text-lg font-700 text-ink">
                Orders didn't load
              </h2>
              <p className="mx-auto mt-1.5 max-w-sm text-sm text-muted">
                The dispatch service didn't respond. Check that the backend is
                running on port 8000, then try again.
              </p>
              <Button intent="quiet" onClick={load} className="mt-5">
                Try again
              </Button>
            </div>
          )}

          {!loading && !loadFailed && visible.length === 0 && (
            <div className="panel p-10 text-center">
              <h2 className="font-display text-xl font-700 tracking-tightest text-ink">
                Nothing to show here
              </h2>
              <p className="mx-auto mt-2 max-w-sm text-sm text-muted">
                {orders.length === 0
                  ? "You have no orders on this account yet."
                  : `No ${serviceLabel(filter)} orders on this account.`}
              </p>
              {orders.length > 0 && filter !== "all" && (
                <Button
                  intent="quiet"
                  onClick={() => setFilter("all")}
                  className="mt-5"
                >
                  Show all orders
                </Button>
              )}
            </div>
          )}

          {!loading && visible.length > 0 && (
            <div className="space-y-10">
              {running.length > 0 && (
                <div>
                  <Signage className="mb-2">Still moving</Signage>
                  <List2 items={running.map(toRow)} dense />
                </div>
              )}

              {past.length > 0 && (
                <div>
                  {running.length > 0 && (
                    <Signage className="mb-2">Delivered and closed</Signage>
                  )}
                  <List2 items={past.map(toRow)} dense />
                </div>
              )}
            </div>
          )}
        </section>

        {/* Starting a case without an order lives in the sidebar now, under
            "Start a case" — repeating it here was the same door twice. */}
      </div>

      {logOrderId && (
        <OrderLog orderId={logOrderId} onClose={() => setLogOrderId(null)} />
      )}
    </AppShell>
  );
}

/**
 * Separates the facts on a row's meta line so they don't read as one string.
 * Purely a delimiter, so it's hidden from screen readers — the spacing between
 * the spans already separates them there.
 */
function Dot() {
  return (
    <span aria-hidden="true" className="text-[#8B9AA8]">
      &middot;
    </span>
  );
}

function Tally({ label, value, tone = "ink" }) {
  const tones = { ink: "text-ink", amber: "text-amber-deep", jade: "text-jade" };
  return (
    <div className="flex flex-col justify-between py-6 pr-4 first:pl-0 [&:not(:first-child)]:pl-5">
      {/* Reserve two lines so a wrapped label never drops its number below the row. */}
      <Signage className="min-h-[2.4em] leading-[1.2]">{label}</Signage>
      <div
        className={cx(
          "mt-1.5 font-display text-[34px] font-700 leading-none tracking-tightest tabular-nums",
          tones[tone]
        )}
      >
        {String(value).padStart(2, "0")}
      </div>
    </div>
  );
}

function FilterChip({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={cx(
        "inline-flex items-center gap-1.5 rounded-card border px-3 py-1.5 text-[13px] transition-colors",
        active
          ? "border-amber/50 bg-amber-wash text-amber-deep"
          : "border-line bg-panel text-muted hover:border-line-strong hover:text-ink"
      )}
    >
      {children}
    </button>
  );
}
