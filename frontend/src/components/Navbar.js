// src/components/Navbar.js
import React from "react";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png"; // Update the path to your actual logo

const Navbar = () => {
  return (
    <nav style={styles.navbar}>
      <div style={styles.logoContainer}>
        <Link to="/">
        <img src={logo} alt="ZeroRedTape Logo" style={styles.logo} />
        {/* <span style={styles.brandText}>ZeroRedTape</span>
        <span style={styles.tagline}>GOV AI COMPLIANCE</span> */}
        </Link>
      </div>

      <div style={styles.navLinks}>
        <Link to="/contract-watchdog" style={styles.navItem}>
          AI Contract Watchdog
        </Link>
        <Link to="/fraud-hunter" style={styles.navItem}>
          Fraud Hunter AI
        </Link>
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
    height: "40px", // Adjust the size to match your logo
    marginRight: "10px",
  },
  brandText: {
    fontSize: "20px",
    fontWeight: "bold",
    color: "#232c4e",
  },
  tagline: {
    fontSize: "12px",
    color: "#555",
    marginLeft: "5px",
  },
  navLinks: {
    display: "flex",
    gap: "20px",
  },
  navItem: {
    textDecoration: "none",
    color: "#232c4e",
    fontWeight: "600",
    fontSize: "16px",
    transition: "color 0.3s",
  },
};

export default Navbar;
