import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ComplianceReport from "./components/ComplianceReport";
import FraudHunterAI from "./components/FraudHunterAI";
import AIContractWatchdog from "./components/AIContractWatchdog";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ComplianceReport />} />
        <Route path="/fraud-hunter" element={<FraudHunterAI />} />
        <Route path="/contract-watchdog" element={<AIContractWatchdog />} />
      </Routes>
    </Router>
  );
}

export default App;
