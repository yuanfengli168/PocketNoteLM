import { useEffect, useState } from 'react'

const SESSION_KEY = 'pocketnotelm_session_id'

function generateId(): string {
  return crypto.randomUUID()
}

export function useSession(): string {
  const [sessionId] = useState<string>(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) return stored
    const id = generateId()
    localStorage.setItem(SESSION_KEY, id)
    return id
  })

  useEffect(() => {
    localStorage.setItem(SESSION_KEY, sessionId)
  }, [sessionId])

  return sessionId
}
