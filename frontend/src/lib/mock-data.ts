import type {
  User,
  AccountSummary,
  Call,
  CallDetail,
  Signal,
} from "./types";

export const mockUser: User = {
  id: "usr_01",
  first_name: "Alex",
  phone: "+1 555 867 5309",
  character_id: "belfort",
  signal_enabled: true,
};

export const mockAccount: AccountSummary = {
  equity: "52341.80",
  available_balance: "37891.40",
  margin_used: "14450.40",
  positions: [
    {
      symbol: "BTC-PERP",
      side: "long",
      size: "0.5",
      entry_price: "67250.00",
      mark_price: "68091.00",
      unrealized_pnl: "420.50",
      liquidation_price: "54600.00",
      leverage: "10",
    },
    {
      symbol: "ETH-PERP",
      side: "short",
      size: "5.0",
      entry_price: "3580.00",
      mark_price: "3597.04",
      unrealized_pnl: "-85.20",
      liquidation_price: "4296.00",
      leverage: "5",
    },
  ],
};

export const mockCalls: Call[] = [
  {
    id: "call_01",
    symbol: "BTC-PERP",
    character_id: "belfort",
    status: "completed",
    outcome: "executed",
    created_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
  },
  {
    id: "call_02",
    symbol: "ETH-PERP",
    character_id: "rick",
    status: "completed",
    outcome: "passed",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
  },
  {
    id: "call_03",
    symbol: "SOL-PERP",
    character_id: "trump",
    status: "missed",
    outcome: "missed",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
  },
];

export const mockCallDetails: Record<string, CallDetail> = {
  call_01: {
    id: "call_01",
    symbol: "BTC-PERP",
    character_id: "belfort",
    signal_data: {
      direction: "long",
      strength: 0.87,
      open: "67150.00",
      high: "68200.00",
      low: "66980.00",
      close: "68091.00",
    },
    status: "completed",
    outcome: "executed",
    order_id: "ord_8f3a2b1c",
    created_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
  },
  call_02: {
    id: "call_02",
    symbol: "ETH-PERP",
    character_id: "rick",
    signal_data: {
      direction: "short",
      strength: 0.64,
      open: "3590.00",
      high: "3610.00",
      low: "3565.00",
      close: "3597.04",
    },
    status: "completed",
    outcome: "passed",
    order_id: null,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
  },
  call_03: {
    id: "call_03",
    symbol: "SOL-PERP",
    character_id: "trump",
    signal_data: {
      direction: "long",
      strength: 0.72,
      open: "178.50",
      high: "183.20",
      low: "177.10",
      close: "181.90",
    },
    status: "missed",
    outcome: "missed",
    order_id: null,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
  },
};

export const mockSignals: Signal[] = [
  {
    symbol: "BTC-PERP",
    direction: "long",
    strength: 0.82,
    triggered_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
];

/** Simulate network latency */
export function delay(ms = 300): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
