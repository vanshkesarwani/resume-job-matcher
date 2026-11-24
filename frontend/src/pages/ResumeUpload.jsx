import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  X,
  RotateCcw,
  Loader2,
  Check,
  ShieldCheck,
  Briefcase,
  GraduationCap,
  FolderGit2,
  User,
} from 'lucide-react';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB
const ALLOWED_EXTENSIONS = ['.pdf', '.docx'];

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const { getAuthHeaders } = useAuth();

  // Lazy state initialization from session storage (idiomatic React 19)
  const [uploadResult, setUploadResult] = useState(() => {
    try {
      const saved = sessionStorage.getItem('uploadedResume');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && parsed.filename) return parsed;
      }
    } catch {
      // Ignore parse errors
    }
    return null;
  });

  const [uploadStatus, setUploadStatus] = useState(() =>
    uploadResult ? 'success' : 'idle'
  );

  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // Format file size nicely
  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Client-side validation
  const validateFile = (selectedFile) => {
    if (!selectedFile) return 'Please select a resume file.';

    const fileName = selectedFile.name.toLowerCase();
    const isAllowed = ALLOWED_EXTENSIONS.some((ext) => fileName.endsWith(ext));
    if (!isAllowed) {
      return 'Unsupported file format. Please upload a PDF or DOCX file.';
    }

    if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
      return `File size (${formatFileSize(selectedFile.size)}) exceeds the 5 MB limit. Please choose a smaller file.`;
    }

    if (selectedFile.size === 0) {
      return 'The selected file is empty. Please choose a valid file.';
    }

    return null;
  };

  // Upload handler to FastAPI backend
  const uploadToBackend = async (fileToUpload) => {
    setUploadStatus('uploading');
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', fileToUpload);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/resume/upload', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        const message = data.detail || 'Upload failed. Please try again.';
        throw new Error(message);
      }

      setUploadResult(data);
      setUploadStatus('success');
      // Save in session storage for Step 2 and Step 3
      sessionStorage.setItem('uploadedResume', JSON.stringify(data));
    } catch (err) {
      setUploadStatus('error');
      setErrorMessage(
        err.message || 'Unable to connect to backend server. Make sure FastAPI is running on port 8000.'
      );
    }
  };

  // Process chosen file
  const processFile = (selectedFile) => {
    setErrorMessage('');
    const validationError = validateFile(selectedFile);

    if (validationError) {
      setErrorMessage(validationError);
      setUploadStatus('error');
      return;
    }

    setFile(selectedFile);
    uploadToBackend(selectedFile);
  };

  // Drag and drop event handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      processFile(droppedFile);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const chosenFile = e.target.files[0];
      processFile(chosenFile);
    }
  };

  // Remove Resume option
  const handleRemoveResume = () => {
    setFile(null);
    setUploadResult(null);
    setUploadStatus('idle');
    setErrorMessage('');
    sessionStorage.removeItem('uploadedResume');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Replace Resume option
  const handleReplaceResume = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const sections = uploadResult?.sections;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />

      <main className="grow max-w-4xl w-full mx-auto px-4 py-12 sm:px-6">
        {/* Step Indicator & Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold mb-2">
            Step 1 of 3: Resume Input & Text Extraction
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Upload Your Resume
          </h1>
          <p className="text-sm text-slate-600 max-w-md mx-auto mt-2 leading-relaxed">
            Upload your resume in PDF or DOCX format (maximum 5 MB). PyMuPDF and python-docx extract your skills, experience, and education.
          </p>
        </div>

        {/* Hidden File Input for Browse / Replace */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={handleFileInputChange}
        />

        {/* Error Banner */}
        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200/80 flex items-start justify-between gap-3 text-left animate-in fade-in duration-200">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-xs font-semibold text-red-900 uppercase tracking-wide">
                  Upload Validation Error
                </h4>
                <p className="text-xs text-red-700 mt-0.5 leading-relaxed">
                  {errorMessage}
                </p>
              </div>
            </div>
            <button
              onClick={() => setErrorMessage('')}
              className="text-red-400 hover:text-red-600 p-1 rounded-md"
              aria-label="Dismiss error"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Upload Container Card */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-6 sm:p-8 shadow-2xs transition-all">
          {/* STATE 1: IDLE OR ERROR (No file uploaded or ready to drag) */}
          {(uploadStatus === 'idle' || (uploadStatus === 'error' && !uploadResult)) && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center transition-all cursor-pointer ${
                isDragging
                  ? 'border-blue-500 bg-blue-50/60 scale-[1.005]'
                  : 'border-slate-300 hover:border-blue-400 bg-slate-50/40 hover:bg-slate-50/80'
              }`}
            >
              <div className="w-14 h-14 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 border border-blue-100 shadow-2xs">
                <UploadCloud className="w-7 h-7" />
              </div>

              <h3 className="text-base font-semibold text-slate-900 mb-1">
                {isDragging ? 'Drop your resume file here' : 'Click to upload or drag & drop'}
              </h3>
              <p className="text-xs text-slate-500 mb-4 max-w-sm mx-auto leading-relaxed">
                Supports PDF (PyMuPDF) and DOCX (python-docx) files up to 5 MB
              </p>

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current && fileInputRef.current.click();
                }}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-white border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:border-slate-400 shadow-2xs transition-colors"
              >
                Browse Resume File
              </button>

              <div className="mt-6 pt-5 border-t border-slate-200/60 flex items-center justify-center gap-6 text-[11px] text-slate-400">
                <span className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                  Stored securely
                </span>
                <span>•</span>
                <span>Max 5 MB</span>
                <span>•</span>
                <span>PDF & DOCX</span>
              </div>
            </div>
          )}

          {/* STATE 2: UPLOADING (In progress spinner) */}
          {uploadStatus === 'uploading' && (
            <div className="py-12 px-4 text-center">
              <div className="w-14 h-14 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 border border-blue-100 shadow-2xs">
                <Loader2 className="w-7 h-7 animate-spin" />
              </div>
              <h3 className="text-base font-semibold text-slate-900 mb-1">
                Uploading & Extracting Resume Text
              </h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mb-4">
                Parsing structured sections using PyMuPDF and python-docx...
              </p>
              {file && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 text-xs text-slate-700 font-medium">
                  <FileText className="w-4 h-4 text-slate-500" />
                  <span>{file.name}</span>
                  <span className="text-slate-400">({formatFileSize(file.size)})</span>
                </div>
              )}
            </div>
          )}

          {/* STATE 3: SUCCESS (File uploaded and parsed) */}
          {uploadStatus === 'success' && uploadResult && (
            <div className="space-y-6">
              {/* Success Notification Bar */}
              <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200/80 flex items-center justify-between text-left">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="text-xs font-semibold text-emerald-900">
                    {uploadResult.message || 'Resume uploaded and parsed successfully!'}
                  </span>
                </div>
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  Ready for Comparison
                </span>
              </div>

              {/* Uploaded File Details Card */}
              <div className="border border-slate-200 rounded-xl p-5 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-left">
                <div className="flex items-start gap-3.5">
                  <div className="w-11 h-11 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 leading-tight">
                      {uploadResult.filename}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                      <span>{formatFileSize(uploadResult.file_size_bytes)}</span>
                      <span>•</span>
                      <span>{uploadResult.extracted_text_length} characters parsed</span>
                    </p>
                  </div>
                </div>

                {/* Replace / Remove Controls */}
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleReplaceResume}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-100 hover:border-slate-300 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
                    Replace
                  </button>
                  <button
                    type="button"
                    onClick={handleRemoveResume}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs font-medium text-red-600 hover:bg-red-50 hover:border-red-200 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                    Remove
                  </button>
                </div>
              </div>

              {/* EXTRACTED RESUME SECTIONS DISPLAY */}
              <div className="space-y-4 pt-2 text-left">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Extracted Resume Sections
                  </h4>
                  <span className="text-[11px] text-slate-400">
                    Organized by PyMuPDF / python-docx parser
                  </span>
                </div>

                {/* 1. Professional Summary */}
                {sections?.professional_summary && (
                  <div className="p-4 rounded-xl border border-slate-200 bg-white">
                    <div className="flex items-center gap-2 mb-2 text-slate-900 font-semibold text-xs">
                      <User className="w-4 h-4 text-blue-600" />
                      <span>Professional Summary</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {sections.professional_summary}
                    </p>
                  </div>
                )}

                {/* 2. Detected Skills */}
                <div className="p-4 rounded-xl border border-slate-200 bg-white">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2 text-slate-900 font-semibold text-xs">
                      <Check className="w-4 h-4 text-blue-600" />
                      <span>Skills & Core Competencies</span>
                    </div>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">
                      {(sections?.skills || uploadResult.detected_skills)?.length || 0} skills
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {(sections?.skills || uploadResult.detected_skills || []).map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-100"
                      >
                        <Check className="w-3 h-3 text-blue-600" />
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* 3. Work Experience */}
                {sections?.work_experience && sections.work_experience.length > 0 && (
                  <div className="p-4 rounded-xl border border-slate-200 bg-white">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2 text-slate-900 font-semibold text-xs">
                        <Briefcase className="w-4 h-4 text-blue-600" />
                        <span>Work Experience</span>
                      </div>
                      <span className="text-xs text-slate-400">
                        {sections.work_experience.length} entries
                      </span>
                    </div>
                    <ul className="space-y-2">
                      {sections.work_experience.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 leading-relaxed">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0 mt-1.5"></span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 4. Projects */}
                {sections?.projects && sections.projects.length > 0 && (
                  <div className="p-4 rounded-xl border border-slate-200 bg-white">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2 text-slate-900 font-semibold text-xs">
                        <FolderGit2 className="w-4 h-4 text-blue-600" />
                        <span>Projects</span>
                      </div>
                      <span className="text-xs text-slate-400">
                        {sections.projects.length} project(s)
                      </span>
                    </div>
                    <ul className="space-y-2">
                      {sections.projects.map((proj, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 leading-relaxed">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0 mt-1.5"></span>
                          <span>{proj}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 5. Education */}
                {sections?.education && sections.education.length > 0 && (
                  <div className="p-4 rounded-xl border border-slate-200 bg-white">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2 text-slate-900 font-semibold text-xs">
                        <GraduationCap className="w-4 h-4 text-blue-600" />
                        <span>Education</span>
                      </div>
                      <span className="text-xs text-slate-400">
                        {sections.education.length} entry
                      </span>
                    </div>
                    <ul className="space-y-1.5">
                      {sections.education.map((edu, idx) => (
                        <li key={idx} className="text-xs text-slate-700">
                          {edu}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Next Step Action Button */}
              <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
                <span className="text-xs text-slate-500">
                  Resume text extracted into structured sections. Proceed to paste target job description.
                </span>
                <button
                  type="button"
                  onClick={() => navigate('/job-description')}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition-colors shadow-xs"
                >
                  Next: Job Description
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
