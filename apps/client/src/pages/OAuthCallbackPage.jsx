import { useEffect, useRef, useState } from "react";

import { useAuth } from "../contexts/AuthContext";

export default function OAuthCallbackPage() {
  const { completeGoogleSignIn } = useAuth();
  const [error, setError] = useState("");
  const hasStarted = useRef(false);

  useEffect(() => {
    if (hasStarted.current) {
      return undefined;
    }

    hasStarted.current = true;
    let cancelled = false;

    async function finishOAuth() {
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");

      if (!token) {
        if (!cancelled) {
          setError("Google callback is missing required parameters.");
        }
        return;
      }

      try {
        window.history.replaceState({}, "", "/oauth/callback");
        await completeGoogleSignIn(token);
        if (!cancelled) {
          window.location.replace("/");
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError.message || "Google sign-in failed");
        }
      }
    }

    finishOAuth();

    return () => {
      cancelled = true;
    };
  }, [completeGoogleSignIn]);

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <h1>Completing Google sign-in...</h1>
        {error ? <p className="form-error">{error}</p> : <p className="muted">Please wait.</p>}
      </section>
    </main>
  );
}
