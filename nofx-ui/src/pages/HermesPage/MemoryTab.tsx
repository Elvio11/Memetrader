import React, { useEffect, useState } from 'react'

interface MemoryFile {
  name: string
  content: string
  size: number
  modified: string
  type: 'user' | 'self' | 'session'
}

interface MemoryState {
  files: MemoryFile[]
  currentFile: MemoryFile | null
  isEditing: boolean
}

export default function MemoryTab() {
  const [state, setState] = useState<MemoryState>({
    files: [],
    currentFile: null,
    isEditing: false
  })
  const [newFileName, setNewFileName] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [status, setStatus] = useState<string>('Loading memory...')

  const fetchMemoryFiles = async () => {
    try {
      setStatus('Loading memory...')
      const response = await fetch('/api/memory')
      const result = await response.json()
      
      if (result.success) {
        const files = result.files || []
        setState(prev => ({
          ...prev,
          files: files.map(f => ({
            ...f,
            modified: new Date(f.modified || Date.now()).toLocaleString()
          }))
        }))
        // Auto-select first file if none selected
        if (!state.currentFile && files.length > 0) {
          setState(prev => ({
            ...prev,
            currentFile: files[0]
          }))
        }
        setStatus('')
      } else {
        setStatus('Failed to load memory files.')
      }
    } catch (error) {
      console.error('Failed to load memory files:', error)
      setStatus('Error loading memory files.')
    }
  }

  const saveMemoryFile = async (file: MemoryFile) => {
    try {
      const response = await fetch('/api/memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: file.name,
          content: file.content
        })
      })
      const result = await response.json()
      if (result.success) {
        setStatus(`Saved ${file.name}`)
        setTimeout(() => setStatus(''), 2000)
        await fetchMemoryFiles()
      } else {
        setStatus(`Failed to save ${file.name}: ${result.error}`)
      }
    } catch (error) {
      console.error('Save memory error:', error)
      setStatus(`Error saving ${file.name}`)
    }
  }

  const deleteMemoryFile = async (name: string) => {
    try {
      const response = await fetch(`/api/memory?name=${encodeURIComponent(name)}`, {
        method: 'DELETE'
      })
      const result = await response.json()
      if (result.success) {
        setStatus(`Deleted ${name}`)
        setTimeout(() => setStatus(''), 2000)
        await fetchMemoryFiles()
      } else {
        setStatus(`Failed to delete ${name}: ${result.error}`)
      }
    } catch (error) {
      console.error('Delete memory error:', error)
      setStatus(`Error deleting ${name}`)
    }
  }

  const createNewFile = async () => {
    if (!newFileName.trim()) {
      setStatus('Please enter a file name')
      return
    }
    
    const exists = state.files.some(f => f.name === newFileName)
    if (exists) {
      setStatus('A file with this name already exists')
      return
    }
    
    const newFile: MemoryFile = {
      name: newFileName,
      content: '',
      size: 0,
      modified: new Date().toISOString(),
      type: 'user'
    }
    
    await saveMemoryFile(newFile)
    setNewFileName('')
    // Select the new file
    setState(prev => ({
      ...prev,
      currentFile: newFile,
      isEditing: true
    }))
  }

  useEffect(() => {
    fetchMemoryFiles()
  }, [])

  useEffect(() => {
    if (state.currentFile && state.isEditing) {
      // Debounce auto-save
      const handler = setTimeout(() => {
        saveMemoryFile(state.currentFile)
      }, 2000)
      return () => clearTimeout(handler)
    }
  }, [state.currentFile, state.isEditing])

  const filteredFiles = state.files.filter(file => 
    file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    file.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6 p-4 text-white">
      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Memory</h2>
        <p className="mt-2 text-sm text-gray-300">Browse and edit memory files stored by Hermes.</p>
      </div>

      {status && (
        <div className="rounded-xl border border-gray-700 bg-black/50 p-4 text-sm text-gray-300">{status}</div>
      )}

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newFileName}
          onChange={(e) => setNewFileName(e.target.value)}
          placeholder="New file name..."
          className="flex-1 p-2 rounded bg-gray-800 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={createNewFile}
          className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-500"
        >
          New File
        </button>
      </div>

      <div className="flex gap-4">
        <div className="w-64 space-y-2">
          <h3 className="text-lg font-semibold mb-2">Files</h3>
          <div className="space-y-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search files..."
              className="w-full p-1 rounded bg-gray-800 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
            <div className="mt-2 space-y-1">
              {filteredFiles.length === 0 ? (
                <p className="text-gray-400 text-xs italic">No files match search</p>
              ) : (
                <>
                  {filteredFiles.map((file) => (
                    <div 
                      key={file.name} 
                      className={`flex items-center px-3 py-2 rounded-lg ${state.currentFile?.name === file.name ? 'bg-blue-600/30' : 'bg-gray-800/20'} hover:bg-gray-700/20 cursor-pointer`}
                      onClick={() => setState(prev => ({
                        ...prev,
                        currentFile: file,
                        isEditing: false
                      }))}
                    >
                      <div className="flex-1">
                        <span className="font-mono text-sm">{file.name}</span>
                        <span className="ml-2 text-xs text-gray-500">
                          {(file.size / 1024).toFixed(1)} KB • {file.modified}
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteMemoryFile(file.name)
                        }}
                        className="ml-2 h-6 w-6 text-xs rounded bg-red-600 hover:bg-red-500"
                        title="Delete file"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex-1 space-y-4">
          {state.currentFile ? (
            <>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">{state.currentFile.name}</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => setState(prev => ({ ...prev, isEditing: !prev.isEditing }))}
                    className={`px-3 py-1 rounded text-xs ${state.isEditing ? 'bg-gray-600' : 'bg-blue-600'}`}
                  >
                    {state.isEditing ? 'View' : 'Edit'}
                  </button>
                  <button
                    onClick={() => saveMemoryFile(state.currentFile!)}
                    className="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-500"
                  >
                    Save
                  </button>
                </div>
              </div>
              
              <div className="flex-1 min-h-[200px]">
                <textarea
                  value={state.isEditing ? state.currentFile.content : ''}
                  onChange={(e) => {
                    setState(prev => ({
                      ...prev,
                      currentFile: {
                        ...prev.currentFile!,
                        content: e.target.value,
                        size: e.target.value.length,
                        modified: new Date().toISOString()
                      }
                    }))
                  }}
                  onBlur={() => {
                    if (state.isEditing) {
                      saveMemoryFile(state.currentFile!)
                    }
                  }}
                  readOnly={!state.isEditing}
                  className="w-full h-full p-3 rounded bg-gray-900 border border-gray-700 text-white resize-none font-mono text-sm leading-5 outline-none focus:outline-none focus:border-blue-500"
                  placeholder="File content..."
                />
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Select a file to view or edit</p>
              <p className="text-xs">Create a new file or select from the list above</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}