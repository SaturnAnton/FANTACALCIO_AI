import React, { useState, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 🔥 VALIDAZIONE PASSWORD NEL FRONTEND
    if (password.length > 50) {
      alert("La password non può superare i 50 caratteri");
      return;
    }
    
    if (password.length < 8) {
      alert("La password deve essere di almeno 8 caratteri");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      // 🔥 CONTROLLO CRITICO: verifica se la risposta è ok PRIMA di fare .json()
      if (!response.ok) {
        let errorMessage = "Errore durante la registrazione";
        
        // Prova a leggere il messaggio di errore dal server
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (jsonError) {
          // Se non riesce a parsare come JSON, usa lo status HTTP
          errorMessage = `Errore ${response.status}: ${response.statusText}`;
        }
        
        throw new Error(errorMessage);
      }

      // Solo se response.ok è true, procedi con il parsing JSON
      const data = await response.json();
      login(data);
      navigate("/");
      
    } catch (error) {
      console.error("Errore fetch:", error);
      alert(error.message || "Errore di connessione al server");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Registrazione</h2>
      <form onSubmit={handleSubmit}>
        <input 
          placeholder="Email" 
          value={email} 
          onChange={e => setEmail(e.target.value)}
          disabled={isLoading}
        />
        <input 
          type="password" 
          placeholder="Password (minimo 8 caratteri)" 
          value={password} 
          onChange={e => setPassword(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Registrazione in corso..." : "Registrati"}
        </button>
      </form>
    </div>
  );
};

export default Register;