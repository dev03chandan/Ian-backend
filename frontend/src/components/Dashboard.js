// src/components/Dashboard.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Navbar";
import FraudHunterAI from "./FraudHunterAI";
import AIContractWatchdog from "./AIContractWatchdog";

const Dashboard = () => {
  return (
    <Router>
      <Navbar />
      <div style={styles.pageContainer}>
        <Routes>
          <Route path="/fraud-hunter" element={<FraudHunterAI />} />
          <Route path="/contract-watchdog" element={<AIContractWatchdog />} />
        </Routes>
      </div>
    </Router>
  );
};

const styles = {
  pageContainer: {
    padding: "20px",
    maxWidth: "1200px",
    margin: "0 auto",
  },
};

export default Dashboard;
