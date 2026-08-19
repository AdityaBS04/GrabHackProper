import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutGrid,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  X,
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { DispatchMark, ServiceMark } from "./Marks";
import { cx } from "./primitives";
import { actorLabel, serviceFull } from "../lib/domain";
import { signOut } from "../services/api";

const STORAGE_KEY = "railExpanded";

/**
 * The console frame: a navigation rail on the left, work on the right.
 *
 * The rail collapses to icons and expands to named items. The choice sticks,
 * because which one you want depends on how well you know the console — and
 * that doesn't change between visits.
 */
export default function AppShell({ user, children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [expanded, setExpanded] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) !== "false";
    } catch {
      return true;
    }
  });
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(expanded));
    } catch {
      /* a rail preference isn't worth failing over */
    }
  }, [expanded]);

  // A route change on mobile means the drawer has done its job.
  useEffect(() => {
    setDrawerOpen(false);
  }, [location.pathname, location.key]);

  function handleSignOut() {
    signOut();
    navigate("/signin", { replace: true });
  }

  const services = user?.services || [];
  const onDashboard = location.pathname.startsWith("/dashboard");
  const activeService = location.state?.service;

  const nav = (
    <RailContents
      user={user}
      expanded={expanded}
      services={services}
      onDashboard={onDashboard}
      activeService={activeService}
      onNavigate={navigate}
      onSignOut={handleSignOut}
    />
  );

  return (
    <div className="relative z-10 flex min-h-full">
      {/* Rail. The column carries the background so it runs the full height of
          a long page; the nav inside it is what sticks. */}
      <div
        className={cx(
          "hidden shrink-0 border-r border-line bg-panel transition-[width] duration-200 md:block",
          expanded ? "w-[232px]" : "w-[68px]"
        )}
      >
        <nav
          aria-label="Main"
          className="sticky top-0 flex h-screen w-full flex-col py-5"
        >
          {nav}
          <button
            onClick={() => setExpanded((v) => !v)}
            aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
            aria-expanded={expanded}
            className={cx(
              "mt-3 flex h-9 items-center gap-2.5 rounded-card text-muted transition-colors hover:bg-raised hover:text-ink",
              expanded ? "mx-3 px-2.5" : "mx-auto w-10 justify-center"
            )}
          >
            {expanded ? (
              <PanelLeftClose size={17} />
            ) : (
              <PanelLeftOpen size={17} />
            )}
            {expanded && <span className="text-[13px]">Collapse</span>}
          </button>
        </nav>
      </div>

      {/* Mobile bar */}
      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center justify-between border-b border-line bg-panel/95 px-4 backdrop-blur md:hidden">
        <div className="flex min-w-0 items-center gap-1">
          <button
            onClick={() => setDrawerOpen(true)}
            aria-label="Open menu"
            className="grid h-9 w-9 shrink-0 place-items-center rounded-card text-muted hover:bg-raised hover:text-ink"
          >
            <Menu size={18} />
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 text-amber-deep"
          >
            <DispatchMark />
            <span className="font-display text-[14px] font-700 tracking-tightest text-ink">
              GrabHack
            </span>
          </button>
        </div>
        <div className="flex min-w-0 items-center gap-2">
          <span className="truncate font-mono text-[11px] text-faint">
            {user?.username}
          </span>
          <button
            onClick={handleSignOut}
            aria-label="Sign out"
            className="grid h-8 w-8 shrink-0 place-items-center rounded-card text-muted hover:bg-raised hover:text-ink"
          >
            <LogOut size={16} />
          </button>
        </div>
      </header>

      {/* Mobile drawer: the same rail, always named. */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDrawerOpen(false)}
              className="fixed inset-0 z-40 bg-ink/40 md:hidden"
            />
            <motion.nav
              aria-label="Main"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
              className="fixed inset-y-0 left-0 z-50 flex w-[248px] flex-col border-r border-line bg-panel py-5 md:hidden"
            >
              <button
                onClick={() => setDrawerOpen(false)}
                aria-label="Close menu"
                className="absolute right-3 top-4 grid h-8 w-8 place-items-center rounded-card text-muted hover:bg-raised hover:text-ink"
              >
                <X size={16} />
              </button>
              <RailContents
                user={user}
                expanded
                services={services}
                onDashboard={onDashboard}
                activeService={activeService}
                onNavigate={navigate}
                onSignOut={handleSignOut}
              />
            </motion.nav>
          </>
        )}
      </AnimatePresence>

      <main className="min-w-0 flex-1 pt-14 md:pt-0">{children}</main>
    </div>
  );
}

