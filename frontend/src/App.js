import React from 'react';
import './App.css';
import Nav from './components/Nav';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import Search from './components/Search';
import Annotation from './components/Annotation';

function App() {

  return (
    <Router>
      <div className="app">
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/annotation" element={<Annotation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
