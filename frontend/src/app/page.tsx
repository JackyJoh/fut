"use client";

import { useState, useMemo } from "react";
import LiquidChrome from './LiquidChrome';
import LandingPage from './LandingPage';
import PredictionPage from './PredictionPage';

type PageView = 'landing' | 'prediction';

export default function Home() {
  const [currentPage, setCurrentPage] = useState<PageView>('landing');
  
  // Memoize the LiquidChrome background to prevent re-renders
  const liquidChromeBackground = useMemo(() => (
    <LiquidChrome
      baseColor={[0.05, 0.12, 0.05]}
      speed={0.2}
      amplitude={0.6}
      interactive={false}
    />
  ), []);

  // Handle navigation to prediction page
  const handleStartPredict = () => {
    setCurrentPage('prediction');
  };

  // Handle navigation back to landing page
  const handleBackToHome = () => {
    setCurrentPage('landing');
  };

  // Main app with LiquidChrome background
  return (
    <div className="relative min-h-screen h-full overflow-x-hidden flex flex-col font-[family-name:var(--font-michroma)]">
      {/* LiquidChrome Background */}
      <div className="fixed inset-0 w-full h-full pointer-events-none" style={{ willChange: 'transform' }}>
        {liquidChromeBackground}
      </div>

      {/* Render current page */}
      {currentPage === 'landing' && <LandingPage onStartPredict={handleStartPredict} />}
      {currentPage === 'prediction' && <PredictionPage onBackToHome={handleBackToHome} />}
    </div>
  );
}
