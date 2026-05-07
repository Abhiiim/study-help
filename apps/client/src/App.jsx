import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import OAuthCallbackPage from "./pages/OAuthCallbackPage";
import { useAuth } from "./contexts/AuthContext";

function LoadingScreen() {
  return (
    <main className="auth-shell">
      <section className="auth-card">
        <h1>Loading...</h1>
        <p className="muted">Checking your session.</p>
      </section>
    </main>
  );
}

export default function App() {
  const { isAuthenticated, isBootstrapping } = useAuth();

  const normalizedPath = window.location.pathname.replace(/\/+$/, "") || "/";

  if (normalizedPath === "/oauth/callback") {
    return <OAuthCallbackPage />;
  }

  if (isBootstrapping) {
    return <LoadingScreen />;
  }

  return isAuthenticated ? <DashboardPage /> : <AuthPage />;
}
