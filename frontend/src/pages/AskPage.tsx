import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ragApi } from '../lib/api';
import type { RAGResponse } from '../types';
import { MessageSquare, Loader2, Send, BookOpen, Sparkles } from 'lucide-react';

export default function AskPage() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setError('');
    setLoading(true);
    setResponse(null);
    try {
      const res = await ragApi.ask(query.trim());
      setResponse(res.data);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'Failed to get an answer. Make sure you have notes and the AI service is configured.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-indigo-600" />
          Ask Your Vault
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Ask questions about your notes. AI will find relevant notes and generate an answer with citations.
        </p>
      </div>

      <form onSubmit={handleAsk} className="mb-8">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MessageSquare className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What have I learned about neural networks?"
              className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl text-sm font-medium hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Ask
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200 mb-6">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-gray-200">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600 mb-4" />
          <p className="text-sm text-gray-500">Searching your notes and generating an answer...</p>
        </div>
      )}

      {response && (
        <div className="space-y-6">
          {/* Answer */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 bg-indigo-100 rounded-lg flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-indigo-600" />
              </div>
              <h2 className="text-sm font-semibold text-gray-900">AI Answer</h2>
            </div>
            <div className="text-gray-700 leading-relaxed text-sm">
              {response.answer.split('\n').map((paragraph, i) => (
                <p key={i} className="mb-2 last:mb-0">
                  {paragraph}
                </p>
              ))}
            </div>
          </div>

          {/* Citations */}
          {response.citations.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                Sources ({response.citations.length})
              </h3>
              <div className="grid gap-3">
                {response.citations.map((citation) => (
                  <Link
                    key={citation.note_id}
                    to={`/notes/${citation.note_id}`}
                    className="block bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition group"
                  >
                    <div className="flex items-start justify-between mb-1.5">
                      <h4 className="text-sm font-semibold text-gray-900 group-hover:text-indigo-600 transition">
                        {citation.title}
                      </h4>
                      <span className="ml-3 shrink-0 text-xs font-medium bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
                        {(citation.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-2">{citation.excerpt}</p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!loading && !response && !error && (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
          <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700">Ask anything</h2>
          <p className="text-gray-500 text-sm mt-1 max-w-md mx-auto">
            Type a question above and the AI will search through your notes to find the answer.
          </p>
        </div>
      )}
    </div>
  );
}
