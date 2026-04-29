import React, { useState, useEffect, useMemo } from 'react';
import { Trophy, Activity, Calendar, Globe2, ChevronRight, PlayCircle, Database, Filter, XCircle } from 'lucide-react';

export default function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const [matches, setMatches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // --- FILTER STATES ---
  const [selectedSport, setSelectedSport] = useState('All');
  const [selectedCountry, setSelectedCountry] = useState('All');
  const [selectedLeague, setSelectedLeague] = useState('All');

  // --- THE LIVE DATA ENGINE ---
  useEffect(() => {
    if (!showDashboard) return;

    const fetchLiveMatches = async () => {
      setIsLoading(true);
      try {
        const response = await fetch("https://v3.football.api-sports.io/fixtures?live=all", {
          method: "GET",
          headers: {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": "aa8230dc24f1659bee125bd45d9681a0" // Your active API key
          }
        });
        
        const data = await response.json();

        if (!data.response || data.response.length === 0) {
           setMatches([]);
           return;
        }

        const realMatches = data.response.map((match) => ({
          id: match.fixture.id,
          sport: 'Football', // Hardcoded until you add the Cricket API!
          country: match.league.country,
          league: match.league.name,
          team1: match.teams.home.name,
          team2: match.teams.away.name,
          status: 'Live', 
          score: `${match.goals.home ?? 0} - ${match.goals.away ?? 0}`
        }));
        
        setMatches(realMatches);
        
      } catch (error) {
        console.error("Failed to fetch live sports data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLiveMatches();
    const interval = setInterval(fetchLiveMatches, 60000);
    return () => clearInterval(interval);
    
  }, [showDashboard]);

  // --- DYNAMIC FILTER GENERATOR ---
  // This automatically extracts unique countries and leagues from the live data
  const uniqueSports = ['All', ...new Set(matches.map(m => m.sport))];
  const uniqueCountries = ['All', ...new Set(matches.map(m => m.country))].sort();
  const uniqueLeagues = ['All', ...new Set(matches.map(m => m.league))].sort();

  // --- THE FILTERING ENGINE ---
  const displayedMatches = matches.filter(match => {
    const sportMatch = selectedSport === 'All' || match.sport === selectedSport;
    const countryMatch = selectedCountry === 'All' || match.country === selectedCountry;
    const leagueMatch = selectedLeague === 'All' || match.league === selectedLeague;
    return sportMatch && countryMatch && leagueMatch;
  });

  // Function to reset all dropdowns
  const resetFilters = () => {
    setSelectedSport('All');
    setSelectedCountry('All');
    setSelectedLeague('All');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      
      {/* NAVIGATION BAR */}
      <nav className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Trophy className="text-emerald-400 w-6 h-6" />
            <span className="text-xl font-bold tracking-wider">UNIVERSAL SPORTS</span>
          </div>
          <div className="hidden md:flex space-x-6 text-sm font-medium text-gray-300">
            <button className="hover:text-white transition">Home</button>
            <button className="hover:text-white transition">Leagues</button>
            <button className="hover:text-white transition">Teams</button>
          </div>
        </div>
      </nav>

      {!showDashboard ? (
        
        /* HOME PAGE */
        <main className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            The World of Sports,<br />Unified.
          </h1>
          <p className="text-lg text-gray-400 mb-10 max-w-2xl">
            Track every fixture, live score, and final result across multiple countries and leagues in real-time. 
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <button 
              onClick={() => setShowDashboard(true)}
              className="group relative px-8 py-4 bg-blue-600 hover:bg-blue-500 transition-all rounded-full font-bold text-lg flex items-center shadow-[0_0_40px_rgba(37,99,235,0.5)] hover:-translate-y-1"
            >
              <Globe2 className="mr-3 w-6 h-6" />
              Explore Live Matches
              <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <a 
              href="http://localhost:8501" 
              target="_blank" 
              rel="noopener noreferrer"
              className="group px-8 py-4 bg-gray-800 border border-gray-700 hover:border-emerald-500 transition-all rounded-full font-bold text-lg flex items-center text-gray-300 hover:text-emerald-400 hover:-translate-y-1"
            >
              <Database className="mr-3 w-5 h-5 group-hover:text-emerald-400 transition-colors" />
              AI App Compiler
            </a>
          </div>
        </main>

      ) : (

        /* DASHBOARD */
        <main className="max-w-7xl mx-auto p-4 py-8 animate-in fade-in zoom-in duration-500">
          
          <div className="flex flex-col md:flex-row justify-between items-end mb-6">
            <div>
              <h2 className="text-3xl font-bold mb-2">Global Action Hub</h2>
              <p className="text-gray-400">Live API data fetching every 60 seconds.</p>
            </div>
            <div className="flex items-center text-red-500 font-bold bg-red-500/10 px-4 py-2 rounded-lg mt-4 md:mt-0 border border-red-500/20">
                <PlayCircle className="w-5 h-5 mr-2 animate-pulse" /> LIVE NOW
            </div>
          </div>

          {/* --- THE NEW FILTER BAR --- */}
          {!isLoading && matches.length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between shadow-lg">
              <div className="flex items-center text-gray-400 font-medium">
                <Filter className="w-5 h-5 mr-2" /> Filter By:
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto flex-1 md:ml-6">
                {/* Sport Dropdown */}
                <select 
                  className="bg-gray-900 border border-gray-600 text-white rounded-lg px-4 py-2 outline-none focus:border-blue-500 w-full sm:w-auto"
                  value={selectedSport}
                  onChange={(e) => setSelectedSport(e.target.value)}
                >
                  <option disabled value="">Sport</option>
                  {uniqueSports.map(sport => <option key={sport} value={sport}>{sport}</option>)}
                </select>

                {/* Country Dropdown */}
                <select 
                  className="bg-gray-900 border border-gray-600 text-white rounded-lg px-4 py-2 outline-none focus:border-blue-500 w-full sm:w-auto"
                  value={selectedCountry}
                  onChange={(e) => setSelectedCountry(e.target.value)}
                >
                  <option disabled value="">Country</option>
                  {uniqueCountries.map(country => <option key={country} value={country}>{country}</option>)}
                </select>

                {/* League Dropdown */}
                <select 
                  className="bg-gray-900 border border-gray-600 text-white rounded-lg px-4 py-2 outline-none focus:border-blue-500 w-full sm:w-auto md:max-w-xs"
                  value={selectedLeague}
                  onChange={(e) => setSelectedLeague(e.target.value)}
                >
                  <option disabled value="">League</option>
                  {uniqueLeagues.map(league => <option key={league} value={league}>{league}</option>)}
                </select>
              </div>

              {/* Reset Button */}
              {(selectedSport !== 'All' || selectedCountry !== 'All' || selectedLeague !== 'All') && (
                <button 
                  onClick={resetFilters}
                  className="flex items-center text-sm text-gray-400 hover:text-red-400 transition-colors w-full md:w-auto justify-center md:justify-start"
                >
                  <XCircle className="w-4 h-4 mr-1" /> Clear
                </button>
              )}
            </div>
          )}

          {/* LOADING SPINNER */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Activity className="w-12 h-12 text-blue-500 animate-spin mb-4" />
              <p className="text-gray-400 animate-pulse">Connecting to API-Sports Global Servers...</p>
            </div>
          ) : (
            /* MATCH CARDS */
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {displayedMatches.length > 0 ? (
                displayedMatches.map((match) => (
                  <div key={match.id} className="bg-gray-800 border border-gray-700 rounded-xl p-5 hover:border-blue-500 transition-colors group">
                    <div className="flex justify-between items-center mb-4 border-b border-gray-700 pb-3">
                      <span className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center">
                        <Globe2 className="w-3 h-3 mr-1" /> {match.country}
                      </span>
                      <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
                        {match.sport}
                      </span>
                    </div>
                    
                    <div className="text-center mb-4">
                      <div className="text-xs text-emerald-400 font-semibold mb-3 uppercase tracking-widest">{match.league}</div>
                      <div className="flex justify-between items-center text-lg font-bold">
                        <span className="truncate w-2/5" title={match.team1}>{match.team1}</span>
                        <span className="text-gray-500 text-sm">vs</span>
                        <span className="truncate w-2/5" title={match.team2}>{match.team2}</span>
                      </div>
                    </div>

                    <div className="bg-gray-900 rounded-lg p-3 text-center border border-gray-700 group-hover:border-blue-500/50 transition-colors">
                      <span className="font-mono text-2xl font-bold text-white">
                        {match.score}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full py-12 text-center text-gray-500 border border-dashed border-gray-700 rounded-xl">
                  <Filter className="w-10 h-10 mx-auto text-gray-600 mb-3" />
                  No live matches match your current filters.<br/>Try clearing them or check back later!
                </div>
              )}
            </div>
          )}
          
          <div className="mt-12 text-center border-t border-gray-800 pt-6">
             <button 
                onClick={() => setShowDashboard(false)} 
                className="text-gray-400 hover:text-white transition-colors underline"
             >
                 ← Return to Universal Sports Home
             </button>
          </div>
        </main>
      )}
    </div>
  );
}