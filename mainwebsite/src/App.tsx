import React, { useEffect } from 'react';
import Header from './components/Header';
import Home from './pages/Home';
import About from './pages/About';
import DevOps from './pages/DevOps';
import AI from './pages/AI';
import Contact from './pages/Contact';
import Footer from './components/Footer';
import './App.css';

const App: React.FC = () => {
  useEffect(() => {
    // Hide page loader
    const loader = document.querySelector('.page-loader');
    if (loader) {
      setTimeout(() => {
        (loader as HTMLElement).style.display = 'none';
      }, 1000);
    }

    // Set copyright year
    const yearElement = document.querySelector('.copyright-year');
    if (yearElement) {
      yearElement.textContent = new Date().getFullYear().toString();
    }
  }, []);

  return (
    <div className="page">
      <Header />
      <Home />
      <About />
      <DevOps />
      <AI />
      <Contact />
      <Footer />
    </div>
  );
};

export default App;
