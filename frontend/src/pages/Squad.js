import React, { useState, useEffect } from "react";
import "./Squad.css";

const roleLimits = { GK: 3, DEF: 8, MID: 8, FWD: 6 };
const roleNames = { GK: "Portieri", DEF: "Difensori", MID: "Centrocampisti", FWD: "Attaccanti" };

const Squad = ({ currentUser }) => {
  const [playerInput, setPlayerInput] = useState("");
  const [playerData, setPlayerData] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [loading, setLoading] = useState(false);

  // 🔹 Squadra dell’utente corrente
  const [squad, setSquad] = useState(() => {
    const saved = localStorage.getItem(`squadra_${currentUser}`);
    return saved ? JSON.parse(saved) : [];
  });

  // 🔹 Aggiorna localStorage quando cambia la squadra o l’utente
  useEffect(() => {
    localStorage.setItem(`squadra_${currentUser}`, JSON.stringify(squad));
  }, [squad, currentUser]);

  // 🔹 Aggiorna la squadra quando cambia utente
  useEffect(() => {
    const saved = localStorage.getItem(`squadra_${currentUser}`);
    setSquad(saved ? JSON.parse(saved) : []);
  }, [currentUser]);

  const normalize = (str) => str.toLowerCase().replace(/\s+/g, " ").trim();

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

  const addPlayer = () => {
    if (!playerData) return;

    const countInRole = squad.filter((p) => p.role === playerData.role).length;
    if (countInRole >= roleLimits[playerData.role]) {
      alert(`Hai già il numero massimo di ${roleNames[playerData.role]}!`);
      return;
    }

    setSquad([...squad, playerData]);
    setPlayerData(null);
    setPlayerInput("");
    setNotFound(false);
  };

  const removePlayer = (player) => {
    setSquad(squad.filter((p) => p !== player));
  };

  const squadByRole = {
    GK: squad.filter((p) => p.role === "GK"),
    DEF: squad.filter((p) => p.role === "DEF"),
    MID: squad.filter((p) => p.role === "MID"),
    FWD: squad.filter((p) => p.role === "FWD"),
  };

  return (
    <div className="squad-container">
      <h1>📊Fantacalcio Squad</h1>

      <div className="search-section">
        <input
          type="text"
          placeholder="Search for players (e.g., Sommer or Di Lorenzo)"
          value={playerInput}
          onChange={(e) => setPlayerInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button onClick={cercaGiocatoreEsatto}>🔍 Search</button>
        {playerData && <button onClick={addPlayer}>➕ Add Player</button>}
      </div>

      {loading && <p>🔄 Loading...</p>}
      {notFound && <p className="notfound">❌ Player not found</p>}

      {Object.entries(squadByRole).map(([role, players]) => {
        const postiLiberi = roleLimits[role] - players.length;
        if (players.length === 0) return null;

        return (
          <div key={role} className="role-section">
            <h2 data-badge={`${postiLiberi} posti liberi`}>
              {roleNames[role]} ({players.length}/{roleLimits[role]})
            </h2>
            <div className="players-grid">
              {players.map((p) => (
                <div key={p.name + Math.random()} className={`player-card ${p.role}`}>
                  <h3>{p.name}</h3>
                  <p>Ruolo: {p.role} | Squadra: {p.team}</p>
                  <ul>
                    <li>PG: {p.stats.pg}</li>
                    <li>MV: {p.stats.mv}</li>
                    <li>MFV: {p.stats.mfv}</li>
                    <li>GOL: {p.stats.gol}</li>
                    <li>ASS: {p.stats.ass}</li>
                    <li>AMM: {p.stats.amm}</li>
                    <li>ESP: {p.stats.esp}</li>
                    <li>xG: {p.fbref_data?.xg || 0}</li>
                    <li>xA: {p.fbref_data?.xg_assist || 0}</li>
                    <li>Progressivi: {p.fbref_data?.progressive_passes || 0}</li>
                    {p.role === "GK" && (
                      <>
                        <li>Gol subiti: {p.stats.gs}</li>
                        <li>Rigori parati: {p.stats.rp}</li>
                        <li>Clean Sheet: {p.fbref_data?.clean_sheets || 0}</li>
                      </>
                    )}
                  </ul>
                  <p>
                    <a href={p.url} target="_blank" rel="noreferrer">
                      🔗 Complete Player Profile
                    </a>
                  </p>
                  <button className="remove-btn" onClick={() => removePlayer(p)}>❌</button>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {/* Pulsante reset alla fine della pagina */}
      <div className="reset-section">
        <button
          className="reset-btn"
          onClick={() => {
            if (window.confirm("Vuoi davvero resettare la tua squadra?")) {
              setSquad([]);
              localStorage.removeItem(`squadra_${currentUser}`);
            }
          }}
        >
          🔄 Reset Team
        </button>
      </div>
    </div>
  );
};

export default Squad;
