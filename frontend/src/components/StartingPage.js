// src/components/StartingPage.js
import React from "react";
import { Link } from "react-router-dom";
import backgroundImage from "../assets/background.jpg"; // Replace with your actual background image
import logo from "../assets/logo.png"; // Ensure your logo is correctly placed

const StartingPage = () => {
  return (
    <div style={styles.container}>
      {/* Hero Section */}
      <div style={styles.heroSection}>
        <div style={styles.heroOverlay}>
          <div style={styles.heroContent}>
            <img src={logo} alt="ZeroRedTape Logo" style={styles.logo} />
            <h1 style={styles.heroTitle}>
              Government Compliance. <br /> AI-Powered.
            </h1>
            <p style={styles.heroSubtitle}>
              Government contracts are complex, full of loopholes, and prone to fraud.
              <br />
              ZeroRedTape uses AI to instantly scan documents for compliance violations and financial fraud.
            </p>
            <div style={styles.buttonContainer}>
              <Link to="/contract-watchdog" style={styles.button}>
                Scan Contract for Violations
              </Link>
              <Link to="/fraud-hunter" style={styles.button}>
                Detect Fraud in Payments
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div style={styles.howItWorks}>
        <h2 style={styles.sectionTitle}>How it works</h2>
        <div style={styles.stepsContainer}>
          <div style={styles.step}>
            <span role="img" aria-label="upload" style={styles.emoji}>
              📂
            </span>
            <h3>1. Upload Your Document</h3>
            <p>
              Drag and drop your contracts, invoices, or payment records (PDF, CSV, XLS), and AI will instantly scan for compliance risks and fraud.
            </p>
          </div>
          <div style={styles.step}>
            <span role="img" aria-label="ai" style={styles.emoji}>
              ⚖️
            </span>
            <h3>2. AI Checks for Violations</h3>
            <p>
              AI analyzes contracts against FAR, GSA, and government rules, detecting fraud like duplicate invoices, overpricing, and vendor risk.
            </p>
          </div>
          <div style={styles.step}>
            <span role="img" aria-label="results" style={styles.emoji}>
              📊
            </span>
            <h3>3. Get Instant Results</h3>
            <p>
              AI generates a risk report with violations, pricing issues, and compliance gaps, allowing you to take action immediately.
            </p>
          </div>
        </div>
      </div>

      {/* Why This Matters Section */}
      <div style={styles.whyMatters}>
        <h2 style={styles.sectionTitle}>Why This Matters?</h2>
        <p style={styles.whyText}>
          <strong>$236 Billion</strong> in improper government payments were reported in 2023.
          <br />
          <strong>100,000+ pages</strong> of legal contracts are manually reviewed, causing delays and errors.
          <br />
          AI can instantly detect fraud, flag contract violations, and eliminate waste.
        </p>
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <p>2025 ZeroRedTape. All rights reserved.</p>
        <div style={styles.footerLinks}>
          <Link to="/privacy-policy" style={styles.footerLink}>
            Privacy Policy
          </Link>
          <Link to="/terms-of-service" style={styles.footerLink}>
            Terms Of Service
          </Link>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    fontFamily: "Arial, sans-serif",
    color: "#232c4e",
    textAlign: "center",
  },
  heroSection: {
    backgroundImage: `url(${backgroundImage})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    height: "500px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  heroOverlay: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    position: "absolute",
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  heroContent: {
    color: "#fff",
    textAlign: "center",
    maxWidth: "700px",
    padding: "20px",
  },
  logo: {
    width: "120px",
    marginBottom: "10px",
  },
  heroTitle: {
    fontSize: "36px",
    fontWeight: "bold",
  },
  heroSubtitle: {
    fontSize: "18px",
    marginBottom: "20px",
  },
  buttonContainer: {
    display: "flex",
    justifyContent: "center",
    gap: "20px",
  },
  button: {
    backgroundColor: "#000",
    color: "#fff",
    padding: "12px 20px",
    textDecoration: "none",
    borderRadius: "6px",
    fontSize: "16px",
    fontWeight: "bold",
    transition: "background 0.3s",
  },
  howItWorks: {
    padding: "50px 20px",
    backgroundColor: "#f9f9f9",
  },
  sectionTitle: {
    fontSize: "28px",
    marginBottom: "20px",
  },
  stepsContainer: {
    display: "flex",
    justifyContent: "center",
    gap: "40px",
    maxWidth: "1000px",
    margin: "0 auto",
  },
  step: {
    maxWidth: "300px",
    textAlign: "center",
  },
  emoji: {
    fontSize: "36px",
  },
  whyMatters: {
    padding: "60px 20px",
    backgroundColor: "#232c4e",
    color: "#fff",
  },
  whyText: {
    fontSize: "18px",
    maxWidth: "700px",
    margin: "0 auto",
    lineHeight: "1.6",
  },
  footer: {
    padding: "20px",
    backgroundColor: "#f9f9f9",
    fontSize: "14px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  footerLinks: {
    display: "flex",
    gap: "20px",
  },
  footerLink: {
    textDecoration: "none",
    color: "#232c4e",
    fontWeight: "bold",
  },
};

export default StartingPage;
