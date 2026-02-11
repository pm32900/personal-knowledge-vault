import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { notesApi } from '@/lib/api';
import type { Note } from '@/types';
import { Plus, FileText, Tag, Loader2, Trash2, Clock } from 'lucide-react';

export default function NotesListPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  const fetchNotes = async () => {
    try {
      const res = await notesApi.list();
      setNotes(res.data);
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this note permanently?')) return;
    setDeleting(id);
    try {
      await notesApi.delete(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } catch {
      alert('Failed to delete note.');
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Notes</h1>
          <p className="text-gray-500 text-sm mt-1">{notes.length} note{notes.length !== 1 ? 's' : ''}</p>
        </div>
        <Link
          to="/notes/new"
          className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
        >
          <Plus className="h-4 w-4" />
          New Note
        </Link>
      </div>

      {notes.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-200">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700">No notes yet</h2>
          <p className="text-gray-500 text-sm mt-1 mb-6">Create your first note to get started.</p>
          <Link
            to="/notes/new"
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
          >
            <Plus className="h-4 w-4" />
            Create Note
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {notes.map((note) => (
            <div
              key={note.id}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition group"
            >
              <div className="flex items-start justify-between">
                <Link to={`/notes/${note.id}`} className="flex-1 min-w-0">
                  <h3 className="text-base font-semibold text-gray-900 group-hover:text-indigo-600 transition truncate">
                    {note.title}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {note.content}
                  </p>
                  <div className="flex items-center gap-4 mt-3">
                    {note.tags.length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <Tag className="h-3 w-3 text-gray-400" />
                        {note.tags.map((tag) => (
                          <span
                            key={tag}
                            className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Clock className="h-3 w-3" />
                      {new Date(note.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                </Link>
                <button
                  onClick={() => handleDelete(note.id)}
                  disabled={deleting === note.id}
                  className="ml-4 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition opacity-0 group-hover:opacity-100"
                >
                  {deleting === note.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
