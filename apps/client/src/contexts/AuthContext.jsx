import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import {
  completeGoogleOAuth,
  fetchMe,
  login as loginRequest,
  logout as logoutRequest,
  refreshAuthToken,
  signup as signupRequest,
  startGoogleOAuth,
} from "../api/authApi";
import { ApiError } from "../api/http";

const ACCESS_TOKEN_KEY = "study_saver_access_token";
const REFRESH_TOKEN_KEY = "study_saver_refresh_token";

function getStoredSession() {
  return {
    accessToken: window.localStorage.getItem(ACCESS_TOKEN_KEY),
    refreshToken: window.localStorage.getItem(REFRESH_TOKEN_KEY),
  };
}

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSessionState] = useState(getStoredSession);
  const [user, setUser] = useState(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  const clearSession = useCallback(() => {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    setSessionState({ accessToken: null, refreshToken: null });
    setUser(null);
  }, []);

  const setSession = useCallback((nextSession, nextUser) => {
    if (nextSession.accessToken) {
      window.localStorage.setItem(ACCESS_TOKEN_KEY, nextSession.accessToken);
    } else {
      window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    }

    if (nextSession.refreshToken) {
      window.localStorage.setItem(REFRESH_TOKEN_KEY, nextSession.refreshToken);
    } else {
      window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    }

    setSessionState(nextSession);
    if (nextUser !== undefined) {
      setUser(nextUser);
    }
  }, []);

  const applyAuthResponse = useCallback(
    (payload) => {
      setSession(
        {
          accessToken: payload.access_token,
          refreshToken: payload.refresh_token,
        },
        payload.user,
      );
      return payload;
    },
    [setSession],
  );

  const refreshSession = useCallback(
    async (refreshTokenOverride) => {
      const refreshToken = refreshTokenOverride || session.refreshToken;
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      try {
        const payload = await refreshAuthToken({ refresh_token: refreshToken });
        applyAuthResponse(payload);
        return payload;
      } catch (error) {
        clearSession();
        throw error;
      }
    },
    [applyAuthResponse, clearSession, session.refreshToken],
  );

  const withAuth = useCallback(
    async (requestFn) => {
      let accessToken = session.accessToken;

      if (!accessToken && session.refreshToken) {
        const refreshed = await refreshSession(session.refreshToken);
        accessToken = refreshed.access_token;
      }

      if (!accessToken) {
        throw new Error("Not authenticated");
      }

      try {
        return await requestFn(accessToken);
      } catch (error) {
        const shouldRetry = error instanceof ApiError && error.status === 401 && session.refreshToken;
        if (!shouldRetry) {
          throw error;
        }

        const refreshed = await refreshSession(session.refreshToken);
        return requestFn(refreshed.access_token);
      }
    },
    [refreshSession, session.accessToken, session.refreshToken],
  );

  const signup = useCallback(
    async ({ email, password }) => {
      const payload = await signupRequest({ email, password });
      applyAuthResponse(payload);
      return payload.user;
    },
    [applyAuthResponse],
  );

  const login = useCallback(
    async ({ email, password }) => {
      const payload = await loginRequest({ email, password });
      applyAuthResponse(payload);
      return payload.user;
    },
    [applyAuthResponse],
  );

  const startGoogleSignIn = useCallback(async () => {
    const payload = await startGoogleOAuth();
    window.location.assign(payload.authorize_url);
  }, []);

  const completeGoogleSignIn = useCallback(
    async (code, state) => {
      const payload = await completeGoogleOAuth(code, state);
      applyAuthResponse(payload);
      return payload.user;
    },
    [applyAuthResponse],
  );

  const logout = useCallback(
    async ({ logoutAll = false } = {}) => {
      try {
        if (session.accessToken) {
          await logoutRequest(session.accessToken, {
            refresh_token: session.refreshToken,
            logout_all: logoutAll,
          });
        }
      } catch (error) {
        // Ignore logout API errors because local logout should always complete.
      } finally {
        clearSession();
      }
    },
    [clearSession, session.accessToken, session.refreshToken],
  );

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      const hasAnyToken = session.accessToken || session.refreshToken;
      if (!hasAnyToken) {
        if (!cancelled) {
          setIsBootstrapping(false);
        }
        return;
      }

      try {
        let accessToken = session.accessToken;
        if (!accessToken && session.refreshToken) {
          const refreshed = await refreshSession(session.refreshToken);
          accessToken = refreshed.access_token;
        }

        if (!accessToken) {
          throw new Error("No access token available");
        }

        const profile = await fetchMe(accessToken);
        if (!cancelled) {
          setUser(profile);
        }
      } catch (error) {
        if (session.refreshToken) {
          try {
            const refreshed = await refreshSession(session.refreshToken);
            const profile = await fetchMe(refreshed.access_token);
            if (!cancelled) {
              setUser(profile);
            }
            return;
          } catch (refreshError) {
            // Fall through to clear local session.
          }
        }

        if (!cancelled) {
          clearSession();
        }
      } finally {
        if (!cancelled) {
          setIsBootstrapping(false);
        }
      }
    }

    bootstrap();

    return () => {
      cancelled = true;
    };
  }, [clearSession, refreshSession, session.accessToken, session.refreshToken]);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isBootstrapping,
      signup,
      login,
      startGoogleSignIn,
      completeGoogleSignIn,
      logout,
      withAuth,
    }),
    [user, isBootstrapping, signup, login, startGoogleSignIn, completeGoogleSignIn, logout, withAuth],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
