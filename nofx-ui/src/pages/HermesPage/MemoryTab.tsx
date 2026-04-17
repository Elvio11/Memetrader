import React, { useEffect, useState } from 'react'

interface MemoryState {
  user: string
  self: string
}

export default function MemoryTab() {
  const [memory, setMemory] = useState<MemoryState>({ user: '', self: '' })
  const [target, setTarget] = useState<'user' | 'self'>('user')
  const [content, setContent] = useState('')
  const [status, setStatus] = useState<string>('')

  const fetchMemory = async () => {
    try {
      const response = await fetch('/api/memory')
      const result = await response.json()
      const memoryData = result.memory || {}
      setMemory({
        user: memoryData.user || '',
        self: memoryData.self || '',
      })
    } catch (error) {
      console.error('Failed to fetch memory', error)
      setStatus('Failed to load memory.')
    }
  }

  useEffect(() => {
    fetchMemory()
  }, [])

  const handleAddMemory = async () => {
    if (!content.trim()) {
      return
    }

    try {
      const response = await fetch('/api/memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, content }),
      })
      const result = await response.json()
      if (result.ok) {
        setContent('')
        setStatus('Memory saved.')
        await fetchMemory()
      } else {
        setStatus('Unable to save memory.')
      }
    } catch (error) {
      console.error('Save memory failed', error)
      setStatus('Unable to save memory.')
    }
  }

  return (
    <div className="space-y-6 p-4 text-white">
      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Memory Overview</h2>
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-gray-800 bg-black/50 p-4">
            <h3 className="font-medium">User Memory</h3>
            <pre className="mt-2 whitespace-pre-wrap text-sm text-gray-200">{memory.user || 'No stored user memory.'}</pre>
          </div>
          <div className="rounded-xl border border-gray-800 bg-black/50 p-4">
            <h3 className="font-medium">Self Memory</h3>
            <pre className="mt-2 whitespace-pre-wrap text-sm text-gray-200">{memory.self || 'No stored self memory.'}</pre>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Add Memory</h2>
        <div className="mt-4 flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="radio"
                checked={target === 'user'}
                onChange={() => setTarget('user')}
                className="accent-blue-500"
              />
              User memory
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="radio"
                checked={target === 'self'}
                onChange={() => setTarget('self')}
                className="accent-blue-500"
              />
              Self memory
            </label>
          </div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={5}
            placeholder="Enter memory text to store for Hermes..."
            className="w-full rounded-xl border border-gray-700 bg-gray-900 p-3 text-sm text-white outline-none focus:border-blue-500"
          />
          <button
            onClick={handleAddMemory}
            className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500"
          >
            Save Memory
          </button>
          {status && <p className="text-sm text-gray-300">{status}</p>}
        </div>
      </div>
    </div>
  )
}
