import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ComplianceReport from "./components/StartingPage";
import FraudHunterAI from "./components/FraudHunterAI";
import AIContractWatchdog from "./components/AIContractWatchdog";

function Navbar() {
  return (
    <Router>
      <Navbar /> {/* Global Navbar appears on all pages */}
      <div style={styles.pageContainer}>
        <Routes>
          <Route path="/" element={<ComplianceReport />} />
          <Route path="/fraud-hunter" element={<FraudHunterAI />} />
          <Route path="/contract-watchdog" element={<AIContractWatchdog />} />
        </Routes>
      </div>
    </Router>
  );
}

const styles = {
  pageContainer: {
    padding: "20px",
    maxWidth: "1200px",
    margin: "0 auto",
  },
};

export default Navbar;
