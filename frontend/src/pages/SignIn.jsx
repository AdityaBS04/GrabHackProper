import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Eye, EyeOff } from "lucide-react";
import api from "../services/api";
import { Button, Signage, Spinner } from "../components/primitives";
import { DispatchMark, ServiceMark } from "../components/Marks";
import { SERVICES } from "../lib/domain";

const DEMO = [
  { role: "Customer", username: "customer1", password: "pass123" },
  { role: "Driver", username: "driver1", password: "pass123" },
  { role: "Restaurant", username: "resto1", password: "pass123" },
];

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [reveal, setReveal] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const { data } = await api.post("/login", { username, password });
      if (!data?.success) {
        setError(data?.message || "That username and password don't match.");
        setBusy(false);
        return;
      }
      const u = data.user;
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: u.id,
          username: u.username,
          type: u.user_type,
          services: u.services || [],
        })
      );
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "That username and password don't match."
      );
      setBusy(false);
    }
  }

  function fillDemo(account) {
    setUsername(account.username);
    setPassword(account.password);
    setError("");
  }

  return (
    <div className="relative z-10 min-h-full lg:grid lg:grid-cols-[1.05fr_minmax(430px,0.95fr)]">
      {/* Left: the thesis. What this console is for, stated plainly. */}
      <section className="relative hidden overflow-hidden border-r border-line lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="flex items-center gap-2.5 text-amber-deep">
          <DispatchMark />
          <span className="font-display text-[15px] font-700 tracking-tightest text-ink">
            GrabHack
          </span>
          <span className="signage ml-1 mt-[2px]">Dispatch</span>
        </div>

        <div className="max-w-lg">
          <motion.h1
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="font-display text-[clamp(2.6rem,4.4vw,4rem)] font-800 leading-[0.94] tracking-tightest text-ink"
          >
            Every complaint
            <br />
            is a case with
            <br />
            <span className="text-amber-deep">a decision</span> at
            <br />
            the end of it.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
            className="mt-7 max-w-md text-[15px] leading-relaxed text-muted"
          >
            Report a problem on an order and the resolution engine works it the
            way a dispatcher would: identify the issue, check it against the
            record of the order, then decide — refund, replacement, escalation
            or explanation.
          </motion.p>

          {/* A worked case, on paper. Records are warm stock lying on a cool
              desk — and this is the first place you see that. */}
          <motion.figure
            initial={{ opacity: 0, y: 20, rotate: -1.6 }}
            animate={{ opacity: 1, y: 0, rotate: -1.1 }}
            transition={{ duration: 0.7, delay: 0.26, ease: [0.16, 1, 0.3, 1] }}
            className="paper mt-9 max-w-[380px] p-5"
          >
            <figcaption className="flex items-center justify-between border-b border-parchment-edge pb-2.5">
              <span className="font-mono text-[10px] uppercase tracking-signage text-parchment-dim">
                Specimen case
              </span>
              <span className="font-mono text-[10px] text-parchment-dim">
                GC-2291
              </span>
            </figcaption>

            <p className="mt-3 text-[14px] leading-snug text-[#3a3324]">
              Driver took an unauthorised detour. The rider was charged the
              longer fare.
            </p>

            <dl className="mt-3.5 grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-[10.5px]">
              <div>
                <dt className="text-parchment-dim">Deviation</dt>
                <dd className="text-parchment-ink">Not justified</dd>
              </div>
              <div>
                <dt className="text-parchment-dim">Fare charged</dt>
                <dd className="text-parchment-ink">$24.60</dd>
              </div>
            </dl>

            {/* The decision, stamped on. */}
            <div className="mt-4 inline-flex -rotate-2 items-center border-[1.5px] border-[#9a5f3c] px-2.5 py-1">
              <span className="font-display text-[12px] font-700 uppercase tracking-[0.14em] text-[#9a5f3c]">
                Fare refunded
              </span>
            </div>
          </motion.figure>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35, duration: 0.6 }}
          className="flex items-end justify-between"
        >
          <div>
            <Signage>Services covered</Signage>
            <div className="mt-3 flex items-center gap-5">
              {Object.keys(SERVICES).map((id) => (
                <div key={id} className="flex items-center gap-2 text-muted">
                  <ServiceMark service={id} width={19} height={19} />
                  <span className="font-mono text-[11px] uppercase tracking-[0.1em]">
                    {SERVICES[id].label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </section>

      {/* Right: the form, on its own lighter panel so the two halves separate
          without a heavy divider. */}
      <section className="flex min-h-full items-center justify-center bg-panel px-5 py-12 sm:px-10">
        <div className="w-full max-w-[400px]">
          <div className="mb-9 flex items-center gap-2.5 text-amber-deep lg:hidden">
            <DispatchMark />
            <span className="font-display text-[15px] font-700 tracking-tightest text-ink">
              GrabHack
            </span>
            <span className="signage ml-1 mt-[2px]">Dispatch</span>
          </div>

          <Signage>Sign in</Signage>
          <h2 className="mt-2 font-display text-[30px] font-700 leading-tight tracking-tightest text-ink">
            Open the console
          </h2>
          <p className="mt-2 text-sm text-muted">
            Your account decides which services and cases you can see.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="username" className="signage block">
                Username
              </label>
              <input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                autoCapitalize="none"
                spellCheck="false"
                required
                className="mt-2 h-11 w-full rounded-card border border-line bg-white px-3.5 font-mono text-sm text-ink placeholder:text-faint focus:border-amber-deep/70 focus:outline-none"
                placeholder="customer1"
              />
            </div>

            <div>
              <label htmlFor="password" className="signage block">
                Password
              </label>
              <div className="relative mt-2">
                <input
                  id="password"
                  type={reveal ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                  className="h-11 w-full rounded-card border border-line bg-white px-3.5 pr-11 font-mono text-sm text-ink placeholder:text-faint focus:border-amber-deep/70 focus:outline-none"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setReveal((v) => !v)}
                  aria-label={reveal ? "Hide password" : "Show password"}
                  className="absolute inset-y-0 right-0 grid w-11 place-items-center text-faint transition-colors hover:text-ink"
                >
                  {reveal ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                role="alert"
                className="rounded-card border border-clay/40 bg-clay-wash px-3 py-2.5 text-[13px] text-clay"
              >
                {error}
              </motion.p>
            )}

            <Button
              type="submit"
              size="lg"
              className="w-full"
              disabled={busy || !username || !password}
            >
              {busy ? (
                <>
                  <Spinner /> Signing in
                </>
              ) : (
                <>
                  Sign in <ArrowRight size={16} />
                </>
              )}
            </Button>
          </form>

          <div className="mt-9 border-t border-line pt-5">
            <Signage>Demo accounts</Signage>
            <div className="mt-3 grid gap-1.5">
              {DEMO.map((account) => (
                <button
                  key={account.username}
                  type="button"
                  onClick={() => fillDemo(account)}
                  className="group flex items-center justify-between rounded-card border border-line bg-panel px-3 py-2 text-left transition-colors hover:border-amber/40 hover:bg-panel"
                >
                  <span className="text-[13px] text-muted group-hover:text-ink">
                    {account.role}
                  </span>
                  <span className="font-mono text-[11px] text-faint">
                    {account.username} / {account.password}
                  </span>
                </button>
              ))}
            </div>
            <p className="mt-3 text-[12px] text-faint">
              Pick one to fill the form.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
