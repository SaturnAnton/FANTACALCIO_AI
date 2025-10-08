import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { predictionsAPI } from '../services/api';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Predictions = () => {
  const { user } = useContext(AuthContext);
  const [predictions, setPredictions] = useState([]);
  const [matchday, setMatchday] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterRole, setFilterRole] = useState('');
  const [filterTeam, setFilterTeam] = useState('');
  const [sortBy, setSortBy] = useState('prediction');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        
        if (!user) {
          setError('User not authenticated');
          setLoading(false);
          return;
        }
        
        // Fetch predictions from the API
        const response = await predictionsAPI.getPredictions(matchday, { 
          user_id: user.id,
          role: filterRole || undefined,
          team: filterTeam || undefined
        });
        
        // If API is not available, use mock data
        let predictionsData;
        if (!response || !response.data) {
          // Mock predictions data
          predictionsData = [
            { id: 1, player_id: 1, player_name: 'Lautaro Martinez', team: 'Inter', role: 'FWD', predicted_score: 8.2, confidence: 0.85, opponent: 'Genoa (H)' },
            { id: 2, player_id: 2, player_name: 'Rafael Leão', team: 'Milan', role: 'FWD', predicted_score: 7.8, confidence: 0.75, opponent: 'Torino (A)' },
            { id: 3, player_id: 3, player_name: 'Hakan Çalhanoğlu', team: 'Inter', role: 'MID', predicted_score: 7.5, confidence: 0.80, opponent: 'Genoa (H)' },
            { id: 4, player_id: 4, player_name: 'Khvicha Kvaratskhelia', team: 'Napoli', role: 'FWD', predicted_score: 7.9, confidence: 0.82, opponent: 'Verona (H)' },
            { id: 5, player_id: 5, player_name: 'Alessandro Bastoni', team: 'Inter', role: 'DEF', predicted_score: 6.8, confidence: 0.70, opponent: 'Genoa (H)' },
            { id: 6, player_id: 6, player_name: 'Mike Maignan', team: 'Milan', role: 'GK', predicted_score: 6.5, confidence: 0.65, opponent: 'Torino (A)' },
            { id: 7, player_id: 7, player_name: 'Gleison Bremer', team: 'Juventus', role: 'DEF', predicted_score: 6.7, confidence: 0.68, opponent: 'Como (H)' },
            { id: 8, player_id: 8, player_name: 'Giovanni Di Lorenzo', team: 'Napoli', role: 'DEF', predicted_score: 6.6, confidence: 0.67, opponent: 'Verona (H)' },
            { id: 9, player_id: 9, player_name: 'Theo Hernández', team: 'Milan', role: 'DEF', predicted_score: 7.2, confidence: 0.78, opponent: 'Torino (A)' },
            { id: 10, player_id: 10, player_name: 'Nicolò Barella', team: 'Inter', role: 'MID', predicted_score: 7.3, confidence: 0.76, opponent: 'Genoa (H)' }
          ];
        } else {
          predictionsData = response.data;
        }
        
        setPredictions(predictionsData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching predictions:', err);
        setError('Failed to load predictions. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchPredictions();
  }, [user, matchday, filterRole, filterTeam]);

  // Sort predictions
  const sortedPredictions = [...predictions].sort((a, b) => {
    let valueA, valueB;
    
    if (sortBy === 'prediction') {
      valueA = a.predicted_score;
      valueB = b.predicted_score;
    } else if (sortBy === 'confidence') {
      valueA = a.confidence;
      valueB = b.confidence;
    } else if (sortBy === 'name') {
      valueA = a.player_name;
      valueB = b.player_name;
    } else if (sortBy === 'team') {
      valueA = a.team;
      valueB = b.team;
    }
    
    if (sortOrder === 'asc') {
      return typeof valueA === 'string' 
        ? valueA.localeCompare(valueB) 
        : valueA - valueB;
    } else {
      return typeof valueA === 'string' 
        ? valueB.localeCompare(valueA) 
        : valueB - valueA;
    }
  });

  // Get unique teams for filter
  const teams = [...new Set(predictions.map(p => p.team))];

  // Prepare chart data
  const chartData = {
    labels: sortedPredictions.slice(0, 10).map(p => p.player_name),
    datasets: [
      {
        label: 'Predicted Score',
        data: sortedPredictions.slice(0, 10).map(p => p.predicted_score),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: 'Confidence',
        data: sortedPredictions.slice(0, 10).map(p => p.confidence * 10), // Scale to match score
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Top 10 Player Predictions',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
      },
    },
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Player Predictions</h1>
        <div className="flex items-center space-x-2">
          <label htmlFor="matchday" className="font-medium">Matchday:</label>
          <select
            id="matchday"
            value={matchday}
            onChange={(e) => setMatchday(Number(e.target.value))}
            className="border rounded p-2"
          >
            {[...Array(38)].map((_, i) => (
              <option key={i + 1} value={i + 1}>
                {i + 1}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {/* Filters and Sorting */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label htmlFor="filterRole" className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Role
                </label>
                <select
                  id="filterRole"
                  value={filterRole}
                  onChange={(e) => setFilterRole(e.target.value)}
                  className="w-full border rounded p-2"
                >
                  <option value="">All Roles</option>
                  <option value="GK">Goalkeeper</option>
                  <option value="DEF">Defender</option>
                  <option value="MID">Midfielder</option>
                  <option value="FWD">Forward</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="filterTeam" className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Team
                </label>
                <select
                  id="filterTeam"
                  value={filterTeam}
                  onChange={(e) => setFilterTeam(e.target.value)}
                  className="w-full border rounded p-2"
                >
                  <option value="">All Teams</option>
                  {teams.map(team => (
                    <option key={team} value={team}>
                      {team}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <select
                  id="sortBy"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full border rounded p-2"
                >
                  <option value="prediction">Prediction</option>
                  <option value="confidence">Confidence</option>
                  <option value="name">Player Name</option>
                  <option value="team">Team</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="sortOrder" className="block text-sm font-medium text-gray-700 mb-1">
                  Sort Order
                </label>
                <select
                  id="sortOrder"
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                  className="w-full border rounded p-2"
                >
                  <option value="desc">Highest First</option>
                  <option value="asc">Lowest First</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Chart */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <Bar data={chartData} options={chartOptions} />
          </div>
          
          {/* Predictions Table */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Player
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Team
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Opponent
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prediction
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedPredictions.map((prediction) => (
                  <tr key={prediction.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{prediction.player_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-gray-900">{prediction.team}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold text-white ${
                        prediction.role === 'GK' ? 'bg-yellow-500' :
                        prediction.role === 'DEF' ? 'bg-blue-500' :
                        prediction.role === 'MID' ? 'bg-green-500' : 'bg-red-500'
                      }`}>
                        {prediction.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-gray-900">{prediction.opponent}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-gray-900 font-bold">{prediction.predicted_score.toFixed(1)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="bg-blue-600 h-2.5 rounded-full" 
                          style={{ width: `${prediction.confidence * 100}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {(prediction.confidence * 100).toFixed(0)}%
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default Predictions;