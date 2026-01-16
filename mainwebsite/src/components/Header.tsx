import React, { useState } from 'react';

const Header: React.FC = () => {
  const [isNavOpen, setIsNavOpen] = useState(false);

  return (
    <header className="section page-header">
      <div className="rd-navbar-wrap rd-navbar-centered">
        <nav
          className="rd-navbar"
          data-layout="rd-navbar-fixed"
          data-sm-layout="rd-navbar-fixed"
          data-md-layout="rd-navbar-fixed"
          data-lg-layout="rd-navbar-fullwidth"
          data-xl-layout="rd-navbar-static"
          data-xxl-layout="rd-navbar-static"
          data-xxxl-layout="rd-navbar-static"
          data-md-device-layout="rd-navbar-fixed"
          data-lg-device-layout="rd-navbar-static"
          data-stick-up="true"
        >
          <div className="rd-navbar-inner">
            <div className="rd-navbar-panel">
              <button
                className="rd-navbar-toggle"
                onClick={() => setIsNavOpen(!isNavOpen)}
              >
                <span></span>
              </button>
              <div className="rd-navbar-brand">
                <a className="brand-name" href="#home">
                  <img
                    className="logo-default"
                    src="/images/logo-default-149x42.png"
                    alt="Logo"
                    width="149"
                    height="42"
                  />
                </a>
              </div>
            </div>
            <div className="rd-navbar-aside-left">
              <div className="rd-navbar-nav-wrap">
                <ul className="rd-navbar-nav">
                  <li className="active">
                    <a href="#home">Home</a>
                  </li>
                  <li>
                    <a href="#about-me">About Me</a>
                  </li>
                  <li>
                    <a href="#devops">DevOps</a>
                  </li>
                  <li>
                    <a href="#ai">AI</a>
                  </li>
                  <li>
                    <a href="#get-in-touch">Get In Touch</a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Header;
