import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FileCheck2, Menu, X, ArrowRight, User, LogOut, LayoutDashboard, Layers } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const isHome = location.pathname === '/';

  const navLinks = [
    { name: 'Home', href: isHome ? '#hero' : '/' },
    { name: 'Features', href: isHome ? '#features' : '/#features' },
    { name: 'How It Works', href: isHome ? '#how-it-works' : '/#how-it-works' },
    { name: 'About', href: isHome ? '#about' : '/#about' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-xs border-b border-slate-100 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs transition-transform group-hover:scale-105">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold text-slate-900 tracking-tight leading-tight">
                ResumeMatch
              </span>
              <span className="text-[10px] text-slate-500 font-medium tracking-wide uppercase">
                Job-Ready Analyzer
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
              >
                {link.name}
              </a>
            ))}
            <Link
              to="/compare"
              className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors inline-flex items-center gap-1.5"
            >
              <Layers className="w-4 h-4 text-blue-600" />
              Compare Jobs
            </Link>
            {isAuthenticated && (
              <Link
                to="/dashboard"
                className="text-sm font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center gap-1.5"
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>
            )}
          </nav>

          {/* Action Buttons */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-full bg-slate-50 border border-slate-200">
                  <div className="w-6 h-6 rounded-full bg-blue-600 text-white text-[11px] font-bold flex items-center justify-center">
                    {user?.name ? user.name[0].toUpperCase() : <User className="w-3.5 h-3.5" />}
                  </div>
                  <span className="text-xs font-semibold text-slate-800">
                    {user?.name?.split(' ')[0] || 'Account'}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={handleLogout}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-red-600 px-3 py-2 rounded-lg hover:bg-red-50/50 transition-colors"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-slate-700 hover:text-slate-900 px-3.5 py-2 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors shadow-xs"
                >
                  Sign Up
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-hidden"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-6 space-y-3">
          <div className="space-y-1">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-base font-medium text-slate-700 hover:text-blue-600 hover:bg-blue-50/50 rounded-md transition-colors"
              >
                {link.name}
              </a>
            ))}
            <Link
              to="/compare"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 text-base font-medium text-slate-700 hover:text-blue-600 hover:bg-blue-50/50 rounded-md transition-colors"
            >
              Compare Multiple Jobs
            </Link>
            {isAuthenticated && (
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-base font-semibold text-blue-600 hover:bg-blue-50/50 rounded-md transition-colors"
              >
                Dashboard
              </Link>
            )}
          </div>
          <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
            {isAuthenticated ? (
              <div className="space-y-2">
                <div className="text-xs text-slate-500 px-3">
                  Signed in as <strong>{user?.email}</strong>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg border border-slate-200 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition-colors"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
