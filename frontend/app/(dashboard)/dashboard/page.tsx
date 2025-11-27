'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'
import { FileText, FolderKanban, Languages, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const { getToken } = useAuth()
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalDocuments: 0,
    totalSegments: 0,
    recentProjects: [] as any[],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const token = await getToken()
        if (token) {
          apiClient.setAuthToken(token)
          // TODO: Replace with actual org_id from user's organization
          const orgId = 'temp-org-id' // In real app, get from Clerk user metadata

          // Load projects
          const projectsData = await apiClient.getProjects(orgId, 1, 5)

          setStats({
            totalProjects: projectsData.total || 0,
            totalDocuments: 0, // TODO: Load from API
            totalSegments: 0, // TODO: Load from API
            recentProjects: projectsData.items || [],
          })
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [getToken])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's an overview of your translation projects.</p>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <FolderKanban className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProjects}</div>
            <p className="text-xs text-gray-500">Active translation projects</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDocuments}</div>
            <p className="text-xs text-gray-500">Files uploaded</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Segments</CardTitle>
            <Languages className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalSegments}</div>
            <p className="text-xs text-gray-500">Translatable units</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+0%</div>
            <p className="text-xs text-gray-500">vs last month</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Projects</CardTitle>
              <CardDescription>Your most recently updated translation projects</CardDescription>
            </div>
            <Link href="/dashboard/projects">
              <Button variant="outline">View All</Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {stats.recentProjects.length === 0 ? (
            <div className="py-12 text-center">
              <FolderKanban className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">No projects yet</h3>
              <p className="mb-4 text-gray-600">Get started by creating your first translation project</p>
              <Link href="/dashboard/projects/new">
                <Button>Create Project</Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {stats.recentProjects.map((project: any) => (
                <div key={project.id} className="flex items-center justify-between border-b pb-4 last:border-0">
                  <div>
                    <h4 className="font-medium">{project.name}</h4>
                    <p className="text-sm text-gray-600">
                      {project.source_language} → {project.target_languages?.join(', ')}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">
                      {project.documents_count || 0} documents
                    </Badge>
                    <Link href={`/dashboard/projects/${project.id}`}>
                      <Button variant="ghost" size="sm">View</Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
