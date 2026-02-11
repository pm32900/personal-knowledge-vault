import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { notesApi } from '@/lib/api';
import type { Note } from '@/types';
import { Loader2, ArrowLeft, Pencil, Trash2, Tag, Clock } from 'lucide-react';

export default function NoteViewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [note, setNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    notesApi
      .get(Number(id))
      .then((res) => setNote(res.data))
      .catch(() => navigate('/notes'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleDelete = async () => {
    if (!confirm('Delete this note permanently?')) return;
    setDeleting(true);
    try {
      await notesApi.delete(Number(id));
      navigate('/notes');
    } catch {
      alert('Failed to delete note.');
      setDeleting(false);
    }
  };

  if (loading || !note) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => navigate('/notes')}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 mb-6 transition"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Notes
      </button>

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="p-8">
          <div className="flex items-start justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900 flex-1">{note.title}</h1>
            <div className="flex items-center gap-2 ml-4">
              <Link
                to={`/notes/${note.id}/edit`}
                className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                <Pencil className="h-3.5 w-3.5" />
                Edit
              </Link>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition disabled:opacity-50"
              >
                {deleting ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Trash2 className="h-3.5 w-3.5" />
                )}
                Delete
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4 mb-6 text-sm text-gray-500">
            <div className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              Created {new Date(note.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </div>
            {note.updated_at !== note.created_at && (
              <div className="flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" />
                Updated {new Date(note.updated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
              </div>
            )}
          </div>

          {note.tags.length > 0 && (
            <div className="flex items-center gap-2 mb-6 flex-wrap">
              <Tag className="h-3.5 w-3.5 text-gray-400" />
              {note.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-full font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          <div className="prose prose-gray max-w-none">
            {note.content.split('\n').map((paragraph, i) => (
              <p key={i} className="text-gray-700 leading-relaxed mb-3">
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
