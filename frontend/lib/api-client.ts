import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiError {
  detail: string
  status: number
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        // Token will be added by Clerk's useAuth hook
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        const apiError: ApiError = {
          detail: error.response?.data?.detail || error.message,
          status: error.response?.status || 500,
        }
        return Promise.reject(apiError)
      }
    )
  }

  setAuthToken(token: string | null) {
    if (token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete this.client.defaults.headers.common['Authorization']
    }
  }

  // Projects
  async getProjects(orgId: string, page: number = 1, pageSize: number = 20) {
    const { data } = await this.client.get(`/api/v1/projects`, {
      params: { org_id: orgId, page, page_size: pageSize },
    })
    return data
  }

  async createProject(orgId: string, projectData: any) {
    const { data } = await this.client.post(`/api/v1/projects`, projectData, {
      params: { org_id: orgId },
    })
    return data
  }

  async getProject(id: string) {
    const { data } = await this.client.get(`/api/v1/projects/${id}`)
    return data
  }

  async updateProject(id: string, projectData: any) {
    const { data } = await this.client.patch(`/api/v1/projects/${id}`, projectData)
    return data
  }

  async deleteProject(id: string) {
    await this.client.delete(`/api/v1/projects/${id}`)
  }

  // Documents
  async getDocuments(projectId: string) {
    const { data } = await this.client.get(`/api/v1/documents`, {
      params: { project_id: projectId },
    })
    return data
  }

  async createDocument(projectId: string, documentData: any) {
    const { data } = await this.client.post(`/api/v1/documents`, documentData, {
      params: { project_id: projectId },
    })
    return data
  }

  async getDocument(id: string) {
    const { data } = await this.client.get(`/api/v1/documents/${id}`)
    return data
  }

  async deleteDocument(id: string) {
    await this.client.delete(`/api/v1/documents/${id}`)
  }

  // Segments
  async getSegments(documentId: string, skip: number = 0, limit: number = 100) {
    const { data } = await this.client.get(`/api/v1/segments`, {
      params: { document_id: documentId, skip, limit },
    })
    return data
  }

  async getSegment(id: string) {
    const { data } = await this.client.get(`/api/v1/segments/${id}`)
    return data
  }

  async lockSegment(id: string, locked: boolean) {
    const { data } = await this.client.patch(`/api/v1/segments/${id}/lock`, null, {
      params: { locked },
    })
    return data
  }

  // Translations
  async getTranslations(documentId: string, targetLanguage: string, statusFilter?: string) {
    const { data } = await this.client.get(`/api/v1/translations`, {
      params: { document_id: documentId, target_language: targetLanguage, status_filter: statusFilter },
    })
    return data
  }

  async createTranslation(segmentId: string, translationData: any) {
    const { data } = await this.client.post(`/api/v1/translations`, translationData, {
      params: { segment_id: segmentId },
    })
    return data
  }

  async updateTranslation(id: string, translationData: any) {
    const { data } = await this.client.patch(`/api/v1/translations/${id}`, translationData)
    return data
  }

  async approveTranslation(id: string) {
    const { data } = await this.client.patch(`/api/v1/translations/${id}/approve`)
    return data
  }

  // Glossaries
  async getGlossaries(orgId: string) {
    const { data } = await this.client.get(`/api/v1/glossaries`, {
      params: { org_id: orgId },
    })
    return data
  }

  async createGlossary(orgId: string, glossaryData: any) {
    const { data } = await this.client.post(`/api/v1/glossaries`, glossaryData, {
      params: { org_id: orgId },
    })
    return data
  }

  async getGlossaryTerms(glossaryId: string) {
    const { data } = await this.client.get(`/api/v1/glossaries/${glossaryId}/terms`)
    return data
  }

  async createGlossaryTerm(glossaryId: string, termData: any) {
    const { data } = await this.client.post(`/api/v1/glossaries/${glossaryId}/terms`, termData)
    return data
  }

  // Translation Memory
  async searchTM(orgId: string, searchData: any) {
    const { data } = await this.client.post(`/api/v1/tm/search`, searchData, {
      params: { org_id: orgId },
    })
    return data
  }

  // Jobs
  async createTranslationJob(jobData: any) {
    const { data } = await this.client.post(`/api/v1/jobs`, jobData)
    return data
  }

  async getJobStatus(id: string) {
    const { data } = await this.client.get(`/api/v1/jobs/${id}`)
    return data
  }

  async getJobs(documentId?: string, statusFilter?: string) {
    const { data } = await this.client.get(`/api/v1/jobs`, {
      params: { document_id: documentId, status_filter: statusFilter },
    })
    return data
  }

  async cancelJob(id: string) {
    const { data } = await this.client.post(`/api/v1/jobs/${id}/cancel`)
    return data
  }
}

export const apiClient = new ApiClient()
