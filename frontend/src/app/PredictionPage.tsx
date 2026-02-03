"use client";

import { useState, useRef } from "react";
import CountUp from './CountUp';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// List of seasons for tabs
const SEASONS = [
  "25/26", "26/27", "27/28", "28/29", "29/30", "30/31", "31/32", "32/33", "33/34"
];

interface PlayerSuggestion {
  idPlayer: string;
  strPlayer: string;
  strTeam: string;
  strNationality: string;
  fullData?: any;
}

interface PredictionPageProps {
  onBackToHome?: () => void;
}

/**
 * Convert nationality name to ISO 3166-1 alpha-2 country code
 * Used for fetching flag images from flagcdn
 * @param nationality - The full nationality name
 * @returns ISO country code (lowercase) or null if not found
 */
function getNationalityCode(nationality: string): string | null {
  const nationalityToCodeMapping: Record<string, string> = {
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
  };

  const normalizedNationality = nationality.trim().toLowerCase();
  return nationalityToCodeMapping[normalizedNationality] || null;
}

export default function PredictionPage({ onBackToHome }: PredictionPageProps) {
  const [playerSearch, setPlayerSearch] = useState("");
  const [displayedPlayerName, setDisplayedPlayerName] = useState("");
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
  const [predictedStatsLib, setPredictedStatsLib] = useState<any[] | null>(null);
  const [nationalityText, setNationalityText] = useState<string | null>(null);
  const [selectedPredictionSeason, setSelectedPredictionSeason] = useState("25/26");
  
  // Get current season's data based on selected tab (0-8 index for years 1-9)
  const getCurrentSeasonData = () => {
    if (!predictedStatsLib || !Array.isArray(predictedStatsLib)) return null;
    const seasonIndex = SEASONS.indexOf(selectedPredictionSeason);
    return predictedStatsLib[seasonIndex] || null;
  };
  
  const currentSeasonData = getCurrentSeasonData();
  const [currentValue, setCurrentValue] = useState<number | null>(null);

  /**
   * Generate market value progression data from predictions
   */
  const getMarketValueData = () => {
    if (!predictedStatsLib || !Array.isArray(predictedStatsLib)) return [];
    
    return predictedStatsLib.map((prediction, index) => ({
      season: SEASONS[index],
      value: prediction.predictValue || 0
    }));
  };

  /**
   * Generate rating/potential progression data from predictions
   */
  const getRatingData = () => {
    if (!predictedStatsLib || !Array.isArray(predictedStatsLib)) return [];
    
    return predictedStatsLib.map((prediction, index) => ({
      season: SEASONS[index],
      rating: prediction.predictOverall || 0,
      potential: prediction.predictedPotential || 0
    }));
  };

  /**
   * Generate goals & assists progression data from predictions
   */
  const getGoalsAssistsData = () => {
    if (!predictedStatsLib || !Array.isArray(predictedStatsLib)) return [];
    
    return predictedStatsLib.map((prediction, index) => ({
      season: SEASONS[index],
      goals: Math.round(prediction.predictedGoals || 0),
      assists: Math.round(prediction.predictedAssists || 0)
    }));
  };

  const marketValueData = getMarketValueData();
  const ratingData = getRatingData();
  const goalsAssistsData = getGoalsAssistsData();

  /**
   * Fetch player suggestions from backend based on search query
   * @param query - The search string entered by user
   */
  const fetchSuggestions = async (query: string): Promise<void> => {
    // Validate query length
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    setIsLoadingSuggestions(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${apiUrl}/searchPlayers?name=${encodeURIComponent(query)}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data && data.length > 0) {
        // Map backend data to PlayerSuggestion format (limit to 5 results)
        const players: PlayerSuggestion[] = data.slice(0, 5).map((playerData: any) => ({
          idPlayer: playerData.playerID?.toString() || playerData.id?.toString(),
          strPlayer: playerData.shortName || playerData.name,
          strTeam: playerData.club_name || "",
          strNationality: playerData.nationality_name || "",
          fullData: playerData
        }));

        setSuggestions(players);
        setShowSuggestions(true);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (error) {
      console.error("Error fetching player suggestions:", error);
      setSuggestions([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  /**
   * Fetch player image and team badge from TheSportsDB API
   * @param playerName - Name of the player to search for
   * @param clubName - Optional club name (not currently used)
   * @param nationality - Optional nationality to display
   */
  const fetchPlayerImage = async (
    playerName: string,
    clubName?: string,
    nationality?: string
  ): Promise<void> => {
    if (!playerName.trim()) {
      setPlayerImage("");
      return;
    }

    setIsLoadingImage(true);
    
    // Temporary variables to batch state updates
    let tempPlayerImage = "";
    let tempTeamBadge: string | null = null;
    
    try {
      // Fetch player data from TheSportsDB
      const playerResponse = await fetch(
        `https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p=${encodeURIComponent(playerName)}`
      );
      
      if (!playerResponse.ok) {
        throw new Error(`HTTP error! status: ${playerResponse.status}`);
      }
      
      const playerData = await playerResponse.json();
      
      if (playerData.player && playerData.player.length > 0) {
        // Filter for soccer players only
        const soccerPlayers = playerData.player.filter(
          (p: any) => p.strSport?.toLowerCase() === 'soccer'
        );
        
        if (soccerPlayers.length > 0) {
          const player = soccerPlayers[0];
          tempPlayerImage = player.strThumb || player.strCutout || "";
          
          // Fetch team badge if team name is available
          if (player.strTeam) {
            try {
              const teamResponse = await fetch(
                `https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=${encodeURIComponent(player.strTeam)}`
              );
              
              if (!teamResponse.ok) {
                throw new Error(`HTTP error! status: ${teamResponse.status}`);
              }
              
              const teamData = await teamResponse.json();
              
              if (teamData.teams && teamData.teams.length > 0) {
                // Filter for soccer teams only
                const soccerTeams = teamData.teams.filter(
                  (t: any) => t.strSport?.toLowerCase() === 'soccer'
                );
                
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
    
    // Batch update all image-related state
    setPlayerImage(tempPlayerImage);
    setTeamBadge(tempTeamBadge);
    
    if (nationality) {
      setNationalityText(nationality);
    }
    
    setIsLoadingImage(false);
  };

  /**
   * Handle search input changes with debouncing
   * @param e - React change event from input field
   */
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const value = e.target.value;
    setPlayerSearch(value);
    
    // Clear existing suggestions immediately
    setSuggestions([]);
    setShowSuggestions(false);
    
    // Clear previous debounce timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    // Debounce search request (300ms delay)
    searchTimeoutRef.current = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);
  };

  /**
   * Handle player selection from suggestions dropdown
   * Fetches player images and predictions
   * @param player - The selected player suggestion
   */
  const handleSelectPlayer = async (player: PlayerSuggestion): Promise<void> => {
    // Clear search input and suggestions
    setPlayerSearch("");
    setDisplayedPlayerName(player.strPlayer);
    setShowSuggestions(false);
    setSuggestions([]);
    
    // Reset all existing player data
    setPlayerImage("");
    setTeamBadge(null);
    setNationalityText(null);
    setPredictedStatsLib(null);
    
    // Load new player data from backend response
    if (player.fullData) {
      const data = player.fullData;
      const playerId = data.id?.toString() || data.playerID?.toString() || null;
      
      // Set basic player information
      setSelectedPlayerId(playerId);
      setAge(data.age_fifa || null);
      setCurrentOverall(data.overall || null);
      setPosition(data.player_positions || null);
      setClub(data.club_name || null);
      setCurrentValue(data.value_eur || null);
      
      // Fetch player images asynchronously (non-blocking)
      fetchPlayerImage(
        player.strPlayer,
        data.club_name,
        data.nationality_name || null
      );
      
      // Fetch player predictions if ID is available
      if (playerId) {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const response = await fetch(
            `${apiUrl}/predictPlayer/${playerId}`
          );
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const predictionData = await response.json();
          setPredictedStatsLib(predictionData.statsLibrary);
        } catch (error) {
          console.error("Error fetching predicted data:", error);
        }
      }
    } else {
      // Fallback: fetch images without full player data
      fetchPlayerImage(player.strPlayer);
    }
  };

  /**
   * Handle Enter key press in search input
   * @param e - React keyboard event
   */
  const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === 'Enter') {
      fetchPlayerImage(playerSearch);
    }
  };

  return (
    <>
      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-3 sm:px-4 md:px-6 py-2 sm:py-3 border-b border-white/25 shrink-0 bg-[#0a0f0a]/90">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg flex items-center justify-center">
            <img src="futpredict-removebg2.png" className="w-full h-full object-cover" alt="Fut Predict Logo" />
          </div>
          <span className="text-white font-semibold text-base sm:text-lg">Fut Predict</span>
        </div>
        {onBackToHome && (
          <button
            onClick={onBackToHome}
            className="text-gray-400 hover:text-white text-sm transition-colors"
          >
            ← Back
          </button>
        )}
      </header>

      {/* Main Content */}
      <main className="relative z-10 px-3 sm:px-4 md:px-6 py-3 sm:py-4 w-full md:w-[95vw] mx-auto flex-1 flex flex-col min-h-0 opacity-100 overflow-x-hidden">
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
              <div className="flex flex-row gap-1 sm:gap-2 items-stretch h-fit mt-1.5 sm:mt-2">
                {/* Left: Player Image - 3/5 width */}
                <div className="w-3/5 md:w-3/5 aspect-[3/5] max-h-[160px] sm:max-h-[180px] md:max-h-[320px] lg:max-h-[360px] xl:max-h-[400px] rounded-md sm:rounded-lg flex items-center justify-center border-2 sm:border-3 border-emerald-500/30 overflow-hidden transition-all duration-300 bg-black/10">
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
                <div className="w-2/5 flex flex-col items-center justify-around max-h-[160px] sm:max-h-[180px] md:max-h-[320px] lg:max-h-[360px] xl:max-h-[400px] min-h-[120px] sm:min-h-[140px] md:min-h-[140px]">
                  {/* Club Badge */}
                  <div className="w-[50px] h-[50px] sm:w-[58px] sm:h-[58px] md:w-[85px] md:h-[85px] lg:w-[106px] lg:h-[106px] rounded flex items-center justify-center overflow-hidden transition-all duration-300">
                    {teamBadge ? (
                      <img src={teamBadge} alt="Club Badge" className="w-full h-full object-contain" />
                    ) : (
                      <span className="text-[9px] sm:text-[10px] font-semibold text-gray-400">CLUB</span>
                    )}
                  </div>
                  {/* Nationality Flag */}
                  <div className="w-[80px] h-[43px] sm:w-[92px] sm:h-[49px] md:w-[113px] md:h-[60px] lg:w-[136px] lg:h-[72px] rounded flex items-center justify-center overflow-hidden transition-all duration-300">
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
                      `h-[32px] sm:h-[36px] lg:h-[37.14px] px-1 sm:px-2 lg:px-0 rounded-md lg:rounded-lg backdrop-blur-md text-[10px] sm:text-xs font-bold transition-all duration-200 flex items-center justify-center lg:flex-1
                      ${selectedPredictionSeason === season
                        ? 'border-2 border-emerald-400 bg-emerald-500/90 shadow-md text-white'
                        : 'border-2 border-emerald-300/60 bg-black/40 hover:bg-emerald-400/30 text-emerald-100 shadow-[0_2px_8px_0_rgba(0,255,180,0.10)]'}
                      `
                    }
                    style={{ minWidth: 0, textShadow: selectedPredictionSeason === season ? '0 1px 4px #000' : '0 1px 2px #000' }}
                  >
                    {season}
                  </button>
                ))}
              </div>
            </div>
            {/* Predicted Rating Card */}
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-3 sm:p-4 flex flex-col shrink-0">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <h3 className="text-gray-400 text-[10px] sm:text-xs mb-1.5 sm:mb-2">Predicted Rating:</h3>
                  <div className="flex items-center justify-center gap-2 sm:gap-3 flex-wrap sm:flex-nowrap">
                    <span className="text-3xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 via-emerald-400 to-blue-500 bg-clip-text text-transparent">
                      {currentSeasonData?.predictOverall ? Number(currentSeasonData.predictOverall.toFixed(0)) : "--"}
                    </span>
                    <div className={`flex items-center gap-1 ${currentSeasonData?.predictRatingChange && currentSeasonData.predictRatingChange < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                      <span className="text-lg sm:text-xl md:text-2xl">{currentSeasonData?.predictRatingChange && currentSeasonData.predictRatingChange < 0 ? '↓' : '↑'}</span>
                      <span className="text-xs sm:text-sm md:text-base font-bold">
                        {currentSeasonData?.predictRatingChange ?
                          (currentSeasonData.predictRatingChange >= 0 ? '+' : '') + (currentSeasonData.predictRatingChange)
                          : "--"}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-center">
                  <h3 className="text-gray-400 text-[10px] sm:text-xs mb-1.5 sm:mb-2">Predicted Value:</h3>
                  <span className="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-green-400 to-green-500 bg-clip-text text-transparent">
                    {currentSeasonData?.predictValue ? (
                      `$${((currentSeasonData.predictValue * 1.18) / 1000000).toFixed(1)}M`
                    ) : (
                      "--"
                    )}
                  </span>
                </div>
              </div>
            </div>

            {/* Predicted Next Season Stats */}
            <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-3 sm:p-4 md:p-4 lg:p-3 xl:p-4 flex-1 flex flex-col shrink-0 md:min-h-0 relative overflow-visible">
              {/* Header Row for Predictions and Columns */}
              <div className="flex flex-col w-full mb-1 sm:mb-1 md:mb-1 lg:mb-1 xl:mb-1">
                <h3 className="text-gray-400 text-[10px] sm:text-xs mb-1.5 sm:mb-2" style={{letterSpacing: '1px'}}>PREDICTIONS</h3>
                <div className="hidden md:flex flex-row w-full items-center justify-between gap-4 min-h-[56px] sm:min-h-[64px] md:min-h-[72px] lg:min-h-[80px] xl:min-h-[90px]">
                  <div className="flex-1 flex items-center justify-center">
                    <span className="text-gray-200 text-sm sm:text-base md:text-base lg:text-lg xl:text-xl font-bold tracking-wide text-center">FIFA Attributes</span>
                  </div>
                  <div className="flex-1 flex items-center justify-center">
                    <span className="text-gray-200 text-sm sm:text-base md:text-base lg:text-lg xl:text-xl font-bold tracking-wide text-center px-2">Season Performance</span>
                  </div>
                </div>
              </div>
              {/* Two Column Layout */}
              <div className="flex-1 flex flex-col md:flex-row gap-4 sm:gap-5 md:gap-3 lg:gap-4 xl:gap-4 min-h-0">
                {/* Left Column - FIFA Attributes and Radar Map */}
                <div className="flex-1 flex flex-col items-center justify-center min-h-0">
                  {/* FIFA Attributes Header for small screens */}
                  <div className="flex md:hidden items-center justify-center mb-4 py-2">
                    <span className="text-gray-200 text-sm sm:text-base font-bold tracking-wide text-center">FIFA Attributes</span>
                  </div>
                  {/* Radar Map */}
                  <div className="relative w-40 h-40 xs:w-44 xs:h-44 sm:w-48 sm:h-48 md:w-48 md:h-48 lg:w-48 lg:h-48 xl:w-56 xl:h-56 2xl:w-64 2xl:h-64 mt-4 sm:mt-2 md:mt-1 lg:mb-8 xl:mb-10">
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
                    {currentSeasonData && (
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
                        {(() => {
                          const centerX = 50;
                          const centerY = 50;
                          const radius = 45;
                          const stats = [
                            currentSeasonData.predictPace || 0,
                            currentSeasonData.predictShooting || 0,
                            currentSeasonData.predictPassing || 0,
                            currentSeasonData.predictDribbling || 0,
                            currentSeasonData.predictDefending || 0,
                            currentSeasonData.predictPhysic || 0,
                          ];
                          const angles = Array.from({length: 6}, (_, i) => -90 + i * 60);
                          const normStats = stats.map(s => Math.max(0, Math.min(1, s / 99)));
                          const points = angles.map((angle, i) => {
                            const rad = (angle * Math.PI) / 180;
                            const r = normStats[i] * radius;
                            const x = centerX + r * Math.cos(rad);
                            const y = centerY + r * Math.sin(rad);
                            return `${x},${y}`;
                          }).join(' ');
                          return (
                            <>
                              <polygon
                                points={points}
                                fill="url(#radarGradient)"
                                stroke="none"
                              />
                              <polygon
                                points={points}
                                fill="none"
                                stroke="rgba(16, 185, 129, 0.9)"
                                strokeWidth="2"
                                filter="url(#glow)"
                              />
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
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{currentSeasonData?.predictPace ? Math.ceil(currentSeasonData.predictPace) : "--"}</div>
                    </div>
                    <div className="absolute top-[12%] right-0 translate-x-4 sm:translate-x-5 md:translate-x-5 lg:translate-x-5 xl:translate-x-6 text-center">
                      <div className="text-blue-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">SHO</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{currentSeasonData?.predictShooting ? Math.ceil(currentSeasonData.predictShooting) : "--"}</div>
                    </div>
                    <div className="absolute bottom-[12%] right-0 translate-x-4 sm:translate-x-5 md:translate-x-5 lg:translate-x-5 xl:translate-x-6 text-center">
                      <div className="text-yellow-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">PAS</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{currentSeasonData?.predictPassing ? Math.ceil(currentSeasonData.predictPassing) : "--"}</div>
                    </div>
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 sm:translate-y-7 md:translate-y-6 lg:translate-y-6 xl:translate-y-7 text-center">
                      <div className="text-purple-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">DRI</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{currentSeasonData?.predictDribbling ? Math.ceil(currentSeasonData.predictDribbling) : "--"}</div>
                    </div>
                    <div className="absolute bottom-[12%] left-0 -translate-x-4 sm:-translate-x-5 md:-translate-x-5 lg:-translate-x-5 xl:-translate-x-6 text-center">
                      <div className="text-red-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">DEF</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{currentSeasonData?.predictDefending ? Math.ceil(currentSeasonData.predictDefending) : "--"}</div>
                    </div>
                    <div className="absolute top-[12%] left-0 -translate-x-4 sm:-translate-x-5 md:-translate-x-5 lg:-translate-x-5 xl:-translate-x-6 text-center">
                      <div className="text-orange-400 text-[9px] sm:text-[10px] md:text-[10px] lg:text-[10px] xl:text-xs font-bold tracking-wider">PHY</div>
                      <div className="text-white text-xs sm:text-sm md:text-sm lg:text-sm font-semibold">{currentSeasonData?.predictPhysic ? Math.ceil(currentSeasonData.predictPhysic) : "--"}</div>
                    </div>
                    {/* Center circle with glow */}
                    <div className="absolute inset-[40%] bg-gradient-to-br from-emerald-500/30 to-emerald-600/20 rounded-full border border-emerald-400/50 shadow-lg shadow-emerald-500/20" />
                  </div>
                </div>

                {/* Right Column - Season Performance 2x2 Grid */}
                <div className="flex-1 flex flex-col justify-center items-center min-h-0">
                  {/* Season Performance Header for small screens */}
                  <div className="flex md:hidden items-center justify-center mb-2 py-2 mt-6 pt-4">
                    <span className="text-gray-200 text-sm sm:text-base font-bold tracking-wide text-center px-2">Season Performance</span>
                  </div>
                  <div className="grid grid-cols-2 grid-rows-2 gap-1 sm:gap-2 w-full min-h-[100px] sm:min-h-[110px] md:min-h-[120px] lg:min-h-[130px] xl:min-h-[140px]">
                    {/* Goals */}
                    <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 rounded-lg">
                      <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Goals</span>
                      <span className="text-blue-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                        {currentSeasonData?.predictedGoals ? Math.ceil(currentSeasonData.predictedGoals) : "--"}
                      </span>
                    </div>
                    {/* Assists */}
                    <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 rounded-lg">
                      <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Assists</span>
                      <span className="text-yellow-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                        {currentSeasonData?.predictedAssists ? Math.ceil(currentSeasonData.predictedAssists) : "--"}
                      </span>
                    </div>
                    {/* Defensive Contributions */}
                    <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 pb-0 rounded-lg">
                      <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5 text-center">Def Contrib.</span>
                      <span className="text-red-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                        {currentSeasonData?.predictedInterceptions && currentSeasonData?.predictedTackles ?
                          Math.ceil(currentSeasonData.predictedInterceptions + currentSeasonData.predictedTackles) : "--"}
                      </span>
                    </div>
                    {/* Key Passes */}
                    <div className="flex flex-col items-center p-1 sm:p-1.5 md:p-1.5 lg:p-1.5 xl:p-2 pb-0 rounded-lg">
                      <span className="text-gray-400 text-[10px] sm:text-xs md:text-xs lg:text-xs xl:text-sm uppercase tracking-wider mb-0.5">Key Passes</span>
                      <span className="text-purple-400 text-xl sm:text-2xl md:text-2xl lg:text-2xl xl:text-3xl 2xl:text-4xl font-bold">
                        {currentSeasonData?.predictedKeyPasses ? Math.ceil(currentSeasonData.predictedKeyPasses) : "--"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Overall Progression Section */}
        <div className="backdrop-blur-md bg-black/20 border border-white/10 rounded-xl p-3 sm:p-4 mt-4" style={{ minHeight: '500px' }}>
          <h3 className="text-gray-400 text-xs sm:text-sm mb-1.5 sm:mb-2">Overall Progression</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full" style={{ height: '400px', minHeight: window.innerWidth < 768 ? '800px' : '400px' }}>
            <div className="flex flex-col">
              <h4 className="text-white text-xs mb-2">Market Value</h4>
              <div
                className="flex-1 outline-none"
                style={{
                  height: '550px',
                  WebkitTapHighlightColor: 'transparent',
                  ...(window.innerWidth < 768 ? { height: '600px' } : {})
                }}
                tabIndex={-1}
              >
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                  style={{ outline: 'none', userSelect: 'none', pointerEvents: 'auto' }}
                >
                  <LineChart
                    data={marketValueData}
                    style={{ outline: 'none', userSelect: 'none', pointerEvents: 'auto' }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#888888" />
                    <XAxis dataKey="season" stroke="#fff" fontSize={10} interval={0} tick={{ fill: '#fff' }} />
                    <YAxis 
                      stroke="#fff" 
                      fontSize={10} 
                      tick={{ fill: '#fff' }}
                      tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        border: '1px solid rgba(255,255,255,0.05)',
                        borderRadius: '6px',
                        color: 'rgba(255,255,255,0.7)',
                        fontSize: '11px',
                        fontWeight: 400
                      }}
                      formatter={(value: any) => [`$${((value || 0) / 1000000).toFixed(1)}M`, 'Market Value']}
                    />
                    <Line type="monotone" dataKey="value" stroke="#10B981" strokeWidth={2} activeDot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="flex flex-col">
              <h4 className="text-white text-xs mb-2">Rating/Potential</h4>
              <div
                className="flex-1 outline-none"
                style={{
                  height: '550px',
                  WebkitTapHighlightColor: 'transparent',
                  ...(window.innerWidth < 768 ? { height: '600px' } : {})
                } as React.CSSProperties}
                tabIndex={-1}
              >
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                  style={{ outline: 'none', userSelect: 'none', pointerEvents: 'auto' }}
                >
                  <LineChart
                    data={ratingData}
                    style={{ outline: 'none', userSelect: 'none', pointerEvents: 'auto' }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#888888" />
                    <XAxis dataKey="season" stroke="#fff" fontSize={10} interval={0} tick={{ fill: '#fff' }} />
                    <YAxis stroke="#fff" fontSize={10} tick={{ fill: '#fff' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        border: '1px solid rgba(255,255,255,0.05)',
                        borderRadius: '6px',
                        color: 'rgba(255,255,255,0.7)',
                        fontSize: '11px',
                        fontWeight: 400
                      }}
                    />
                    <Line type="monotone" dataKey="rating" stroke="#3B82F6" strokeWidth={2} activeDot={false} />
                    <Line type="monotone" dataKey="potential" stroke="#F59E0B" strokeWidth={2} activeDot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="flex flex-col">
              <h4 className="text-white text-xs mb-2">Goals & Assists</h4>
              <div
                className="flex-1 outline-none"
                style={{
                  height: '550px',
                  WebkitTapHighlightColor: 'transparent',
                  ...(window.innerWidth < 768 ? { height: '600px' } : {})
                }}
                tabIndex={-1}
              >
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                  style={{ outline: 'none', userSelect: 'none', pointerEvents: 'auto' }}
                >
                  <LineChart
                    data={goalsAssistsData}
                    style={{ outline: 'none', userSelect: 'none', pointerEvents: 'auto' }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#888888" />
                    <XAxis dataKey="season" stroke="#fff" fontSize={10} interval={0} tick={{ fill: '#fff' }} />
                    <YAxis stroke="#fff" fontSize={10} tick={{ fill: '#fff' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        border: '1px solid rgba(255,255,255,0.05)',
                        borderRadius: '6px',
                        color: 'rgba(255,255,255,0.7)',
                        fontSize: '11px',
                        fontWeight: 400
                      }}
                    />
                    <Line type="monotone" dataKey="goals" stroke="#EF4444" strokeWidth={2} activeDot={false} />
                    <Line type="monotone" dataKey="assists" stroke="#F59E0B" strokeWidth={2} activeDot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-3 text-center text-gray-500 text-xs shrink-0">
        </div>
      </main>
    </>
  );
}
