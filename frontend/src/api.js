// src/api.js - Enhanced API Client with Timeout & Exponential Backoff

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    return response;
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

export async function createSession(data, retries = 2) {
  let attempt = 0;
  while (attempt <= retries) {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/api/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        throw new Error(`Session creation failed with status ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      if (attempt === retries) throw err;
      attempt++;
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)));
    }
  }
}

export async function fetchSession(sessionId) {
  const res = await fetchWithTimeout(`${API_BASE}/api/session/${sessionId}`);
  if (!res.ok) throw new Error(`Fetch session failed (${res.status})`);
  return await res.json();
}
