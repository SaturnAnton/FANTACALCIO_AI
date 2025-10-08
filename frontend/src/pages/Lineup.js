import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { predictionsAPI, squadAPI } from '../services/api';

const Lineup = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [squad, setSquad] = useState([]);
  const [selectedFormation, setSelectedFormation] = useState('3-4-3');
  const [lineup, setLineup] = useState({
    GK: [],
    DEF: [],
    MID: [],
    FWD: []
  });
  const [benchPlayers, setBenchPlayers] = useState([]);
  const [optimizationLoading, setOptimizationLoading] = useState(false);
  const [matchday, setMatchday] = useState(1);

  // Available formations
  const formations = ['3-4-3', '3-5-2', '4-3-3', '4-4-2', '4-5-1', '5-3-2', '5-4-1'];

  useEffect(() => {
    const fetchSquadData = async () => {
      try {
        setLoading(true);
        
        if (!user) {
          setError('User not authenticated');
          setLoading(false);
          return;
        }
        
        // Fetch user's squad and predictions
        const squadResponse = await squadAPI.getSquad(user.id);
        const predictionsResponse = await predictionsAPI.getPredictions(matchday, { user_id: user.id });
        
        // If API is not available, use mock data
        if (!squadResponse.data || !predictionsResponse.data) {
          // Mock squad data with predictions for the current matchday
          const mockSquad = [
            { id: 1, name: 'Lautaro Martinez', team: 'Inter', role: 'FWD', price: 35, prediction: 8.2, opponent: 'Genoa (H)' },
            { id: 2, name: 'Rafael Leão', team: 'Milan', role: 'FWD', price: 30, prediction: 7.8, opponent: 'Torino (A)' },
            { id: 3, name: 'Hakan Çalhanoğlu', team: 'Inter', role: 'MID', price: 25, prediction: 7.5, opponent: 'Genoa (H)' },
            { id: 4, name: 'Khvicha Kvaratskhelia', team: 'Napoli', role: 'FWD', price: 28, prediction: 7.9, opponent: 'Verona (H)' },
            { id: 5, name: 'Alessandro Bastoni', team: 'Inter', role: 'DEF', price: 18, prediction: 6.8, opponent: 'Genoa (H)' },
            { id: 6, name: 'Mike Maignan', team: 'Milan', role: 'GK', price: 20, prediction: 6.5, opponent: 'Torino (A)' },
            { id: 7, name: 'Gleison Bremer', team: 'Juventus', role: 'DEF', price: 17, prediction: 6.7, opponent: 'Como (H)' },
            { id: 8, name: 'Giovanni Di Lorenzo', team: 'Napoli', role: 'DEF', price: 16, prediction: 6.6, opponent: 'Verona (H)' },
            { id: 9, name: 'Theo Hernández', team: 'Milan', role: 'DEF', price: 22, prediction: 7.2, opponent: 'Torino (A)' },
            { id: 10, name: 'Nicolò Barella', team: 'Inter', role: 'MID', price: 23, prediction: 7.3, opponent: 'Genoa (H)' },
            { id: 11, name: 'Adrien Rabiot', team: 'Juventus', role: 'MID', price: 18, prediction: 6.9, opponent: 'Como (H)' },
            { id: 12, name: 'Matteo Politano', team: 'Napoli', role: 'MID', price: 16, prediction: 6.8, opponent: 'Verona (H)' },
            { id: 13, name: 'Davide Frattesi', team: 'Inter', role: 'MID', price: 17, prediction: 6.7, opponent: 'Genoa (H)' },
            { id: 14, name: 'Mateo Retegui', team: 'Atalanta', role: 'FWD', price: 19, prediction: 7.1, opponent: 'Lecce (A)' },
            { id: 15, name: 'Wojciech Szczęsny', team: 'Juventus', role: 'GK', price: 18, prediction: 6.7, opponent: 'Como (H)' },
            { id: 16, name: 'Federico Dimarco', team: 'Inter', role: 'DEF', price: 19, prediction: 7.0, opponent: 'Genoa (H)' },
            { id: 17, name: 'Riccardo Calafiori', team: 'Bologna', role: 'DEF', price: 15, prediction: 6.5, opponent: 'Udinese (H)' },
            { id: 18, name: 'Teun Koopmeiners', team: 'Atalanta', role: 'MID', price: 22, prediction: 7.4, opponent: 'Lecce (A)' },
            { id: 19, name: 'Paulo Dybala', team: 'Roma', role: 'FWD', price: 27, prediction: 7.7, opponent: 'Empoli (H)' },
            { id: 20, name: 'Dusan Vlahovic', team: 'Juventus', role: 'FWD', price: 29, prediction: 7.6, opponent: 'Como (H)' }
          ];
          
          setSquad(mockSquad);
          // Initialize with a default lineup based on the selected formation
          generateInitialLineup(mockSquad, selectedFormation);
        } else {
          // Process API data
          const squadData = squadResponse.data;
          const predictionsData = predictionsResponse.data;
          
          // Combine squad and predictions data
          const squadWithPredictions = squadData.map(player => {
            const prediction = predictionsData.find(p => p.player_id === player.id);
            return {
              ...player,
              prediction: prediction ? prediction.predicted_score : 6.0,
              confidence: prediction ? prediction.confidence : 0.5
            };
          });
          
          setSquad(squadWithPredictions);
          // Initialize with a default lineup based on the selected formation
          generateInitialLineup(squadWithPredictions, selectedFormation);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching squad data:', err);
        setError('Failed to load squad data. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchSquadData();
  }, [user, matchday]);
  
  // Generate initial lineup based on player predictions
  const generateInitialLineup = (players, formation) => {
    const [defCount, midCount, fwdCount] = formation.split('-').map(Number);
    
    // Sort players by role and prediction
    const sortedByRole = {
      GK: [...players.filter(p => p.role === 'GK')].sort((a, b) => b.prediction - a.prediction),
      DEF: [...players.filter(p => p.role === 'DEF')].sort((a, b) => b.prediction - a.prediction),
      MID: [...players.filter(p => p.role === 'MID')].sort((a, b) => b.prediction - a.prediction),
      FWD: [...players.filter(p => p.role === 'FWD')].sort((a, b) => b.prediction - a.prediction)
    };
    
    // Select top players for each position based on formation
    const newLineup = {
      GK: sortedByRole.GK.slice(0, 1),
      DEF: sortedByRole.DEF.slice(0, defCount),
      MID: sortedByRole.MID.slice(0, midCount),
      FWD: sortedByRole.FWD.slice(0, fwdCount)
    };
    
    // Remaining players go to bench
    const starters = [
      ...newLineup.GK,
      ...newLineup.DEF,
      ...newLineup.MID,
      ...newLineup.FWD
    ];
    
    const bench = players.filter(player => 
      !starters.some(starter => starter.id === player.id)
    );
    
    setLineup(newLineup);
    setBenchPlayers(bench);
  };
  
  // Handle formation change
  const handleFormationChange = (e) => {
    const newFormation = e.target.value;
    setSelectedFormation(newFormation);
    generateInitialLineup(squad, newFormation);
  };
  
  // Handle player swap (between lineup and bench)
  const handlePlayerSwap = (player, isInLineup) => {
    if (isInLineup) {
      // Remove from lineup, add to bench
      const role = player.role;
      const updatedLineup = {
        ...lineup,
        [role]: lineup[role].filter(p => p.id !== player.id)
      };
      
      setBenchPlayers([...benchPlayers, player]);
      setLineup(updatedLineup);
    } else {
      // Check if we can add to lineup (based on formation constraints)
      const role = player.role;
      const [defCount, midCount, fwdCount] = selectedFormation.split('-').map(Number);
      const maxCounts = {
        GK: 1,
        DEF: defCount,
        MID: midCount,
        FWD: fwdCount
      };
      
      if (lineup[role].length < maxCounts[role]) {
        // Add to lineup, remove from bench
        const updatedLineup = {
          ...lineup,
          [role]: [...lineup[role], player]
        };
        
        setBenchPlayers(benchPlayers.filter(p => p.id !== player.id));
        setLineup(updatedLineup);
      } else {
        alert(`Cannot add more ${role === 'GK' ? 'goalkeepers' : 
              role === 'DEF' ? 'defenders' : 
              role === 'MID' ? 'midfielders' : 
              'forwards'} to the current formation (${selectedFormation}).`);
      }
    }
  };
  
  // Optimize lineup based on predictions
  const optimizeLineup = async () => {
    setOptimizationLoading(true);
    
    try {
      if (!user) {
        setError('User not authenticated');
        setOptimizationLoading(false);
        return;
      }
      
      // Call the API to get the optimized lineup
      const response = await predictionsAPI.optimizeFormation(user.id, {
        formation: selectedFormation,
        matchday: matchday
      });
      
      if (response && response.data) {
        // Process API response
        const optimizedData = response.data;
        
        // Update lineup based on API response
        setLineup(optimizedData.lineup || {
          GK: [],
          DEF: [],
          MID: [],
          FWD: []
        });
        setBenchPlayers(optimizedData.bench || []);
      } else {
        // Fallback to client-side optimization
        generateInitialLineup(squad, selectedFormation);
      }
      
      setOptimizationLoading(false);
    } catch (err) {
      console.error('Error optimizing lineup:', err);
      setError('Failed to optimize lineup. Please try again.');
      setOptimizationLoading(false);
      
      // Fallback to client-side optimization
      generateInitialLineup(squad, selectedFormation);
    }
  };
  
  // Calculate average prediction for the current lineup
  const calculateAveragePrediction = () => {
    const allPlayers = [
      ...lineup.GK,
      ...lineup.DEF,
      ...lineup.MID,
      ...lineup.FWD
    ];
    
    if (allPlayers.length === 0) return 0;
    
    const sum = allPlayers.reduce((total, player) => total + player.prediction, 0);
    return (sum / allPlayers.length).toFixed(2);
  };
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Lineup Optimizer</h1>
        <div className="flex space-x-4">
          <div>
            <label htmlFor="matchday" className="block text-sm font-medium text-gray-700">Matchday</label>
            <select
              id="matchday"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={matchday}
              onChange={(e) => setMatchday(parseInt(e.target.value))}
            >
              {[...Array(38)].map((_, i) => (
                <option key={i + 1} value={i + 1}>Matchday {i + 1}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="formation" className="block text-sm font-medium text-gray-700">Formation</label>
            <select
              id="formation"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={selectedFormation}
              onChange={handleFormationChange}
            >
              {formations.map(formation => (
                <option key={formation} value={formation}>{formation}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={optimizeLineup}
              disabled={optimizationLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
            >
              {optimizationLoading ? 'Optimizing...' : 'Optimize Lineup'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Lineup Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Formation</h2>
          <div className="text-2xl font-bold text-blue-600">{selectedFormation}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Average Prediction</h2>
          <div className="text-2xl font-bold text-green-600">{calculateAveragePrediction()}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Starting Players</h2>
          <div className="text-2xl font-bold text-purple-600">
            {lineup.GK.length + lineup.DEF.length + lineup.MID.length + lineup.FWD.length} / 11
          </div>
        </div>
      </div>
      
      {/* Football Field Visualization */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Lineup Visualization</h2>
        <div className="relative w-full h-[500px] bg-green-600 rounded-lg overflow-hidden">
          {/* Field markings */}
          <div className="absolute inset-0 flex flex-col">
            {/* Center circle */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 border-2 border-white rounded-full"></div>
            {/* Center line */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-0.5 h-full bg-white"></div>
            {/* Penalty areas */}
            <div className="absolute top-1/2 left-0 transform -translate-y-1/2 w-24 h-48 border-2 border-white"></div>
            <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-24 h-48 border-2 border-white"></div>
            {/* Goal areas */}
            <div className="absolute top-1/2 left-0 transform -translate-y-1/2 w-8 h-24 border-2 border-white"></div>
            <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-8 h-24 border-2 border-white"></div>
          </div>
          
          {/* Players positioning based on formation */}
          <div className="absolute inset-0">
            {/* Goalkeeper */}
            <div className="absolute top-1/2 left-[5%] transform -translate-y-1/2 flex flex-col items-center">
              {lineup.GK.map(player => (
                <div 
                  key={player.id}
                  onClick={() => handlePlayerSwap(player, true)}
                  className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center mb-2 cursor-pointer hover:bg-yellow-600 transition-colors"
                  title={`${player.name} (${player.prediction})`}
                >
                  <div className="text-center">
                    <div className="text-xs font-bold text-white">{player.name.split(' ').pop()}</div>
                    <div className="text-xs text-white">{player.prediction}</div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Defenders */}
            <div className="absolute top-0 left-[20%] w-[5%] h-full flex flex-col justify-around items-center">
              {lineup.DEF.map((player, index) => {
                const totalPlayers = lineup.DEF.length;
                const position = `${(index + 1) * (100 / (totalPlayers + 1))}%`;
                
                return (
                  <div 
                    key={player.id}
                    onClick={() => handlePlayerSwap(player, true)}
                    className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center cursor-pointer hover:bg-blue-600 transition-colors"
                    style={{ position: 'absolute', top: position }}
                    title={`${player.name} (${player.prediction})`}
                  >
                    <div className="text-center">
                      <div className="text-xs font-bold text-white">{player.name.split(' ').pop()}</div>
                      <div className="text-xs text-white">{player.prediction}</div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Midfielders */}
            <div className="absolute top-0 left-[45%] w-[5%] h-full flex flex-col justify-around items-center">
              {lineup.MID.map((player, index) => {
                const totalPlayers = lineup.MID.length;
                const position = `${(index + 1) * (100 / (totalPlayers + 1))}%`;
                
                return (
                  <div 
                    key={player.id}
                    onClick={() => handlePlayerSwap(player, true)}
                    className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center cursor-pointer hover:bg-green-600 transition-colors"
                    style={{ position: 'absolute', top: position }}
                    title={`${player.name} (${player.prediction})`}
                  >
                    <div className="text-center">
                      <div className="text-xs font-bold text-white">{player.name.split(' ').pop()}</div>
                      <div className="text-xs text-white">{player.prediction}</div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Forwards */}
            <div className="absolute top-0 left-[70%] w-[5%] h-full flex flex-col justify-around items-center">
              {lineup.FWD.map((player, index) => {
                const totalPlayers = lineup.FWD.length;
                const position = `${(index + 1) * (100 / (totalPlayers + 1))}%`;
                
                return (
                  <div 
                    key={player.id}
                    onClick={() => handlePlayerSwap(player, true)}
                    className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center cursor-pointer hover:bg-red-600 transition-colors"
                    style={{ position: 'absolute', top: position }}
                    title={`${player.name} (${player.prediction})`}
                  >
                    <div className="text-center">
                      <div className="text-xs font-bold text-white">{player.name.split(' ').pop()}</div>
                      <div className="text-xs text-white">{player.prediction}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      
      {/* Bench Players */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Bench Players</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {benchPlayers.map(player => (
            <div 
              key={player.id}
              onClick={() => handlePlayerSwap(player, false)}
              className="bg-gray-100 p-3 rounded-lg cursor-pointer hover:bg-gray-200 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full 
                  ${player.role === 'GK' ? 'bg-yellow-500' : 
                    player.role === 'DEF' ? 'bg-blue-500' : 
                    player.role === 'MID' ? 'bg-green-500' : 
                    'bg-red-500'}`}></div>
                <span className="font-medium text-gray-800">{player.name}</span>
              </div>
              <div className="mt-2 flex justify-between text-sm">
                <span className="text-gray-600">{player.team}</span>
                <span className="font-semibold text-blue-600">{player.prediction}</span>
              </div>
              <div className="mt-1 text-xs text-gray-500">
                vs {player.opponent}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Lineup;