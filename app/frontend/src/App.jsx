import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/Home';
import AboutPage from './pages/AboutPage';
import LoginPage from './pages/AuthPage';
import MyTokens from './pages/MyTokens';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/login" element={<LoginPage />} />
        
        <Route
          path="/tokens"
          element={
            <ProtectedRoute>
              <MyTokens />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
