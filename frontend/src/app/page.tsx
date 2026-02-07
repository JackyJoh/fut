"use client";

import { useState } from "react";
import LandingPage from './LandingPage';
import PredictionPage from './PredictionPage';

type PageView = 'landing' | 'prediction';

export default function Home() {
  const [currentPage, setCurrentPage] = useState<PageView>('landing');

  // Handle navigation to prediction page
  const handleStartPredict = () => {
    setCurrentPage('prediction');
  };

  // Handle navigation back to landing page
  const handleBackToHome = () => {
    setCurrentPage('landing');
  };

  return (
    <div className="relative min-h-screen h-full overflow-x-hidden flex flex-col bg-[#151829]">
      {/* Render current page */}
      {currentPage === 'landing' && <LandingPage onStartPredict={handleStartPredict} />}
      {currentPage === 'prediction' && <PredictionPage onBackToHome={handleBackToHome} />}
    </div>
  );
}
