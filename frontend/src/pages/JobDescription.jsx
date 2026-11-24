import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import {
  ArrowLeft,
  ArrowRight,
  Sparkles,
  Loader2,
  AlertCircle,
  FileText,
  Briefcase,
  Clock,
  GraduationCap,
  ListChecks,
  CheckCircle2,
  RotateCcw,
  Check,
  Plus,
  X,
} from 'lucide-react';

export default function JobDescription() {
  const { getAuthHeaders } = useAuth();
  const [jobText, setJobText] = useState(() => {
    try {
      return sessionStorage.getItem('currentJobDescription') || '';
    } catch {
      return '';
    }
  });

  const [isExtracting, setIsExtracting] = useState(false);
  const [isMatching, setIsMatching] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Lazy state initialization from session storage
  const [extractedData, setExtractedData] = useState(() => {
    try {
      const saved = sessionStorage.getItem('extractedJobData');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Resume uploaded in Step 4 / Step 1
  const [resumeData] = useState(() => {
    try {
      const saved = sessionStorage.getItem('uploadedResume');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const navigate = useNavigate();

  const handleUseSample = () => {
    const sample = `Job Title: Senior Full-Stack Engineer
Company: CloudNexus Systems
Location: Remote / San Francisco, CA

About the Role:
We are looking for an experienced Senior Full-Stack Engineer to architect, build, and scale our core cloud SaaS platform and responsive developer tools.

Key Responsibilities:
• Architect, build, and deploy performant web applications using modern full-stack technologies.
• Lead backend API service design with Python, FastAPI, and PostgreSQL.
• Implement responsive, accessible, and intuitive frontends using React, TypeScript, and Tailwind CSS.
• Collaborate with cross-functional teams to design high-throughput microservices.
• Maintain high test coverage through unit testing and integration testing with Pytest and Jest.
• Optimize application performance, caching strategies, and database query throughput.

Required Qualifications & Skills:
• 5+ years of professional software engineering experience.
• Strong proficiency in Python, FastAPI, React, TypeScript, and modern JavaScript.
• Solid background in database design and optimization with PostgreSQL or MySQL.
• Practical experience containerizing services with Docker and version control with Git.
• Bachelor's degree in Computer Science, Software Engineering, or equivalent practical experience.

Preferred Qualifications:
• Experience deploying with Kubernetes, AWS cloud services, and automated CI/CD pipelines.
• Familiarity with Redis caching and GraphQL APIs is a strong plus.
• Master's degree in Computer Science is desirable.`;

    setJobText(sample);
    setErrorMessage('');
  };

  const handleClear = () => {
    setJobText('');
    setExtractedData(null);
    setErrorMessage('');
    sessionStorage.removeItem('currentJobDescription');
    sessionStorage.removeItem('extractedJobData');
    sessionStorage.removeItem('skillMatchResult');
    sessionStorage.removeItem('embeddingResult');
  };

  const handleAnalyzeJD = async (e) => {
    if (e) e.preventDefault();
    setErrorMessage('');

    const cleanText = jobText.trim();

    // Client-side empty & length validation
    if (!cleanText) {
      setErrorMessage('Please paste or type a Job Description before submitting.');
      return;
    }

    if (cleanText.length < 20) {
      setErrorMessage(
        'The Job Description is too brief. Please paste the full job posting including requirements and responsibilities.'
      );
      return;
    }

    setIsExtracting(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/job/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        body: JSON.stringify({ job_description: cleanText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to extract job description details.');
      }

      setExtractedData(data);
      // Persist in session storage for match analysis
      sessionStorage.setItem('extractedJobData', JSON.stringify(data));
      sessionStorage.setItem('currentJobDescription', cleanText);
    } catch (err) {
      setErrorMessage(
        err.message || 'Unable to connect to the backend server. Make sure FastAPI is running on port 8000.'
      );
    } finally {
      setIsExtracting(false);
    }
  };

  const handleProceedToMatch = async () => {
    setIsMatching(true);
    setErrorMessage('');

    const cleanJD = jobText.trim();
    const resumeRaw = resumeData?.raw_text || (resumeData?.detected_skills?.join(', ') || '');

    try {
      const skillsPayload = {
        resume_skills: resumeData?.detected_skills || resumeData?.sections?.skills || [],
        resume_text: resumeRaw,
        required_skills: extractedData?.required_skills || [],
        preferred_skills: extractedData?.preferred_skills || [],
        job_description: cleanJD,
      };

      const embeddingPayload = {
        resume_text: resumeRaw || 'Resume with technical experience and qualifications.',
        job_description: cleanJD,
      };

      const llmPayload = {
        resume_text: resumeRaw || 'Resume with technical experience and qualifications.',
        job_description: cleanJD,
        resume_sections: resumeData?.sections || null,
        job_title: extractedData?.job_title || '',
        missing_skills: extractedData?.required_skills || [],
      };

      const dashboardPayload = {
        resume_text: resumeRaw || 'Resume with technical experience and qualifications.',
        job_description: cleanJD,
        resume_sections: resumeData?.sections || null,
        required_skills: extractedData?.required_skills || [],
        preferred_skills: extractedData?.preferred_skills || [],
        job_title: extractedData?.job_title || '',
        required_experience: extractedData?.required_experience || '',
        education_requirements: extractedData?.education_requirements || '',
      };

      // Perform Skill Matching, Embeddings, Dashboard Summary, and LLM Analysis in parallel
      const [skillsRes, embedRes, llmRes, dashRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/v1/skills/match', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(skillsPayload),
        }),
        fetch('http://127.0.0.1:8000/api/v1/embeddings/similarity', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(embeddingPayload),
        }),
        fetch('http://127.0.0.1:8000/api/v1/llm/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(llmPayload),
        }),
        fetch('http://127.0.0.1:8000/api/v1/dashboard/summary', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          body: JSON.stringify(dashboardPayload),
        }),
      ]);

      const skillsData = await skillsRes.json();
      const embedData = await embedRes.json();

      let llmData = null;
      try {
        if (llmRes.ok) {
          llmData = await llmRes.json();
        }
      } catch (e) {
        console.warn('Could not parse LLM response', e);
      }

      let dashData = null;
      try {
        if (dashRes.ok) {
          dashData = await dashRes.json();
        }
      } catch (e) {
        console.warn('Could not parse Dashboard response', e);
      }

      if (!skillsRes.ok) {
        throw new Error(skillsData.detail || 'Skill matching failed.');
      }

      sessionStorage.setItem('skillMatchResult', JSON.stringify(skillsData));

      if (embedRes.ok) {
        sessionStorage.setItem('embeddingResult', JSON.stringify(embedData));
      }

      if (llmData) {
        sessionStorage.setItem('llmAnalysisResult', JSON.stringify(llmData));
      }

      if (dashData) {
        sessionStorage.setItem('dashboardSummary', JSON.stringify(dashData));
      }

      navigate('/dashboard');
    } catch (err) {
      setErrorMessage(err.message || 'Failed to match skills and embeddings with backend.');
    } finally {
      setIsMatching(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />

      <main className="grow max-w-5xl w-full mx-auto px-4 py-12 sm:px-6">
        {/* Step Indicator & Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold mb-2">
            Step 2 of 3: Job Description Input & Extraction
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Job Description Analysis
          </h1>
          <p className="text-sm text-slate-600 max-w-xl mx-auto mt-2 leading-relaxed">
            Paste any job description to automatically extract required skills, experience,
            education, and key responsibilities using our NLP engine.
          </p>
        </div>

        {/* Active Resume Reminder Banner (from Step 4) */}
        {resumeData && (
          <div className="mb-6 p-4 rounded-xl bg-white border border-slate-200/90 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-left">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">Active Uploaded Resume (Step 1):</p>
                <h4 className="text-sm font-semibold text-slate-900">
                  {resumeData.filename}
                </h4>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500 hidden sm:inline">
                {resumeData.detected_skills?.length || 0} skills detected
              </span>
              <Link
                to="/upload"
                className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline"
              >
                Change resume
              </Link>
            </div>
          </div>
        )}

        {/* Error Alert Banner */}
        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200/80 flex items-start justify-between gap-3 text-left animate-in fade-in duration-200">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-xs font-semibold text-red-900 uppercase tracking-wide">
                  Validation Error
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

        {/* Input Card Container */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-6 sm:p-8 shadow-2xs space-y-6">
          <form onSubmit={handleAnalyzeJD} className="space-y-4 text-left">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-blue-600" />
                Paste Job Description (JD)
              </label>

              <div className="flex items-center gap-3">
                {jobText && (
                  <button
                    type="button"
                    onClick={handleClear}
                    className="text-xs text-slate-500 hover:text-slate-800 transition-colors"
                  >
                    Clear text
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleUseSample}
                  className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-semibold transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Load sample JD
                </button>
              </div>
            </div>

            {/* Textarea */}
            <div className="relative">
              <textarea
                rows={10}
                required
                value={jobText}
                onChange={(e) => {
                  setJobText(e.target.value);
                  if (errorMessage) setErrorMessage('');
                }}
                placeholder="Paste the full job posting here (job title, responsibilities, required qualifications, preferred skills, experience, education)..."
                className="w-full text-xs font-mono p-4 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-900 placeholder:text-slate-400 leading-relaxed transition-all"
              ></textarea>

              <div className="flex justify-between items-center text-[11px] text-slate-400 px-1 pt-1">
                <span>Supports plain text formatting from any job board</span>
                <span>
                  {jobText.trim().length > 0
                    ? `${jobText.trim().split(/\s+/).length} words • ${jobText.length} characters`
                    : '0 words'}
                </span>
              </div>
            </div>

            {/* Submit / Extract Button */}
            <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-100">
              <Link
                to="/upload"
                className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 order-2 sm:order-1"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                Back to Resume Upload
              </Link>

              <button
                type="submit"
                disabled={isExtracting}
                className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs font-semibold shadow-xs transition-colors order-1 sm:order-2"
              >
                {isExtracting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Extracting JD with NLP...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Analyze & Extract JD
                  </>
                )}
              </button>
            </div>
          </form>

          {/* EXTRACTED INFORMATION SECTION DISPLAY */}
          {extractedData && (
            <div className="pt-8 border-t border-slate-200/80 space-y-6 animate-in fade-in duration-300">
              {/* Success Notification */}
              <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200/80 flex items-center justify-between text-left">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="text-xs font-semibold text-emerald-900">
                    {extractedData.message || 'Job description analyzed and extracted successfully!'}
                  </span>
                </div>
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  NLP Parsed
                </span>
              </div>

              {/* 1. Header Information: Job Title & Experience Required */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-left flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                    Extracted Job Title
                  </span>
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-blue-600" />
                    <h3 className="text-lg font-bold text-slate-900">
                      {extractedData.job_title}
                    </h3>
                  </div>
                </div>

                <div className="sm:text-right space-y-1">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                    Experience Required
                  </span>
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white border border-slate-200 text-xs font-semibold text-slate-800 shadow-2xs">
                    <Clock className="w-3.5 h-3.5 text-blue-600" />
                    <span>{extractedData.experience_required}</span>
                  </div>
                </div>
              </div>

              {/* 2 & 3. Required Skills and Preferred Skills */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-left">
                {/* Required Skills */}
                <div className="border border-slate-200 rounded-xl p-5 bg-white shadow-2xs space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                        Required Skills
                      </h4>
                      <p className="text-[11px] text-slate-500">
                        Mandatory technical proficiencies
                      </p>
                    </div>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100">
                      {extractedData.required_skills?.length || 0}
                    </span>
                  </div>

                  {extractedData.required_skills && extractedData.required_skills.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {extractedData.required_skills.map((skill) => (
                        <span
                          key={skill}
                          className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-100"
                        >
                          <Check className="w-3 h-3 text-blue-600" />
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">
                      No explicit mandatory skills detected.
                    </p>
                  )}
                </div>

                {/* Preferred Skills */}
                <div className="border border-slate-200 rounded-xl p-5 bg-white shadow-2xs space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                        Preferred Skills
                      </h4>
                      <p className="text-[11px] text-slate-500">
                        Nice-to-have bonus competencies
                      </p>
                    </div>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-100">
                      {extractedData.preferred_skills?.length || 0}
                    </span>
                  </div>

                  {extractedData.preferred_skills && extractedData.preferred_skills.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {extractedData.preferred_skills.map((skill) => (
                        <span
                          key={skill}
                          className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-200/60"
                        >
                          <Plus className="w-3 h-3 text-amber-600" />
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">
                      No specific secondary / bonus qualifications stated.
                    </p>
                  )}
                </div>
              </div>

              {/* 4. Education Requirements */}
              <div className="border border-slate-200 rounded-xl p-5 bg-white shadow-2xs text-left space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <GraduationCap className="w-4 h-4 text-blue-600" />
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Education Requirements
                    </h4>
                  </div>
                  <span className="text-xs text-slate-400">
                    {extractedData.education_requirements?.length || 0} requirement(s)
                  </span>
                </div>

                {extractedData.education_requirements && extractedData.education_requirements.length > 0 ? (
                  <ul className="space-y-2 pt-1">
                    {extractedData.education_requirements.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-slate-700">
                        <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">
                    Degree requirements not explicitly listed.
                  </p>
                )}
              </div>

              {/* 5. Key Responsibilities */}
              <div className="border border-slate-200 rounded-xl p-5 bg-white shadow-2xs text-left space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <ListChecks className="w-4 h-4 text-blue-600" />
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Key Responsibilities & Deliverables
                    </h4>
                  </div>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                    {extractedData.key_responsibilities?.length || 0} core duties
                  </span>
                </div>

                {extractedData.key_responsibilities && extractedData.key_responsibilities.length > 0 ? (
                  <ul className="space-y-2.5 pt-1">
                    {extractedData.key_responsibilities.map((resp, idx) => (
                      <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 leading-relaxed">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0 mt-1.5"></span>
                        <span>{resp}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">
                    No bulleted responsibilities explicitly outlined.
                  </p>
                )}
              </div>

              {/* Bottom Actions: Re-extract or Proceed to Match */}
              <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center gap-4">
                  <button
                    type="button"
                    onClick={() => {
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900"
                  >
                    <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
                    Edit or Re-analyze Description
                  </button>

                  <Link
                    to="/compare"
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Compare Multiple Roles
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>

                <button
                  type="button"
                  onClick={handleProceedToMatch}
                  disabled={isMatching}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium text-sm transition-colors shadow-xs"
                >
                  {isMatching ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Matching Skills & Embeddings...
                    </>
                  ) : (
                    <>
                      Proceed to Resume Match
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
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
