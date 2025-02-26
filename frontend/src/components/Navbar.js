import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import logo from "../assets/logo.png";

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={styles.navbar}>
      <div style={styles.logoContainer}>
        <Link to="/">
          <img src={logo} alt="ZeroRedTape Logo" style={styles.logo} />
        </Link>
      </div>

      <div style={styles.navLinks}>
        <Link to="/contract-watchdog" style={styles.navItem}>
          AI Contract Watchdog
        </Link>
        <Link to="/fraud-hunter" style={styles.navItem}>
          Fraud Hunter AI
        </Link>
        <Link to="/dashboard" style={styles.navItem}>
          Dashboard
        </Link>
        {isAuthenticated && (
          <button 
            onClick={handleLogout} 
            style={styles.logoutButton}
          >
            Logout
          </button>
        )}
      </div>
    </nav>
  );
};

const styles = {
  navbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 20px",
    backgroundColor: "#fff",
    boxShadow: "0px 2px 10px rgba(0,0,0,0.1)",
  },
  logoContainer: {
    display: "flex",
    alignItems: "center",
  },
  logo: {
    height: "40px",
    marginRight: "10px",
  },
  navLinks: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
  },
  navItem: {
    textDecoration: "none",
    color: "#232c4e",
    fontWeight: "600",
    fontSize: "16px",
    padding: "8px 12px",
    borderRadius: "4px",
    transition: "background-color 0.3s, color 0.3s",
    cursor: "pointer",
  },
  logoutButton: {
    padding: "8px 16px",
    backgroundColor: "#dc3545",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "600",
    transition: "background-color 0.3s",
  },
};

export default Navbar;
