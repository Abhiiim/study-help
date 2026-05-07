import { useEffect, useState } from "react";

import { useAuth } from "../contexts/AuthContext";

export default function OAuthCallbackPage() {
  const { completeGoogleSignIn } = useAuth();
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function finishOAuth() {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      const state = params.get("state");

      if (!code || !state) {
        if (!cancelled) {
          setError("Google callback is missing required parameters.");
        }
        return;
      }

      try {
        await completeGoogleSignIn(code, state);
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
