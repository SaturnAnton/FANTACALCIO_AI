// Squad.js
import React, { useState, useEffect } from 'react';
import './Squad.css';

const Squad = () => {
  const [squad, setSquad] = useState([]);
  const [playerInput, setPlayerInput] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [playerStats, setPlayerStats] = useState({});
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  // Limiti per ruolo
  const roleLimits = {
    'GK': 3,
    'DEF': 8,
    'MID': 8,
    'FWD': 6
  };

  // Conta giocatori per ruolo
  const countByRole = (role) => {
    return squad.filter(player => player.role === role).length;
  };

  // Verifica se si può aggiungere un giocatore
  const canAddPlayer = (player) => {
    const currentCount = countByRole(player.role);
    const limit = roleLimits[player.role];
    return currentCount < limit;
  };

  // Cerca giocatori tramite API
  const searchPlayers = async (query) => {
    if (!query || query.length < 3) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/players/search?name=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setSearchResults(data.players);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Error searching players:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Aggiungi giocatore alla squadra
  const addPlayer = async (player) => {
    if (!player) return;
    
    if (!canAddPlayer(player)) {
      alert(`Non puoi aggiungere più ${getRoleName(player.role)}! Limite: ${roleLimits[player.role]}`);
      return;
    }

    try {
      // Prima salviamo nel database
      const response = await fetch('http://localhost:8000/api/players/add-to-squad', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: player.name,
          team: player.team,
          role: player.role,
          price: player.price,
          stats: player.stats,
          fantacalcio_data: player.fantacalcio_data
        })
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        // Aggiungi alla squadra locale
        const newPlayer = {
          id: result.player_id || Date.now(),
          ...player
        };
        
        setSquad([...squad, newPlayer]);
        setPlayerInput('');
        setSearchResults([]);
        setSelectedPlayer(null);
        
        // Carica statistiche dettagliate
        loadPlayerStats(newPlayer);
        
        alert(`✅ ${player.name} aggiunto alla squadra!`);
      }
    } catch (error) {
      console.error('Error adding player:', error);
      alert('❌ Errore nell\'aggiungere il giocatore');
    }
  };

  // Aggiungi il primo giocatore dai risultati
  const addFirstPlayer = () => {
    if (searchResults.length > 0) {
      addPlayer(searchResults[0]);
    } else if (selectedPlayer) {
      addPlayer(selectedPlayer);
    }
  };

  // Gestione del tasto Invio
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      if (selectedPlayer) {
        addPlayer(selectedPlayer);
      } else if (searchResults.length > 0) {
        addPlayer(searchResults[0]);
      } else if (playerInput.length >= 3) {
        searchPlayers(playerInput);
      }
    }
  };

  // Seleziona un giocatore dai risultati
  const selectPlayer = (player) => {
    setSelectedPlayer(player);
  };

  // Carica statistiche dettagliate per un giocatore
  const loadPlayerStats = async (player) => {
    try {
      const response = await fetch(`http://localhost:8000/api/players/${player.id}/stats`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setPlayerStats(prev => ({
          ...prev,
          [player.id]: data.stats
        }));
      }
    } catch (error) {
      console.error('Error loading player stats:', error);
    }
  };

  // Rimuovi giocatore
  const removePlayer = async (playerId) => {
    const player = squad.find(p => p.id === playerId);
    
    try {
      await fetch(`http://localhost:8000/api/players/${playerId}/remove-from-squad`, {
        method: 'DELETE'
      });

      setSquad(squad.filter(p => p.id !== playerId));
      
      // Rimuovi statistiche dalla cache
      setPlayerStats(prev => {
        const newStats = { ...prev };
        delete newStats[playerId];
        return newStats;
      });

      alert(`🗑️ ${player.name} rimosso dalla squadra!`);
    } catch (error) {
      console.error('Error removing player:', error);
      alert('❌ Errore nella rimozione del giocatore');
    }
  };

  // Raggruppa giocatori per ruolo
  const squadByRole = {
    'GK': squad.filter(player => player.role === 'GK'),
    'DEF': squad.filter(player => player.role === 'DEF'),
    'MID': squad.filter(player => player.role === 'MID'),
    'FWD': squad.filter(player => player.role === 'FWD')
  };

  // Nomi dei ruoli in italiano
  const getRoleName = (role) => {
    const roleNames = {
      'GK': 'portieri',
      'DEF': 'difensori',
      'MID': 'centrocampisti',
      'FWD': 'attaccanti'
    };
    return roleNames[role] || role;
  };

  // Effetto per la ricerca
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (playerInput.length >= 3) {
        searchPlayers(playerInput);
        setSelectedPlayer(null);
      } else {
        setSearchResults([]);
        setSelectedPlayer(null);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [playerInput]);

  return (
    <div className="squad-container">
      <h1>🏆 La Mia Squadra Fantacalcio</h1>
      
      {/* Riepilogo Ruoli */}
      <div className="squad-summary">
        <div className="role-summary">
          {Object.entries(roleLimits).map(([role, limit]) => {
            const currentCount = countByRole(role);
            const roleNames = {
              'GK': '🥅 Portieri',
              'DEF': '🛡️ Difensori',
              'MID': '⚽ Centrocampisti',
              'FWD': '🎯 Attaccanti'
            };

            return (
              <div key={role} className="role-stats">
                <h4>{roleNames[role]}</h4>
                <div className="role-progress">
                  <span className="role-count">{currentCount}/{limit}</span>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${(currentCount / limit) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="role-status">
                  {currentCount === limit ? (
                    <span className="status-full">Completo</span>
                  ) : (
                    <span className="status-available">{limit - currentCount} posti liberi</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Ricerca e Inserimento Giocatori */}
      <div className="player-search-section">
        <h2>🔍 Aggiungi Giocatore</h2>
        
        <div className="search-instructions">
          <div className="instruction-item">
            <span className="instruction-icon">⌨️</span>
            <span>Scrivi il nome e premi <strong>INVIO</strong> per aggiungere il primo risultato</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon">👆</span>
            <span>Oppure clicca su un giocatore per selezionarlo</span>
          </div>
        </div>

        <div className="search-container">
          <div className="input-with-button">
            <input
              type="text"
              placeholder="Es: Lautaro Martinez..."
              value={playerInput}
              onChange={(e) => setPlayerInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="search-input"
            />
            <button 
              onClick={addFirstPlayer}
              disabled={searchResults.length === 0 && !selectedPlayer}
              className="enter-button"
              title="Premi Invio o clicca qui per aggiungere il primo giocatore"
            >
              ⏎ INVIO
            </button>
          </div>
          {loading && <div className="loading-spinner">🔍 Cercando...</div>}
        </div>

        {/* Giocatore Selezionato */}
        {selectedPlayer && (
          <div className="selected-player">
            <h4>🎯 Giocatore Selezionato:</h4>
            <div className="selected-player-card">
              <div className="player-main-info">
                <div className="player-header-selected">
                  <h5>{selectedPlayer.name}</h5>
                  <span className="player-team-role">{selectedPlayer.team} • {selectedPlayer.role}</span>
                </div>
                <div className="player-price-tag">€{selectedPlayer.price}M</div>
              </div>
              
              <div className="player-stats-preview">
                {selectedPlayer.fantacalcio_data?.basic?.fantamedia && (
                  <div className="stat-item-preview">
                    <span className="stat-label-preview">Fantamedia</span>
                    <span className="stat-value-preview">
                      {selectedPlayer.fantacalcio_data.basic.fantamedia}
                    </span>
                  </div>
                )}
                {selectedPlayer.fantacalcio_data?.basic?.media_voto && (
                  <div className="stat-item-preview">
                    <span className="stat-label-preview">Media Voto</span>
                    <span className="stat-value-preview">
                      {selectedPlayer.fantacalcio_data.basic.media_voto}
                    </span>
                  </div>
                )}
                {selectedPlayer.fantacalcio_data?.basic?.gol_fatti && (
                  <div className="stat-item-preview">
                    <span className="stat-label-preview">Gol</span>
                    <span className="stat-value-preview">
                      {selectedPlayer.fantacalcio_data.basic.gol_fatti}
                    </span>
                  </div>
                )}
                {selectedPlayer.fantacalcio_data?.basic?.assist && (
                  <div className="stat-item-preview">
                    <span className="stat-label-preview">Assist</span>
                    <span className="stat-value-preview">
                      {selectedPlayer.fantacalcio_data.basic.assist}
                    </span>
                  </div>
                )}
              </div>

              <div className="confirmation-actions">
                <button 
                  onClick={() => addPlayer(selectedPlayer)}
                  className="confirm-add-button"
                >
                  ✅ Conferma Aggiunta
                </button>
                <button 
                  onClick={() => setSelectedPlayer(null)}
                  className="cancel-button"
                >
                  ❌ Annulla
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Risultati Ricerca */}
        {searchResults.length > 0 && !selectedPlayer && (
          <div className="search-results">
            <h4>📋 Risultati trovati ({searchResults.length}):</h4>
            <div className="results-grid">
              {searchResults.map(player => (
                <div 
                  key={player.id} 
                  className={`player-card ${!canAddPlayer(player) ? 'disabled' : ''}`}
                  onClick={() => canAddPlayer(player) && selectPlayer(player)}
                >
                  <div className="player-info">
                    <h5>{player.name}</h5>
                    <p className="player-team">{player.team} • {player.role}</p>
                    <p className="player-price">€{player.price}M</p>
                  </div>
                  
                  <div className="player-stats-preview">
                    {player.fantacalcio_data?.basic?.fantamedia && (
                      <span className="stat-badge">
                        FM: {player.fantacalcio_data.basic.fantamedia}
                      </span>
                    )}
                    {player.fantacalcio_data?.basic?.media_voto && (
                      <span className="stat-badge">
                        MV: {player.fantacalcio_data.basic.media_voto}
                      </span>
                    )}
                    {player.fantacalcio_data?.basic?.gol_fatti && (
                      <span className="stat-badge">
                        Gol: {player.fantacalcio_data.basic.gol_fatti}
                      </span>
                    )}
                  </div>

                  <div className="player-actions">
                    {canAddPlayer(player) ? (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          selectPlayer(player);
                        }}
                        className="select-button"
                      >
                        👆 Seleziona
                      </button>
                    ) : (
                      <span className="limit-warning">
                        ❌ Limite {getRoleName(player.role)} raggiunto
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="quick-actions">
          <div className="action-item">
            <strong>⚡ Azione Rapida:</strong> Scrivi il nome → Premi <kbd>INVIO</kbd>
          </div>
        </div>
      </div>

      {/* Rosa Completa per Ruolo */}
      <div className="squad-roster">
        <h2>👥 Rosa Completa ({squad.length}/25 giocatori)</h2>
        
        {Object.entries(squadByRole).map(([role, players]) => {
          const roleNames = {
            'GK': '🥅 Portieri',
            'DEF': '🛡️ Difensori', 
            'MID': '⚽ Centrocampisti',
            'FWD': '🎯 Attaccanti'
          };

          return (
            <div key={role} className="role-section">
              <h3 className="role-title">
                {roleNames[role]} ({players.length}/{roleLimits[role]})
              </h3>
              
              {players.length === 0 ? (
                <p className="no-players">Nessun giocatore</p>
              ) : (
                <div className="players-grid">
                  {players.map(player => (
                    <div key={player.id} className="squad-player-card">
                      <div className="player-header">
                        <h4>{player.name}</h4>
                        <button 
                          onClick={() => removePlayer(player.id)}
                          className="remove-button"
                          title="Rimuovi giocatore"
                        >
                          ❌
                        </button>
                      </div>
                      
                      <div className="player-details">
                        <p className="team-role">{player.team} • {player.role}</p>
                        <p className="price">€{player.price}M</p>
                      </div>

                      {/* Statistiche Dettagliate */}
                      {playerStats[player.id] && (
                        <div className="player-stats">
                          <div className="stats-grid">
                            {playerStats[player.id].fantacalcio_data?.basic?.fantamedia && (
                              <div className="stat-item">
                                <span className="stat-label">Fantamedia</span>
                                <span className="stat-value">
                                  {playerStats[player.id].fantacalcio_data.basic.fantamedia}
                                </span>
                              </div>
                            )}
                            {playerStats[player.id].fantacalcio_data?.basic?.media_voto && (
                              <div className="stat-item">
                                <span className="stat-label">Media Voto</span>
                                <span className="stat-value">
                                  {playerStats[player.id].fantacalcio_data.basic.media_voto}
                                </span>
                              </div>
                            )}
                            {playerStats[player.id].fantacalcio_data?.basic?.gol_fatti && (
                              <div className="stat-item">
                                <span className="stat-label">Gol</span>
                                <span className="stat-value">
                                  {playerStats[player.id].fantacalcio_data.basic.gol_fatti}
                                </span>
                              </div>
                            )}
                            {playerStats[player.id].fantacalcio_data?.basic?.assist && (
                              <div className="stat-item">
                                <span className="stat-label">Assist</span>
                                <span className="stat-value">
                                  {playerStats[player.id].fantacalcio_data.basic.assist}
                                </span>
                              </div>
                            )}
                          </div>
                          
                          {/* Statistiche FBref se disponibili */}
                          {playerStats[player.id].fbref_data && (
                            <div className="advanced-stats">
                              <h5>Statistiche Avanzate</h5>
                              <div className="advanced-stats-grid">
                                {playerStats[player.id].fbref_data.shooting?.goals && (
                                  <span className="advanced-stat">Gol: {playerStats[player.id].fbref_data.shooting.goals}</span>
                                )}
                                {playerStats[player.id].fbref_data.passing?.assists && (
                                  <span className="advanced-stat">Assist: {playerStats[player.id].fbref_data.passing.assists}</span>
                                )}
                                {playerStats[player.id].fbref_data.defense?.tackles && (
                                  <span className="advanced-stat">Tackle: {playerStats[player.id].fbref_data.defense.tackles}</span>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Squad;