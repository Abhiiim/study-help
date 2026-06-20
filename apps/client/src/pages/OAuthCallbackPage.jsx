import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function OAuthCallbackPage() {
  const { completeGoogleSignIn } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const hasStarted = useRef(false);

  useEffect(() => {
    if (hasStarted.current) return;
    hasStarted.current = true;

    async function finishOAuth() {
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");

      if (!token) {
        setError("Google callback is missing required parameters.");
        return;
      }

      try {
        window.history.replaceState({}, "", "/oauth/callback");
        await completeGoogleSignIn(token);
        navigate("/dashboard", { replace: true });
      } catch (nextError) {
        setError(nextError.message || "Google sign-in failed");
      }
    }

    finishOAuth();
  }, [completeGoogleSignIn, navigate]);

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <h1>Completing Google sign-in...</h1>
        {error ? <p className="form-error">{error}</p> : <p className="muted">Please wait.</p>}
      </section>
    </main>
  );
}
