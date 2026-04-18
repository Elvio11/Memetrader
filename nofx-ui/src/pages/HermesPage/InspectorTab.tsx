import React, { useEffect, useState } from 'react'

interface ToolCall {
  id: string
  name: string
  arguments: string
  result?: string
  startTime: number
  endTime?: number
  error?: string
}

interface InspectorState {
  toolCalls: ToolCall[]
  decisions: string[]
  errors: string[]
}

export default function InspectorTab() {
  const [state, setState] = useState<InspectorState>({
    toolCalls: [],
    decisions: [],
    errors: []
  })
  const [expandedTool, setExpandedTool] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'tools' | 'errors'>('all')

  const fetchInspectorData = async () => {
    try {
      const response = await fetch('/api/inspector/state')
      if (response.ok) {
        const data = await response.json()
        setState({
          toolCalls: data.toolCalls || [],
          decisions: data.decisions || [],
          errors: data.errors || []
        })
      }
    } catch (error) {
      console.error('Failed to load inspector data', error)
    }
  }

  useEffect(() => {
    fetchInspectorData()
    const interval = setInterval(fetchInspectorData, 2000)
    return () => clearInterval(interval)
  }, [])

  const getDuration = (start: number, end?: number) => {
    if (!end) return 'running...'
    return `${(end - start).toFixed(0)}ms`
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const filteredTools = state.toolCalls.filter(tc => {
    if (filter === 'errors') return tc.error
    return true
  })

  return (
    <div className="p-4 text-white space-y-6">
      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Inspector</h2>
        <p className="mt-2 text-sm text-gray-300">View tool calls, timing, decisions, and errors from the current session.</p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded text-sm ${filter === 'all' ? 'bg-blue-600' : 'bg-gray-700'}`}
        >
          All ({state.toolCalls.length})
        </button>
        <button
          onClick={() => setFilter('tools')}
          className={`px-3 py-1 rounded text-sm ${filter === 'tools' ? 'bg-blue-600' : 'bg-gray-700'}`}
        >
          Tools ({state.toolCalls.filter(t => !t.error).length})
        </button>
        <button
          onClick={() => setFilter('errors')}
          className={`px-3 py-1 rounded text-sm ${filter === 'errors' ? 'bg-red-600' : 'bg-gray-700'}`}
        >
          Errors ({state.errors.length})
        </button>
      </div>

      <div className="rounded-xl border border-gray-700 bg-black/50 p-4">
        <h3 className="text-lg font-semibold mb-4">Tool Calls</h3>
        
        {filteredTools.length === 0 ? (
          <p className="text-gray-400 text-sm">No tool calls in this session.</p>
        ) : (
          <div className="space-y-3">
            {filteredTools.map((tc) => (
              <div key={tc.id} className={`rounded-lg border ${tc.error ? 'border-red-700 bg-red-900/20' : 'border-gray-700 bg-gray-800/50'} p-3`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm text-blue-400">{tc.name}</span>
                    <span className="text-xs text-gray-500">{getDuration(tc.startTime, tc.endTime)}</span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setExpandedTool(expandedTool === tc.id ? null : tc.id)}
                      className="text-xs px-2 py-1 bg-gray-700 rounded hover:bg-gray-600"
                    >
                      {expandedTool === tc.id ? 'Collapse' : 'Expand'}
                    </button>
                    <button
                      onClick={() => copyToClipboard(tc.arguments)}
                      className="text-xs px-2 py-1 bg-gray-700 rounded hover:bg-gray-600"
                    >
                      Copy
                    </button>
                  </div>
                </div>

                {expandedTool === tc.id && (
                  <div className="mt-3 space-y-2">
                    <div>
                      <span className="text-xs text-gray-400">Arguments:</span>
                      <pre className="mt-1 text-xs bg-black p-2 rounded overflow-x-auto text-gray-300">
                        {JSON.stringify(JSON.parse(tc.arguments || '{}'), null, 2)}
                      </pre>
                    </div>
                    {tc.result && (
                      <div>
                        <span className="text-xs text-gray-400">Result:</span>
                        <pre className="mt-1 text-xs bg-black p-2 rounded overflow-x-auto text-green-400 max-h-40">
                          {tc.result.substring(0, 500)}
                        </pre>
                      </div>
                    )}
                    {tc.error && (
                      <div>
                        <span className="text-xs text-red-400">Error:</span>
                        <pre className="mt-1 text-xs bg-red-900/30 p-2 rounded text-red-300">
                          {tc.error}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-gray-700 bg-black/50 p-4">
        <h3 className="text-lg font-semibold mb-4">AI Decisions & Reasoning</h3>
        
        {state.decisions.length === 0 ? (
          <p className="text-gray-400 text-sm">No reasoning traces available.</p>
        ) : (
          <div className="space-y-2">
            {state.decisions.map((decision, idx) => (
              <div key={idx} className="text-sm text-gray-300 border-l-2 border-blue-500 pl-3">
                {decision}
              </div>
            ))}
          </div>
        )}
      </div>

      {state.errors.length > 0 && (
        <div className="rounded-xl border border-red-700 bg-red-900/20 p-4">
          <h3 className="text-lg font-semibold mb-4 text-red-400">Failed Tool Calls</h3>
          
          <div className="space-y-3">
            {state.errors.map((error, idx) => (
              <div key={idx} className="text-sm">
                <span className="text-red-400 font-mono">{error.tool}: </span>
                <span className="text-red-300">{error.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}