import React, { useEffect, useState } from 'react'

interface ModelInfo {
  provider: string
  models: Array<{ id: string; description: string }>
}

export default function InspectorTab() {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [status, setStatus] = useState<string>('Loading inspector data...')

  const fetchModelInfo = async () => {
    try {
      const response = await fetch('/api/available-models')
      const result = await response.json()
      setModelInfo(result)
      setStatus('')
    } catch (error) {
      console.error('Failed to load inspector data', error)
      setModelInfo(null)
      setStatus('Unable to load model details.')
    }
  }

  useEffect(() => {
    fetchModelInfo()
  }, [])

  return (
    <div className="p-4 text-white">
      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Inspector</h2>
        <p className="mt-2 text-sm text-gray-300">View current Hermes system details and model availability.</p>
      </div>

      {status && (
        <div className="mt-5 rounded-xl border border-gray-700 bg-black/50 p-4 text-sm text-gray-300">{status}</div>
      )}

      {modelInfo && (
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-gray-800 bg-black/50 p-4">
            <h3 className="text-lg font-semibold text-white">Current Provider</h3>
            <p className="mt-2 text-sm text-gray-300">{modelInfo.provider}</p>
          </div>

          <div className="rounded-xl border border-gray-800 bg-black/50 p-4">
            <h3 className="text-lg font-semibold text-white">Available Models</h3>
            <ul className="mt-2 space-y-2 text-sm text-gray-300">
              {modelInfo.models.map((model) => (
                <li key={model.id}>
                  <strong>{model.id}</strong> - {model.description}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
