import React, { useState, useEffect } from 'react';
import './Squad.css';

const Squad = () => {
  const [squad, setSquad] = useState([]);
  const [playerInput, setPlayerInput] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  const roleLimits = { GK: 3, DEF: 8, MID: 8, FWD: 6 };
  const countByRole = role => squad.filter(p => p.role === role).length;
  const canAddPlayer = player => countByRole(player.role) < roleLimits[player.role];

  const addPlayer = (player) => {
    if (!player || !canAddPlayer(player)) return;
    const newPlayer = { id: Date.now(), ...player };
    setSquad([...squad, newPlayer]);
    setPlayerInput('');
    setSearchResults([]);
    setSelectedPlayer(null);
  };

  const handleKeyPress = async (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (searchResults.length > 0) {
        addPlayer(searchResults[0]);
      } else if (selectedPlayer) {
        addPlayer(selectedPlayer);
      }
    }
  };

  useEffect(() => {
    const delay = setTimeout(async () => {
      if (playerInput.length >= 2) {
        try {
          const response = await fetch(`http://localhost:8000/api/players/search?name=${encodeURIComponent(playerInput)}`);
          const data = await response.json();
          setSearchResults(data.status === 'success' ? data.players : []);
          setSelectedPlayer(null);
        } catch (err) {
          console.error(err);
          setSearchResults([]);
        }
      } else {
        setSearchResults([]);
      }
    }, 300);
    return () => clearTimeout(delay);
  }, [playerInput]);

  const squadByRole = {
    GK: squad.filter(p => p.role === 'GK'),
    DEF: squad.filter(p => p.role === 'DEF'),
    MID: squad.filter(p => p.role === 'MID'),
    FWD: squad.filter(p => p.role === 'FWD')
  };

  const getRoleName = role => ({ GK: 'portieri', DEF: 'difensori', MID: 'centrocampisti', FWD: 'attaccanti' }[role] || role);

  return (
    <div className="squad-container">
      <h1>🏆 La Mia Squadra Fantacalcio</h1>

      {/* Ricerca giocatori */}
      <input
        type="text"
        placeholder="Es: Lautaro Martinez..."
        value={playerInput}
        onChange={e => setPlayerInput(e.target.value)}
        onKeyPress={handleKeyPress}
      />

      {searchResults.length > 0 && (
        <div className="search-results">
          {searchResults.map(player => (
            <div
              key={player.id}
              className={`player-card ${!canAddPlayer(player) ? 'disabled' : ''}`}
              onClick={() => canAddPlayer(player) && setSelectedPlayer(player)}
            >
              <h5>{player.name}</h5>
              <p>{player.team} • {player.role}</p>
              <p>€{player.price || 0}M</p>
            </div>
          ))}
        </div>
      )}

      {selectedPlayer && (
        <div className="selected-player">
          <h4>🎯 Giocatore selezionato</h4>
          <p>{selectedPlayer.name} • {selectedPlayer.team} • {selectedPlayer.role}</p>
        </div>
      )}

      {/* Rosa completa */}
      {Object.entries(squadByRole).map(([role, players]) => (
        <div key={role} className="role-section">
          <h3>{getRoleName(role)} ({players.length}/{roleLimits[role]})</h3>
          {players.map(player => (
            <div key={player.id} className="squad-player-card">
              <div className="player-header">
                <h4>{player.name}</h4>
              </div>
              <p>{player.team} • {player.role}</p>
              <p>€{player.price || 0}M</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default Squad;
