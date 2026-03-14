const TOKEN_KEY = "token";
const PHONE_KEY = "phone";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getPhone(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(PHONE_KEY);
}

export function setPhone(phone: string): void {
  localStorage.setItem(PHONE_KEY, phone);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(PHONE_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}
