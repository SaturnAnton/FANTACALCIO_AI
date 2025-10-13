import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";
import "./Navbar.css";

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h2>Fantacalcio AI</h2>
      </div>
      <div className="navbar-center">
        <Link to="/">Home</Link>
        <Link to="/squad">Squad</Link>
        <Link to="/search">Cerca</Link>
        <Link to="/info">Info</Link>
      </div>
      <div className="navbar-right">
        {user && (
          <>
            <button onClick={logout}>Logout</button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
