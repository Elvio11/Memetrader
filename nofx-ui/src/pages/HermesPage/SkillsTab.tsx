import React, { useEffect, useState } from 'react'

interface Skill {
  name: string
  description: string
  category?: string
}

export default function SkillsTab() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [status, setStatus] = useState<string>('Loading skills...')

  const fetchSkills = async () => {
    try {
      const response = await fetch('/api/skills')
      const result = await response.json()
      if (result.success && Array.isArray(result.skills)) {
        setSkills(result.skills)
        setStatus('')
      } else {
        setSkills([])
        setStatus('No skills available.')
      }
    } catch (error) {
      console.error('Failed to load skills', error)
      setSkills([])
      setStatus('Failed to load skills.')
    }
  }

  useEffect(() => {
    fetchSkills()
  }, [])

  return (
    <div className="space-y-6 p-4 text-white">
      <div className="rounded-xl border border-gray-700 bg-slate-950/80 p-4">
        <h2 className="text-xl font-semibold">Skills</h2>
        <p className="mt-2 text-sm text-gray-300">Browse Hermes skills available to the workspace.</p>
      </div>

      {status && (
        <div className="rounded-xl border border-gray-700 bg-black/50 p-4 text-sm text-gray-300">{status}</div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {skills.map((skill) => (
          <div key={skill.name} className="rounded-xl border border-gray-800 bg-black/50 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-white">{skill.name}</h3>
                <p className="text-sm text-gray-400">{skill.category || 'Uncategorized'}</p>
              </div>
            </div>
            <p className="mt-3 text-sm leading-6 text-gray-300">{skill.description || 'No description available.'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
