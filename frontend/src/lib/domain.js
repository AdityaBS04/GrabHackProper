/**
 * The vocabulary of the platform, in one place.
 *
 * Everything the interface says about a service, an actor or an order status is
 * derived here, so a status never renders one way on the dashboard and another
 * way inside a case.
 */

export const SERVICES = {
  grab_food: { label: "Food", full: "Grab Food", unit: "order" },
  grab_cabs: { label: "Cabs", full: "Grab Cabs", unit: "ride" },
  grab_mart: { label: "Mart", full: "Grab Mart", unit: "order" },
  grab_express: { label: "Express", full: "Grab Express", unit: "consignment" },
};

export const ACTORS = {
  customer: "Customer",
  driver: "Driver",
  delivery_agent: "Delivery agent",
  restaurant: "Restaurant",
  darkstore: "Dark store",
  dark_house: "Dark store",
  express_delivery_partner: "Express partner",
};

/** Order status → the tone it carries and the word we show. */
const STATUS = {
  completed: { label: "Completed", tone: "jade" },
  in_progress: { label: "In progress", tone: "amber" },
  active: { label: "Active", tone: "amber" },
  assigned: { label: "Assigned", tone: "amber" },
  preparing: { label: "Preparing", tone: "amber" },
  delivering: { label: "Delivering", tone: "amber" },
  pending: { label: "Pending", tone: "slate" },
  cancelled: { label: "Cancelled", tone: "clay" },
  failed: { label: "Failed", tone: "clay" },
};

const LIVE = new Set([
  "in_progress",
  "active",
  "assigned",
  "preparing",
  "delivering",
]);

export const serviceLabel = (id) => SERVICES[id]?.label ?? titleCase(id);
export const serviceFull = (id) => SERVICES[id]?.full ?? titleCase(id);
export const actorLabel = (id) => ACTORS[id] ?? titleCase(id);

export function statusOf(status) {
  const key = String(status || "").toLowerCase();
  return STATUS[key] ?? { label: titleCase(key) || "Unknown", tone: "slate" };
}

export const isLive = (status) => LIVE.has(String(status || "").toLowerCase());
export const isSettled = (status) =>
  String(status || "").toLowerCase() === "completed";

export function titleCase(value) {
  return String(value || "")
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

export function money(amount) {
  if (amount === null || amount === undefined || Number.isNaN(Number(amount))) {
    return null;
  }
  return `$${Number(amount).toFixed(2)}`;
}

/** What this order actually was — the line a person would recognise it by. */
export function orderSummary(order) {
  if (order.food_items) return order.food_items;
  if (order.products_ordered) return order.products_ordered;
  if (order.cab_type) return `${titleCase(order.cab_type)} ride`;
  if (order.restaurant_name) return order.restaurant_name;
  return SERVICES[order.service]?.unit
    ? titleCase(SERVICES[order.service].unit)
    : "Order";
}

/** Where it went, when both ends are known. */
export function orderRoute(order) {
  const from = shortenAddress(order.start_address);
  const to = shortenAddress(order.end_address);
  if (from && to) return { from, to };
  return null;
}

function shortenAddress(address) {
  if (!address) return null;
  return String(address).split(",")[0].trim() || null;
}

export function formatDate(value) {
  if (!value) return null;
  const date = new Date(String(value).replace(" ", "T"));
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatTime(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function formatStamp(value) {
  if (!value) return "";
  const date = new Date(String(value).replace(" ", "T"));
  if (Number.isNaN(date.getTime())) return String(value);
  return date
    .toLocaleString(undefined, {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    })
    .replace(",", "");
}

/**
 * The stages the resolution engine runs for a case, in order.
 *
 * These are the real steps in the server-side handler workflow — identify the
 * issue, check it against records and evidence, weigh the account's standing,
 * decide, then write the outcome. We show them while the request is in flight
 * so the wait explains itself instead of spinning.
 */
export const RESOLUTION_STAGES = [
  { key: "identify", label: "Identify issue" },
  { key: "verify", label: "Check records" },
  { key: "account", label: "Review account" },
  { key: "decide", label: "Decide outcome" },
  { key: "compose", label: "Write resolution" },
];
