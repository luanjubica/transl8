'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { TranslationEditor } from '@/components/translation-editor'
import { apiClient } from '@/lib/api-client'
import { ArrowLeft, Download, FileText } from 'lucide-react'
import Link from 'next/link'

export default function DocumentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { getToken } = useAuth()
  const documentId = params.id as string

  const [document, setDocument] = useState<any>(null)
  const [segments, setSegments] = useState<any[]>([])
  const [selectedLanguage, setSelectedLanguage] = useState('')
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    loadDocument()
  }, [documentId])

  useEffect(() => {
    if (selectedLanguage) {
      loadSegments()
    }
  }, [documentId, selectedLanguage])

  async function loadDocument() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const docData = await apiClient.getDocument(documentId)
        setDocument(docData)

        // Set default target language if available
        if (docData.target_languages && docData.target_languages.length > 0) {
          setSelectedLanguage(docData.target_languages[0])
        }
      }
    } catch (error) {
      console.error('Failed to load document:', error)
    } finally {
      setLoading(false)
    }
  }

  async function loadSegments() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)

        // Load segments
        const segmentsData = await apiClient.getDocumentSegments(documentId)

        // Load translations for selected language
        const translationsData = await apiClient.getDocumentTranslations(
          documentId,
          selectedLanguage
        )

        // Merge segments with translations
        const mergedSegments = segmentsData.items.map((segment: any) => {
          const translation = translationsData.items.find(
            (t: any) => t.segment_id === segment.id
          )
          return {
            ...segment,
            target_text: translation?.translated_text,
            status: translation?.status || 'untranslated'
          }
        })

        setSegments(mergedSegments)
      }
    } catch (error) {
      console.error('Failed to load segments:', error)
    }
  }

  async function handleSave(segmentId: string, translation: string) {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)

        // Check if translation exists
        const segment = segments.find((s) => s.id === segmentId)
        const hasExistingTranslation = !!segment?.target_text

        if (hasExistingTranslation) {
          // Update existing translation
          await apiClient.updateTranslation(segmentId, {
            translated_text: translation,
            target_language: selectedLanguage
          })
        } else {
          // Create new translation
          await apiClient.createTranslation({
            segment_id: segmentId,
            target_language: selectedLanguage,
            translated_text: translation,
            status: 'translated'
          })
        }

        // Reload segments to get updated data
        await loadSegments()
      }
    } catch (error) {
      console.error('Failed to save translation:', error)
      throw error
    }
  }

  async function handleApprove(segmentId: string) {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        await apiClient.approveTranslation(segmentId)
        await loadSegments()
      }
    } catch (error) {
      console.error('Failed to approve translation:', error)
    }
  }

  async function handleReject(segmentId: string) {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        // Update status back to translated
        await apiClient.updateTranslation(segmentId, {
          status: 'translated'
        })
        await loadSegments()
      }
    } catch (error) {
      console.error('Failed to reject translation:', error)
    }
  }

  async function getTMMatches(sourceText: string) {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const orgId = 'temp-org-id'
        const matches = await apiClient.searchTranslationMemory({
          org_id: orgId,
          source_text: sourceText,
          source_language: document.source_language,
          target_language: selectedLanguage,
          min_score: 0.7
        })
        return matches || []
      }
    } catch (error) {
      console.error('Failed to get TM matches:', error)
    }
    return []
  }

  async function getGlossaryTerms(sourceText: string) {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const orgId = 'temp-org-id'

        // Get glossaries for this language pair
        const glossaries = await apiClient.getGlossaries(orgId)
        const relevantGlossary = glossaries.items?.find(
          (g: any) =>
            g.source_language === document.source_language &&
            g.target_language === selectedLanguage
        )

        if (relevantGlossary) {
          const terms = await apiClient.getGlossaryTerms(relevantGlossary.id)
          // Filter terms that appear in source text
          return (
            terms.items?.filter((term: any) =>
              sourceText.toLowerCase().includes(term.source_term.toLowerCase())
            ) || []
          )
        }
      }
    } catch (error) {
      console.error('Failed to get glossary terms:', error)
    }
    return []
  }

  async function handleExport(format: string = 'original') {
    setExporting(true)
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)

        // Trigger export job
        const job = await apiClient.createTranslationJob({
          document_id: documentId,
          target_language: selectedLanguage,
          job_type: 'export',
          export_format: format
        })

        // Poll for job completion
        let attempts = 0
        const maxAttempts = 30

        while (attempts < maxAttempts) {
          await new Promise((resolve) => setTimeout(resolve, 2000))

          const jobStatus = await apiClient.getTranslationJob(job.id)

          if (jobStatus.status === 'completed') {
            // Download file
            if (jobStatus.result?.download_url) {
              window.open(jobStatus.result.download_url, '_blank')
            }
            break
          } else if (jobStatus.status === 'failed') {
            alert('Export failed: ' + jobStatus.error)
            break
          }

          attempts++
        }

        if (attempts >= maxAttempts) {
          alert('Export timeout. Please try again.')
        }
      }
    } catch (error) {
      console.error('Failed to export document:', error)
      alert('Export failed. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading document...</div>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Document Not Found</h2>
          <Button className="mt-4" onClick={() => router.push('/dashboard/documents')}>
            Back to Documents
          </Button>
        </div>
      </div>
    )
  }

  const stats = {
    total: segments.length,
    translated: segments.filter((s) => s.status === 'translated').length,
    approved: segments.filter((s) => s.status === 'approved').length,
    untranslated: segments.filter((s) => s.status === 'untranslated').length
  }

  const progress =
    stats.total > 0 ? ((stats.translated + stats.approved) / stats.total) * 100 : 0

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <div className="border-b bg-white p-4">
        <div className="mb-4">
          <Link href="/dashboard/documents">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Documents
            </Button>
          </Link>
        </div>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <FileText className="h-6 w-6 text-gray-400" />
              <h1 className="text-2xl font-bold">{document.filename}</h1>
            </div>
            <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
              <span>Source: {document.source_language?.toUpperCase()}</span>
              <span>•</span>
              <span>{stats.total} segments</span>
              <span>•</span>
              <span>{progress.toFixed(0)}% complete</span>
            </div>

            {/* Progress Bar */}
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Stats */}
            <div className="mt-3 flex gap-4">
              <Badge variant="outline">{stats.untranslated} untranslated</Badge>
              <Badge variant="outline" className="bg-yellow-50">
                {stats.translated} translated
              </Badge>
              <Badge variant="outline" className="bg-green-50">
                {stats.approved} approved
              </Badge>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Target language" />
              </SelectTrigger>
              <SelectContent>
                {document.target_languages?.map((lang: string) => (
                  <SelectItem key={lang} value={lang}>
                    {lang.toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button onClick={() => handleExport('original')} disabled={exporting}>
              <Download className="mr-2 h-4 w-4" />
              {exporting ? 'Exporting...' : 'Export'}
            </Button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden p-4">
        {selectedLanguage && segments.length > 0 ? (
          <TranslationEditor
            segments={segments}
            targetLanguage={selectedLanguage}
            sourceLanguage={document.source_language}
            onSave={handleSave}
            onApprove={handleApprove}
            onReject={handleReject}
            getTMMatches={getTMMatches}
            getGlossaryTerms={getGlossaryTerms}
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <FileText className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">
                {!selectedLanguage ? 'Select a target language' : 'No segments found'}
              </h3>
              <p className="text-gray-600">
                {!selectedLanguage
                  ? 'Choose a target language to start translating'
                  : 'This document has no segments to translate'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
