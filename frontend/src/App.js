import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import StartingPage from "./components/StartingPage";
import Login from "./components/Login";
import FraudHunterAI from "./components/FraudHunterAI";
import AIContractWatchdog from "./components/AIContractWatchdog";
import Navbar from "./components/Navbar";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar/>
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