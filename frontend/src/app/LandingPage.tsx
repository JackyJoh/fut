"use client";

import { useState } from "react";

interface LandingPageProps {
  onStartPredict: () => void;
}

export default function LandingPage({ onStartPredict }: LandingPageProps) {
  return (
    <>
      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-3 sm:px-4 md:px-6 py-2 sm:py-3 border-b border-white/25 shrink-0 bg-[#0a0f0a]/90">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg flex items-center justify-center">
            <img src="/futPredict-removebg2.png" className="w-full h-full object-cover" alt="Fut Predict Logo" />
          </div>
          <span className="text-white font-semibold text-base sm:text-lg">Fut Predict</span>
        </div>
      </header>

      {/* Landing Content */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 sm:px-6 md:px-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* Hero Section */}
          <div className="mb-8 sm:mb-12">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-4 sm:mb-6">
              Uncover Football&apos;s
              <br />
              <span className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-blue-500 bg-clip-text text-transparent">
                Next Superstars
              </span>
            </h1>
            <p className="text-gray-300 text-base sm:text-lg md:text-xl max-w-2xl mx-auto mb-8 sm:mb-10">
              AI-powered predictions for FIFA player ratings, market values, and performance stats. 
              See how your favorite players will evolve across multiple seasons.
            </p>
            
            {/* CTA Button */}
            <button
              onClick={onStartPredict}
              className="group relative px-8 sm:px-10 py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:from-emerald-400 hover:to-cyan-400 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-emerald-500/50 hover:shadow-emerald-400/60"
            >
              Start Predicting
              <span className="ml-2 inline-block transition-transform group-hover:translate-x-1">→</span>
            </button>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mt-12 sm:mt-16">
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-4 sm:p-6">
              <div className="text-3xl sm:text-4xl mb-3">⚡</div>
              <h3 className="text-white font-bold text-base sm:text-lg mb-2">AI Predictions</h3>
              <p className="text-gray-400 text-xs sm:text-sm">
                Advanced machine learning models trained on historical FIFA and FBref data
              </p>
            </div>
            
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-4 sm:p-6">
              <div className="text-3xl sm:text-4xl mb-3">📊</div>
              <h3 className="text-white font-bold text-base sm:text-lg mb-2">Multi-Season</h3>
              <p className="text-gray-400 text-xs sm:text-sm">
                Project player development up to 9 seasons into the future
              </p>
            </div>
            
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-4 sm:p-6">
              <div className="text-3xl sm:text-4xl mb-3">💎</div>
              <h3 className="text-white font-bold text-base sm:text-lg mb-2">Market Value</h3>
              <p className="text-gray-400 text-xs sm:text-sm">
                Track predicted market value changes alongside performance metrics
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 text-center text-gray-500 text-xs py-4">
        <p>Powered by AI • Data from FIFA & FBref</p>
      </footer>
    </>
  );
}
