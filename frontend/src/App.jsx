import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ResumeUpload from './pages/ResumeUpload';
import JobDescription from './pages/JobDescription';
import MultiJobComparison from './pages/MultiJobComparison';
import AnalysisDasboard from './pages/AnalysisDasboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/upload" element={<ResumeUpload />} />
          <Route path="/job-description" element={<JobDescription />} />
          <Route path="/compare" element={<MultiJobComparison />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <AnalysisDasboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Home />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
