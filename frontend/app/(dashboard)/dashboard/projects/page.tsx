'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'
import { FolderKanban, Plus, Search } from 'lucide-react'

export default function ProjectsPage() {
  const { getToken } = useAuth()
  const [projects, setProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    async function loadProjects() {
      try {
        const token = await getToken()
        if (token) {
          apiClient.setAuthToken(token)
          // TODO: Replace with actual org_id from user's organization
          const orgId = 'temp-org-id'
          const data = await apiClient.getProjects(orgId)
          setProjects(data.items || [])
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
      } finally {
        setLoading(false)
      }
    }

    loadProjects()
  }, [getToken])

  const filteredProjects = projects.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading projects...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">Projects</h1>
          <p className="text-gray-600">Manage your translation projects</p>
        </div>
        <Link href="/dashboard/projects/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Projects Grid */}
      {filteredProjects.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <FolderKanban className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">
                {searchQuery ? 'No projects found' : 'No projects yet'}
              </h3>
              <p className="mb-4 text-gray-600">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Get started by creating your first translation project'}
              </p>
              {!searchQuery && (
                <Link href="/dashboard/projects/new">
                  <Button>Create Project</Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle>{project.name}</CardTitle>
                <CardDescription>{project.description || 'No description'}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Languages:</span>
                    <span className="font-medium">
                      {project.source_language} → {project.target_languages?.length || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Documents:</span>
                    <Badge variant="outline">{project.documents_count || 0}</Badge>
                  </div>
                  <div className="pt-3">
                    <Link href={`/dashboard/projects/${project.id}`}>
                      <Button className="w-full" variant="outline">
                        View Project
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
