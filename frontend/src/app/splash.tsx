"use client";

import { useMemo } from "react";
import LiquidChrome from './LiquidChrome';

interface SplashProps {
  onComplete?: () => void;
}

export default function Splash({ onComplete }: SplashProps) {
  const liquidChromeBackground = useMemo(() => (
    <LiquidChrome
      baseColor={[0.05, 0.12, 0.05]}
      speed={0.2}
      amplitude={0.6}
      interactive={false}
    />
  ), []);

  return (
    <div className="relative h-screen w-screen overflow-hidden flex items-center justify-center">
      {/* LiquidChrome Background */}
      <div className="absolute inset-0">
        {liquidChromeBackground}
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-8 animate-fade-in">
        {/* Logo */}
        <div className="w-64 h-64 flex items-center justify-center">
          <img 
            src="/futPredict-removebg2.png" 
            alt="Fut Predict Logo" 
            className="w-full h-full object-contain drop-shadow-2xl"
          />
        </div>

        {/* Title */}
        <div className="text-center backdrop-blur-md bg-black/20 px-12 py-8 rounded-2xl border border-white/10">
          <h1 className="text-5xl font-bold text-white mb-3 tracking-wide">
            FUT PREDICT
          </h1>
          <p className="text-emerald-400 text-lg tracking-widest">
            Uncover Football's Next Superstars
          </p>
        </div>

        {/* Optional: Click to continue */}
        {onComplete && (
          <button
            onClick={onComplete}
            className="mt-8 px-8 py-3 backdrop-blur-md bg-black/20 border-2 border-emerald-500/50 hover:border-emerald-500 text-emerald-400 hover:text-emerald-300 font-semibold rounded-xl transition-all hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/20"
          >
            Get Started
          </button>
        )}
      </div>

      {/* fade-in animation is now in globals.css as a utility class */}
    </div>
  );
}
