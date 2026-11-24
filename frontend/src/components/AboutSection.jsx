import { Target, Lock, CheckCircle2 } from 'lucide-react';

export default function AboutSection() {
  const values = [
    {
      icon: Target,
      title: 'Targeted Relevance',
      description:
        'Generic resumes get filtered out. We help you calibrate your specific experiences directly to what the hiring team is looking for.',
    },
    {
      icon: Lock,
      title: 'Privacy By Design',
      description:
        'Your resume and application details are parsed securely in your session. We do not sell user data to recruiters or third parties.',
    },
    {
      icon: CheckCircle2,
      title: 'Practical Guidance',
      description:
        'No vague scores or confusing buzzwords. Every insight is backed by clear keyword matches and actionable bullet-point recommendations.',
    },
  ];

  return (
    <section id="about" className="py-20 bg-slate-50/50 border-t border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Mission / Background */}
          <div className="lg:col-span-5 space-y-5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-medium border border-blue-100">
              About ResumeMatch
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
              Built to Eliminate the Guesswork in Job Applications
            </h2>
            <p className="text-base text-slate-600 leading-relaxed">
              Applying for jobs shouldn't feel like sending resumes into a black hole.
              Most modern companies rely on Applicant Tracking Systems (ATS) to filter
              hundreds of candidates before a recruiter ever reads a single line.
            </p>
            <p className="text-base text-slate-600 leading-relaxed">
              ResumeMatch provides candid, transparent feedback so candidates know exactly
              how well their resume mirrors the job description—and what changes will make the biggest difference.
            </p>
          </div>

          {/* Right Column: Key Principles */}
          <div className="lg:col-span-7 space-y-4">
            {values.map((v) => {
              const Icon = v.icon;
              return (
                <div
                  key={v.title}
                  className="bg-white rounded-xl border border-slate-200 p-6 flex items-start gap-4"
                >
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 mb-1">
                      {v.title}
                    </h3>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      {v.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
