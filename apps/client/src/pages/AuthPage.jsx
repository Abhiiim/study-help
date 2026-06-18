import { useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

import AuthForm from "../components/AuthForm";
import { useAuth } from "../contexts/AuthContext";

export default function AuthPage() {
  const location = useLocation();
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState("");

  const { login, signup, startGoogleSignIn } = useAuth();

  const verifiedNotice = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return params.get("verified") === "true" ? "Email verified. You can log in now." : "";
  }, [location.search]);

  const handleSubmit = async ({ email, password }) => {
    setLoading(true);
    setError(null);
    setNotice("");

    try {
      if (mode === "signup") {
        const payload = await signup({ email, password });
        setNotice(payload.message || "Verification email sent.");
        setMode("login");
      } else {
        await login({ email, password });
      }
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    setLoading(true);
    setError(null);
    setNotice("");

    try {
      await startGoogleSignIn();
    } catch (nextError) {
      setError(nextError);
      setLoading(false);
    }
  };

  const handleModeChange = (nextMode) => {
    setMode(nextMode);
    setError(null);
    setNotice("");
  };

  return (
    <main className="auth-shell">
      <AuthForm
        mode={mode}
        loading={loading}
        error={error}
        notice={notice || verifiedNotice}
        onModeChange={handleModeChange}
        onSubmit={handleSubmit}
        onGoogleSignIn={handleGoogle}
      />
    </main>
  );
}
