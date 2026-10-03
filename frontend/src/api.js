export const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function createSession() {
  const res = await fetch(`${API}/intake/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) {
    throw new Error(`Failed to create session: ${res.status} ${res.statusText}`)
  }
  return await res.json()
}

export async function sendChat(sessionId, message, turnNumber) {
  const res = await fetch(`${API}/intake/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      turn_number: turnNumber,
    }),
  })
  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.status} ${res.statusText}`)
  }
  return await res.json()
}

export async function uploadFile(sessionId, file) {
  const formData = new FormData()
  formData.append('session_id', sessionId)
  formData.append('file', file)

  const res = await fetch(`${API}/intake/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    throw new Error(`File upload failed: ${res.status} ${res.statusText}`)
  }
  return await res.json()
}

export async function triggerGeneration(sessionId) {
  const res = await fetch(`${API}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  if (!res.ok) {
    throw new Error(`Generation trigger failed: ${res.status} ${res.statusText}`)
  }
  return await res.json()
}

export async function fetchBRD(sessionId) {
  const res = await fetch(`${API}/brd/${sessionId}`)
  if (!res.ok) {
    throw new Error(`Fetch BRD failed: ${res.status} ${res.statusText}`)
  }
  return await res.json()
}

export async function fetchPDF(sessionId, view = 'investor') {
  const res = await fetch(`${API}/brd/${sessionId}/pdf?view=${encodeURIComponent(view)}`)
  if (!res.ok) {
    throw new Error(`Fetch PDF failed: ${res.status} ${res.statusText}`)
  }
  return await res.blob()
}
