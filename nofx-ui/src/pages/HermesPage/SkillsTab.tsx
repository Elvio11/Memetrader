import React, { useEffect, useState } from 'react'

interface Skill {
  name: string
  description: string
  category?: string
  tags?: string[]
}

export default function SkillsTab() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [filteredSkills, setFilteredSkills] = useState<Skill[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [status, setStatus] = useState<string>('Loading skills...')
  const [installingSkill, setInstallingSkill] = useState<string | null>(null)

  const fetchSkills = async () => {
    try {
      setStatus('Loading skills...')
      const response = await fetch('/api/skills')
      const result = await response.json()
      
      if (result.success && Array.isArray(result.skills)) {
        setSkills(result.skills)
        const cats = [...new Set(result.skills.map(s => s.category || 'Uncategorized').filter(Boolean))]
        setCategories(['All', ...cats.sort()])
        setSelectedCategory('All')
        setFilteredSkills(result.skills)
        setStatus('')
      } else {
        setSkills([])
        setCategories(['All'])
        setSelectedCategory('All')
        setFilteredSkills([])
        setStatus('No skills available.')
      }
    } catch (error) {
      console.error('Failed to load skills', error)
      setSkills([])
      setCategories(['All'])
      setSelectedCategory('All')
      setFilteredSkills([])
      setStatus('Failed to load skills.')
    }
  }

  const installSkill = async (skillName: string) => {
    setInstallingSkill(skillName)
    try {
      const response = await fetch(`/api/skills/${skillName}/install`, {
        method: 'POST'
      })
      const result = await response.json()
      if (result.success) {
        setStatus(`Skill ${skillName} installed successfully!`)
        setTimeout(() => setStatus(''), 3000)
      } else {
        setStatus(`Failed to install ${skillName}: ${result.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Install skill error:', error)
      setStatus(`Failed to install ${skillName}`)
    } finally {
      setInstallingSkill(null)
    }
  }

  const toggleSkill = async (skillName: string) => {
    try {
      const response = await fetch(`/api/skills/${skillName}/toggle`, {
        method: 'POST'
      })
      const result = await response.json()
      if (result.success) {
        setStatus(`Skill ${skillName} ${result.enabled ? 'enabled' : 'disabled'}!`)
        setTimeout(() => setStatus(''), 3000)
        // Refresh skills list to show updated status
        fetchSkills()
      } else {
        setStatus(`Failed to toggle ${skillName}: ${result.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Toggle skill error:', error)
      setStatus(`Failed to toggle ${skillName}`)
    }
  }

  useEffect(() => {
    fetchSkills()
  }, [])

  useEffect(() => {
    if (!skills.length) {
      setFilteredSkills([])
      return
    }

    let filtered = [...skills]
    
    // Filter by category
    if (selectedCategory && selectedCategory !== 'All') {
      filtered = filtered.filter(skill => skill.category === selectedCategory)
    }
    
    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      filtered = filtered.filter(skill => 
        skill.name.toLowerCase().includes(query) ||
        (skill.description && skill.description.toLowerCase().includes(query)) ||
        (skill.category && skill.category.toLowerCase().includes(query)) ||
        (skill.tags && skill.tags.some(tag => tag.toLowerCase().includes(query)))
      )
    }
    
    setFilteredSkills(filtered)
  }, [skills, selectedCategory, searchQuery])

  return (
    <div className="space-y-6 p-4 text-white">
      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Skills</h2>
        <p className="mt-2 text-sm text-gray-300">Browse Hermes skills available to the workspace.</p>
      </div>

      {status && (
        <div className="rounded-xl border border-gray-700 bg-black/50 p-4 text-sm text-gray-300">{status}</div>
      )}

      <div className="mb-4">
        <div className="flex flex-wrap gap-2">
          {categories.map((cat, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded text-sm ${selectedCategory === cat ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            >
              {cat} ({skills.filter(s => s.category === cat || (cat === 'All' && true)).length})
            }
          ))}
        </div>
        
        <div className="mt-3 w-full">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search skills by name, description, or tag..."
            className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {filteredSkills.length === 0 && !status ? (
        <div className="rounded-xl border border-gray-700 bg-black/50 p-4 text-center">
          <p className="text-gray-400">No skills match the current filters.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredSkills.map((skill) => (
            <div 
              key={skill.name} 
              className="rounded-xl border border-gray-800 bg-black/50 p-4 hover:bg-gray-700 transition-colors"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{skill.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="px-2 py-0.5 rounded text-xs ${skill.category ? 'bg-gray-700' : 'bg-gray-600'}">
                        {skill.category || 'Uncategorized'}
                      </span>
                      {skill.tags && skill.tags.length > 0 && (
                        <>
                          {skill.tags.map((tag, idx) => (
                            <span key={idx} className="px-1 py-0 rounded text-xs bg-gray-600 hover:bg-gray-500">
                              #{tag}
                            </span>
                          ))}
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {installingSkill === skill.name ? (
                      <span className="px-2 py-0.5 rounded text-xs bg-yellow-600">
                        Installing...
                      </span>
                    ) : (
                      <>
                        <button
                          onClick={() => installSkill(skill.name)}
                          disabled={installingSkill !== null}
                          className="px-2 py-0.5 rounded text-xs bg-blue-600 hover:bg-blue-500"
                        >
                          Install
                        </button>
                        <button
                          onClick={() => toggleSkill(skill.name)}
                          className="px-2 py-0.5 rounded text-xs bg-gray-600 hover:bg-gray-500"
                        >
                          Toggle
                        </button>
                      </>
                    )}
                  </div>
                </div>
                <p className="text-sm leading-5 text-gray-300">{skill.description || 'No description available.'}</p>
              </div>
            </>
          ))}
        </div>
      )}
    </div>
  )
}