import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function CtaBanner() {
  return (
    <section className="py-16 bg-white border-t border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 rounded-2xl p-8 sm:p-12 text-center text-white relative overflow-hidden">
          {/* Subtle accent border */}
          <div className="max-w-2xl mx-auto space-y-4">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Ready to Make Your Resume Job-Ready?
            </h2>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Upload your resume and test it against your target job posting in less than two minutes.
            </p>
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3.5">
              <Link
                to="/upload"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-colors shadow-xs"
              >
                Upload Resume Now
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href="#features"
                className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm border border-slate-700 transition-colors"
              >
                Explore Features
              </a>
            </div>
            <p className="text-xs text-slate-400 pt-2">
              Free to get started • No account required to test sample resumes
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
