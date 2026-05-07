import { useState } from "react";

import AuthForm from "../components/AuthForm";
import { useAuth } from "../contexts/AuthContext";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { login, signup, startGoogleSignIn } = useAuth();

  const handleSubmit = async ({ email, password }) => {
    setLoading(true);
    setError(null);

    try {
      if (mode === "signup") {
        await signup({ email, password });
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

    try {
      await startGoogleSignIn();
    } catch (nextError) {
      setError(nextError);
      setLoading(false);
    }
  };

  return (
    <main className="auth-shell">
      <AuthForm
        mode={mode}
        loading={loading}
        error={error}
        onModeChange={setMode}
        onSubmit={handleSubmit}
        onGoogleSignIn={handleGoogle}
      />
    </main>
  );
}
