import React, { useState } from "react";
import "./Squad.css"; // riutilizziamo lo stesso CSS

const Search = () => {
  const [playerInput, setPlayerInput] = useState("");
  const [playerData, setPlayerData] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [loading, setLoading] = useState(false);

  const normalize = (str) => str.toLowerCase().replace(/\s+/g, " ").trim();

  // 🔍 Ricerca esatta del giocatore
  const cercaGiocatoreEsatto = async () => {
    const nome = normalize(playerInput.trim());
    if (!nome) return;

    setLoading(true);
    setNotFound(false);
    setPlayerData(null);

    try {
      const response = await fetch("http://localhost:8000/api/players/");
      const data = await response.json();

      const trovato = data.players.find((p) => {
        const playerName = normalize(p.name || "");
        const fbrefName = normalize(p.fbref_data?.player || "");
        return playerName === nome || fbrefName === nome;
      });

      if (trovato) setPlayerData(trovato);
      else setNotFound(true);
    } catch (err) {
      console.error("Errore nel caricamento JSON:", err);
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") cercaGiocatoreEsatto();
  };

  return (
    <div className="squad-container">
      <h1>🔍 Search for a Player</h1>

      <div className="search-section">
        <input
          type="text"
          placeholder="Enter player name (e.g., Leao, Lautaro)"
          value={playerInput}
          onChange={(e) => setPlayerInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button onClick={cercaGiocatoreEsatto}>🔍 Search</button>
      </div>

      {loading && <p>🔄 Loading player data...</p>}
      {notFound && <p className="notfound">❌ Player not found</p>}

      {playerData && (
        <div className="players-grid">
          <div className={`player-card ${playerData.role}`}>
            <h3>{playerData.name}</h3>
            <p>
              Ruolo: {playerData.role} | Squadra: {playerData.team}
            </p>

            <ul>
              <li>PG: {playerData.stats.pg}</li>
              <li>MV: {playerData.stats.mv}</li>
              <li>MFV: {playerData.stats.mfv}</li>
              <li>GOL: {playerData.stats.gol}</li>
              <li>ASS: {playerData.stats.ass}</li>
              <li>AMM: {playerData.stats.amm}</li>
              <li>ESP: {playerData.stats.esp}</li>
              <li>xG: {playerData.fbref_data?.xg || 0}</li>
              <li>xA: {playerData.fbref_data?.xg_assist || 0}</li>
              <li>Progressivi: {playerData.fbref_data?.progressive_passes || 0}</li>
              {playerData.role === "GK" && (
                <>
                  <li>Gol subiti: {playerData.stats.gs}</li>
                  <li>Rigori parati: {playerData.stats.rp}</li>
                  <li>Clean Sheet: {playerData.fbref_data?.clean_sheets || 0}</li>
                </>
              )}
            </ul>

            <p>
              <a href={playerData.url} target="_blank" rel="noreferrer">
                🔗 Complete Player Profile
              </a>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;
