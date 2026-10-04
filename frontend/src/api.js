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

export async function fetchSession(sessionId) {
  const res = await fetch(`${API}/intake/session/${sessionId}`)
  if (!res.ok) {
    throw new Error(`Fetch session failed: ${res.status} ${res.statusText}`)
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

  // Pass session_id in query and form data for maximum compatibility
  const res = await fetch(`${API}/intake/upload?session_id=${encodeURIComponent(sessionId)}`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    throw new Error(`File upload failed: ${res.status} ${res.statusText}`)
  }
  return await res.json()
}

export async function triggerGeneration(sessionId) {
  // Pass session_id in query string for FastAPI scalar parameter and body for compatibility
  const res = await fetch(`${API}/generate?session_id=${encodeURIComponent(sessionId)}`, {
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
  const contentType = res.headers.get('content-type') || ''
  const contentDisposition = res.headers.get('content-disposition') || ''
  let serverFilename = null
  if (contentDisposition) {
    const match = contentDisposition.match(/filename=["']?([^"';]+)["']?/)
    if (match?.[1]) {
      serverFilename = match[1].trim()
    }
  }

  if (contentType.includes('application/pdf') || contentType.includes('octet-stream')) {
    const blob = await res.blob()
    if (serverFilename) {
      blob.suggestedFilename = serverFilename
    }
    return blob
  }
  const json = await res.json()
  if (serverFilename && json) {
    json.suggestedFilename = serverFilename
  }
  return json
}

export async function fetchPresetCacheStatus() {
  const res = await fetch(`${API}/presets/cache`)
  if (!res.ok) {
    throw new Error(`Failed to fetch preset cache status: ${res.status}`)
  }
  return await res.json()
}

export async function launchInstantDemo(preset = 'b2b_code_review') {
  const res = await fetch(`${API}/presets/instant-demo?preset=${encodeURIComponent(preset)}`, {
    method: 'POST',
  })
  if (!res.ok) {
    throw new Error(`Failed to launch instant demo: ${res.status}`)
  }
  return await res.json()
}
