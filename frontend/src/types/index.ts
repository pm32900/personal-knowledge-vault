export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Note {
  id: number;
  title: string;
  content: string;
  tags: string[];
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  title: string;
  content: string;
  tags: string[];
}

export interface NoteUpdate {
  title?: string;
  content?: string;
  tags?: string[];
}

export interface NoteSearchResult {
  note: Note;
  similarity: number;
  excerpt: string;
}

export interface Citation {
  note_id: number;
  title: string;
  excerpt: string;
  similarity: number;
}

export interface RAGResponse {
  answer: string;
  citations: Citation[];
}
