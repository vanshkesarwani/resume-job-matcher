import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Features from '../components/Features';
import HowItWorks from '../components/HowItWorks';
import AboutSection from '../components/AboutSection';
import CtaBanner from '../components/CtaBanner';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-white text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />
      <main className="grow">
        <Hero />
        <Features />
        <HowItWorks />
        <AboutSection />
        <CtaBanner />
      </main>
      <Footer />
    </div>
  );
}
