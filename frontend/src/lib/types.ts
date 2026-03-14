export interface User {
  id: string;
  first_name: string;
  phone: string;
  character_id: string | null;
  signal_enabled: boolean;
}

export interface Position {
  symbol: string;
  side: "long" | "short";
  size: string;
  entry_price: string;
  mark_price: string;
  unrealized_pnl: string;
  liquidation_price: string;
  leverage: string;
}

export interface AccountSummary {
  equity: string;
  available_balance: string;
  margin_used: string;
  positions: Position[];
}

export interface Call {
  id: string;
  symbol: string;
  character_id: string;
  status: "active" | "completed" | "missed";
  outcome: "executed" | "passed" | "missed" | null;
  created_at: string;
}

export interface SignalData {
  direction: string;
  strength: number;
  open: string;
  high: string;
  low: string;
  close: string;
}

export interface CallDetail {
  id: string;
  symbol: string;
  character_id: string;
  signal_data: SignalData;
  status: "active" | "completed" | "missed";
  outcome: "executed" | "passed" | "missed" | null;
  order_id: string | null;
  created_at: string;
}

export interface Signal {
  symbol: string;
  direction: "long" | "short";
  strength: number;
  triggered_at: string;
}

export interface Character {
  id: string;
  name: string;
  tagline: string;
  color: string;
}
