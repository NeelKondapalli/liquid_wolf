import { getToken, setToken, getPhone } from "./auth";
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

const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

// ─── Legacy apiFetch (for Next.js auth routes) ─────────────────────
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch("/api" + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ─── Backend fetch (proxied through /api/v1/*) ─────────────────────
async function backendFetch<T>(
  path: string,
  body: Record<string, unknown>
): Promise<T> {
  const res = await fetch(`/api/v1/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Backend request failed: ${res.status}`);
  }
  const json = await res.json();
  if (!json.success) {
    throw new Error(json.error || "Backend returned failure");
  }
  return json.data;
}

// Mock state
let mockSignalEnabled = true;

export const api = {
  // ─── OTP (hits our Next.js Twilio routes) ───────────────────────
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

  // ─── User management (backend) ─────────────────────────────────
  checkUserExists: async (
    phone: string
  ): Promise<{ exists: boolean }> => {
    if (USE_MOCKS) {
      await delay();
      return { exists: false };
    }
    return backendFetch("user/check", { phone_number: phone });
  },

  createUser: async (
    phone: string
  ): Promise<{ created: boolean }> => {
    if (USE_MOCKS) {
      await delay();
      return { created: true };
    }
    return backendFetch("user/create", { phone_number: phone });
  },

  checkUserHasKeys: async (
    phone: string
  ): Promise<{ has_keys: boolean }> => {
    if (USE_MOCKS) {
      await delay();
      return { has_keys: false };
    }
    return backendFetch("user/has_keys", { phone_number: phone });
  },

  saveKeys: async (
    phone: string,
    apiKey: string,
    apiSecret: string
  ): Promise<{ saved: boolean }> => {
    if (USE_MOCKS) {
      await delay();
      return { saved: true };
    }
    return backendFetch("user/save_keys", {
      phone_number: phone,
      api_key: apiKey,
      api_secret: apiSecret,
    });
  },

  // ─── Account (backend) ─────────────────────────────────────────
  getAccountInfo: async (phone: string): Promise<AccountSummary> => {
    if (USE_MOCKS) {
      await delay();
      return mockAccount;
    }
    return backendFetch("account/info", { phone_number: phone });
  },

  getPositions: async (phone: string): Promise<AccountSummary["positions"]> => {
    if (USE_MOCKS) {
      await delay();
      return mockAccount.positions;
    }
    return backendFetch("account/positions", { phone_number: phone });
  },

  // ─── User profile (backend) ────────────────────────────────────
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
    const phone = getPhone() || "";
    try {
      return await backendFetch("user/update", {
        phone_number: phone,
        ...data,
      });
    } catch {
      // Backend endpoint may not exist yet — return local state
      return { ...mockUser, ...data, phone };
    }
  },

  getMe: async (): Promise<User> => {
    if (USE_MOCKS) {
      await delay();
      return { ...mockUser, signal_enabled: mockSignalEnabled };
    }
    const phone = getPhone() || "";
    try {
      return await backendFetch("user/me", { phone_number: phone });
    } catch {
      // Backend endpoint may not exist yet — return local fallback
      return {
        id: "user",
        first_name: "",
        phone,
        character_id: "belfort",
        signal_enabled: true,
      };
    }
  },

  getAccount: async (): Promise<AccountSummary> => {
    const phone = getPhone() || "";
    return api.getAccountInfo(phone);
  },

  // ─── Calls & signals (backend) ───────────────────────────────────
  getCalls: async (): Promise<Call[]> => {
    if (USE_MOCKS) {
      await delay();
      return mockCalls;
    }
    const phone = getPhone() || "";
    try {
      return await backendFetch("calls/history", { phone_number: phone });
    } catch {
      return [];
    }
  },

  getCall: async (id: string): Promise<CallDetail> => {
    if (USE_MOCKS) {
      await delay();
      const detail = mockCallDetails[id];
      if (!detail) throw new Error("Call not found");
      return detail;
    }
    const phone = getPhone() || "";
    return backendFetch(`calls/${id}`, { phone_number: phone });
  },

  getSignals: async (): Promise<Signal[]> => {
    if (USE_MOCKS) {
      await delay();
      return mockSignals;
    }
    const phone = getPhone() || "";
    try {
      return await backendFetch("signals/active", { phone_number: phone });
    } catch {
      return [];
    }
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
    return { call_id: "call_demo_" + Date.now() };
  },
};
