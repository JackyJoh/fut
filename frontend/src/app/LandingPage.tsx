"use client";

import { useState } from "react";

interface LandingPageProps {
  onStartPredict: () => void;
}

export default function LandingPage({ onStartPredict }: LandingPageProps) {
  return (
    <>
      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-3 sm:px-4 md:px-6 py-2 sm:py-3 border-b border-white/10 shrink-0 bg-[#1a1f3a]/90">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg flex items-center justify-center">
            <img src="/futPredict-removebg2.png" className="w-full h-full object-cover" alt="Fut Predict Logo" />
          </div>
          <span className="text-white font-heading font-semibold text-base sm:text-lg tracking-tight">FutPredict</span>
        </div>
      </header>

      {/* Landing Content */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 sm:px-6 md:px-8">
        {/* Ambient glow behind hero */}
        <div className="ambient-glow top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          {/* Hero Section */}
          <div className="mb-8 sm:mb-12">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-heading font-bold text-white mb-4 sm:mb-6 tracking-tight">
              Uncover Football&apos;s
              <br />
              <span className="text-cyan-400">
                Next Superstars
              </span>
            </h1>
            <p className="text-slate-300 text-base sm:text-lg md:text-xl max-w-2xl mx-auto mb-8 sm:mb-10 leading-relaxed font-light">
              AI-powered predictions for FIFA player ratings, market values, and performance stats.
              See how your favorite players will evolve across multiple seasons.
            </p>

            {/* CTA Button */}
            <button
              onClick={onStartPredict}
              className="group relative px-8 sm:px-10 py-3 sm:py-4 rounded-lg font-heading font-semibold text-base sm:text-lg bg-cyan-500 hover:bg-cyan-600 text-white transition-all duration-200 shadow-[0_0_20px_rgba(34,211,238,0.15)] hover:shadow-[0_0_30px_rgba(34,211,238,0.3)]"
            >
              Start Predicting
              <span className="ml-2 inline-block transition-transform group-hover:translate-x-1">→</span>
            </button>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mt-12 sm:mt-16">
            <div className="card-glow bg-white/5 border border-white/10 rounded-lg p-4 sm:p-6 hover:border-cyan-400/30 hover:bg-white/[0.07] transition-all duration-200">
              <svg className="w-6 h-6 text-cyan-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              <h3 className="text-white font-heading font-semibold text-base sm:text-lg mb-2">AI Predictions</h3>
              <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                Advanced machine learning models trained on historical FIFA and FBref data
              </p>
            </div>

            <div className="card-glow bg-white/5 border border-white/10 rounded-lg p-4 sm:p-6 hover:border-cyan-400/30 hover:bg-white/[0.07] transition-all duration-200">
              <svg className="w-6 h-6 text-cyan-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              <h3 className="text-white font-heading font-semibold text-base sm:text-lg mb-2">Multi-Season</h3>
              <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                Project player development up to 9 seasons into the future
              </p>
            </div>

            <div className="card-glow bg-white/5 border border-white/10 rounded-lg p-4 sm:p-6 hover:border-cyan-400/30 hover:bg-white/[0.07] transition-all duration-200">
              <svg className="w-6 h-6 text-cyan-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <h3 className="text-white font-heading font-semibold text-base sm:text-lg mb-2">Market Value</h3>
              <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                Track predicted market value changes alongside performance metrics
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 text-center py-4 border-t border-white/10">
        <p className="text-sm text-slate-400">Powered by AI • Data from FIFA & FBref</p>
      </footer>
    </>
  );
}
