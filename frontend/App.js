import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import StartingPage from "./components/StartingPage";
import FraudHunterAI from "./components/FraudHunterAI";
import AIContractWatchdog from "./components/AIContractWatchdog";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<StartingPage />} />
        <Route path="/fraud-hunter" element={<FraudHunterAI />} />
        <Route path="/contract-watchdog" element={<AIContractWatchdog />} />
      </Routes>
    </Router>
  );
}

export default App;
