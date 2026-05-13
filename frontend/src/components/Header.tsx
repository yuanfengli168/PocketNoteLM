import { useState } from 'react'
import { stopService } from '../utils/api'
import styles from './Header.module.css'

interface Props {
  onClear: () => void
}

export function Header({ onClear }: Props) {
  const [stopping, setStopping] = useState(false)
  const [stopMsg, setStopMsg] = useState<string | null>(null)

  async function handleStop() {
    if (!confirm('Stop the backend server? This will take the chatbot offline.')) return
    setStopping(true)
    const result = await stopService()
    setStopMsg(result.message)
    setStopping(false)
    setTimeout(() => setStopMsg(null), 4000)
  }

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <span className={styles.logo}>🧩</span>
        <span className={styles.title}>PocketNoteLM</span>
      </div>
      <div className={styles.right}>
        {stopMsg && <span className={styles.stopMsg}>{stopMsg}</span>}
        <button className={styles.clearBtn} onClick={onClear} title="Clear chat">
          New chat
        </button>
        <button
          className={styles.stopBtn}
          onClick={handleStop}
          disabled={stopping}
          title="Stop backend server"
        >
          {stopping ? 'Stopping…' : '⏹ Stop Service'}
        </button>
      </div>
    </header>
  )
}
