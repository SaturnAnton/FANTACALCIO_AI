import React, { useState } from "react";
import "./Squad.css";

const roleLimits = { GK: 3, DEF: 8, MID: 8, FWD: 6 };
const roleNames = { GK: "Portieri", DEF: "Difensori", MID: "Centrocampisti", FWD: "Attaccanti" };

const Squad = () => {
  const [playerInput, setPlayerInput] = useState("");
  const [playerData, setPlayerData] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [loading, setLoading] = useState(false);
  const [squad, setSquad] = useState([]);

  const normalize = (str) => str.toLowerCase().replace(/\s+/g, " ").trim();

  // 🔹 Cerca giocatore nel JSON con nome preciso
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
      <h1>📊 Squadra Fantacalcio</h1>

      <div className="search-section">
        <input
          type="text"
          placeholder="Nome giocatore (es: Sommer o Di Lorenzo)"
          value={playerInput}
          onChange={(e) => setPlayerInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button onClick={cercaGiocatoreEsatto}>Cerca</button>
        {playerData && <button onClick={addPlayer}>➕ Aggiungi</button>}
      </div>

      {loading && <p>🔄 Caricamento...</p>}
      {notFound && <p className="notfound">❌ Giocatore non trovato</p>}

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
                      🔗 Scheda completa
                    </a>
                  </p>
                  <button className="remove-btn" onClick={() => removePlayer(p)}>❌</button>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Squad;
