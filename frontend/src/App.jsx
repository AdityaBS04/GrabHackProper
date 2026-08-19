import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import SignIn from "./pages/SignIn";
import Dashboard from "./pages/Dashboard";
import Case from "./pages/Case";
import { currentUser } from "./services/api";

/** Everything behind sign-in returns you here, remembering where you meant to go. */
function Protected({ children }) {
  const location = useLocation();
  if (!currentUser()) {
    return <Navigate to="/signin" replace state={{ from: location.pathname }} />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Navigate to={currentUser() ? "/dashboard" : "/signin"} replace />
          }
        />
        <Route path="/signin" element={<SignIn />} />
        <Route
          path="/dashboard"
          element={
            <Protected>
              <Dashboard />
            </Protected>
          }
        />
        <Route
          path="/case"
          element={
            <Protected>
              <Case />
            </Protected>
          }
        />
        {/* Links from the previous build still land somewhere sensible. */}
        <Route path="/login" element={<Navigate to="/signin" replace />} />
        <Route path="/complaint" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

function NotFound() {
  return (
    <div className="relative z-10 grid min-h-full place-items-center px-6 text-center">
      <div>
        <div className="signage">Not found</div>
        <h1 className="mt-3 font-display text-[42px] font-800 leading-none tracking-tightest text-ink">
          No such page
        </h1>
        <p className="mt-3 text-muted">
          That address doesn't match anything in the console.
        </p>
        <a
          href="/dashboard"
          className="mt-6 inline-flex h-10 items-center rounded-card bg-amber px-5 text-sm font-semibold text-ink hover:bg-amber-bright"
        >
          Go to your orders
        </a>
      </div>
    </div>
  );
}
