import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { resetPassword } from "../api/authApi";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await resetPassword({ token, password });
      setDone(true);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <main className="auth-shell">
        <div className="auth-card">
          <div className="auth-header">
            <p className="eyebrow">Personal Study Saver</p>
            <h1>Invalid link</h1>
            <p className="muted">
              This password reset link is invalid or has expired.
            </p>
          </div>
          <Link to="/forgot-password" className="primary-btn text-center">
            Request a new link
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <div className="auth-header">
          <p className="eyebrow">Personal Study Saver</p>
          <h1>Set new password</h1>
          <p className="muted">Enter your new password below.</p>
        </div>

        {done ? (
          <div className="auth-form">
            <p className="form-success">
              Your password has been reset successfully.
            </p>
            <Link to="/login" className="primary-btn text-center">
              Log in
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              New password
              <input
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </label>

            <label>
              Confirm password
              <input
                type="password"
                autoComplete="new-password"
                placeholder="Repeat password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                minLength={8}
                required
              />
            </label>

            {error ? <p className="form-error">{error}</p> : null}

            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? "Resetting..." : "Reset password"}
            </button>

            <Link to="/login" className="auth-back-link">
              ← Back to login
            </Link>
          </form>
        )}
      </div>
    </main>
  );
}
