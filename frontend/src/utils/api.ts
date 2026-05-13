import type { ChatRequest } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const ADMIN_TOKEN = import.meta.env.VITE_ADMIN_TOKEN ?? ''

/**
 * Sends a chat message and streams the response token by token.
 * Calls onToken for each chunk, onDone when complete, onError on failure.
 */
export async function streamChat(
  req: ChatRequest,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    })
  } catch {
    onError('Cannot reach the backend. Make sure the server is running.')
    return
  }

  if (!response.ok) {
    onError(`Backend error: ${response.status} ${response.statusText}`)
    return
  }

  const reader = response.body?.getReader()
  if (!reader) {
    onError('Streaming not supported by this browser.')
    return
  }

  const decoder = new TextDecoder()
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      // Each chunk is a plain text token (backend sends text/event-stream)
      const text = decoder.decode(value, { stream: true })
      // Parse SSE lines: "data: <token>\n\n"
      for (const line of text.split('\n')) {
        if (line.startsWith('data: ')) {
          const token = line.slice(6)
          if (token === '[DONE]') break
          onToken(token)
        }
      }
    }
  } catch {
    onError('Stream interrupted unexpectedly.')
  } finally {
    onDone()
  }
}

/**
 * Sends a stop signal to gracefully shut down the backend server.
 */
export async function stopService(): Promise<{ ok: boolean; message: string }> {
  try {
    const res = await fetch(`${API_URL}/admin/stop`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${ADMIN_TOKEN}` },
    })
    const data = await res.json().catch(() => ({ message: 'No response body' }))
    return { ok: res.ok, message: data.message ?? 'Done' }
  } catch {
    return { ok: false, message: 'Could not reach the backend.' }
  }
}
