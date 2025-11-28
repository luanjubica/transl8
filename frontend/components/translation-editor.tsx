'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  AlertCircle,
  Check,
  ChevronDown,
  ChevronUp,
  Copy,
  Database,
  BookOpen,
  Save,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Segment {
  id: string
  index: number
  source_text: string
  target_text?: string
  context?: string
  placeholders?: string[]
  char_count: number
  word_count: number
  max_length?: number
  is_locked: boolean
  status: 'untranslated' | 'translated' | 'reviewed' | 'approved'
}

interface TMMatch {
  source_text: string
  target_text: string
  score: number
  context?: string
  project_name?: string
}

interface GlossaryTerm {
  source_term: string
  target_term: string
  context?: string
}

interface TranslationEditorProps {
  segments: Segment[]
  targetLanguage: string
  sourceLanguage: string
  onSave: (segmentId: string, translation: string) => Promise<void>
  onApprove?: (segmentId: string) => Promise<void>
  onReject?: (segmentId: string) => Promise<void>
  getTMMatches?: (sourceText: string) => Promise<TMMatch[]>
  getGlossaryTerms?: (sourceText: string) => Promise<GlossaryTerm[]>
}

export function TranslationEditor({
  segments,
  targetLanguage,
  sourceLanguage,
  onSave,
  onApprove,
  onReject,
  getTMMatches,
  getGlossaryTerms
}: TranslationEditorProps) {
  const [activeSegmentIndex, setActiveSegmentIndex] = useState(0)
  const [editedTranslations, setEditedTranslations] = useState<Record<string, string>>({})
  const [tmMatches, setTmMatches] = useState<TMMatch[]>([])
  const [glossaryTerms, setGlossaryTerms] = useState<GlossaryTerm[]>([])
  const [loadingTM, setLoadingTM] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  const activeSegment = segments[activeSegmentIndex]

  // Load TM matches and glossary terms when segment changes
  useEffect(() => {
    if (activeSegment && !activeSegment.is_locked) {
      loadSegmentHelpers()
    }
  }, [activeSegmentIndex])

  async function loadSegmentHelpers() {
    if (!activeSegment) return

    // Load TM matches
    if (getTMMatches) {
      setLoadingTM(true)
      try {
        const matches = await getTMMatches(activeSegment.source_text)
        setTmMatches(matches)
      } catch (error) {
        console.error('Failed to load TM matches:', error)
      } finally {
        setLoadingTM(false)
      }
    }

    // Load glossary terms
    if (getGlossaryTerms) {
      try {
        const terms = await getGlossaryTerms(activeSegment.source_text)
        setGlossaryTerms(terms)
      } catch (error) {
        console.error('Failed to load glossary terms:', error)
      }
    }
  }

  function getCurrentTranslation(segment: Segment): string {
    return editedTranslations[segment.id] ?? segment.target_text ?? ''
  }

  function updateTranslation(segmentId: string, text: string) {
    setEditedTranslations((prev) => ({ ...prev, [segmentId]: text }))
  }

  async function saveTranslation(segment: Segment) {
    const translation = getCurrentTranslation(segment)
    if (!translation.trim()) return

    await onSave(segment.id, translation)
    // Clear edited state after saving
    setEditedTranslations((prev) => {
      const next = { ...prev }
      delete next[segment.id]
      return next
    })
  }

  function copySourceToTarget() {
    if (activeSegment) {
      updateTranslation(activeSegment.id, activeSegment.source_text)
    }
  }

  function insertTMMatch(match: TMMatch) {
    if (activeSegment) {
      updateTranslation(activeSegment.id, match.target_text)
    }
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'reviewed':
        return 'bg-blue-100 text-blue-800'
      case 'translated':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  function validatePlaceholders(segment: Segment, translation: string): string[] {
    const errors: string[] = []

    if (!segment.placeholders || segment.placeholders.length === 0) {
      return errors
    }

    // Check each placeholder is present in translation
    for (const placeholder of segment.placeholders) {
      if (!translation.includes(placeholder)) {
        errors.push(`Missing placeholder: ${placeholder}`)
      }
    }

    return errors
  }

  function checkLength(segment: Segment, translation: string): string | null {
    if (segment.max_length && translation.length > segment.max_length) {
      return `Translation is ${translation.length - segment.max_length} characters too long`
    }
    return null
  }

  const filteredSegments = segments.filter((seg) => {
    const matchesSearch =
      !searchQuery ||
      seg.source_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      seg.target_text?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      seg.context?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesFilter =
      filterStatus === 'all' ||
      (filterStatus === 'untranslated' && !seg.target_text) ||
      (filterStatus === 'translated' && seg.target_text && seg.status === 'translated') ||
      (filterStatus === 'approved' && seg.status === 'approved')

    return matchesSearch && matchesFilter
  })

  if (!activeSegment) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-500">No segments to translate</p>
      </div>
    )
  }

  const currentTranslation = getCurrentTranslation(activeSegment)
  const placeholderErrors = validatePlaceholders(activeSegment, currentTranslation)
  const lengthError = checkLength(activeSegment, currentTranslation)
  const hasChanges = editedTranslations[activeSegment.id] !== undefined

  return (
    <div className="flex h-full gap-4">
      {/* Left Panel: Segment List */}
      <div className="w-80 space-y-4">
        <div className="space-y-2">
          <Input
            placeholder="Search segments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Tabs value={filterStatus} onValueChange={setFilterStatus}>
            <TabsList className="w-full">
              <TabsTrigger value="all" className="flex-1">All</TabsTrigger>
              <TabsTrigger value="untranslated" className="flex-1">Todo</TabsTrigger>
              <TabsTrigger value="approved" className="flex-1">Done</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="space-y-2 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 250px)' }}>
          {filteredSegments.map((segment, idx) => {
            const actualIndex = segments.indexOf(segment)
            const isActive = actualIndex === activeSegmentIndex

            return (
              <Card
                key={segment.id}
                className={cn(
                  'cursor-pointer transition-all hover:shadow-md',
                  isActive && 'ring-2 ring-primary'
                )}
                onClick={() => setActiveSegmentIndex(actualIndex)}
              >
                <CardContent className="p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-500">
                      Segment {segment.index + 1}
                    </span>
                    <Badge className={getStatusColor(segment.status)} variant="outline">
                      {segment.status}
                    </Badge>
                  </div>
                  <p className="line-clamp-2 text-sm">{segment.source_text}</p>
                  {segment.target_text && (
                    <p className="mt-1 line-clamp-1 text-xs text-gray-500">
                      → {segment.target_text}
                    </p>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Right Panel: Translation Editor */}
      <div className="flex-1 space-y-4">
        {/* Navigation */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={activeSegmentIndex === 0}
              onClick={() => setActiveSegmentIndex(activeSegmentIndex - 1)}
            >
              <ChevronUp className="h-4 w-4" />
            </Button>
            <span className="text-sm">
              Segment {activeSegment.index + 1} of {segments.length}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={activeSegmentIndex === segments.length - 1}
              onClick={() => setActiveSegmentIndex(activeSegmentIndex + 1)}
            >
              <ChevronDown className="h-4 w-4" />
            </Button>
          </div>

          {activeSegment.context && (
            <Badge variant="outline" className="text-xs">
              {activeSegment.context}
            </Badge>
          )}
        </div>

        {/* Source Text */}
        <Card>
          <CardContent className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500">
                Source ({sourceLanguage.toUpperCase()})
              </span>
              <Button variant="ghost" size="sm" onClick={copySourceToTarget}>
                <Copy className="mr-2 h-4 w-4" />
                Copy Source
              </Button>
            </div>
            <div className="rounded-md bg-gray-50 p-3">
              <p className="whitespace-pre-wrap">{activeSegment.source_text}</p>
            </div>
            {activeSegment.placeholders && activeSegment.placeholders.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {activeSegment.placeholders.map((ph, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {ph}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Target Text Editor */}
        <Card>
          <CardContent className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500">
                Translation ({targetLanguage.toUpperCase()})
              </span>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>
                  {currentTranslation.length}
                  {activeSegment.max_length && ` / ${activeSegment.max_length}`} chars
                </span>
                <span>•</span>
                <span>{currentTranslation.split(/\s+/).filter(Boolean).length} words</span>
              </div>
            </div>

            <Textarea
              value={currentTranslation}
              onChange={(e) => updateTranslation(activeSegment.id, e.target.value)}
              disabled={activeSegment.is_locked}
              placeholder={
                activeSegment.is_locked
                  ? 'This segment is locked and cannot be translated'
                  : 'Enter translation...'
              }
              className="min-h-[120px]"
            />

            {/* Validation Warnings */}
            {(placeholderErrors.length > 0 || lengthError) && (
              <div className="mt-2 space-y-1">
                {placeholderErrors.map((error, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs text-red-600">
                    <AlertCircle className="h-3 w-3" />
                    {error}
                  </div>
                ))}
                {lengthError && (
                  <div className="flex items-center gap-2 text-xs text-orange-600">
                    <AlertCircle className="h-3 w-3" />
                    {lengthError}
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-4 flex items-center justify-between">
              <div className="flex gap-2">
                <Button
                  onClick={() => saveTranslation(activeSegment)}
                  disabled={
                    activeSegment.is_locked ||
                    !currentTranslation.trim() ||
                    placeholderErrors.length > 0
                  }
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save{hasChanges ? ' *' : ''}
                </Button>
                {onApprove && activeSegment.status === 'translated' && (
                  <Button
                    variant="outline"
                    onClick={() => onApprove(activeSegment.id)}
                  >
                    <Check className="mr-2 h-4 w-4" />
                    Approve
                  </Button>
                )}
                {onReject && activeSegment.status !== 'untranslated' && (
                  <Button
                    variant="outline"
                    onClick={() => onReject(activeSegment.id)}
                  >
                    <X className="mr-2 h-4 w-4" />
                    Reject
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* TM Matches & Glossary */}
        <Tabs defaultValue="tm" className="w-full">
          <TabsList>
            <TabsTrigger value="tm">
              <Database className="mr-2 h-4 w-4" />
              TM Matches ({tmMatches.length})
            </TabsTrigger>
            <TabsTrigger value="glossary">
              <BookOpen className="mr-2 h-4 w-4" />
              Glossary ({glossaryTerms.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="tm" className="space-y-2">
            {loadingTM ? (
              <div className="py-4 text-center text-sm text-gray-500">Loading matches...</div>
            ) : tmMatches.length === 0 ? (
              <div className="py-4 text-center text-sm text-gray-500">No TM matches found</div>
            ) : (
              tmMatches.map((match, idx) => (
                <Card key={idx} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-3">
                    <div className="mb-2 flex items-center justify-between">
                      <Badge variant="outline">
                        {(match.score * 100).toFixed(0)}% match
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => insertTMMatch(match)}
                      >
                        Use This
                      </Button>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div>
                        <div className="text-xs text-gray-500">Source:</div>
                        <div className="text-gray-700">{match.source_text}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Translation:</div>
                        <div className="font-medium">{match.target_text}</div>
                      </div>
                      {match.context && (
                        <div className="text-xs text-gray-500">{match.context}</div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="glossary" className="space-y-2">
            {glossaryTerms.length === 0 ? (
              <div className="py-4 text-center text-sm text-gray-500">
                No glossary terms found
              </div>
            ) : (
              glossaryTerms.map((term, idx) => (
                <Card key={idx}>
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <span className="font-medium">{term.source_term}</span>
                        <span className="mx-2 text-gray-400">→</span>
                        <span className="text-primary">{term.target_term}</span>
                      </div>
                    </div>
                    {term.context && (
                      <p className="mt-1 text-xs text-gray-500">{term.context}</p>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
