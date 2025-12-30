"use client";

import { useState, useEffect, useRef, useMemo } from "react";
// List of seasons for tabs
const SEASONS = [
  "25/26", "26/27", "27/28", "28/29", "29/30", "30/31", "31/32", "32/33", "33/34"
];
import GlareHover from './GlareHover';
import LiquidChrome from './LiquidChrome';
import CountUp from './CountUp';
import Splash from './splash';

interface PlayerSuggestion {
  idPlayer: string;
  strPlayer: string;
  strTeam: string;
  strNationality: string;
  fullData?: any; // Store the full player object from backend
}

// Helper function to convert nationality name to ISO 3166-1 alpha-2 country code (lowercase, for flagcdn)
function getNationalityCode(nationality: string) {
  const mapping: Record<string, string> = {
    "france": "fr",
    "england": "gb",
    "germany": "de",
    "spain": "es",
    "italy": "it",
    "portugal": "pt",
    "netherlands": "nl",
    "brazil": "br",
    "argentina": "ar",
    "belgium": "be",
    "croatia": "hr",
    "uruguay": "uy",
    "poland": "pl",
    "denmark": "dk",
    "norway": "no",
    "sweden": "se",
    "switzerland": "ch",
    "austria": "at",
    "turkey": "tr",
    "morocco": "ma",
    "united states": "us",
    "canada": "ca",
    "mexico": "mx",
    "japan": "jp",
    "south korea": "kr",
    "serbia": "rs",
    "slovenia": "si",
    "czech republic": "cz",
    "slovakia": "sk",
    "hungary": "hu",
    "russia": "ru",
    "ukraine": "ua",
    "ghana": "gh",
    "nigeria": "ng",
    "cameroon": "cm",
    "senegal": "sn",
    "ivory coast": "ci",
    "egypt": "eg",
    "australia": "au",
    "chile": "cl",
    "colombia": "co",
    "ecuador": "ec",
    "paraguay": "py",
    "peru": "pe",
    "saudi arabia": "sa",
    "iran": "ir",
    "algeria": "dz",
    "tunisia": "tn",
    "greece": "gr",
    "romania": "ro",
    "bosnia and herzegovina": "ba",
    "wales": "gb-wls",
    "scotland": "gb-sct",
    "northern ireland": "gb-nir",
    // Add more mappings as needed
  };
  const normalizedNationality = nationality.trim().toLowerCase();
  return mapping[normalizedNationality] || null;
}

