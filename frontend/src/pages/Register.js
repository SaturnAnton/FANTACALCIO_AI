import React, { useState, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { Link, useNavigate } from "react-router-dom";
import "./Register.css";

const Register = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password.length > 50) {
      setError("La password non può superare i 50 caratteri");
      return;
    }

    if (password.length < 8) {
      setError("La password deve essere di almeno 8 caratteri");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        let errorMessage = "Errore durante la registrazione";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          errorMessage = `Errore ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      login(data);
      navigate("/");
    } catch (err) {
      console.error(err);
      setError(err.message || "Errore di connessione al server");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h2>Registrazione</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            required
          />
          <input
            type="password"
            placeholder="Password (minimo 8 caratteri)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            required
          />
          {error && <p style={{ color: "red", marginBottom: "10px" }}>{error}</p>}
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Registrazione in corso..." : "Registrati"}
          </button>
        </form>
        <p>
          Hai già un account? <Link to="/login">Torna al login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
