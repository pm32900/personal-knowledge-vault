import { useState } from 'react';
import { Link } from 'react-router-dom';
import { searchApi } from '../lib/api';
import type { NoteSearchResult } from '../types';
import { Search, Loader2, FileText, Tag } from 'lucide-react';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<NoteSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setError('');
    setLoading(true);
    setSearched(true);
    try {
      const res = await searchApi.search(query.trim());
      setResults(res.data);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'Search failed. Make sure you have notes with embeddings.';
      setError(msg);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Semantic Search</h1>
        <p className="text-gray-500 text-sm mt-1">
          Search your notes using natural language. Powered by AI embeddings.
        </p>
      </div>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What did I write about machine learning?"
              className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl text-sm font-medium hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Search
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200 mb-6">
          {error}
        </div>
      )}

      {searched && !loading && results.length === 0 && !error && (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700">No results found</h2>
          <p className="text-gray-500 text-sm mt-1">Try a different search query.</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500 font-medium">
            {results.length} result{results.length !== 1 ? 's' : ''} found
          </p>
          {results.map((result) => (
            <Link
              key={result.note.id}
              to={`/notes/${result.note.id}`}
              className="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition group"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-base font-semibold text-gray-900 group-hover:text-indigo-600 transition">
                  {result.note.title}
                </h3>
                <span className="ml-3 shrink-0 text-xs font-medium bg-green-50 text-green-700 px-2.5 py-1 rounded-full">
                  {(result.similarity * 100).toFixed(0)}% match
                </span>
              </div>
              <p className="text-sm text-gray-600 line-clamp-2 mb-3">{result.excerpt}</p>
              {result.note.tags.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <Tag className="h-3 w-3 text-gray-400" />
                  {result.note.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
