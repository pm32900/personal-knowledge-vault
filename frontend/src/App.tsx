import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Layout from '@/components/Layout';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import NotesListPage from '@/pages/NotesListPage';
import NoteEditorPage from '@/pages/NoteEditorPage';
import NoteViewPage from '@/pages/NoteViewPage';
import SearchPage from '@/pages/SearchPage';
import AskPage from '@/pages/AskPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/notes" element={<NotesListPage />} />
            <Route path="/notes/new" element={<NoteEditorPage />} />
            <Route path="/notes/:id" element={<NoteViewPage />} />
            <Route path="/notes/:id/edit" element={<NoteEditorPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/ask" element={<AskPage />} />
          </Route>

          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/notes" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