export default function Home() {
  const [showSplash, setShowSplash] = useState(true);
  const [playerSearch, setPlayerSearch] = useState("");
  const [displayedPlayerName, setDisplayedPlayerName] = useState("");
  const [selectedSeason, setSelectedSeason] = useState("2024-25");
  const [playerImage, setPlayerImage] = useState("");
  const [isLoadingImage, setIsLoadingImage] = useState(false);
  const [teamBadge, setTeamBadge] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<PlayerSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [age, setAge] = useState<number | null>(null);
  const [currentOverall, setCurrentOverall] = useState<number | null>(null);
  const [position, setPosition] = useState<string | null>(null);
  const [club, setClub] = useState<string | null>(null);
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | null>(null);
  const [predictedStatsLib, setPredictedStatsLib] = useState<any>(null);
  const [nationalityText, setNationalityText] = useState<string | null>(null);
  const [selectedPredictionSeason, setSelectedPredictionSeason] = useState("25/26");
  const [currentValue, setCurrentValue] = useState<number | null>(null);
  
  // Memoize the LiquidChrome background to prevent re-renders
  const liquidChromeBackground = useMemo(() => (
    <LiquidChrome
      baseColor={[0.05, 0.12, 0.05]}
      speed={0.2}
      amplitude={0.6}
      interactive={false}
    />
  ), []);
  
  if (showSplash) {
    return <Splash onComplete={() => setShowSplash(false)} />;
  }
  
  const fetchSuggestions = async (query: string) => {
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    setIsLoadingSuggestions(true);
    try {
      const response = await fetch(
        `http://localhost:8000/searchPlayers?name=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      
      if (data && data.length > 0) {
        // Map backend data to PlayerSuggestion format and store full data
        const players = data.slice(0, 5).map((p: any) => ({
          idPlayer: p.playerID?.toString() || p.id?.toString(),
          strPlayer: p.shortName || p.name,
          strTeam: p.club_name || "",
          strNationality: p.nationality_name || "",
          fullData: p // Store the complete player object
        }));
        setSuggestions(players);
        setShowSuggestions(true);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (error) {
      console.error("Error fetching suggestions:", error);
      setSuggestions([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const fetchPlayerImage = async (playerName: string, clubName?: string, nationality?: string) => {
    if (!playerName.trim()) {
      setPlayerImage("");
      return;
    }

    setIsLoadingImage(true);
    
    // Store fetched data temporarily
    let tempPlayerImage = "";
    let tempTeamBadge: string | null = null;
    
    try {
      const response = await fetch(
        `https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p=${encodeURIComponent(playerName)}`
      );
      const data = await response.json();
      
      if (data.player && data.player.length > 0) {
        // Filter for soccer players only
        const soccerPlayers = data.player.filter((p: any) => p.strSport?.toLowerCase() === 'soccer');
        
        if (soccerPlayers.length > 0) {
          const player = soccerPlayers[0];
          const image = player.strThumb || player.strCutout;
          tempPlayerImage = image || "";
          
          // Fetch team badge using team name
          if (player.strTeam) {
            try {
              const teamResponse = await fetch(
                `https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=${encodeURIComponent(player.strTeam)}`
              );
              const teamData = await teamResponse.json();
              if (teamData.teams && teamData.teams.length > 0) {
                // Filter for soccer teams only
                const soccerTeams = teamData.teams.filter((t: any) => t.strSport?.toLowerCase() === 'soccer');
                if (soccerTeams.length > 0) {
                  tempTeamBadge = soccerTeams[0].strBadge || null;
                }
              }
            } catch (error) {
              console.error("Error fetching team badge:", error);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error fetching player image:", error);
    }
    
    // Set all data at once after everything is loaded
    setPlayerImage(tempPlayerImage);
    setTeamBadge(tempTeamBadge);
    if (nationality) {
      setNationalityText(nationality);
    }
    setIsLoadingImage(false);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPlayerSearch(value);
    // Clear suggestions immediately on input
    setSuggestions([]);
    setShowSuggestions(false);
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    // Debounce search
    searchTimeoutRef.current = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);
  };

  const handleSelectPlayer = async (player: PlayerSuggestion) => {
    setPlayerSearch("");
    setDisplayedPlayerName(player.strPlayer);
    setShowSuggestions(false);
    setSuggestions([]);
    
    // Clear all images and data first
    setPlayerImage("");
    setTeamBadge(null);
    setNationalityText(null);
    setPredictedStatsLib(null);
    
    // Set player data from backend
    if (player.fullData) {
      const data = player.fullData;
      const playerId = data.id?.toString() || data.playerID?.toString() || null;
      setSelectedPlayerId(playerId);
      setAge(data.age_fifa || null);
      setCurrentOverall(data.overall || null);
      setPosition(data.player_positions || null);
      setClub(data.club_name || null);
      setCurrentValue(data.value_eur || null);
      
      // Fetch images independently (don't wait for them)
      fetchPlayerImage(player.strPlayer, data.club_name, data.nationality_name || null);
      
      // Automatically predict rating (runs in parallel with image loading)
      if (playerId) {
        setPredictedStatsLib(null);
        try {
          const response = await fetch(
            `http://localhost:8000/predictPlayer/${playerId}`
          );
          const predData = await response.json();
          console.log("Predicted Data:", predData);
          setPredictedStatsLib(predData.predicted_stats);
        } catch (error) {
          console.error("Error fetching predicted data:", error);
        }
      }
    } else {
      // Fallback if no fullData
      fetchPlayerImage(player.strPlayer);
    }
  };

  const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      fetchPlayerImage(playerSearch);
    }
  };

  const handlePredict = async () => {
    // Get the selected player's ID from stored data
    const playerID = selectedPlayerId;
    if (!playerID) return;

    //setall data to null/loading states
    setPredictedStatsLib(null);

    try {
      const response = await fetch(
        `http://localhost:8000/predictPlayer/${playerID}`
      );
      const data = await response.json();
      console.log("Predicted Data:", data);
      setPredictedStatsLib(data.predicted_stats);
    } catch (error) {
      console.error("Error fetching predicted data:", error);
    }
  }

  return (
    <div className="relative h-screen overflow-hidden md:overflow-hidden flex flex-col font-[family-name:var(--font-michroma)]">
      {/* LiquidChrome Background */}
      <div className="absolute inset-0">
        {liquidChromeBackground}
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-3 sm:px-4 md:px-6 py-2 sm:py-3 border-b border-white/25 shrink-0 bg-[#0a0f0a]/90">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg flex items-center justify-center">
            <img src= "futpredict-removebg2.png" className="w-full h-full object-cover" alt="Fut Predict Logo" />
          </div>
          <span className="text-white font-semibold text-base sm:text-lg">Fut Predict</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 px-3 sm:px-4 md:px-6 py-3 sm:py-4 w-full md:w-[95vw] mx-auto flex-1 flex flex-col min-h-0 opacity-100 overflow-y-auto">
        {/* Title Section */}
        <div className="mb-3 sm:mb-4 shrink-0">
          <h1 className="text-xl sm:text-2xl font-bold text-white mb-1">FIFA Rating Predictor</h1>
          <p className="text-gray-400 text-xs sm:text-sm">Uncover Football&apos;s Next Superstars</p>
        </div>

        {/* Main Grid */}
        <div className="flex flex-col md:grid md:grid-cols-2 lg:grid-cols-[1fr_2fr] gap-2 sm:gap-3 md:gap-4 pb-4 md:pb-0 md:flex-1 md:min-h-0 md:items-stretch">
          {/* Left Column - Narrower */}
          <div className="flex flex-col gap-2 sm:gap-3 shrink-0 md:shrink md:min-h-0 md:h-full">
            {/* Search Row */}
            <div className="flex gap-2 sm:gap-3 shrink-0">
              <div className="flex-1 relative">
                <input
                  type="text"
                  placeholder="e.g., Kylian Mbappe"
                  value={playerSearch}
                  onChange={handleSearchChange}
                  onKeyDown={handleSearchSubmit}
                  onFocus={() => {
                    if (suggestions.length > 0) setShowSuggestions(true);
                  }}
                  className="w-full backdrop-blur-md bg-black/20 border border-white/10 rounded-lg py-1.5 sm:py-2 pl-2.5 sm:pl-3 pr-2.5 sm:pr-3 text-white text-xs sm:text-sm placeholder-gray-500 focus:outline-none focus:border-emerald-500/50"
                />
                
                {/* Suggestions Dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 backdrop-blur-md bg-black/20 border border-white/10 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                    {suggestions.map((player) => (
                      <div
                        key={player.idPlayer}
                        onClick={() => handleSelectPlayer(player)}
                        className="px-3 py-2 hover:bg-emerald-500/20 cursor-pointer border-b border-white/5 last:border-b-0 transition-colors"
                      >
                        <div className="text-white text-sm font-semibold">{player.strPlayer}</div>
                        <div className="text-gray-400 text-xs">{player.strTeam} • {player.strNationality}</div>
                      </div>
                    ))}
                  </div>
                )}
                
                {isLoadingSuggestions && (
                  <div className="absolute top-full left-0 right-0 mt-1 backdrop-blur-md bg-black/20 border border-white/10 rounded-lg shadow-lg z-50 px-3 py-2">
                    <div className="text-gray-400 text-sm">Searching...</div>
                  </div>
                )}
              </div>
            </div>

            {/* Current Player Info Card - New Layout */}
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-2.5 sm:p-3 md:p-4 flex flex-col shrink-0 md:flex-1">
              {/* Top: Name and Info - 1/3 */}
              <div className="flex flex-col gap-1.5 sm:gap-2">
                <div className="text-white font-bold text-base sm:text-lg md:text-xl lg:text-2xl leading-tight truncate">{displayedPlayerName || '--'}</div>
                <div className="flex flex-row justify-around text-base text-white/90 font-mono w-full mt-0.5 sm:mt-1">
                  {/* OVR */}
                  <div className="flex flex-col items-center px-1">
                    <span className="font-semibold text-[9px] sm:text-[10px] md:text-xs uppercase tracking-wider text-gray-400">OVR</span>
                    <span className="block text-center text-base sm:text-lg md:text-xl font-bold text-white">{currentOverall !== null ? currentOverall : '--'}</span>
                  </div>
                  {/* Age */}
                  <div className="flex flex-col items-center px-1">
                    <span className="font-semibold text-[9px] sm:text-[10px] md:text-xs uppercase tracking-wider text-gray-400">Age</span>
                    <span className="block text-center text-base sm:text-lg md:text-xl font-bold text-white">{age !== null ? age : '--'}</span>
                  </div>
                  {/* Position */}
                  <div className="flex flex-col items-center px-1">
                    <span className="font-semibold text-[9px] sm:text-[10px] md:text-xs uppercase tracking-wider text-gray-400">Pos</span>
                    <span className="block text-center text-base sm:text-lg md:text-xl font-bold text-white">{position || '--'}</span>
                  </div>
                  {/* Value */}
                  <div className="flex flex-col items-center px-1">
                    <span className="font-semibold text-[9px] sm:text-[10px] md:text-xs uppercase tracking-wider text-gray-400">Value</span>
                    <span className="block text-center text-base sm:text-lg md:text-xl font-bold text-white">{currentValue !== null ? `$${((currentValue * 1.18) / 1000000).toFixed(1)}M` : '--'}</span>
                  </div>
                </div>
              </div>

              {/* Spacer for large screens */}
              <div className="hidden md:block md:flex-1"></div>

              {/* Images Section - 2/3 */}
              <div className="flex flex-row gap-1 sm:gap-2 items-end h-fit mt-1.5 sm:mt-2">
                {/* Left: Player Image - 3/5 width */}
                <div className="w-3/5 md:w-3/5 aspect-[3/5] max-h-[160px] sm:max-h-[180px] md:max-h-none rounded-md sm:rounded-lg flex items-center justify-center border-2 sm:border-3 border-emerald-500/30 overflow-hidden transition-all duration-300 bg-black/10">
                  {isLoadingImage ? (
                    <span className="text-white text-[10px] sm:text-xs">Loading...</span>
                  ) : playerImage ? (
                    <img
                      src={playerImage}
                      alt={playerSearch}
                      className="w-full h-full object-cover object-top lg:object-center"
                    />
                  ) : (
                    <span className="text-3xl sm:text-4xl">👤</span>
                  )}
                </div>
                {/* Right: Club badge (top), Flag (bottom) - 2/5 width */}
                <div className="w-2/5 flex flex-col items-center justify-around h-full min-h-[100px] sm:min-h-[120px] md:min-h-[180px] pb-1 sm:pb-2">
                  {/* Club Badge */}
                  <div className="w-[50px] h-[50px] sm:w-[58px] sm:h-[58px] md:w-[85px] md:h-[85px] lg:w-[106px] lg:h-[106px] rounded flex items-center justify-center overflow-hidden transition-all duration-300">
                    {teamBadge ? (
                      <img src={teamBadge} alt="Club Badge" className="w-full h-full object-contain" />
                    ) : (
                      <span className="text-[9px] sm:text-[10px] font-semibold text-gray-400">CLUB</span>
                    )}
                  </div>
                  {/* Nationality Flag */}
                  <div className="w-[60px] h-[32px] sm:w-[69px] sm:h-[37px] md:w-[100px] md:h-[53px] lg:w-[127px] lg:h-[67px] rounded flex items-center justify-center overflow-hidden transition-all duration-300">
                    {nationalityText && getNationalityCode(nationalityText) ? (
                      <img
                        src={`https://flagcdn.com/${getNationalityCode(nationalityText)}.svg`}
                        alt={nationalityText}
                        className="w-full h-full object-contain rounded"
                        onError={(e) => {
                          console.error("Flag failed to load");
                          e.currentTarget.outerHTML = '<span class=\"text-[9px] sm:text-[10px] font-semibold text-gray-400\">NAT</span>';
                        }}
                        onLoad={() => console.log("Flag loaded successfully")}
                      />
                    ) : (
                      <span className="text-[9px] sm:text-[10px] font-semibold text-gray-400">NAT</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="flex flex-col gap-2 sm:gap-3 shrink-0 md:shrink md:min-h-0 md:h-full">
            {/* Season Tabs - responsive grid layout */}
            <div className="w-full mb-0">
              {/* Mobile: 3x3 grid, Tablet portrait: 3x3 grid, Tablet landscape+: single row */}
              <div className="grid grid-cols-3 sm:grid-cols-3 lg:flex lg:flex-row gap-1.5 sm:gap-2 w-full lg:justify-between">
                {SEASONS.map((season) => (
                  <button
                    key={season}
                    onClick={() => setSelectedPredictionSeason(season)}
                    className={
                      `h-[32px] sm:h-[36px] lg:h-[37.14px] px-1 sm:px-2 lg:px-0 rounded-md lg:rounded-lg backdrop-blur-md bg-transparent text-[10px] sm:text-xs font-bold transition-all duration-200 flex items-center justify-center lg:flex-1
                      ${selectedPredictionSeason === season ? 'border-2 border-emerald-400 bg-emerald-500/90 shadow-md text-white' : 'border border-white/4 hover:bg-emerald-400/30 text-gray-400'}
                      `
                    }
                    style={{ minWidth: 0 }}
                  >
                    {season}
                  </button>
                ))}
              </div>
            </div>
            {/* Predicted Rating Card */}
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-3 sm:p-4 flex flex-col shrink-0">
              <h3 className="text-gray-400 text-[10px] sm:text-xs mb-1.5 sm:mb-2">Predicted Rating:</h3>
              <div className="flex items-center gap-2 sm:gap-3 flex-wrap sm:flex-nowrap">
                <span className="text-3xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 via-emerald-400 to-blue-500 bg-clip-text text-transparent">
                  {predictedStatsLib?.predictOverall ? (
                    <CountUp to={Number(predictedStatsLib.predictOverall.toFixed(0))} duration={1.0} />
                  ) : (
                    "--"
                  )}
                </span>
                <div className={`flex items-center gap-1 ${predictedStatsLib?.predictRatingChange && predictedStatsLib.predictRatingChange < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  <span className="text-lg sm:text-xl md:text-2xl">{predictedStatsLib?.predictRatingChange && predictedStatsLib.predictRatingChange < 0 ? '↓' : '↑'}</span>
                  <span className="text-base sm:text-lg md:text-xl font-semibold">
                    {predictedStatsLib?.predictRatingChange ?
                      (predictedStatsLib.predictRatingChange >= 0 ? '+' : '') + (predictedStatsLib.predictRatingChange)
                      : "--"}
                  </span>
                </div>
              </div>
            </div>

            {/* Predicted Next Season Stats */}
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-3 sm:p-4 md:p-4 lg:p-3 xl:p-4 flex-1 flex flex-col shrink-0 md:min-h-0 relative overflow-visible">
              {/* Predictions Header */}
              <div className="flex justify-start mb-2 sm:mb-3 md:mb-3 lg:mb-2 xl:mb-3">
                <span className="text-white text-sm sm:text-base md:text-base lg:text-base xl:text-lg font-semibold tracking-wider" style={{letterSpacing: '1px'}}>PREDICTIONS</span>
              </div>
              {/* Two Column Layout */}
              <div className="flex-1 flex flex-col md:flex-row gap-4 sm:gap-5 md:gap-3 lg:gap-4 xl:gap-4 min-h-0">
                {/* Left Column - Radar Chart */}
                <div className="flex-1 flex flex-col items-center justify-center min-h-0">
                  <div className="flex w-full justify-center mb-2 lg:pt-4 md:mb-4 sm:mb-2 pb-3 xs:mb-2 pb-4 ">
                    <span className="text-gray-200 text-sm sm:text-base md:text-base lg:text-base xl:text-lg font-bold tracking-wide text-center">FIFA Attributes</span>
                  </div>
                  <div className="relative w-40 h-40 xs:w-48 xs:h-48 sm:w-52 sm:h-52 md:w-48 md:h-48 lg:w-48 lg:h-48 xl:w-56 xl:h-56 2xl:w-64 2xl:h-64 mt-2 sm:mt-3 md:mt-2 lg:mt-4 xl:mt-6">
                    {/* Background rings with gradient */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-full h-full border border-white/5 rounded-full" />
                    </div>
                    <div className="absolute inset-[16.67%] flex items-center justify-center">
                      <div className="w-full h-full border border-white/8 rounded-full" />
                    </div>
                    <div className="absolute inset-[33.33%] flex items-center justify-center">
                      <div className="w-full h-full border border-white/12 rounded-full" />
                    </div>
                    <div className="absolute inset-[50%] flex items-center justify-center">
                      <div className="w-full h-full border border-white/15 rounded-full" />
                    </div>
                    <div className="absolute inset-[66.67%] flex items-center justify-center">
                      <div className="w-full h-full border border-white/20 rounded-full" />
                    </div>
                    
                    {/* Grid lines */}
                    <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                      {/* Vertical lines */}
                      <line x1="50" y1="0" x2="50" y2="100" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                      <line x1="0" y1="50" x2="100" y2="50" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                      
                      {/* Diagonal lines for hexagon */}
                      <line x1="50" y1="0" x2="93.3" y2="25" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
                      <line x1="93.3" y1="25" x2="93.3" y2="75" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
                      <line x1="93.3" y1="75" x2="50" y2="100" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
                      <line x1="50" y1="100" x2="6.7" y2="75" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
                      <line x1="6.7" y1="75" x2="6.7" y2="25" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
                      <line x1="6.7" y1="25" x2="50" y2="0" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
                    </svg>
                    
                    {/* Hexagon polygon for stats */}
                    {predictedStatsLib && (
                      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                        <defs>
                          <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="rgba(16, 185, 129, 0.3)" />
                            <stop offset="50%" stopColor="rgba(16, 185, 129, 0.2)" />
                            <stop offset="100%" stopColor="rgba(16, 185, 129, 0.1)" />
                          </linearGradient>
                          <filter id="glow">
                            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                            <feMerge> 
                              <feMergeNode in="coloredBlur"/>
                              <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                          </filter>
                        </defs>
                        {/* Calculate hexagon vertices using trigonometry */}
                        {(() => {
                          const centerX = 50;
                          const centerY = 50;
                          const radius = 45; // max radius for stat
                          // Order: Pace, Shooting, Passing, Dribbling, Defending, Physic
                          const stats = [
                            predictedStatsLib.predictPace || 0,
                            predictedStatsLib.predictShooting || 0,
                            predictedStatsLib.predictPassing || 0,
                            predictedStatsLib.predictDribbling || 0,
                            predictedStatsLib.predictDefending || 0,
                            predictedStatsLib.predictPhysic || 0,
                          ];
                          // Each vertex is 60 degrees apart, starting at -90deg (top)
                          const angles = Array.from({length: 6}, (_, i) => -90 + i * 60);
                          // Convert stat to radius (normalized to 0-1, assuming max 99)
                          const normStats = stats.map(s => Math.max(0, Math.min(1, s / 99)));
                          // Get points for polygon
                          const points = angles.map((angle, i) => {
                            const rad = (angle * Math.PI) / 180;
                            const r = normStats[i] * radius;
                            const x = centerX + r * Math.cos(rad);
                            const y = centerY + r * Math.sin(rad);
                            return `${x},${y}`;
                          }).join(' ');
                          // For outline, use same points
                          // For dots, get each vertex
                          return (
                            <>
                              {/* Background fill */}
                              <polygon
                                points={points}
                                fill="url(#radarGradient)"
                                stroke="none"
                              />
                              {/* Main polygon outline */}
                              <polygon
                                points={points}
                                fill="none"
                                stroke="rgba(16, 185, 129, 0.9)"
                                strokeWidth="2"
                                filter="url(#glow)"
                              />
                              {/* Value dots on vertices */}
                              {angles.map((angle, i) => {
                                const rad = (angle * Math.PI) / 180;
                                const r = normStats[i] * radius;
                                const x = centerX + r * Math.cos(rad);
                                const y = centerY + r * Math.sin(rad);
                                return <circle key={i} cx={x} cy={y} r="2" fill="rgba(16, 185, 129, 1)" />;
                              })}
                            </>
                          );
                        })()}
                      </svg>
                    )}
                    
                    {/* Stat Labels with values - responsive positioning */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-6 sm:-translate-y-7 md:-translate-y-6 lg:-translate-y-6 xl:-translate-y-7 text-center">
                      <div className="text-emerald-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">PAC</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{predictedStatsLib?.predictPace ? Math.ceil(predictedStatsLib.predictPace) : "--"}</div>
                    </div>
                    <div className="absolute top-[12%] right-0 translate-x-4 sm:translate-x-5 md:translate-x-5 lg:translate-x-5 xl:translate-x-6 text-center">
                      <div className="text-blue-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">SHO</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{predictedStatsLib?.predictShooting ? Math.ceil(predictedStatsLib.predictShooting) : "--"}</div>
                    </div>
                    <div className="absolute bottom-[12%] right-0 translate-x-4 sm:translate-x-5 md:translate-x-5 lg:translate-x-5 xl:translate-x-6 text-center">
                      <div className="text-yellow-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">PAS</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{predictedStatsLib?.predictPassing ? Math.ceil(predictedStatsLib.predictPassing) : "--"}</div>
                    </div>
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 sm:translate-y-7 md:translate-y-6 lg:translate-y-6 xl:translate-y-7 text-center">
                      <div className="text-purple-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">DRI</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{predictedStatsLib?.predictDribbling ? Math.ceil(predictedStatsLib.predictDribbling) : "--"}</div>
                    </div>
                    <div className="absolute bottom-[12%] left-0 -translate-x-4 sm:-translate-x-5 md:-translate-x-5 lg:-translate-x-5 xl:-translate-x-6 text-center">
                      <div className="text-red-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">DEF</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{predictedStatsLib?.predictDefending ? Math.ceil(predictedStatsLib.predictDefending) : "--"}</div>
                    </div>
                    <div className="absolute top-[12%] left-0 -translate-x-4 sm:-translate-x-5 md:-translate-x-5 lg:-translate-x-5 xl:-translate-x-6 text-center">
                      <div className="text-orange-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">PHY</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{predictedStatsLib?.predictPhysic ? Math.ceil(predictedStatsLib.predictPhysic) : "--"}</div>
                    </div>
                    
                    {/* Center circle with glow */}
                    <div className="absolute inset-[40%] bg-gradient-to-br from-emerald-500/30 to-emerald-600/20 rounded-full border border-emerald-400/50 shadow-lg shadow-emerald-500/20" />
                  </div>
                </div>

                {/* Right Column - Number Stats */}
                <div className="flex-1 flex flex-col justify-center items-center">
                  <div className="flex w-full justify-center mb-2 lg:pb-8 mb-6 md:mb-2 mt-2 md:mt-0 sm:pt-4 mt-4 xs: pt-4 mt-2">
                    <span className="text-gray-200 text-sm sm:text-base md:text-sm lg:text-base xl:text-lg font-bold tracking-wide text-center px-2">Season Performance (League Only)</span>
                  </div>
                  <div className="grid grid-cols-1 gap-1 sm:gap-1.5 md:gap-1.5 lg:gap-1.5 xl:gap-2 mt-1 w-full">
                    {/* Goals & Assists Row */}
                    <div className="grid grid-cols-2 gap-1 sm:gap-1.5 md:gap-1.5 lg:gap-1.5 xl:gap-2">
                      <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 rounded-lg">
                        <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Goals</span>
                        <span className="text-blue-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                          {predictedStatsLib?.predictedGoals ? Math.ceil(predictedStatsLib.predictedGoals) : "--"}
                        </span>
                      </div>
                      <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 rounded-lg">
                        <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Assists</span>
                        <span className="text-yellow-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                          {predictedStatsLib?.predictedAssists ? Math.ceil(predictedStatsLib.predictedAssists) : "--"}
                        </span>
                      </div>
                    </div>

                    {/* Defense & Key Passes Row */}
                    <div className="grid grid-cols-2 gap-1 sm:gap-1.5 md:gap-1.5 lg:gap-1.5 xl:gap-2">
                      <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 pb-0 rounded-lg">
                        <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Defense</span>
                        <span className="text-red-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                          {predictedStatsLib?.predictedInterceptions && predictedStatsLib?.predictedTackles ?
                            Math.ceil(predictedStatsLib.predictedInterceptions + predictedStatsLib.predictedTackles) : "--"}
                        </span>
                      </div>
                      <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 pb-0 rounded-lg">
                        <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Key Passes</span>
                        <span className="text-purple-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                          {predictedStatsLib?.predictedKeyPasses ? Math.ceil(predictedStatsLib.predictedKeyPasses) : "--"}
                        </span>
                      </div>
                    </div>

                    {/* Spacer to move only Market Value down */}
                    <div className="h-2 sm:h-3 md:h-3 lg:h-3 xl:h-4" />

                    {/* Market Value */}
                    <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 pt-0 rounded-lg">
                      <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Market Value</span>
                      <span className="text-emerald-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                        {predictedStatsLib?.predictValue ? `$${(1.18 * (predictedStatsLib.predictValue / 1000000)).toFixed(1)}M` : "--"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-3 text-center text-gray-500 text-xs shrink-0">
        </div>
      </main>
    </div>
  );
}
