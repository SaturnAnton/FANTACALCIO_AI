import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { predictionsAPI } from '../services/api';

const Trades = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [budget, setBudget] = useState(100);
  const [maxTransfers, setMaxTransfers] = useState(3);
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        if (isAuthenticated && user) {
          const response = await predictionsAPI.getTransferRecommendations(user.id, {
            budget,
            max_transfers: maxTransfers
          });
          setRecommendations(response.data.recommendations || []);
        } else {
          // Mock data for development
          setRecommendations([
            {
              sell: { id: 1, name: 'Immobile', team: 'Lazio', role: 'FWD', price: 25, predicted_points: 6.2 },
              buy: { id: 2, name: 'Osimhen', team: 'Napoli', role: 'FWD', price: 30, predicted_points: 8.5 },
              improvement: 2.3
            },
            {
              sell: { id: 3, name: 'Barella', team: 'Inter', role: 'MID', price: 18, predicted_points: 5.8 },
              buy: { id: 4, name: 'Zaccagni', team: 'Lazio', role: 'MID', price: 20, predicted_points: 7.1 },
              improvement: 1.3
            },
            {
              sell: { id: 5, name: 'Romagnoli', team: 'Lazio', role: 'DEF', price: 12, predicted_points: 5.1 },
              buy: { id: 6, name: 'Bremer', team: 'Juventus', role: 'DEF', price: 15, predicted_points: 6.8 },
              improvement: 1.7
            }
          ]);
        }
      } catch (error) {
        console.error('Error fetching trade recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [isAuthenticated, user, budget, maxTransfers]);

  const handleBudgetChange = (e) => {
    setBudget(parseInt(e.target.value));
  };

  const handleMaxTransfersChange = (e) => {
    setMaxTransfers(parseInt(e.target.value));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Trade Recommendations</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Optimization Settings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Available Budget: {budget} credits
            </label>
            <input
              type="range"
              min="0"
              max="500"
              value={budget}
              onChange={handleBudgetChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Transfers: {maxTransfers}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={maxTransfers}
              onChange={handleMaxTransfersChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {recommendations.map((rec, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover-card-effect">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Recommendation #{index + 1}</h3>
                  <span className="text-green-600 font-bold">+{rec.improvement.toFixed(1)} pts</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-red-50 p-4 rounded-lg">
                    <h4 className="text-red-600 font-medium mb-2">Sell</h4>
                    <div className="flex items-center">
                      <div className="flex-1">
                        <p className="font-semibold">{rec.sell.name}</p>
                        <p className="text-sm text-gray-600">{rec.sell.team}</p>
                        <div className="mt-1">
                          <span className={`inline-block px-2 py-1 text-xs rounded role-${rec.sell.role}`}>
                            {rec.sell.role}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">{rec.sell.price} cr</p>
                        <p className="text-sm text-gray-600">{rec.sell.predicted_points.toFixed(1)} pts</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="text-green-600 font-medium mb-2">Buy</h4>
                    <div className="flex items-center">
                      <div className="flex-1">
                        <p className="font-semibold">{rec.buy.name}</p>
                        <p className="text-sm text-gray-600">{rec.buy.team}</p>
                        <div className="mt-1">
                          <span className={`inline-block px-2 py-1 text-xs rounded role-${rec.buy.role}`}>
                            {rec.buy.role}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">{rec.buy.price} cr</p>
                        <p className="text-sm text-gray-600">{rec.buy.predicted_points.toFixed(1)} pts</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {recommendations.length === 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <p className="text-gray-600">No trade recommendations available with current settings.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Trades;