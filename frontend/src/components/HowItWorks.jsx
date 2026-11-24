import { UploadCloud, FileText, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function HowItWorks() {
  const steps = [
    {
      step: '01',
      title: 'Upload your resume',
      description:
        'Select your current resume in PDF or Word (.docx) format. Our parser extracts experience, skills, and education cleanly.',
      icon: UploadCloud,
    },
    {
      step: '02',
      title: 'Paste the job description',
      description:
        'Copy and paste the responsibilities, qualifications, and requirements from the specific role you are applying for.',
      icon: FileText,
    },
    {
      step: '03',
      title: 'Review match & optimize',
      description:
        'Instantly review your compatibility score, identify missing keywords, and follow targeted recommendations to tailor your resume.',
      icon: CheckCircle2,
    },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-medium border border-blue-100 mb-3">
            Simple 3-Step Process
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight mb-4">
            How It Works
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            A straightforward process designed to save you time and give you clear,
            actionable guidance for every job you apply to.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {steps.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className="relative bg-white rounded-xl border border-slate-200 p-8 flex flex-col justify-between"
              >
                <div>
                  {/* Step Number & Icon */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-3xl font-extrabold text-slate-200">
                      {item.step}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    {item.description}
                  </p>
                </div>

                {/* Subtle indicator */}
                <div className="mt-6 pt-4 border-t border-slate-100 text-xs font-medium text-blue-600 flex items-center gap-1">
                  <span>Step {index + 1} of 3</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Action Link */}
        <div className="mt-12 text-center">
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700 group"
          >
            Try it with your resume
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </div>
    </section>
  );
}