/** Shared between the desktop rail and the mobile drawer. */
function RailContents({
  user,
  expanded,
  services,
  onDashboard,
  activeService,
  onNavigate,
  onSignOut,
}) {
  return (
    <>
      <button
        onClick={() => onNavigate("/dashboard")}
        aria-label="GrabHack Dispatch home"
        className={cx(
          "flex items-center gap-2.5 rounded-card text-amber-deep transition-colors hover:bg-raised",
          expanded ? "mx-3 h-10 px-2.5" : "mx-auto h-10 w-10 justify-center"
        )}
      >
        <DispatchMark />
        {expanded && (
          <span className="whitespace-nowrap font-display text-[15px] font-700 tracking-tightest text-ink">
            GrabHack
          </span>
        )}
      </button>

      <div className="mt-7 flex flex-1 flex-col overflow-y-auto">
        {expanded && <RailLabel>Console</RailLabel>}
        <RailItem
          label="Orders"
          expanded={expanded}
          active={onDashboard}
          onClick={() => onNavigate("/dashboard")}
          icon={<LayoutGrid size={18} />}
        />

        {services.length > 0 && (
          <>
            {expanded && <RailLabel className="mt-5">Start a case</RailLabel>}
            {!expanded && <div className="my-3 mx-auto h-px w-6 bg-line" />}
            {services.map((service) => (
              <RailItem
                key={service}
                label={serviceFull(service)}
                expanded={expanded}
                active={activeService === service}
                onClick={() =>
                  onNavigate("/case", {
                    state: { service, userType: user?.type },
                  })
                }
                icon={<ServiceMark service={service} width={18} height={18} />}
              />
            ))}
          </>
        )}
      </div>

      <div className="mt-3 border-t border-line pt-3">
        <div
          className={cx(
            "flex items-center gap-2.5",
            expanded ? "mx-3 px-2.5" : "justify-center"
          )}
          title={`${user?.username} — ${actorLabel(user?.type)}`}
        >
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-line bg-raised font-display text-[13px] font-700 text-amber-deep">
            {(user?.username || "?").slice(0, 2).toUpperCase()}
          </span>
          {expanded && (
            <span className="min-w-0">
              <span className="block truncate text-[13px] font-medium text-ink">
                {user?.username}
              </span>
              <span className="block truncate font-mono text-[10px] uppercase tracking-[0.1em] text-faint">
                {actorLabel(user?.type)}
              </span>
            </span>
          )}
        </div>

        <RailItem
          label="Sign out"
          expanded={expanded}
          onClick={onSignOut}
          icon={<LogOut size={17} />}
          className="mt-2"
        />
      </div>
    </>
  );
}

function RailLabel({ children, className = "" }) {
  return (
    <div className={cx("signage mb-1.5 px-6", className)}>{children}</div>
  );
}

function RailItem({
  label,
  icon,
  expanded,
  active,
  onClick,
  className = "",
}) {
  return (
    <button
      onClick={onClick}
      title={expanded ? undefined : label}
      aria-label={label}
      aria-current={active ? "page" : undefined}
      className={cx(
        "relative flex h-10 items-center gap-2.5 rounded-card transition-colors",
        expanded ? "mx-3 px-2.5" : "mx-auto w-10 justify-center",
        active
          ? "bg-raised text-amber-deep"
          : "text-muted hover:bg-raised hover:text-ink",
        className
      )}
    >
      {active && (
        <span
          className={cx(
            "absolute h-5 w-[2px] rounded-full bg-amber",
            expanded ? "-left-3" : "-left-[13px]"
          )}
        />
      )}
      <span className="shrink-0">{icon}</span>
      {expanded && (
        <span className="truncate whitespace-nowrap text-[13.5px]">
          {label}
        </span>
      )}
    </button>
  );
}
