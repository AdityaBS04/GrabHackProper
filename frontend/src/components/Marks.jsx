import React from "react";

/**
 * Service marks, drawn rather than borrowed.
 *
 * One stroke weight, one geometric language, so four different services read as
 * one fleet. Each mark is the object the service actually moves.
 */

const base = {
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

/** A cloche: the dish arrives covered. */
export const FoodMark = (props) => (
  <svg {...base} {...props}>
    <path d="M3.4 16.6h17.2" />
    <path d="M5.2 16.6a6.8 6.8 0 0 1 13.6 0" />
    <path d="M12 9.9V8.4" />
    <circle cx="12" cy="7" r="1.05" />
  </svg>
);

/** A sedan in profile. */
export const CabsMark = (props) => (
  <svg {...base} {...props}>
    <path d="M4.6 15.4v-2.5a1.6 1.6 0 0 1 .5-1.16l1.35-1.24 1.5-2.9a1.8 1.8 0 0 1 1.6-.98h5a1.8 1.8 0 0 1 1.6.98l1.5 2.9 1.35 1.24a1.6 1.6 0 0 1 .5 1.16v2.5" />
    <path d="M6.45 10.5h11.1" />
    <circle cx="8.3" cy="15.8" r="1.6" />
    <circle cx="15.7" cy="15.8" r="1.6" />
  </svg>
);

/** A carry tote. */
export const MartMark = (props) => (
  <svg {...base} {...props}>
    <path d="M5.6 8.6h12.8l1 10.4a.9.9 0 0 1-.9 1H5.5a.9.9 0 0 1-.9-1z" />
    <path d="M9.1 8.6V7.2a2.9 2.9 0 0 1 5.8 0v1.4" />
  </svg>
);

/** A banded parcel. */
export const ExpressMark = (props) => (
  <svg {...base} {...props}>
    <rect x="4.1" y="7.4" width="15.8" height="11.2" rx="1.1" />
    <path d="M4.1 11.6h15.8" />
    <path d="M12 7.4v11.2" />
  </svg>
);

const MARKS = {
  grab_food: FoodMark,
  grab_cabs: CabsMark,
  grab_mart: MartMark,
  grab_express: ExpressMark,
};

export function ServiceMark({ service, ...props }) {
  const Mark = MARKS[service] || ExpressMark;
  return <Mark {...props} />;
}

/**
 * The dispatch mark: an origin node, a route, and an arrival arrow.
 * The whole product in one glyph — something leaves, something arrives.
 */
export const DispatchMark = ({ className = "", ...props }) => (
  <svg
    width="22"
    height="22"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.7"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    {...props}
  >
    <circle cx="5.8" cy="18.2" r="2.6" />
    <path d="M5.8 15.6V9.4A3.6 3.6 0 0 1 9.4 5.8h5.2" />
    <path d="m14.4 2.6 3.9 3.2-3.9 3.2" />
  </svg>
);
