import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckCircle,
  AlertCircle,
  FileText,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';

export default function Hero() {
  return (
    <section id="hero" className="pt-12 pb-20 lg:pt-16 lg:pb-28 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Content Area */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          {/* Subtle Tag */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-medium mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
            Automated Resume & Job Description Comparison
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight leading-[1.15] mb-6">
            Make Your Resume <span className="text-blue-600">Job-Ready</span>
          </h1>

          {/* Description */}
          <p className="text-lg sm:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto mb-8">
            Upload your resume, compare it directly with any job description, and
            instantly identify missing skills and keywords before submitting your application.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-8">
            <Link
              to="/upload"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-base shadow-xs transition-colors"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#how-it-works"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 font-medium text-base border border-slate-200 transition-colors"
            >
              Learn More
            </a>
          </div>

          {/* Micro trust indicators */}
          <div className="flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-xs text-slate-500 font-normal">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-slate-400" />
              Private & secure
            </span>
            <span className="hidden sm:inline text-slate-300">•</span>
            <span className="flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-slate-400" />
              Supports PDF & Word (.docx)
            </span>
            <span className="hidden sm:inline text-slate-300">•</span>
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-slate-400" />
              Actionable feedback
            </span>
          </div>
        </div>

        {/* Realistic Product Preview / Resume Illustration */}
        <div className="max-w-5xl mx-auto">
          <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-3 sm:p-5 shadow-xs">
            {/* Top Mock Window Bar */}
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200/80 px-2">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-slate-300"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-slate-300"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-slate-300"></div>
                <span className="ml-2 text-xs font-medium text-slate-400">
                  Analysis Workspace — resume_v3.pdf vs. Senior_Frontend_Dev.txt
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 font-medium">
                  Report Generated
                </span>
              </div>
            </div>

            {/* Split Screen Preview */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
              {/* Left Pane: Resume Document View */}
              <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-5 sm:p-6 text-left shadow-2xs">
                <div className="flex items-start justify-between pb-4 border-b border-slate-100 mb-4">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">
                      Alex Rivera
                    </h3>
                    <p className="text-xs text-slate-500">
                      Senior Frontend Engineer • Austin, TX • alex.rivera@example.com
                    </p>
                  </div>
                  <span className="text-[11px] font-medium text-slate-400 border border-slate-200 rounded px-2 py-0.5">
                    1-page parsed
                  </span>
                </div>

                {/* Resume Summary */}
                <div className="mb-4">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Professional Summary
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Frontend engineer with 5+ years building accessible user interfaces using{' '}
                    <mark className="bg-blue-50 text-blue-700 px-1 py-0.5 rounded font-medium">
                      React
                    </mark>
                    ,{' '}
                    <mark className="bg-blue-50 text-blue-700 px-1 py-0.5 rounded font-medium">
                      TypeScript
                    </mark>
                    , and modern CSS architecture. Experienced in state management and performance tuning.
                  </p>
                </div>

                {/* Experience section */}
                <div className="mb-4">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Relevant Experience
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between items-baseline text-xs font-semibold text-slate-800">
                        <span>Lead UI Engineer — CloudMatrix Inc.</span>
                        <span className="text-[11px] font-normal text-slate-500">2023 – Present</span>
                      </div>
                      <ul className="mt-1 space-y-1 text-xs text-slate-600 list-disc list-inside">
                        <li>
                          Architected component design system reducing frontend technical debt by 30%.
                        </li>
                        <li>
                          Engineered client-side state caching using{' '}
                          <mark className="bg-blue-50 text-blue-700 px-1 py-0.5 rounded font-medium">
                            Redux Toolkit
                          </mark>{' '}
                          and RESTful endpoints.
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Extracted Skills */}
                <div>
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Detected Skills
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {['React', 'TypeScript', 'Tailwind CSS', 'Next.js', 'REST APIs', 'Git', 'Vite'].map((skill) => (
                      <span
                        key={skill}
                        className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Pane: Match Analysis & Action Items */}
              <div className="lg:col-span-5 flex flex-col gap-3.5">
                {/* Score Card */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-2xs">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-medium text-slate-500">
                      Target Role Match Score
                    </span>
                    <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full">
                      Strong Match
                    </span>
                  </div>

                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-3xl font-bold text-slate-900">86</span>
                    <span className="text-slate-400 text-sm font-normal">/ 100</span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full bg-slate-100 rounded-full h-2 mb-3 overflow-hidden">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: '86%' }}
                    ></div>
                  </div>

                  <p className="text-xs text-slate-500">
                    Matches 18 out of 21 key requirements found in the target job description.
                  </p>
                </div>

                {/* Keyword Comparison */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-3">
                  {/* Matched Keywords */}
                  <div>
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-2">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Key Qualifications Matched (5)</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {['React', 'TypeScript', 'Responsive Design', 'REST APIs', 'State Management'].map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center text-[11px] font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Missing Keywords */}
                  <div className="pt-2 border-t border-slate-100">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-2">
                      <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                      <span>Missing / Recommended Terms (3)</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {[
                        { name: 'GraphQL', note: 'Mentioned 3x in job description' },
                        { name: 'Jest / Testing', note: 'Required qualification' },
                        { name: 'CI/CD Pipelines', note: 'Preferred requirement' },
                      ].map((item) => (
                        <span
                          key={item.name}
                          title={item.note}
                          className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200/60"
                        >
                          + {item.name}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Actionable Suggestions snippet */}
                <div className="bg-blue-50/70 border border-blue-200/70 rounded-xl p-3.5 text-left">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-900 mb-1">
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    <span>Quick Suggestion</span>
                  </div>
                  <p className="text-xs text-blue-800/90 leading-relaxed">
                    Add unit test coverage or testing frameworks (e.g. Jest, Vitest) in your
                    work experience to increase ATS match by +7%.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
