'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'
import { FileText, Search, Upload } from 'lucide-react'

export default function DocumentsPage() {
  const { getToken } = useAuth()
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadDocuments()
  }, [])

  async function loadDocuments() {
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const orgId = 'temp-org-id' // TODO: Get from user's organization

        // Load documents from all projects
        const projectsData = await apiClient.getProjects(orgId)

        const allDocs: any[] = []
        for (const project of projectsData.items || []) {
          const docsData = await apiClient.getProjectDocuments(project.id)
          allDocs.push(
            ...(docsData.items || []).map((doc: any) => ({
              ...doc,
              project_name: project.name,
              project_id: project.id
            }))
          )
        }

        setDocuments(allDocs)
      }
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredDocuments = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.project_name?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  function getStatusColor(status: string) {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading documents...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">Documents</h1>
          <p className="text-gray-600">All translation documents across projects</p>
        </div>
        <Link href="/dashboard/projects">
          <Button>
            <Upload className="mr-2 h-4 w-4" />
            Upload to Project
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Documents Grid */}
      {filteredDocuments.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">
                {searchQuery ? 'No documents found' : 'No documents yet'}
              </h3>
              <p className="mb-4 text-gray-600">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Upload documents to projects to start translating'}
              </p>
              {!searchQuery && (
                <Link href="/dashboard/projects">
                  <Button>Go to Projects</Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((document) => (
            <Card key={document.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="mb-1 text-base">{document.filename}</CardTitle>
                    <CardDescription className="text-xs">
                      {document.project_name}
                    </CardDescription>
                  </div>
                  <Badge className={getStatusColor(document.status)} variant="outline">
                    {document.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Source:</span>
                    <span className="font-medium">
                      {document.source_language?.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Segments:</span>
                    <Badge variant="outline">{document.segments_count || 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Uploaded:</span>
                    <span className="text-xs text-gray-500">
                      {new Date(document.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {document.status === 'ready' && (
                    <div className="pt-3">
                      <Link href={`/dashboard/documents/${document.id}`}>
                        <Button className="w-full" size="sm">
                          Translate
                        </Button>
                      </Link>
                    </div>
                  )}

                  {document.status === 'error' && document.error_message && (
                    <div className="rounded-md bg-red-50 p-2 text-xs text-red-600">
                      {document.error_message}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
