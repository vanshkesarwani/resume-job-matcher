import { Link } from 'react-router-dom';
import { FileCheck2 } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-50 border-t border-slate-200/80 text-slate-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 lg:gap-12 mb-12">
          {/* Brand info */}
          <div className="md:col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center">
                <FileCheck2 className="w-4 h-4" />
              </div>
              <span className="text-base font-bold text-slate-900 tracking-tight">
                ResumeMatch
              </span>
            </Link>
            <p className="text-sm text-slate-500 leading-relaxed max-w-sm">
              Helping job seekers compare their resumes directly against job descriptions,
              identify missing skills, and format with confidence for applicant tracking systems.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
              All systems operational
            </div>
          </div>

          {/* Product links */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-4">
              Product
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a href="#features" className="hover:text-blue-600 transition-colors">
                  Resume Upload
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-blue-600 transition-colors">
                  ATS Score Analysis
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-blue-600 transition-colors">
                  Job Match Engine
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-blue-600 transition-colors">
                  How It Works
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-4">
              Resources
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  ATS Guide 2026
                </span>
              </li>
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  Resume Formatting Tips
                </span>
              </li>
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  Keyword Optimization
                </span>
              </li>
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  Action Verbs Directory
                </span>
              </li>
            </ul>
          </div>

          {/* Company & Support */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-4">
              Company
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a href="#about" className="hover:text-blue-600 transition-colors">
                  About Us
                </a>
              </li>
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  Privacy Policy
                </span>
              </li>
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  Terms of Service
                </span>
              </li>
              <li>
                <span className="text-slate-600 hover:text-blue-600 cursor-pointer transition-colors">
                  Support
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-slate-200/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} ResumeMatch. Designed for focused, job-ready applications.</p>
          <div className="flex items-center gap-6">
            <span className="hover:text-slate-800 cursor-pointer transition-colors">Privacy</span>
            <span className="hover:text-slate-800 cursor-pointer transition-colors">Security</span>
            <span className="hover:text-slate-800 cursor-pointer transition-colors">Terms</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
