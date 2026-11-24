import { UploadCloud, BarChart3, GitCompare, Sparkles, Check } from 'lucide-react';

export default function Features() {
  const features = [
    {
      id: 1,
      title: 'Resume Upload',
      description:
        'Upload resumes in PDF or Word (.docx) formats. The parser extracts your contact info, work history, education, and technical competencies cleanly.',
      icon: UploadCloud,
      badge: 'PDF & DOCX',
      benefits: ['Fast document extraction', 'Preserves clean hierarchy', 'No complex reformatting needed'],
    },
    {
      id: 2,
      title: 'ATS Score Analysis',
      description:
        'Check formatting compliance and keyword density to see how standard Applicant Tracking Systems parse and score your profile.',
      icon: BarChart3,
      badge: 'Scoring Engine',
      benefits: ['Layout readability checks', 'Scoring benchmark (0–100)', 'Formatting risk alerts'],
    },
    {
      id: 3,
      title: 'Job Description Matching',
      description:
        'Paste any job posting to perform a direct side-by-side keyword and qualification comparison. See your exact coverage rate instantly.',
      icon: GitCompare,
      badge: 'Gap Analysis',
      benefits: ['Matched vs. missing skills', 'Keyword density detection', 'Role requirement alignment'],
    },
    {
      id: 4,
      title: 'Improvement Suggestions',
      description:
        'Receive actionable, bullet-by-bullet recommendations to rephrase achievements, include critical missing terms, and highlight measurable impact.',
      icon: Sparkles,
      badge: 'Actionable Tips',
      benefits: ['Action verb recommendations', 'Measurable impact prompts', 'Keyword placement guidance'],
    },
  ];

  return (
    <section id="features" className="py-20 bg-slate-50/60 border-y border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-medium border border-blue-100 mb-3">
            Core Capabilities
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight mb-4">
            Everything You Need to Tailor Your Application
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            Focused, practical tools engineered to help you identify missing qualifications
            and optimize your resume before submitting to competitive roles.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.id}
                className="bg-white rounded-xl border border-slate-200/90 p-6 flex flex-col justify-between hover:border-slate-300 hover:shadow-xs transition-all duration-200"
              >
                <div>
                  {/* Icon & Badge */}
                  <div className="flex items-center justify-between mb-5">
                    <div className="w-11 h-11 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                      {feature.badge}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed mb-6">
                    {feature.description}
                  </p>
                </div>

                {/* Benefits List */}
                <div className="pt-4 border-t border-slate-100">
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit, i) => (
                      <li key={i} className="flex items-center gap-2 text-xs text-slate-600">
                        <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
