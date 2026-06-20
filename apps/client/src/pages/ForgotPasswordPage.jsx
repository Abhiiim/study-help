import { useState } from "react";
import { Link } from "react-router-dom";

import { forgotPassword } from "../api/authApi";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <div className="auth-header">
          <p className="eyebrow">Personal Study Saver</p>
          <h1>Reset your password</h1>
          <p className="muted">
            Enter your email and we'll send you a link to reset your password.
          </p>
        </div>

        {sent ? (
          <div className="auth-form">
            <p className="form-success">
              If an account exists for <strong>{email}</strong>, a reset link has been sent. Check your inbox.
            </p>
            <Link to="/login" className="primary-btn text-center">
              Back to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Email
              <input
                type="email"
                autoComplete="email"
                placeholder="you@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>

            {error ? <p className="form-error">{error}</p> : null}

            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? "Sending..." : "Send reset link"}
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
