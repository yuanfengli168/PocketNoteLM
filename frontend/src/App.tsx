import { Header } from './components/Header'
import { ChatWindow } from './components/ChatWindow'
import { InputBar } from './components/InputBar'
import { useChat } from './hooks/useChat'
import { useSession } from './hooks/useSession'
import './App.css'

function App() {
  const sessionId = useSession()
  const { messages, isLoading, sendMessage, clearMessages } = useChat(sessionId)

  return (
    <div className="app">
      <Header onClear={clearMessages} />
      <ChatWindow messages={messages} isLoading={isLoading} />
      <InputBar onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}

export default App
