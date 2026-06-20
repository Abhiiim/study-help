import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

function buildErrorMessage(error) {
  if (!error) {
    return "";
  }
  return error.message || "Something went wrong. Please try again.";
}

export default function AuthForm({
  mode,
  loading,
  error,
  notice,
  onModeChange,
  onSubmit,
  onGoogleSignIn,
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validationError, setValidationError] = useState("");

  const isSignup = mode === "signup";

  const heading = isSignup ? "Create account" : "Welcome back";
  const submitLabel = isSignup ? "Sign up" : "Log in";

  const activeError = useMemo(
    () => validationError || buildErrorMessage(error),
    [validationError, error],
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    setValidationError("");

    if (isSignup && password !== confirmPassword) {
      setValidationError("Passwords do not match");
      return;
    }

    await onSubmit({ email, password });
  };

  return (
    <div className="auth-card">
      <div className="auth-header">
        <p className="eyebrow">Personal Study Saver</p>
        <h1>{heading}</h1>
        <p className="muted">Use a Gmail account only</p>
      </div>

      <div className="auth-mode-toggle" role="tablist" aria-label="Auth mode">
        <button
          type="button"
          className={mode === "login" ? "active" : ""}
          onClick={() => onModeChange("login")}
        >
          Login
        </button>
        <button
          type="button"
          className={mode === "signup" ? "active" : ""}
          onClick={() => onModeChange("signup")}
        >
          Sign up
        </button>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <label>
          Email
          <input
            type="email"
            autoComplete="email"
            placeholder="you@gmail.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            autoComplete={isSignup ? "new-password" : "current-password"}
            placeholder="At least 8 characters"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            required
          />
        </label>

        {isSignup ? (
          <label>
            Confirm password
            <input
              type="password"
              autoComplete="new-password"
              placeholder="Repeat password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
        ) : (
          <Link to="/forgot-password" className="auth-forgot-link">
            Forgot password?
          </Link>
        )}

        {activeError ? <p className="form-error">{activeError}</p> : null}
        {!activeError && notice ? <p className="form-success">{notice}</p> : null}

        <button type="submit" className="primary-btn" disabled={loading}>
          {loading ? "Please wait..." : submitLabel}
        </button>
      </form>

      <div className="auth-divider">or</div>

      <button type="button" className="secondary-btn" onClick={onGoogleSignIn} disabled={loading}>
        Continue with Google
      </button>
    </div>
  );
}
