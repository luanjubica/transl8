'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { apiClient } from '@/lib/api-client'
import { Database, Search } from 'lucide-react'

export default function TranslationMemoryPage() {
  const { getToken } = useAuth()
  const [searchText, setSearchText] = useState('')
  const [sourceLang, setSourceLang] = useState('en')
  const [targetLang, setTargetLang] = useState('de')
  const [minScore, setMinScore] = useState(0.7)
  const [matches, setMatches] = useState<any[]>([])
  const [searching, setSearching] = useState(false)

  async function searchTM() {
    if (!searchText.trim()) return

    setSearching(true)
    try {
      const token = await getToken()
      if (token) {
        apiClient.setAuthToken(token)
        const orgId = 'temp-org-id' // TODO: Get from user's organization

        const results = await apiClient.searchTranslationMemory({
          org_id: orgId,
          source_text: searchText,
          source_language: sourceLang,
          target_language: targetLang,
          min_score: minScore
        })

        setMatches(results || [])
      }
    } catch (error) {
      console.error('Failed to search TM:', error)
    } finally {
      setSearching(false)
    }
  }

  function getMatchColor(score: number) {
    if (score >= 0.95) return 'bg-green-100 text-green-800'
    if (score >= 0.85) return 'bg-blue-100 text-blue-800'
    if (score >= 0.75) return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  function getMatchLabel(score: number) {
    if (score >= 0.95) return 'Exact Match'
    if (score >= 0.85) return 'High Match'
    if (score >= 0.75) return 'Good Match'
    return 'Fuzzy Match'
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">Translation Memory</h1>
        <p className="text-gray-600">
          Search previously translated segments to reuse existing translations
        </p>
      </div>

      {/* Search Form */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Search Translation Memory</CardTitle>
          <CardDescription>
            Find similar segments that have been translated before
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-3 space-y-2">
                <Label htmlFor="search-text">Source Text</Label>
                <Input
                  id="search-text"
                  placeholder="Enter text to search for similar translations..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && searchTM()}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="source-lang">Source Language</Label>
                <Select value={sourceLang} onValueChange={setSourceLang}>
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
                <Select value={targetLang} onValueChange={setTargetLang}>
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

              <div className="space-y-2">
                <Label htmlFor="min-score">Minimum Match Score</Label>
                <Select
                  value={minScore.toString()}
                  onValueChange={(v) => setMinScore(parseFloat(v))}
                >
                  <SelectTrigger id="min-score">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0.95">95% (Exact)</SelectItem>
                    <SelectItem value="0.85">85% (High)</SelectItem>
                    <SelectItem value="0.75">75% (Good)</SelectItem>
                    <SelectItem value="0.70">70% (Fuzzy)</SelectItem>
                    <SelectItem value="0.50">50% (Low)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex justify-end">
              <Button onClick={searchTM} disabled={!searchText.trim() || searching}>
                <Search className="mr-2 h-4 w-4" />
                {searching ? 'Searching...' : 'Search TM'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {matches.length > 0 ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              {matches.length} Match{matches.length !== 1 ? 'es' : ''} Found
            </h2>
            <Badge variant="outline">{sourceLang.toUpperCase()} → {targetLang.toUpperCase()}</Badge>
          </div>

          {matches.map((match, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <Badge className={getMatchColor(match.score)}>
                      {(match.score * 100).toFixed(0)}% {getMatchLabel(match.score)}
                    </Badge>
                    {match.project_name && (
                      <span className="text-sm text-gray-500">
                        from project: {match.project_name}
                      </span>
                    )}
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className="mb-1 text-xs font-medium text-gray-500">
                        Source ({sourceLang.toUpperCase()})
                      </div>
                      <div className="rounded-md bg-gray-50 p-3 text-sm">
                        {match.source_text}
                      </div>
                    </div>

                    <div>
                      <div className="mb-1 text-xs font-medium text-gray-500">
                        Translation ({targetLang.toUpperCase()})
                      </div>
                      <div className="rounded-md bg-blue-50 p-3 text-sm">
                        {match.target_text}
                      </div>
                    </div>

                    {match.context && (
                      <div className="text-xs text-gray-600">
                        <span className="font-medium">Context:</span> {match.context}
                      </div>
                    )}

                    <Separator />

                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <div className="flex items-center gap-4">
                        <span>Created {new Date(match.created_at).toLocaleDateString()}</span>
                        {match.updated_by && <span>Updated by {match.updated_by}</span>}
                      </div>
                      <Button variant="outline" size="sm">
                        Use This Translation
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : searchText && !searching ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Database className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">No Matches Found</h3>
              <p className="text-gray-600">
                No similar translations found in Translation Memory. Try:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-gray-600">
                <li>• Lowering the minimum match score</li>
                <li>• Using different search terms</li>
                <li>• Checking the language pair selection</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Database className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">Search Translation Memory</h3>
              <p className="text-gray-600">
                Enter text above to find similar previously translated segments
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
