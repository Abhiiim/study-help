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

const AuthContext = createContext(null);
let sharedRefreshPromise = null;

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  const clearSession = useCallback(() => {
    setAccessToken(null);
    setUser(null);
  }, []);

  const applyAuthResponse = useCallback((payload) => {
    setAccessToken(payload.access_token);
    setUser(payload.user);
    return payload;
  }, []);

  const refreshSession = useCallback(async () => {
    if (!sharedRefreshPromise) {
      sharedRefreshPromise = refreshAuthToken().finally(() => {
        sharedRefreshPromise = null;
      });
    }

    try {
      const payload = await sharedRefreshPromise;
      applyAuthResponse(payload);
      return payload;
    } catch (error) {
      clearSession();
      throw error;
    }
  }, [applyAuthResponse, clearSession]);

  const withAuth = useCallback(
    async (requestFn) => {
      let token = accessToken;

      if (!token) {
        const refreshed = await refreshSession();
        token = refreshed.access_token;
      }

      try {
        return await requestFn(token);
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 401) {
          throw error;
        }

        const refreshed = await refreshSession();
        return requestFn(refreshed.access_token);
      }
    },
    [accessToken, refreshSession],
  );

  const signup = useCallback(
    async ({ email, password }) => {
      const payload = await signupRequest({ email, password });
      return payload;
    },
    [],
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
    async (token) => {
      const payload = await completeGoogleOAuth(token);
      applyAuthResponse(payload);
      return payload.user;
    },
    [applyAuthResponse],
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest(accessToken, undefined);
    } catch (error) {
      // Local logout should still complete if the API call fails.
    } finally {
      clearSession();
    }
  }, [accessToken, clearSession]);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const refreshed = await refreshSession();
        const profile = await fetchMe(refreshed.access_token);
        if (!cancelled) {
          setUser(profile);
        }
      } catch (error) {
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
  }, [clearSession, refreshSession]);

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
