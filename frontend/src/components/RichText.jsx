import React from "react";

/**
 * Renders the resolution engine's replies.
 *
 * The engine writes plain text with light markdown — bold runs, bullets,
 * numbered steps and the occasional link. We parse it into real elements
 * rather than injecting HTML, so a reply can never carry markup into the page.
 */
/**
 * Some stored replies still decorate their headings and list items with emoji.
 * The console sets its own typographic tone, so they're dropped on the way in —
 * the words they sat next to always carry the meaning.
 */
/* Pictographs and dingbats only — arrows (U+2190–21FF) and bullets stay,
   since a reply may use them to mean something. */
const DECORATIVE = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}]/gu;

const strip = (value) =>
  String(value)
    .replace(DECORATIVE, "")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/^[ \t]+/gm, "");

export default function RichText({ text, tone = "ink" }) {
  if (!text) return null;

  const linkClass =
    tone === "paper"
      ? "font-medium text-[#8a5a11] underline underline-offset-2 hover:text-parchment-ink"
      : "font-medium text-amber-deep underline underline-offset-2 hover:text-ink";

  const blocks = strip(text)
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean);

  return (
    <div className="space-y-3">
      {blocks.map((block, i) => {
        const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);

        const bulleted = lines.every((l) => /^[-•*]\s+/.test(l));
        if (bulleted && lines.length > 0) {
          return (
            <ul key={i} className="space-y-1.5">
              {lines.map((line, j) => (
                <li key={j} className="flex gap-2.5">
                  <span
                    className={
                      tone === "paper"
                        ? "mt-[9px] h-[3px] w-[3px] shrink-0 rounded-full bg-parchment-dim"
                        : "mt-[9px] h-[3px] w-[3px] shrink-0 rounded-full bg-faint"
                    }
                  />
                  <span>
                    <Inline text={line.replace(/^[-•*]\s+/, "")} linkClass={linkClass} />
                  </span>
                </li>
              ))}
            </ul>
          );
        }

        const numbered = lines.every((l) => /^\d+[.)]\s+/.test(l));
        if (numbered && lines.length > 0) {
          return (
            <ol key={i} className="space-y-1.5">
              {lines.map((line, j) => {
                const [, num, rest] = line.match(/^(\d+)[.)]\s+(.*)$/) || [];
                return (
                  <li key={j} className="flex gap-2.5">
                    <span
                      className={
                        tone === "paper"
                          ? "font-mono text-[11px] leading-6 text-parchment-dim"
                          : "font-mono text-[11px] leading-6 text-faint"
                      }
                    >
                      {String(num).padStart(2, "0")}
                    </span>
                    <span>
                      <Inline text={rest} linkClass={linkClass} />
                    </span>
                  </li>
                );
              })}
            </ol>
          );
        }

        return (
          <p key={i} className="leading-relaxed">
            {lines.map((line, j) => (
              <React.Fragment key={j}>
                {j > 0 && <br />}
                <Inline text={line} linkClass={linkClass} />
              </React.Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
}

/** Bold runs and links, in one pass. */
function Inline({ text, linkClass }) {
  const pattern = /(\*\*[^*]+\*\*)|(https?:\/\/[^\s<>()]+)/g;
  const out = [];
  let last = 0;
  let match;
  let key = 0;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) out.push(text.slice(last, match.index));

    if (match[1]) {
      out.push(
        <strong key={key++} className="font-semibold">
          {match[1].slice(2, -2)}
        </strong>
      );
    } else if (match[2]) {
      const href = match[2].replace(/[.,;:]$/, "");
      out.push(
        <a
          key={key++}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className={linkClass}
        >
          {href}
        </a>
      );
      if (href.length < match[2].length) out.push(match[2].slice(href.length));
    }
    last = match.index + match[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return <>{out}</>;
}
