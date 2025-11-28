'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { ArrowLeft, Edit, Plus, Search, Trash2 } from 'lucide-react'
import Link from 'next/link'

export default function GlossaryDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { getToken } = useAuth()
  const glossaryId = params.id as string

  const [glossary, setGlossary] = useState<any>(null)
  const [terms, setTerms] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isAddTermOpen, setIsAddTermOpen] = useState(false)
  const [editingTerm, setEditingTerm] = useState<any>(null)

  const [newTerm, setNewTerm] = useState({
    source_term: '',
    target_term: '',
    context: ''
  })

  useEffect(() => {
    loadGlossaryAndTerms()
  }, [glossaryId])

  async function loadGlossaryAndTerms() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)

        // Load glossary details
        const glossaryData = await apiClient.getGlossary(glossaryId)
        setGlossary(glossaryData)

        // Load terms
        const termsData = await apiClient.getGlossaryTerms(glossaryId)
        setTerms(termsData.items || [])
      }
    } catch (error) {
      console.error('Failed to load glossary:', error)
    } finally {
      setLoading(false)
    }
  }

  async function addTerm() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        await apiClient.addGlossaryTerm(glossaryId, newTerm)
        setIsAddTermOpen(false)
        setNewTerm({ source_term: '', target_term: '', context: '' })
        loadGlossaryAndTerms()
      }
    } catch (error) {
      console.error('Failed to add term:', error)
    }
  }

  async function updateTerm() {
    if (!editingTerm) return

    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        await apiClient.updateGlossaryTerm(glossaryId, editingTerm.id, {
          source_term: editingTerm.source_term,
          target_term: editingTerm.target_term,
          context: editingTerm.context
        })
        setEditingTerm(null)
        loadGlossaryAndTerms()
      }
    } catch (error) {
      console.error('Failed to update term:', error)
    }
  }

  async function deleteTerm(termId: string) {
    if (!confirm('Are you sure you want to delete this term?')) return

    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        await apiClient.deleteGlossaryTerm(glossaryId, termId)
        loadGlossaryAndTerms()
      }
    } catch (error) {
      console.error('Failed to delete term:', error)
    }
  }

  const filteredTerms = terms.filter((term) =>
    term.source_term.toLowerCase().includes(searchQuery.toLowerCase()) ||
    term.target_term.toLowerCase().includes(searchQuery.toLowerCase()) ||
    term.context?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading glossary...</div>
      </div>
    )
  }

  if (!glossary) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Glossary Not Found</h2>
          <Button className="mt-4" onClick={() => router.push('/dashboard/glossaries')}>
            Back to Glossaries
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-4">
          <Link href="/dashboard/glossaries">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Glossaries
            </Button>
          </Link>
        </div>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="mb-2 text-3xl font-bold">{glossary.name}</h1>
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <Badge variant="outline">
                {glossary.source_language.toUpperCase()} → {glossary.target_language.toUpperCase()}
              </Badge>
              <span>•</span>
              <span>{terms.length} terms</span>
            </div>
            {glossary.description && (
              <p className="mt-2 text-gray-600">{glossary.description}</p>
            )}
          </div>
          <Dialog open={isAddTermOpen} onOpenChange={setIsAddTermOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Term
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Term</DialogTitle>
                <DialogDescription>
                  Add a new term to this glossary for consistent translations
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="source-term">
                    Source Term ({glossary.source_language.toUpperCase()})
                  </Label>
                  <Input
                    id="source-term"
                    placeholder="e.g., Software"
                    value={newTerm.source_term}
                    onChange={(e) => setNewTerm({ ...newTerm, source_term: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="target-term">
                    Target Term ({glossary.target_language.toUpperCase()})
                  </Label>
                  <Input
                    id="target-term"
                    placeholder="e.g., Software"
                    value={newTerm.target_term}
                    onChange={(e) => setNewTerm({ ...newTerm, target_term: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="context">Context (optional)</Label>
                  <Textarea
                    id="context"
                    placeholder="Usage notes, context, or definition"
                    value={newTerm.context}
                    onChange={(e) => setNewTerm({ ...newTerm, context: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddTermOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={addTerm}
                  disabled={!newTerm.source_term || !newTerm.target_term}
                >
                  Add Term
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            type="text"
            placeholder="Search terms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Terms Table */}
      <Card>
        <CardHeader>
          <CardTitle>Terms</CardTitle>
          <CardDescription>
            Terminology database for {glossary.source_language.toUpperCase()} to{' '}
            {glossary.target_language.toUpperCase()} translations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredTerms.length === 0 ? (
            <div className="py-12 text-center">
              <h3 className="mb-2 text-lg font-semibold">
                {searchQuery ? 'No terms found' : 'No terms yet'}
              </h3>
              <p className="mb-4 text-gray-600">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Add terms to build your glossary'}
              </p>
              {!searchQuery && (
                <Button onClick={() => setIsAddTermOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add First Term
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Source Term</TableHead>
                  <TableHead>Target Term</TableHead>
                  <TableHead>Context</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTerms.map((term) => (
                  <TableRow key={term.id}>
                    <TableCell className="font-medium">{term.source_term}</TableCell>
                    <TableCell>{term.target_term}</TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {term.context || '—'}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingTerm(term)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteTerm(term.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Edit Term Dialog */}
      <Dialog open={!!editingTerm} onOpenChange={(open) => !open && setEditingTerm(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Term</DialogTitle>
            <DialogDescription>Update the term translation and context</DialogDescription>
          </DialogHeader>
          {editingTerm && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-source-term">
                  Source Term ({glossary.source_language.toUpperCase()})
                </Label>
                <Input
                  id="edit-source-term"
                  value={editingTerm.source_term}
                  onChange={(e) =>
                    setEditingTerm({ ...editingTerm, source_term: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-target-term">
                  Target Term ({glossary.target_language.toUpperCase()})
                </Label>
                <Input
                  id="edit-target-term"
                  value={editingTerm.target_term}
                  onChange={(e) =>
                    setEditingTerm({ ...editingTerm, target_term: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-context">Context (optional)</Label>
                <Textarea
                  id="edit-context"
                  value={editingTerm.context || ''}
                  onChange={(e) =>
                    setEditingTerm({ ...editingTerm, context: e.target.value })
                  }
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingTerm(null)}>
              Cancel
            </Button>
            <Button onClick={updateTerm}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
