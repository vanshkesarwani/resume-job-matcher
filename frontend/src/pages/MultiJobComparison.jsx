import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import {
  Briefcase,
  Sparkles,
  ArrowRight,
  Plus,
  Trash2,
  Trophy,
  CheckCircle2,
  XCircle,
  BarChart3,
  Loader2,
  AlertCircle,
  FileText,
  RotateCcw,
  Check,
  ChevronRight,
  ExternalLink,
  Layers,
  GraduationCap,
  Clock,
  Building2,
  TrendingUp,
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const SAMPLE_ROLES = [
  {
    job_id: 'sample_1',
    job_title: 'Senior Full-Stack Engineer',
    company: 'CloudNexus SaaS',
    job_description: `Senior Full-Stack Engineer with 5+ years experience building cloud applications.
Required Skills: Python, FastAPI, React, TypeScript, PostgreSQL, Docker, REST APIs.
Responsibilities: Architect responsive SPAs and scale high-throughput microservices.`,
  },
  {
    job_id: 'sample_2',
    job_title: 'Backend API Architect',
    company: 'FinTech Core',
    job_description: `Senior Backend Engineer. 5+ years writing production services.
Required Skills: Python, Django, PostgreSQL, Redis, Microservices, Docker, AWS, System Design.
Responsibilities: Design secure transactional APIs, caching layers, and high-availability databases.`,
  },
  {
    job_id: 'sample_3',
    job_title: 'DevOps & Platform Engineer',
    company: 'InfraScale Systems',
    job_description: `Lead DevOps & Cloud Engineer with 6+ years experience.
Required Skills: Kubernetes, Docker, Terraform, AWS, CI/CD, Linux, Prometheus, Python.
Responsibilities: Orchestrate multi-cluster Kubernetes deployments and automate infrastructure.`,
  },
];

export default function MultiJobComparison() {
  const { getAuthHeaders } = useAuth();
  const navigate = useNavigate();

  // Retrieve resume from session storage if uploaded earlier
  const [resumeData] = useState(() => {
    try {
      const saved = sessionStorage.getItem('uploadedResume');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [resumeText, setResumeText] = useState(() => {
    if (resumeData && resumeData.raw_text) return resumeData.raw_text;
    try {
      return sessionStorage.getItem('currentResumeText') || '';
    } catch {
      return '';
    }
  });

  const [resumeFilename] = useState(() => {
    if (resumeData && resumeData.filename) return resumeData.filename;
    return 'Candidate_Resume.pdf';
  });

  const [jobs, setJobs] = useState([
    {
      job_id: 'job_1',
      job_title: 'Senior Full-Stack Engineer',
      company: 'CloudNexus SaaS',
      job_description: '',
    },
    {
      job_id: 'job_2',
      job_title: 'Backend Python Engineer',
      company: 'DataFlow Systems',
      job_description: '',
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [comparisonResult, setComparisonResult] = useState(() => {
    try {
      const saved = sessionStorage.getItem('multiJobComparisonResult');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const handleAddJob = () => {
    if (jobs.length >= 8) {
      setErrorMessage('You can compare up to 8 job postings simultaneously.');
      return;
    }
    setErrorMessage('');
    const nextIdx = jobs.length + 1;
    setJobs([
      ...jobs,
      {
        job_id: `job_${nextIdx}`,
        job_title: `Target Role #${nextIdx}`,
        company: 'Company',
        job_description: '',
      },
    ]);
  };

  const handleRemoveJob = (indexToRemove) => {
    if (jobs.length <= 2) {
      setErrorMessage('A minimum of 2 job descriptions is required for comparison.');
      return;
    }
    setErrorMessage('');
    setJobs(jobs.filter((_, idx) => idx !== indexToRemove));
  };

  const handleJobChange = (index, field, value) => {
    const updated = [...jobs];
    updated[index][field] = value;
    setJobs(updated);
  };

  const handleLoadSampleRoles = () => {
    setJobs(SAMPLE_ROLES);
    setErrorMessage('');
    if (!resumeText) {
      setResumeText(`ALICE DEVELOPER
Senior Software Engineer | Python, React, PostgreSQL
Email: alice@example.com | 6+ years professional software development experience.

TECHNICAL SKILLS:
Languages & Frameworks: Python, FastAPI, Django, React, TypeScript, JavaScript, SQL, HTML, CSS.
Databases & Cloud: PostgreSQL, Redis, MongoDB, Docker, AWS, Git, CI/CD, Microservices.

EXPERIENCE:
Senior Full Stack Engineer (2020 - Present)
- Architected and deployed microservices using Python and FastAPI with PostgreSQL databases.
- Built responsive UI components with React, TypeScript, and Tailwind CSS.
- Managed containerized Docker deployments with automated CI/CD pipelines.`);
    }
  };

  const handleRunComparison = async () => {
    setErrorMessage('');

    if (!resumeText.trim() || resumeText.trim().length < 15) {
      setErrorMessage('Please provide a valid resume text (at least 15 characters).');
      return;
    }

    for (let i = 0; i < jobs.length; i++) {
      if (!jobs[i].job_description.trim() || jobs[i].job_description.trim().length < 15) {
        setErrorMessage(`Job #${i + 1} (${jobs[i].job_title || 'Untitled'}) description is too short (min 15 characters).`);
        return;
      }
    }

    setIsLoading(true);

    try {
      const payload = {
        resume_text: resumeText.trim(),
        resume_filename: resumeFilename,
        jobs: jobs.map((j, i) => ({
          job_id: j.job_id || `job_${i + 1}`,
          job_title: j.job_title?.trim() || `Target Role ${i + 1}`,
          company: j.company?.trim() || 'Company',
          job_description: j.job_description.trim(),
        })),
      };

      const response = await fetch(`${API_BASE_URL}/compare/multi-jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned error ${response.status}`);
      }

      const data = await response.json();
      setComparisonResult(data);
      sessionStorage.setItem('multiJobComparisonResult', JSON.stringify(data));
      window.scrollTo({ top: 500, behavior: 'smooth' });
    } catch (err) {
      setErrorMessage(err.message || 'Comparison failed. Please verify the backend service is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewFullReport = (jobMatch) => {
    if (!jobMatch || !jobMatch.full_report) return;

    // Cache the job and full report into sessionStorage so the main Dashboard can open it immediately
    sessionStorage.setItem('currentJobTitle', jobMatch.job_title);
    sessionStorage.setItem('currentCompany', jobMatch.company || '');
    sessionStorage.setItem('currentJobDescription', jobMatch.full_report.job_description_raw || '');
    sessionStorage.setItem('analysisReport', JSON.stringify(jobMatch.full_report));

    navigate('/dashboard');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 65) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 50) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-rose-600 bg-rose-50 border-rose-200';
  };

  const getBarColor = (score) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 65) return 'bg-blue-500';
    if (score >= 50) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      <Navbar />

      <main className="grow py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-8">
        {/* Header Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold uppercase tracking-wider mb-2">
              <Layers className="w-3.5 h-3.5" />
              Phase 6: Multi-Job Comparison
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Compare 1 Resume Against Multiple Roles
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-2xl">
              Evaluate your resume across multiple target jobs simultaneously. Discover your highest-matching offer, analyze skill overlap, and rank roles from best to lowest fit.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleLoadSampleRoles}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-2xs transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              Load 3 Sample Roles
            </button>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition-colors"
            >
              Single Match Dashboard
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3 shadow-2xs">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="grow flex items-center justify-between">
              <span>{errorMessage}</span>
              <button
                type="button"
                onClick={() => setErrorMessage('')}
                className="text-rose-500 hover:text-rose-700 text-xs font-bold ml-3"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Resume Input / Status */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Target Resume: <span className="text-blue-600">{resumeFilename}</span>
                </h3>
                <p className="text-xs text-slate-500">
                  {resumeData?.detected_skills?.length
                    ? `${resumeData.detected_skills.length} detected skills loaded from upload session`
                    : 'Paste or review your resume text below'}
                </p>
              </div>
            </div>

            <Link
              to="/upload"
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center gap-1"
            >
              Upload Different Resume
              <ExternalLink className="w-3 h-3" />
            </Link>
          </div>

          <div className="pt-3">
            <textarea
              rows={4}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your candidate resume text or experience highlights here..."
              className="w-full text-xs font-mono text-slate-700 bg-slate-50 border border-slate-200 rounded-lg p-3 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 transition-all leading-relaxed"
            />
          </div>
        </div>

        {/* Multiple Job Inputs Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">
                Target Job Descriptions ({jobs.length})
              </h2>
            </div>
            <button
              type="button"
              onClick={handleAddJob}
              disabled={jobs.length >= 8}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors disabled:opacity-50"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Another Job
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((job, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs flex flex-col justify-between relative group hover:border-blue-300 transition-all"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Role #{idx + 1}
                    </span>
                    {jobs.length > 2 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveJob(idx)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded-md transition-colors"
                        title="Remove this role"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 uppercase mb-1">
                      Job Title
                    </label>
                    <input
                      type="text"
                      value={job.job_title}
                      onChange={(e) => handleJobChange(idx, 'job_title', e.target.value)}
                      placeholder="e.g. Senior Backend Engineer"
                      className="w-full text-xs font-semibold text-slate-800 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 uppercase mb-1">
                      Company
                    </label>
                    <input
                      type="text"
                      value={job.company}
                      onChange={(e) => handleJobChange(idx, 'company', e.target.value)}
                      placeholder="e.g. Stripe, Remote Startup"
                      className="w-full text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 uppercase mb-1">
                      Job Description
                    </label>
                    <textarea
                      rows={6}
                      value={job.job_description}
                      onChange={(e) => handleJobChange(idx, 'job_description', e.target.value)}
                      placeholder="Paste requirements, duties, and tech stack here..."
                      className="w-full text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg p-2.5 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 leading-relaxed font-sans"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-2 flex justify-center">
            <button
              type="button"
              onClick={handleRunComparison}
              disabled={isLoading}
              className="inline-flex items-center justify-center gap-2.5 px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold text-sm shadow-md transition-all cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing & Ranking {jobs.length} Roles...
                </>
              ) : (
                <>
                  <BarChart3 className="w-5 h-5" />
                  Compare All {jobs.length} Job Postings
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* COMPARISON RESULTS DASHBOARD */}
        {/* ========================================================================= */}
        {comparisonResult && (
          <div className="space-y-8 pt-6 border-t border-slate-200">
            {/* Top Recommended Job Banner */}
            {comparisonResult.top_recommended_job && (
              <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-900 rounded-3xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>

                <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                  <div className="space-y-2 max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 text-xs font-bold uppercase tracking-wider">
                      <Trophy className="w-4 h-4 text-amber-300" />
                      Rank #1 Highest Alignment Match
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                      {comparisonResult.top_recommended_job.job_title}
                    </h2>
                    <p className="text-blue-100 text-sm flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-blue-300" />
                      {comparisonResult.top_recommended_job.company}
                      <span className="text-blue-300">•</span>
                      <span>ATS Grade: <strong>{comparisonResult.top_recommended_job.ats_grade}</strong></span>
                      <span className="text-blue-300">•</span>
                      <span>{comparisonResult.top_recommended_job.experience_status}</span>
                    </p>
                    <p className="text-blue-100/90 text-xs leading-relaxed pt-1">
                      {comparisonResult.comparison_summary}
                    </p>
                  </div>

                  <div className="shrink-0 flex flex-col items-center sm:items-end gap-3 w-full sm:w-auto">
                    <div className="flex items-baseline gap-1.5 bg-white/10 backdrop-blur-md px-5 py-3 rounded-2xl border border-white/20">
                      <span className="text-4xl sm:text-5xl font-black text-amber-300">
                        {comparisonResult.top_recommended_job.match_score}%
                      </span>
                      <span className="text-xs font-semibold text-blue-200 uppercase tracking-wide">
                        Match Score
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleViewFullReport(comparisonResult.top_recommended_job)}
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-blue-50 text-blue-900 font-bold text-xs shadow-md transition-transform hover:scale-102"
                    >
                      View Full Analysis & AI Suggestions
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Ranked Roles Leaderboard */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-bold text-slate-900">
                    Ranked Match Leaderboard ({comparisonResult.ranked_jobs?.length || 0})
                  </h3>
                </div>
                <span className="text-xs text-slate-500 font-medium">
                  Ordered from Highest to Lowest Alignment
                </span>
              </div>

              <div className="space-y-4">
                {comparisonResult.ranked_jobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col lg:flex-row lg:items-center justify-between gap-6"
                  >
                    {/* Left: Rank & Title */}
                    <div className="space-y-2 max-w-xl">
                      <div className="flex items-center gap-2.5">
                        <span
                          className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-black shrink-0 ${
                            job.rank === 1
                              ? 'bg-amber-400 text-amber-950 shadow-xs'
                              : job.rank === 2
                              ? 'bg-slate-200 text-slate-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          #{job.rank}
                        </span>
                        <h4 className="text-base font-bold text-slate-900 leading-tight">
                          {job.job_title}
                        </h4>
                        <span className="text-xs font-medium text-slate-500">
                          @ {job.company}
                        </span>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed">
                        {job.summary}
                      </p>

                      {/* Matched & Missing Skills Tags */}
                      <div className="space-y-1.5 pt-1">
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="text-[11px] font-bold text-emerald-700 flex items-center gap-1 mr-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            {job.matched_skills_count} Matched:
                          </span>
                          {job.matched_skills.slice(0, 6).map((skill, idx) => (
                            <span
                              key={idx}
                              className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200"
                            >
                              {skill}
                            </span>
                          ))}
                          {job.matched_skills.length > 6 && (
                            <span className="text-[11px] text-slate-400 font-medium">
                              +{job.matched_skills.length - 6} more
                            </span>
                          )}
                        </div>

                        {job.missing_skills.length > 0 && (
                          <div className="flex flex-wrap items-center gap-1.5">
                            <span className="text-[11px] font-bold text-amber-700 flex items-center gap-1 mr-1">
                              <XCircle className="w-3.5 h-3.5" />
                              {job.missing_skills_count} Missing:
                            </span>
                            {job.missing_skills.slice(0, 5).map((skill, idx) => (
                              <span
                                key={idx}
                                className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200"
                              >
                                {skill}
                              </span>
                            ))}
                            {job.missing_skills.length > 5 && (
                              <span className="text-[11px] text-slate-400 font-medium">
                                +{job.missing_skills.length - 5} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Right: Scores & CTA */}
                    <div className="flex flex-row lg:flex-col items-center lg:items-end justify-between lg:justify-center gap-4 shrink-0 pt-4 lg:pt-0 border-t lg:border-t-0 border-slate-100">
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <div className="flex items-baseline gap-1">
                            <span className="text-2xl font-black text-slate-900">
                              {job.match_score}%
                            </span>
                            <span className="text-[10px] font-bold uppercase text-slate-500">
                              Match
                            </span>
                          </div>
                          <span
                            className={`inline-block text-[11px] font-bold px-2 py-0.5 rounded-full border ${getScoreColor(
                              job.match_score
                            )}`}
                          >
                            ATS {job.ats_grade} ({job.ats_score}/100)
                          </span>
                        </div>

                        {/* Progress mini bar */}
                        <div className="w-16 h-2 rounded-full bg-slate-100 overflow-hidden hidden sm:block">
                          <div
                            className={`h-full rounded-full ${getBarColor(job.match_score)}`}
                            style={{ width: `${job.match_score}%` }}
                          ></div>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleViewFullReport(job)}
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold transition-colors cursor-pointer"
                      >
                        Inspect Detailed Breakdown
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Side-by-Side Comparison Matrix Table */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-2xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-blue-600" />
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                    Side-by-Side Comparison Matrix
                  </h3>
                </div>
                <span className="text-xs text-slate-500">All Metrics at a Glance</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider bg-slate-50/70">
                      <th className="py-3 px-3">Rank & Role</th>
                      <th className="py-3 px-3">Company</th>
                      <th className="py-3 px-3 text-center">Match %</th>
                      <th className="py-3 px-3 text-center">ATS Score</th>
                      <th className="py-3 px-3 text-center">Skills Score</th>
                      <th className="py-3 px-3 text-center">Semantic Sim.</th>
                      <th className="py-3 px-3">Experience</th>
                      <th className="py-3 px-3">Top Actionable Tip</th>
                      <th className="py-3 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {comparisonResult.ranked_jobs.map((job) => (
                      <tr key={job.job_id} className="hover:bg-slate-50/60 transition-colors">
                        <td className="py-3.5 px-3 font-semibold text-slate-900 flex items-center gap-2">
                          <span
                            className={`w-5 h-5 rounded-md text-[10px] font-black flex items-center justify-center shrink-0 ${
                              job.rank === 1
                                ? 'bg-amber-400 text-amber-950'
                                : 'bg-slate-200 text-slate-700'
                            }`}
                          >
                            #{job.rank}
                          </span>
                          <span className="truncate max-w-[160px]">{job.job_title}</span>
                        </td>
                        <td className="py-3.5 px-3 text-slate-600">{job.company}</td>
                        <td className="py-3.5 px-3 text-center font-bold text-slate-900">
                          <span
                            className={`px-2 py-0.5 rounded-full font-bold ${getScoreColor(
                              job.match_score
                            )}`}
                          >
                            {job.match_score}%
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-center">
                          <span className="font-semibold">{job.ats_score}</span>{' '}
                          <span className="text-[10px] text-slate-400">({job.ats_grade})</span>
                        </td>
                        <td className="py-3.5 px-3 text-center font-semibold text-slate-800">
                          {job.skills_score}%
                        </td>
                        <td className="py-3.5 px-3 text-center text-slate-600">
                          {job.semantic_similarity}%
                        </td>
                        <td className="py-3.5 px-3">
                          <span className="inline-block px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[11px]">
                            {job.experience_status}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-slate-600 max-w-xs text-[11px] leading-relaxed">
                          {job.key_recommendation}
                        </td>
                        <td className="py-3.5 px-3 text-right">
                          <button
                            type="button"
                            onClick={() => handleViewFullReport(job)}
                            className="text-xs font-bold text-blue-600 hover:text-blue-800 underline"
                          >
                            Report
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

