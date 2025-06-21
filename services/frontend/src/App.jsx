import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Projects from './pages/Projects';
import Store from './pages/Store';
import ImageManager from './pages/ImageManager';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/store" element={<Store />} />
            <Route path="/images" element={<ImageManager />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;

