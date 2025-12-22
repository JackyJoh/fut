"use client";

import { useState, useEffect, useRef } from "react";
import GlareHover from './GlareHover';

interface PlayerSuggestion {
  idPlayer: string;
  strPlayer: string;
  strTeam: string;
  strNationality: string;
  fullData?: any; // Store the full player object from backend
}

export default function Home() {
  const [playerSearch, setPlayerSearch] = useState("");
  const [selectedSeason, setSelectedSeason] = useState("2024-25");
  const [playerImage, setPlayerImage] = useState("");
  const [isLoadingImage, setIsLoadingImage] = useState(false);
  const [nationality, setNationality] = useState<string | null>(null);
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

  const fetchPlayerImage = async (playerName: string, clubName?: string) => {
    if (!playerName.trim()) {
      setPlayerImage("");
      return;
    }

    setIsLoadingImage(true);
    try {
      const response = await fetch(
        `https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p=${encodeURIComponent(playerName)}`
      );
      const data = await response.json();
      
      if (data.player && data.player.length > 0) {
        const player = data.player[0];
        const image = player.strThumb || player.strCutout;
        setPlayerImage(image || "");
        setNationality(player.strNationality || null);
        
        
        // Fetch team badge using team name
        if (player.strTeam) {
          try {
            const teamResponse = await fetch(
              `https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=${encodeURIComponent(player.strTeam)}`
            );
            const teamData = await teamResponse.json();
            if (teamData.teams && teamData.teams.length > 0) {
              setTeamBadge(teamData.teams[0].strBadge || null);
            } else {
              setTeamBadge(null);
            }
          } catch (error) {
            console.error("Error fetching team badge:", error);
            setTeamBadge(null);
          }
        } else {
          setTeamBadge(null);
        }
      } else {
        setPlayerImage("");
        setTeamBadge(null);
      }
    } catch (error) {
      console.error("Error fetching player image:", error);
      setPlayerImage("");
      setNationality(null);
      setTeamBadge(null);
    } finally {
      setIsLoadingImage(false);
    }
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

  const handleSelectPlayer = (player: PlayerSuggestion) => {
    setPlayerSearch(player.strPlayer);
    setShowSuggestions(false);
    setSuggestions([]);
    
    // Set player data from backend
    if (player.fullData) {
      const data = player.fullData;
      setSelectedPlayerId(data.id?.toString() || data.playerID?.toString() || null);
      setAge(data.age_fifa || null);
      setCurrentOverall(data.overall || null);
      setPosition(data.player_positions || null);
      setClub(data.club_name || null);
      setNationality(data.nationality_name || null);
      
      // Fetch image and team badge from TheSportsDB using database club name
      fetchPlayerImage(player.strPlayer, data.club_name);
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
    <div className="relative h-screen bg-[#0a0f0a] overflow-hidden flex flex-col font-[family-name:var(--font-michroma)]">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Gradient orbs */}
        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-emerald-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-30%] left-[-10%] w-[500px] h-[500px] bg-emerald-600/8 rounded-full blur-[100px]" />
        <div className="absolute top-[40%] left-[30%] w-[300px] h-[300px] bg-emerald-400/5 rounded-full blur-[80px]" />
        
        {/* Grid lines */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px'
          }}
        />
        
        {/* Diagonal lines */}
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `repeating-linear-gradient(
              45deg,
              transparent,
              transparent 100px,
              rgba(255,255,255,0.05) 100px,
              rgba(255,255,255,0.05) 101px
            )`
          }}
        />

        {/* Star/sparkle decorations */}
        <div className="absolute bottom-20 right-20 text-emerald-500/20 text-6xl">✦</div>
        <div className="absolute top-40 left-[20%] text-emerald-500/10 text-4xl">✦</div>
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-3 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center">
            <img src= "futpredict-removebg2.png" className="w-full h-full object-cover" alt="Fut Predict Logo" />
          </div>
          <span className="text-white font-semibold text-lg">Fut Predict</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 px-6 py-4 w-[90vw] mx-auto flex-1 flex flex-col min-h-0">
        {/* Title Section */}
        <div className="mb-4 shrink-0">
          <h1 className="text-2xl font-bold text-white mb-1">FIFA Rating Predictor</h1>
          <p className="text-gray-400 text-sm">Uncover Football&apos;s Next Superstars</p>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1 min-h-0">
          {/* Left Column */}
          <div className="flex flex-col gap-3 min-h-0">
            {/* Search Row */}
            <div className="flex gap-3 shrink-0">
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
                  className="w-full bg-[#1a1f1a] border border-white/10 rounded-lg py-2 pl-3 pr-3 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-emerald-500/50"
                />
                
                {/* Suggestions Dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-[#1a1f1a] border border-white/10 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
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
                  <div className="absolute top-full left-0 right-0 mt-1 bg-[#1a1f1a] border border-white/10 rounded-lg shadow-lg z-50 px-3 py-2">
                    <div className="text-gray-400 text-sm">Searching...</div>
                  </div>
                )}
              </div>
              <select
                value={selectedSeason}
                onChange={(e) => setSelectedSeason(e.target.value)}
                className="bg-[#1a1f1a] border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-500/50 min-w-[120px]"
              >
                <option value="2025-26">Season 25-26</option>
                <option value="2026-27">Season 26-27</option>
                <option value="2027-28">Season 27-28</option>
              </select>
            </div>

            {/* Current Stats Card */}
            <div className="bg-[#141914] border border-white/10 rounded-xl p-4 flex-1">
              <h3 className="text-gray-400 text-xs mb-3">Current Stats</h3>
              
              <div className="flex gap-4">
                {/* Player Image and Badges */}
                <div className="flex flex-col gap-2">
                  {/* Player Image */}
                  <div className="w-54 h-62   rounded-lg flex items-center justify-center border-4 border-emerald-500/30 overflow-hidden">
                    {isLoadingImage ? (
                      <span className="text-white text-xs">Loading...</span>
                    ) : playerImage ? (
                      <img 
                        src={playerImage} 
                        alt={playerSearch}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-6xl">👤</span>
                    )}
                  </div>
                  
                  {/* Club Badge and Nationality */}
                  <div className="grid grid-cols-2 gap-2 w-full">
                    {/* Club Badge */}
                    <div className="w-24 h-24 rounded-lg p-2 flex items-center justify-center aspect-square overflow-hidden">
                      {teamBadge ? (
                        <img src={teamBadge} alt="Club Badge" className="w-full h-full object-contain" />
                      ) : (
                        <span className="text-xs font-semibold text-gray-400">CLUB</span>
                      )}
                    </div>
                    {/* Nationality */}
                    <div className="w-24 h-24 rounded-lg p-2 flex items-center justify-center aspect-square overflow-hidden">
                      {nationality ? (
                        <img 
                          src={`https://flagcdn.com/w80/${nationality.toLowerCase().slice(0, 2)}.png`}
                          alt={nationality}
                          className="w-full h-full object-contain rounded"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.nextElementSibling?.classList.remove('hidden');
                          }}
                        />
                      ) : null}
                      <span className={`text-xs font-semibold text-gray-400 ${nationality ? 'hidden' : ''}`}>NAT</span>
                    </div>
                  </div>
                </div>
                
                {/* Player Info */}
                <div className="flex-1 space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-white font-bold">OVR: {currentOverall !== null ? currentOverall : "--"}</span>
                    <span className="text-gray-400 text-xs">2024-25 🏴</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Age</span>
                    <span className="text-white">{age !== null ? age : "--"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Position</span>
                    <span className="text-white">{position || "--"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Club</span>
                    <span className="text-white">{club || "--"}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Predicted Performance */}
            <div className="flex flex-col shrink-0">
              <h3 className="text-white font-semibold text-sm mb-2 shrink-0">Predicted Performance</h3>
              <div className="grid grid-cols-4 gap-3">
                {[
                  { label: "Goals", value: predictedStatsLib?.predictedGoals ? Math.ceil(predictedStatsLib.predictedGoals) : "--" },
                  { label: "Assists", value: predictedStatsLib?.predictedAssists ? Math.ceil(predictedStatsLib.predictedAssists) : "--" },
                  { label: "Key Passes", value: predictedStatsLib?.predictedKeyPasses ? Math.ceil(predictedStatsLib.predictedKeyPasses) : "--" },
                  { label: "Def. Contributions", value: (predictedStatsLib?.predictedInterceptions && predictedStatsLib?.predictedTackles) ? Math.ceil(predictedStatsLib.predictedInterceptions + predictedStatsLib.predictedTackles) : "--" },
                ].map((stat, idx) => (
                  <GlareHover
                    key={idx}
                    width="100%"
                    height="100%"
                    background="#1a1f1a"
                    borderRadius="0.5rem"
                    borderColor="rgba(255,255,255,0.1)"
                    glareColor="#10b981"
                    glareOpacity={0.3}
                    glareAngle={-30}
                    glareSize={300}
                    transitionDuration={800}
                    playOnce={false}
                    className="aspect-square"
                  >
                    <div className="p-3 flex flex-col items-center justify-center text-center w-full h-full">
                      <span className="text-gray-400 text-xs mb-2">{stat.label}</span>
                      <span className="text-white font-bold text-2xl">{stat.value}</span>
                    </div>
                  </GlareHover>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="flex flex-col gap-3 min-h-0">
            {/* Predicted Rating Card */}
            <div className="bg-[#141914] border border-white/10 rounded-xl p-4 shrink-0">
              <h3 className="text-gray-400 text-xs mb-2">Predicted Rating:</h3>
              <div className="flex items-baseline gap-3">
                <span className="text-5xl font-bold text-white">{predictedStatsLib?.predictOverall.toFixed(0) ?? "--"}</span>
                <div className="flex items-center gap-1 text-emerald-400">
                  <span className="text-2xl">↑</span>
                  <span className="text-xl font-semibold">{"+" + (predictedStatsLib?.predictRatingChange ? Math.ceil(predictedStatsLib.predictRatingChange) : "--")}</span>
                </div>
              </div>
            </div>

            {/* Predicted Next Season Stats */}
            <div className="bg-[#141914] border border-white/10 rounded-xl p-4 flex-1 flex flex-col min-h-0">
              <h3 className="text-white font-semibold text-sm mb-3 shrink-0">Predicted Next Season Stats</h3>
              
              {/* Radar Chart */}
              <div className="relative flex-1 flex items-center justify-center min-h-0">
                <div className="relative w-64 h-64">
                  {/* Rings */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-full h-full border border-white/10 rounded-full" />
                  </div>
                  <div className="absolute inset-[20%] flex items-center justify-center">
                    <div className="w-full h-full border border-white/10 rounded-full" />
                  </div>
                  <div className="absolute inset-[40%] flex items-center justify-center">
                    <div className="w-full h-full border border-white/10 rounded-full" />
                  </div>
                  
                  {/* Hexagon polygon for stats */}
                  {predictedStatsLib && (
                    <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                      <polygon
                        points={`
                          50,${50 - (predictedStatsLib.predictPace || 0) * 0.4}
                          ${50 + (predictedStatsLib.predictShooting || 0) * 0.35},${50 - (predictedStatsLib.predictShooting || 0) * 0.2}
                          ${50 + (predictedStatsLib.predictPassing || 0) * 0.35},${50 + (predictedStatsLib.predictPassing || 0) * 0.2}
                          50,${50 + (predictedStatsLib.predictDribbling || 0) * 0.4}
                          ${50 - (predictedStatsLib.predictPhysic || 0) * 0.35},${50 + (predictedStatsLib.predictPhysic || 0) * 0.2}
                          ${50 - (predictedStatsLib.predictPhysic || 0) * 0.35},${50 - (predictedStatsLib.predictPhysic || 0) * 0.2}
                        `.trim()}
                        fill="rgba(16, 185, 129, 0.2)"
                        stroke="rgba(16, 185, 129, 0.8)"
                        strokeWidth="2"
                      />
                    </svg>
                  )}
                  
                  {/* Stat Labels with values */}
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-6 text-center">
                    <div className="text-emerald-400 text-sm font-semibold">PAC</div>
                    <div className="text-white text-xs">{predictedStatsLib?.predictPace ? Math.ceil(predictedStatsLib.predictPace) : "--"}</div>
                  </div>
                  <div className="absolute top-[15%] right-0 translate-x-8 text-center">
                    <div className="text-blue-400 text-sm font-semibold">SHO</div>
                    <div className="text-white text-xs">{predictedStatsLib?.predictShooting ? Math.ceil(predictedStatsLib.predictShooting) : "--"}</div>
                  </div>
                  <div className="absolute bottom-[15%] right-0 translate-x-8 text-center">
                    <div className="text-yellow-400 text-sm font-semibold">PAS</div>
                    <div className="text-white text-xs">{predictedStatsLib?.predictPassing ? Math.ceil(predictedStatsLib.predictPassing) : "--"}</div>
                  </div>
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 text-center">
                    <div className="text-purple-400 text-sm font-semibold">DRI</div>
                    <div className="text-white text-xs">{predictedStatsLib?.predictDribbling ? Math.ceil(predictedStatsLib.predictDribbling) : "--"}</div>
                  </div>
                  <div className="absolute bottom-[15%] left-0 -translate-x-8 text-center">
                    <div className="text-red-400 text-sm font-semibold">DEF</div>
                    <div className="text-white text-xs">{predictedStatsLib?.predictDefending ? Math.ceil(predictedStatsLib.predictDefending) : "--"}</div>
                  </div>
                  <div className="absolute top-[15%] left-0 -translate-x-8 text-center">
                    <div className="text-orange-400 text-sm font-semibold">PHY</div>
                    <div className="text-white text-xs">{predictedStatsLib?.predictPhysic ? Math.ceil(predictedStatsLib.predictPhysic) : "--"}</div>
                  </div>
                  
                  {/* Center placeholder */}
                  <div className="absolute inset-[35%] bg-emerald-500/20 rounded-full border-2 border-emerald-500/50" />
                </div>
              </div>

              {/* Predict Button */}
              <button onClick={handlePredict} className="w-full bg-emerald-500 hover:bg-emerald-600 text-black font-semibold py-3 rounded-xl transition-colors shrink-0 mt-3">
                Predict Rating
              </button>
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
