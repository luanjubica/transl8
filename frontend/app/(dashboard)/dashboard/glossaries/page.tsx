'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'
import { BookOpen, Plus, Search, Upload } from 'lucide-react'

export default function GlossariesPage() {
  const { getToken } = useAuth()
  const [glossaries, setGlossaries] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isImportOpen, setIsImportOpen] = useState(false)

  // Create glossary form
  const [newGlossary, setNewGlossary] = useState({
    name: '',
    description: '',
    source_language: 'en',
    target_language: 'de'
  })

  useEffect(() => {
    loadGlossaries()
  }, [])

  async function loadGlossaries() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const orgId = 'temp-org-id' // TODO: Get from user's organization
        const data = await apiClient.getGlossaries(orgId)
        setGlossaries(data.items || [])
      }
    } catch (error) {
      console.error('Failed to load glossaries:', error)
    } finally {
      setLoading(false)
    }
  }

  async function createGlossary() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const orgId = 'temp-org-id'
        await apiClient.createGlossary({
          ...newGlossary,
          org_id: orgId
        })
        setIsCreateOpen(false)
        setNewGlossary({
          name: '',
          description: '',
          source_language: 'en',
          target_language: 'de'
        })
        loadGlossaries()
      }
    } catch (error) {
      console.error('Failed to create glossary:', error)
    }
  }

  const filteredGlossaries = glossaries.filter((glossary) =>
    glossary.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    glossary.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading glossaries...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">Glossaries</h1>
          <p className="text-gray-600">Manage terminology databases for consistent translations</p>
        </div>
        <div className="flex gap-3">
          <Dialog open={isImportOpen} onOpenChange={setIsImportOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Import CSV
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Import Glossary from CSV</DialogTitle>
                <DialogDescription>
                  Upload a CSV file with columns: source_term, target_term, context (optional)
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="csv-file">CSV File</Label>
                  <Input id="csv-file" type="file" accept=".csv" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="import-glossary">Select Glossary</Label>
                  <Select>
                    <SelectTrigger id="import-glossary">
                      <SelectValue placeholder="Choose glossary" />
                    </SelectTrigger>
                    <SelectContent>
                      {glossaries.map((g) => (
                        <SelectItem key={g.id} value={g.id}>
                          {g.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsImportOpen(false)}>
                  Cancel
                </Button>
                <Button>Import</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Glossary
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Glossary</DialogTitle>
                <DialogDescription>
                  Create a terminology database for a specific language pair
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    placeholder="Technical Terms - EN to DE"
                    value={newGlossary.name}
                    onChange={(e) => setNewGlossary({ ...newGlossary, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description (optional)</Label>
                  <Input
                    id="description"
                    placeholder="Technical terminology for product documentation"
                    value={newGlossary.description}
                    onChange={(e) => setNewGlossary({ ...newGlossary, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="source-lang">Source Language</Label>
                    <Select
                      value={newGlossary.source_language}
                      onValueChange={(value) => setNewGlossary({ ...newGlossary, source_language: value })}
                    >
                      <SelectTrigger id="source-lang">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="it">Italian</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="target-lang">Target Language</Label>
                    <Select
                      value={newGlossary.target_language}
                      onValueChange={(value) => setNewGlossary({ ...newGlossary, target_language: value })}
                    >
                      <SelectTrigger id="target-lang">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="de">German</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="it">Italian</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={createGlossary} disabled={!newGlossary.name}>
                  Create Glossary
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
            placeholder="Search glossaries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Glossaries Grid */}
      {filteredGlossaries.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <BookOpen className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">
                {searchQuery ? 'No glossaries found' : 'No glossaries yet'}
              </h3>
              <p className="mb-4 text-gray-600">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Create a glossary to ensure consistent terminology across translations'}
              </p>
              {!searchQuery && (
                <Button onClick={() => setIsCreateOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Glossary
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredGlossaries.map((glossary) => (
            <Card key={glossary.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="mb-1">{glossary.name}</CardTitle>
                    <CardDescription className="text-xs">
                      {glossary.source_language.toUpperCase()} → {glossary.target_language.toUpperCase()}
                    </CardDescription>
                  </div>
                  <Badge variant="outline">{glossary.terms_count || 0} terms</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-sm text-gray-600">
                  {glossary.description || 'No description'}
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Updated {new Date(glossary.updated_at).toLocaleDateString()}</span>
                  <Link href={`/dashboard/glossaries/${glossary.id}`}>
                    <Button variant="ghost" size="sm">
                      View Terms
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
