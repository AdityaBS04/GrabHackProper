import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import api, { currentUser } from "../services/api";
import AppShell from "../components/AppShell";
import CaseConsole from "../components/CaseConsole";
import ResolutionTrace from "../components/ResolutionTrace";
import { ServiceMark } from "../components/Marks";
import { Signage, Spinner } from "../components/primitives";
import { ChoiceList, EvidencePicker } from "../components/Conversation";
import RichText from "../components/RichText";
import { CaseChat } from "../components/ui/case-chat";
import { actorLabel, serviceFull } from "../lib/domain";

let seq = 0;
const nextId = () => `m${Date.now()}_${seq++}`;

export default function Case() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user] = useState(currentUser);
  const { service, userType, orderId, order } = location.state || {};

  const [entries, setEntries] = useState([]);
  const [category, setCategory] = useState(null);
  const [subIssue, setSubIssue] = useState(null);
  const [draft, setDraft] = useState("");
  const [working, setWorking] = useState(false);
  const [booting, setBooting] = useState(true);
  const [conversationId] = useState(() => `c${Date.now()}`);

  const endRef = useRef(null);
  const inputRef = useRef(null);

  const append = useCallback(
    (entry) => setEntries((prev) => [...prev, { id: nextId(), at: new Date(), ...entry }]),
    []
  );

  useEffect(() => {
    if (!user) {
      navigate("/signin", { replace: true });
    } else if (!service || !userType) {
      navigate("/dashboard", { replace: true });
    }
  }, [user, service, userType, navigate]);

  // Open the case: ask for a category.
  useEffect(() => {
    if (!service || !userType) return;
    let live = true;
    (async () => {
      try {
        const { data } = await api.get(`/categories/${service}/${userType}`);
        if (!live) return;
        const list = data.categories || [];
        append({
          kind: "engine",
          text: list.length
            ? `This case is open on ${serviceFull(service)}${
                orderId ? ` for order ${orderId}` : ""
              }. Start by telling me which area the problem falls in.`
            : `This case is open on ${serviceFull(service)}, but no issue categories are configured for it. Go back and pick another service.`,
          choices: list.length ? { label: "Choose an area", options: list, step: "category" } : null,
        });
      } catch {
        if (!live) return;
        append({
          kind: "engine",
          text: "The issue list didn't load. Check that the dispatch service is running, then reload this page.",
        });
      } finally {
        if (live) setBooting(false);
      }
    })();
    return () => {
      live = false;
    };
  }, [service, userType, orderId, append]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [entries, working]);

  async function pickCategory(option) {
    setCategory(option);
    setSubIssue(null);
    append({ kind: "operator", text: option.name });
    setWorking(true);
    try {
      const { data } = await api.get(
        `/subissues/${service}/${userType}/${option.id}`
      );
      const list = data.subissues || [];
      append({
        kind: "engine",
        text: list.length
          ? "Which of these matches what happened?"
          : "No specific issues are listed under that area. Pick a different one.",
        choices: list.length
          ? { label: "Choose the issue", options: list, step: "subissue" }
          : null,
      });
    } catch {
      append({
        kind: "engine",
        text: "That area's issue list didn't load. Choose it again, or pick a different area.",
      });
    } finally {
      setWorking(false);
    }
  }

  function pickSubIssue(option) {
    setSubIssue(option);
    append({ kind: "operator", text: option.name });
    append({
      kind: "engine",
      text: "Now describe what happened, in your own words. Include anything that pins it down — times, amounts, what you were told.",
    });
    setTimeout(() => inputRef.current?.focus(), 60);
  }

  async function send() {
    const message = draft.trim();
    if (!message || working || !subIssue) return;
    append({ kind: "operator", text: message });
    setDraft("");
    setWorking(true);
    try {
      const { data } = await api.post("/chat", {
        message,
        service,
        user_type: userType,
        username: user.username,
        conversation_id: conversationId,
        category: category?.id,
        sub_issue: subIssue?.id,
        order_id: orderId,
        messages: [],
      });
      append({
        kind: "engine",
        text: data.response || "The engine returned an empty reply. Send that again.",
        resolution: true,
        needsEvidence: Boolean(data.requires_image),
      });
    } catch {
      append({
        kind: "engine",
        text: "That didn't reach the resolution engine. Check your connection and send it again.",
      });
    } finally {
      setWorking(false);
    }
  }

  async function attachEvidence(dataUrl, name) {
    append({ kind: "evidence", src: dataUrl, name });
    setWorking(true);
    try {
      const { data } = await api.post("/chat/image", {
        image_data: dataUrl,
        service,
        user_type: userType,
        username: user.username,
        conversation_id: conversationId,
      });
      append({
        kind: "engine",
        text: data.response || "The photo was received.",
        resolution: true,
        needsEvidence: Boolean(data.requires_image),
      });
    } catch {
      append({
        kind: "engine",
        text: "The photo didn't upload. Try attaching it again.",
      });
    } finally {
      setWorking(false);
    }
  }

  const stage = useMemo(() => {
    if (!category) return "Choosing an area";
    if (!subIssue) return "Choosing the issue";
    return "Describing what happened";
  }, [category, subIssue]);

  /**
   * Case entries as chat rows. Choice lists and the attachment prompt stay
   * live only on the most recent reply, so an old prompt can't be re-answered.
   */
  const chatEntries = useMemo(() => {
    const lastEngineId = [...entries].reverse().find((e) => e.kind === "engine")?.id;

    return entries.map((entry) => {
      if (entry.kind === "operator") {
        return {
          id: entry.id,
          sender: "You",
          initials: (user?.username || "You").slice(0, 2).toUpperCase(),
          isOwn: true,
          at: entry.at,
          body: <p>{entry.text}</p>,
        };
      }

      if (entry.kind === "evidence") {
        return {
          id: entry.id,
          sender: "You",
          initials: (user?.username || "You").slice(0, 2).toUpperCase(),
          isOwn: true,
          at: entry.at,
          body: (
            <figure className="space-y-2">
              <img
                src={entry.src}
                alt={entry.name || "Attached evidence"}
                className="block max-h-64 w-full rounded-[2px] object-cover"
              />
              <figcaption className="font-mono text-[10.5px] text-faint">
                {entry.name || "photo"}
              </figcaption>
            </figure>
          ),
        };
      }

      const live = entry.id === lastEngineId;
      return {
        id: entry.id,
        sender: "Resolution engine",
        initials: "RE",
        isOwn: false,
        at: entry.at,
        resolution: entry.resolution,
        body: (
          <>
            <RichText text={entry.text} tone={entry.resolution ? "paper" : "ink"} />
            {entry.choices && live && (
              <ChoiceList
                label={entry.choices.label}
                options={entry.choices.options}
                disabled={working}
                onPick={
                  entry.choices.step === "category" ? pickCategory : pickSubIssue
                }
              />
            )}
            {entry.needsEvidence && live && (
              <EvidencePicker disabled={working} onAttach={attachEvidence} />
            )}
          </>
        ),
      };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entries, working, user]);

  if (!user || !service || !userType) return null;

  return (
    <AppShell user={user}>
      <div className="flex h-[calc(100vh-3.5rem)] flex-col md:h-screen">
        {/* Case header */}
        <header className="shrink-0 border-b border-line px-5 py-4 sm:px-8">
          <div className="flex w-full items-center gap-4">
            <button
              onClick={() => navigate("/dashboard")}
              className="grid h-9 w-9 shrink-0 place-items-center rounded-card border border-line text-muted transition-colors hover:bg-raised hover:text-ink"
              aria-label="Back to orders"
            >
              <ArrowLeft size={16} />
            </button>
            <div className="min-w-0 flex-1">
              <Signage>{stage}</Signage>
              <h1 className="mt-1 flex items-center gap-2.5 font-display text-[20px] font-700 leading-none tracking-tightest text-ink">
                <span className="text-amber-deep">
                  <ServiceMark service={service} width={18} height={18} />
                </span>
                <span className="truncate">{serviceFull(service)}</span>
                {orderId && (
                  <span className="shrink-0 font-mono text-[12px] font-400 text-faint">
                    {orderId}
                  </span>
                )}
              </h1>
            </div>
            <span className="hidden shrink-0 font-mono text-[11px] uppercase tracking-[0.12em] text-faint sm:block">
              {actorLabel(userType)}
            </span>
          </div>
        </header>

        <div className="flex w-full flex-1 gap-7 overflow-hidden px-5 sm:px-8 lg:px-10">
          {/* Transcript */}
          <div className="flex min-w-0 flex-1 flex-col">
            <CaseChat
              entries={chatEntries}
              draft={draft}
              onDraftChange={setDraft}
              onSend={send}
              disabled={!subIssue || working}
              busy={working}
              placeholder={
                subIssue
                  ? "Describe what happened"
                  : "Pick the issue above to start writing"
              }
              footer={
                <>
                  {booting && (
                    <div className="flex items-center gap-2.5 text-sm text-muted">
                      <Spinner /> Opening the case
                    </div>
                  )}
                  {/* On narrow screens the trace lives in the transcript. */}
                  {working && (
                    <motion.div
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="lg:hidden"
                    >
                      <ResolutionTrace compact />
                    </motion.div>
                  )}
                </>
              }
            />
          </div>

          {/* Case console */}
          <aside className="hidden w-[286px] shrink-0 overflow-y-auto py-6 lg:block">
            <CaseConsole
              service={service}
              userType={userType}
              order={order}
              orderId={orderId}
              category={category}
              subIssue={subIssue}
              working={working}
            />
          </aside>
        </div>
      </div>
    </AppShell>
  );
}

