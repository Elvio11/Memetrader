import React, { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  id: string;
  status?: 'streaming' | 'complete' | 'error';
  toolCalls?: Array<{
    name: string;
    args: any;
    result?: any;
  }>;
  reasoning?: string;
}

export default function ChatTab() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const [stopTokens, setStopTokens] = useState<AbortController | null>(null)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
      id: Math.random().toString(36).substr(2, 9)
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setStopTokens(new AbortController())

    try {
      const response = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'anthropic/claude-sonnet-4-20250514',
          messages: [{ role: 'user', content: input }],
          stream: true
        }),
        signal: stopTokens?.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      let assistantContent = ''
      let assistantMessage: Message | null = null
      let currentToolCalls: any[] = []
      let currentReasoning = ''

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = new TextDecoder().decode(value)
          
          if (chunk.includes('data: ')) {
            const data = chunk.split('data: ')[1]
            if (data && data !== '[DONE]') {
              try {
                const parsed = JSON.parse(data)
                const content = parsed.choices?.[0]?.delta?.content || ''
                const tool_calls = parsed.choices?.[0]?.delta?.tool_calls || []
                const reasoning = parsed.choices?.[0]?.delta?.reasoning || ''
                
                if (content) assistantContent += content
                if (tool_calls.length) currentToolCalls.push(...tool_calls)
                if (reasoning) currentReasoning += reasoning

                if (!assistantMessage) {
                  assistantMessage = {
                    role: 'assistant',
                    content: assistantContent,
                    timestamp: new Date(),
                    id: Math.random().toString(36).substr(2, 9),
                    toolCalls: currentToolCalls,
                    reasoning: currentReasoning
                  }
                  setMessages(prev => [...prev, assistantMessage!])
                } else {
                  setMessages(prev => {
                    const newMessages = [...prev]
                    const lastIdx = newMessages.length - 1
                    if (newMessages[lastIdx].role === 'assistant') {
                      newMessages[lastIdx] = {
                        ...newMessages[lastIdx],
                        content: assistantContent,
                        toolCalls: currentToolCalls,
                        reasoning: currentReasoning
                      }
                    }
                    return newMessages
                  })
                }
              } catch (e) {
                console.log('Parse error:', e)
              }
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Chat error:', error)
        const errorMessage: Message = {
          role: 'assistant',
          content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
          id: Math.random().toString(36).substr(2, 9),
          status: 'error'
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } finally {
      setIsLoading(false)
      setStopTokens(null)
    }
  }

  const stopGeneration = () => {
    if (stopTokens) {
      stopTokens.abort()
      setStopTokens(null)
    }
  }

  const retryLastMessage = () => {
    const lastUserMsg = messages.slice().reverse().find(m => m.role === 'user')
    if (lastUserMsg) {
      setInput(lastUserMsg.content)
      // Remove the last assistant message if exists
      const withoutLastAssistant = messages.filter((m, idx) => {
        return !(m.role === 'assistant' && idx === messages.length - 1 && 
                messages.slice(0, idx).reverse().find(m2 => m2.role === 'user'))
      })
      setMessages(withoutLastAssistant)
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-[600px] bg-gray-900 rounded-lg">
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user'
          const isAssistant = msg.role === 'assistant'
          
          return (
            <div key={msg.id} className={`mb-4 ${isUser ? 'text-right' : 'text-left'}`}>
              <div className={`inline-block p-3 rounded-lg max-w-[80%] ${
                isUser
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-100'
              }`}>
                <div className="whitespace-pre-wrap break-words">
                  {msg.content}
                </div>
                
                {isAssistant && msg.toolCalls && msg.toolCalls.length > 0 && (
                  <div className="mt-2">
                    <h4 className="text-xs font-medium text-blue-400 mb-1">Tool Calls:</h4>
                    <div className="space-y-1 text-xs bg-gray-800/50 p-2 rounded">
                      {msg.toolCalls.map((tc, tcIdx) => (
                        <div key={tcIdx} className="flex items-center gap-2">
                          <span className="font-mono">{tc.name}</span>
                          <span className="text-gray-400">{JSON.stringify(tc.args || {})}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {isAssistant && msg.reasoning && (
                  <div className="mt-2">
                    <h4 className="text-xs font-medium text-purple-400 mb-1">Reasoning:</h4>
                    <p className="text-xs text-gray-300 italic bg-gray-800/50 p-2 rounded">
                      {msg.reasoning}
                    </p>
                  </div>
                )}
              </div>
              
              <div className="text-xs text-gray-400 mt-1">
                {msg.timestamp.toLocaleTimeString()}
              </div>
              
              {isAssistant && !msg.status?.includes('error') && (
                <div className="flex gap-1 mt-1">
                  <button
                    onClick={() => copyMessage(msg.content)}
                    className="text-xs px-2 py-0.5 bg-gray-700 rounded hover:bg-gray-600"
                  >
                    Copy
                  </button>
                  {msg.status === 'streaming' && (
                    <button
                      onClick={stopGeneration}
                      className="text-xs px-2 py-0.5 bg-red-600 rounded hover:bg-red-500"
                    >
                      Stop
                    </button>
                  )}
                  <button
                    onClick={retryLastMessage}
                    className="text-xs px-2 py-0.5 bg-gray-700 rounded hover:bg-gray-600"
                  >
                    Retry
                  </button>
                </div>
              )}
            </div>
          )
        })}
        <div ref={scrollRef} />
      </div>
      
      <div className="flex gap-2 p-4 border-t border-gray-700">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1 p-2 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  )
}