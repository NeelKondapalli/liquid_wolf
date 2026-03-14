import { getToken, setToken } from "./auth";
import type {
  User,
  AccountSummary,
  Call,
  CallDetail,
  Signal,
} from "./types";
import {
  mockUser,
  mockAccount,
  mockCalls,
  mockCallDetails,
  mockSignals,
  delay,
} from "./mock-data";

// In production, all API calls go through /api/* which Next.js rewrites to the
// backend (configured via server-only API_URL env var in next.config.ts).
// No CORS needed — browser only ever talks to its own origin.
const BASE = "/api";
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(BASE + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

// Mock state (mutable for demo interactions)
let mockSignalEnabled = true;

export const api = {
  sendCode: async (phone: string): Promise<{ success: boolean }> => {
    if (USE_MOCKS) {
      await delay();
      return { success: true };
    }
    return apiFetch("/auth/send-code", {
      method: "POST",
      body: JSON.stringify({ phone }),
    });
  },

  verifyCode: async (
    phone: string,
    code: string
  ): Promise<{ access_token: string }> => {
    if (USE_MOCKS) {
      await delay();
      if (code !== "000000") throw new Error("Invalid code");
      const token = "mock_jwt_" + Date.now();
      setToken(token);
      return { access_token: token };
    }
    const data = await apiFetch<{ access_token: string }>("/auth/verify", {
      method: "POST",
      body: JSON.stringify({ phone, code }),
    });
    setToken(data.access_token);
    return data;
  },

  saveKeys: async (
    liquid_api_key: string,
    liquid_api_secret: string
  ): Promise<{ success: boolean }> => {
    if (USE_MOCKS) {
      await delay();
      return { success: true };
    }
    return apiFetch("/users/keys", {
      method: "POST",
      body: JSON.stringify({ liquid_api_key, liquid_api_secret }),
    });
  },

  updateMe: async (
    data: Partial<{
      first_name: string;
      phone: string;
      character_id: string;
      signal_enabled: boolean;
    }>
  ): Promise<User> => {
    if (USE_MOCKS) {
      await delay();
      if (data.signal_enabled !== undefined) {
        mockSignalEnabled = data.signal_enabled;
      }
      return {
        ...mockUser,
        ...data,
        signal_enabled:
          data.signal_enabled !== undefined
            ? data.signal_enabled
            : mockSignalEnabled,
      };
    }
    return apiFetch("/users/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  getMe: async (): Promise<User> => {
    if (USE_MOCKS) {
      await delay();
      return { ...mockUser, signal_enabled: mockSignalEnabled };
    }
    return apiFetch("/users/me");
  },

  getAccount: async (): Promise<AccountSummary> => {
    if (USE_MOCKS) {
      await delay();
      return mockAccount;
    }
    return apiFetch("/account/summary");
  },

  getCalls: async (): Promise<Call[]> => {
    if (USE_MOCKS) {
      await delay();
      return mockCalls;
    }
    return apiFetch("/calls/history");
  },

  getCall: async (id: string): Promise<CallDetail> => {
    if (USE_MOCKS) {
      await delay();
      const detail = mockCallDetails[id];
      if (!detail) throw new Error("Call not found");
      return detail;
    }
    return apiFetch("/calls/" + id);
  },

  getSignals: async (): Promise<Signal[]> => {
    if (USE_MOCKS) {
      await delay();
      return mockSignals;
    }
    return apiFetch("/signals/active");
  },

  triggerDemo: async (
    symbol: string,
    direction: string,
    strength: number
  ): Promise<{ call_id: string }> => {
    if (USE_MOCKS) {
      await delay();
      return { call_id: "call_demo_" + Date.now() };
    }
    return apiFetch("/demo/trigger-call", {
      method: "POST",
      body: JSON.stringify({ symbol, direction, strength }),
    });
  },
};
