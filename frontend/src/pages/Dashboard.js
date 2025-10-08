import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = 'http://localhost:8000';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [formation, setFormation] = useState(null);
  const [tradeSuggestions, setTradeSuggestions] = useState([]);
  const [currentMatchday, setCurrentMatchday] = useState(1);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // For demo purposes, we'll use matchday 1
        // In a real app, you'd get the current matchday from the API
        const matchday = currentMatchday;
        
        // Fetch predictions for user's squad
        const predictionsRes = await axios.get(`${API_URL}/api/predict/${matchday}?user_id=${user.id}`);
        setPredictions(predictionsRes.data);
        
        // Fetch recommended formation
        const formationRes = await axios.get(`${API_URL}/api/formation?user_id=${user.id}&matchday=${matchday}`);
        setFormation(formationRes.data);
        
        // Fetch trade suggestions
        const tradeRes = await axios.get(`${API_URL}/api/trade-suggestions?user_id=${user.id}&matchday=${matchday}&limit=3`);
        setTradeSuggestions(tradeRes.data.trade_suggestions);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
        setLoading(false);
        
        // For demo purposes, set some mock data
        setMockData();
      }
    };
    
    if (user) {
      fetchDashboardData();
    }
  }, [user, currentMatchday]);
  
  // Mock data for development/demo purposes
  const setMockData = () => {
    // Mock predictions
    setPredictions([
      { player_id: 1, player_name: 'Lautaro Martinez', team: 'Inter', role: 'FWD', predicted_score: 7.8, confidence: 0.85 },
      { player_id: 2, player_name: 'Rafael Leão', team: 'Milan', role: 'FWD', predicted_score: 7.5, confidence: 0.82 },
      { player_id: 3, player_name: 'Hakan Çalhanoğlu', team: 'Inter', role: 'MID', predicted_score: 7.3, confidence: 0.79 },
      { player_id: 4, player_name: 'Khvicha Kvaratskhelia', team: 'Napoli', role: 'FWD', predicted_score: 7.2, confidence: 0.78 },
      { player_id: 5, player_name: 'Alessandro Bastoni', team: 'Inter', role: 'DEF', predicted_score: 6.9, confidence: 0.75 }
    ]);
    
    // Mock formation
    setFormation({
      formation: '4-3-3',
      players: [
        { player_id: 10, player_name: 'Mike Maignan', team: 'Milan', role: 'GK', predicted_score: 6.8, confidence: 0.74 },
        { player_id: 4, player_name: 'Alessandro Bastoni', team: 'Inter', role: 'DEF', predicted_score: 6.9, confidence: 0.75 },
        { player_id: 11, player_name: 'Gleison Bremer', team: 'Juventus', role: 'DEF', predicted_score: 6.7, confidence: 0.73 },
        { player_id: 12, player_name: 'Giovanni Di Lorenzo', team: 'Napoli', role: 'DEF', predicted_score: 6.6, confidence: 0.72 },
        { player_id: 13, player_name: 'Theo Hernández', team: 'Milan', role: 'DEF', predicted_score: 6.8, confidence: 0.74 },
        { player_id: 3, player_name: 'Hakan Çalhanoğlu', team: 'Inter', role: 'MID', predicted_score: 7.3, confidence: 0.79 },
        { player_id: 14, player_name: 'Nicolò Barella', team: 'Inter', role: 'MID', predicted_score: 7.0, confidence: 0.76 },
        { player_id: 15, player_name: 'Adrien Rabiot', team: 'Juventus', role: 'MID', predicted_score: 6.7, confidence: 0.73 },
        { player_id: 1, player_name: 'Lautaro Martinez', team: 'Inter', role: 'FWD', predicted_score: 7.8, confidence: 0.85 },
        { player_id: 2, player_name: 'Rafael Leão', team: 'Milan', role: 'FWD', predicted_score: 7.5, confidence: 0.82 },
        { player_id: 4, player_name: 'Khvicha Kvaratskhelia', team: 'Napoli', role: 'FWD', predicted_score: 7.2, confidence: 0.78 }
      ],
      expected_total_score: 76.3
    });
    
    // Mock trade suggestions
    setTradeSuggestions([
      {
        underperforming_player: {
          id: 20, name: 'Matteo Darmian', team: 'Inter', role: 'DEF', predicted_score: 6.1, confidence: 0.65
        },
        alternatives: [
          { id: 21, name: 'Federico Dimarco', team: 'Inter', role: 'DEF', predicted_score: 6.8, confidence: 0.74 },
          { id: 22, name: 'Juan Cuadrado', team: 'Inter', role: 'DEF', predicted_score: 6.5, confidence: 0.71 }
        ]
      },
      {
        underperforming_player: {
          id: 23, name: 'Alexis Saelemaekers', team: 'Milan', role: 'MID', predicted_score: 6.0, confidence: 0.64
        },
        alternatives: [
          { id: 24, name: 'Tijjani Reijnders', team: 'Milan', role: 'MID', predicted_score: 6.7, confidence: 0.73 },
          { id: 25, name: 'Ruben Loftus-Cheek', team: 'Milan', role: 'MID', predicted_score: 6.5, confidence: 0.71 }
        ]
      }
    ]);
  };
  
  // Prepare chart data for top players
  const topPlayersChartData = {
    labels: predictions.slice(0, 5).map(p => p.player_name),
    datasets: [
      {
        label: 'Predicted Score',
        data: predictions.slice(0, 5).map(p => p.predicted_score),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        borderColor: 'rgb(53, 162, 235)',
        borderWidth: 1
      }
    ]
  };
  
  // Prepare chart data for role distribution
  const roleDistribution = predictions.reduce((acc, player) => {
    acc[player.role] = (acc[player.role] || 0) + 1;
    return acc;
  }, {});
  
  const roleDistributionChartData = {
    labels: Object.keys(roleDistribution),
    datasets: [
      {
        label: 'Players by Role',
        data: Object.values(roleDistribution),
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
      }
    ]
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
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <div className="flex space-x-2">
          <button 
            onClick={() => setCurrentMatchday(Math.max(1, currentMatchday - 1))}
            className="px-3 py-1 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Previous
          </button>
          <span className="px-3 py-1 bg-blue-500 text-white rounded-md">
            Matchday {currentMatchday}
          </span>
          <button 
            onClick={() => setCurrentMatchday(currentMatchday + 1)}
            className="px-3 py-1 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Next
          </button>
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Squad Overview</h2>
          <div className="text-3xl font-bold text-blue-600">{predictions.length}</div>
          <p className="text-gray-500">Players in your squad</p>
          <div className="mt-4">
            <Link to="/squad" className="text-blue-500 hover:underline">Manage Squad →</Link>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Recommended Formation</h2>
          <div className="text-3xl font-bold text-green-600">{formation?.formation || 'N/A'}</div>
          <p className="text-gray-500">Expected Score: {formation?.expected_total_score?.toFixed(1) || 'N/A'}</p>
          <div className="mt-4">
            <Link to="/lineup" className="text-blue-500 hover:underline">View Lineup →</Link>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Trade Opportunities</h2>
          <div className="text-3xl font-bold text-purple-600">{tradeSuggestions.length}</div>
          <p className="text-gray-500">Suggested trades available</p>
          <div className="mt-4">
            <Link to="/trades" className="text-blue-500 hover:underline">View Trades →</Link>
          </div>
        </div>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Top Players</h2>
          {predictions.length > 0 ? (
            <Bar 
              data={topPlayersChartData} 
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Predicted Performance'
                  }
                }
              }}
            />
          ) : (
            <p className="text-gray-500">No player data available</p>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Squad Composition</h2>
          {predictions.length > 0 ? (
            <Bar 
              data={roleDistributionChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Players by Role'
                  }
                }
              }}
            />
          ) : (
            <p className="text-gray-500">No player data available</p>
          )}
        </div>
      </div>
      
      {/* Top Predictions */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Top Predicted Performers</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Player</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Predicted Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {predictions.slice(0, 5).map((player) => (
                <tr key={player.player_id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{player.player_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-gray-500">{player.team}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${player.role === 'GK' ? 'bg-yellow-100 text-yellow-800' : 
                        player.role === 'DEF' ? 'bg-blue-100 text-blue-800' : 
                        player.role === 'MID' ? 'bg-green-100 text-green-800' : 
                        'bg-red-100 text-red-800'}`}>
                      {player.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-gray-900 font-medium">{player.predicted_score.toFixed(1)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="bg-blue-600 h-2.5 rounded-full" 
                          style={{ width: `${player.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="ml-2 text-gray-500">{(player.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4">
          <Link to="/predictions" className="text-blue-500 hover:underline">View All Predictions →</Link>
        </div>
      </div>
      
      {/* Trade Suggestions */}
      {tradeSuggestions.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Recommended Trades</h2>
          <div className="space-y-4">
            {tradeSuggestions.map((suggestion, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between">
                  <div className="mb-4 md:mb-0">
                    <h3 className="font-medium text-gray-900">Consider replacing:</h3>
                    <div className="flex items-center mt-2">
                      <div className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                        {suggestion.underperforming_player.name} ({suggestion.underperforming_player.team})
                      </div>
                      <span className="mx-2 text-gray-500">•</span>
                      <span className="text-gray-500">{suggestion.underperforming_player.role}</span>
                      <span className="mx-2 text-gray-500">•</span>
                      <span className="text-gray-500">Score: {suggestion.underperforming_player.predicted_score.toFixed(1)}</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">With one of:</h3>
                    <div className="space-y-2 mt-2">
                      {suggestion.alternatives.map((alt, altIndex) => (
                        <div key={altIndex} className="flex items-center">
                          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                            {alt.name} ({alt.team})
                          </div>
                          <span className="mx-2 text-gray-500">•</span>
                          <span className="text-gray-500">{alt.role}</span>
                          <span className="mx-2 text-gray-500">•</span>
                          <span className="text-gray-500">Score: {alt.predicted_score.toFixed(1)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Link to="/trades" className="text-blue-500 hover:underline">View All Trade Suggestions →</Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;