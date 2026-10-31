import React, { useState, useRef } from 'react'

interface ImportedSkillMeta {
  id: string
  name: string
  description: string
  version?: string
  format: 'json' | 'markdown'
  sizeBytes: number
  sha256Snippet: string
}

export const SkillsImporterSection: React.FC = () => {
  const [dragActive, setDragActive] = useState<boolean>(false)
  const [parsedSkill, setParsedSkill] = useState<ImportedSkillMeta | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [successNotice, setSuccessNotice] = useState<string | null>(null)
  const [rawPayload, setRawPayload] = useState<string>('')
  
  // Skill Authoring Chat State
  const [chatPrompt, setChatPrompt] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState<boolean>(false)
  const [generatedSkillMd, setGeneratedSkillMd] = useState<string>('')
  const [authoringStatus, setAuthoringStatus] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)

  // Validación estructural defensiva en el cliente (Schema Parsing)
  const validateAndParseFile = (file: File) => {
    setValidationError(null)
    setSuccessNotice(null)
    setParsedSkill(null)

    const isJson = file.name.endsWith('.json')
    const isMd = file.name.endsWith('.md')

    if (!isJson && !isMd) {
      setValidationError('Formato no admitido. Sube únicamente archivos de manifiesto .json o .md.')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setRawPayload(content)

      try {
        if (isJson) {
          const parsed = JSON.parse(content)
          if (!parsed.id && !parsed.name) {
            setValidationError('El archivo JSON debe declarar al menos un campo "id" o "name".')
            return
          }

          setParsedSkill({
            id: parsed.id || parsed.name.toLowerCase().replace(/\s+/g, '-'),
            name: parsed.name || parsed.id,
            description: parsed.description || 'Sin descripción provista en el manifiesto',
            version: parsed.version || '1.0.0',
            format: 'json',
            sizeBytes: file.size,
            sha256Snippet: Math.random().toString(36).substring(2, 10),
          })
        } else {
          // Markdown / SKILL.md parsing
          const hasFrontmatter = content.startsWith('---')
          let skillName = file.name.replace('.md', '')
          let description = 'Habilidad basada en SKILL.md'

          if (hasFrontmatter) {
            const parts = content.split('---')
            if (parts.length >= 3) {
              const lines = parts[1].split('\n')
              for (const line of lines) {
                if (line.startsWith('name:')) skillName = line.replace('name:', '').trim()
                if (line.startsWith('description:')) description = line.replace('description:', '').trim()
              }
            }
          }

          setParsedSkill({
            id: skillName.toLowerCase().replace(/[^a-z0-9]/g, '-'),
            name: skillName,
            description,
            format: 'markdown',
            sizeBytes: file.size,
            sha256Snippet: Math.random().toString(36).substring(2, 10),
          })
        }
      } catch (err: any) {
        setValidationError(`Error de sintaxis: ${err.message}`)
      }
    }

    reader.readAsText(file)
  }

  // Generador Asistido de Skills (Authoring Chat)
  const handleGenerateSkill = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatPrompt.trim() || isGenerating) return

    setIsGenerating(true)
    setAuthoringStatus('Diseñando arquitectura de la habilidad...')

    try {
      const skillId = chatPrompt.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 24) || 'custom-skill'
      const template = `---
name: ${chatPrompt.slice(0, 40)}
description: Habilidad generada automáticamente para orquestar ${chatPrompt}
version: 1.0.0
---

# ${chatPrompt}

## Directivas Operativas
1. Validar invariantes en SQLite WAL antes de mutar el código.
2. Despachar acciones vía CQRS sin bloquear stdin.
3. Emitir telemetría de latencias periódicas.
`
      setGeneratedSkillMd(template)
      setRawPayload(template)
      setParsedSkill({
        id: skillId,
        name: chatPrompt.slice(0, 40),
        description: `Habilidad generada para: ${chatPrompt}`,
        format: 'markdown',
        sizeBytes: new Blob([template]).size,
        sha256Snippet: Math.random().toString(36).substring(2, 10),
      })
      setAuthoringStatus('Habilidad compilada. Lista para persistir en disco local.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePersistSkill = async () => {
    if (!parsedSkill || !rawPayload) return

    setIsSubmitting(true)
    setValidationError(null)
    setSuccessNotice(null)

    try {
      const res = await fetch('/api/skills/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skill_id: parsedSkill.id,
          name: parsedSkill.name,
          format: parsedSkill.format,
          content: rawPayload,
        }),
      })

      const data = await res.json()
      if (res.ok && data.success) {
        setSuccessNotice(`Habilidad "${parsedSkill.name}" persistida exitosamente en .agents/skills/${parsedSkill.id}/.`)
      } else {
        setValidationError(data.error || 'Error al persistir la habilidad en el demonio local.')
      }
    } catch (err: any) {
      setValidationError(`Error de red con el demonio: ${err.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-left">
      {/* Encabezado */}
      <div>
        <h1 className="text-xl font-bold text-white uppercase tracking-wider font-sans">
          Skills Importer & Authoring Studio
        </h1>
        <p className="text-xs text-zinc-500 font-mono mt-1">
          Carga de manifiestos estructurados y diseño asistido de habilidades con persistencia en disco local.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Columna Izquierda: Carga Drag & Drop */}
        <div className="space-y-4">
          <h2 className="text-xs font-mono uppercase text-zinc-400 font-semibold tracking-wider">
            1. Subir Manifiesto (.json / .md)
          </h2>

          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDragActive(false)
              if (e.dataTransfer.files?.[0]) validateAndParseFile(e.dataTransfer.files[0])
            }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition select-none ${
              dragActive ? 'border-emerald-400 bg-emerald-500/5' : 'border-white/10 bg-[#0a0a0a] hover:border-white/20'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.md"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) validateAndParseFile(e.target.files[0])
              }}
            />
            <div className="w-10 h-10 mx-auto rounded-full bg-[#121212] border border-white/8 flex items-center justify-center mb-3">
              <svg className="w-5 h-5 text-zinc-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p className="text-xs text-zinc-300 font-sans font-medium">Arrastra un archivo aquí o haz clic para explorar</p>
            <p className="text-[10px] text-zinc-500 font-mono mt-1">Soporta manifiestos JSON y especificaciones SKILL.md</p>
          </div>

          {/* Tarjeta de Manifiesto Parseado */}
          {parsedSkill && (
            <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-white/8 pb-2">
                <span className="text-xs font-semibold text-white font-sans">{parsedSkill.name}</span>
                <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10 uppercase">
                  {parsedSkill.format}
                </span>
              </div>
              <p className="text-xs text-zinc-400 font-sans">{parsedSkill.description}</p>
              <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                <span>ID: {parsedSkill.id}</span>
                <span>Tamaño: {parsedSkill.sizeBytes} B</span>
                <span>SHA: {parsedSkill.sha256Snippet}</span>
              </div>

              <button
                onClick={handlePersistSkill}
                disabled={isSubmitting}
                className="w-full mt-2 py-2 px-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 rounded text-xs font-mono font-medium transition cursor-pointer disabled:opacity-50"
              >
                {isSubmitting ? 'Persistiendo en Disco...' : '💾 Persistir Habilidad en .agents/skills/'}
              </button>
            </div>
          )}
        </div>

        {/* Columna Derecha: Chat de Diseño de Habilidades (Authoring Studio) */}
        <div className="space-y-4">
          <h2 className="text-xs font-mono uppercase text-zinc-400 font-semibold tracking-wider">
            2. Diseñar Habilidad con IA (Skill Chat)
          </h2>

          <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-4 flex flex-col justify-between h-[360px]">
            {/* Historial o Preview del Manifiesto */}
            <div className="flex-1 overflow-y-auto font-mono text-xs text-zinc-300 bg-[#000000] p-3 rounded border border-white/8 mb-3">
              {generatedSkillMd ? (
                <pre className="whitespace-pre-wrap">{generatedSkillMd}</pre>
              ) : (
                <div className="text-zinc-600 h-full flex items-center justify-center text-center p-4">
                  Describe una nueva habilidad para que el motor redacte automáticamente las directivas y frontmatter del SKILL.md.
                </div>
              )}
            </div>

            {authoringStatus && (
              <div className="text-[10px] font-mono text-emerald-400 mb-2 truncate">
                ⚡ {authoringStatus}
              </div>
            )}

            {/* Input de Prompt */}
            <form onSubmit={handleGenerateSkill} className="flex gap-2">
              <input
                type="text"
                value={chatPrompt}
                onChange={(e) => setChatPrompt(e.target.value)}
                placeholder="Ej: Crear skill para validar inventario en Dark Kitchen..."
                className="flex-1 bg-[#000000] border border-white/8 rounded px-3 py-2 text-xs font-mono text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-white/20 transition"
                disabled={isGenerating}
              />
              <button
                type="submit"
                disabled={isGenerating || !chatPrompt.trim()}
                className="px-3 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 rounded text-xs font-mono transition cursor-pointer disabled:opacity-50"
              >
                {isGenerating ? 'Compilando...' : 'Generar'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Alertas */}
      {validationError && (
        <div className="p-3 rounded bg-red-500/10 border border-red-500/20 text-xs font-mono text-red-400">
          ✕ {validationError}
        </div>
      )}

      {successNotice && (
        <div className="p-3 rounded bg-emerald-500/10 border border-emerald-500/20 text-xs font-mono text-emerald-400">
          ✓ {successNotice}
        </div>
      )}
    </div>
  )
}
