import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import StartingPage from "./components/StartingPage";
import Login from "./components/Login";
import FraudHunterAI from "./components/FraudHunterAI";
import AIContractWatchdog from "./components/AIContractWatchdog";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <StartingPage />
            </ProtectedRoute>
          } />
          <Route path="/fraud-hunter" element={
            <ProtectedRoute>
              <FraudHunterAI />
            </ProtectedRoute>
          } />
          <Route path="/contract-watchdog" element={
            <ProtectedRoute>
              <AIContractWatchdog />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;