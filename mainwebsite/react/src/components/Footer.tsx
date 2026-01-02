import React from 'react';
import ContactForm from './ContactForm';

const Footer: React.FC = () => {
  return (
    <footer className="section page-footer page-footer-default text-start bg-gray-darker">
      <div className="container-wide">
        <div className="row row-50 justify-content-sm-center">
          <div className="col-md-6 col-xl-3">
            <div className="inset-xxl">
              <h6>About Me</h6>
              <p className="text-spacing-sm">
                I know how to design and develop a website or app of any complexity. Regardless of what you are looking for, I can deliver a solution, which will elevate your business to unbelievable heights.
              </p>
            </div>
          </div>
          <div className="col-md-6 col-xl-2">
            <h6>Quick Links</h6>
            <ul className="list-marked list-marked-primary">
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
              <li>
                <a href="#get-in-touch">Contacts</a>
              </li>
            </ul>
          </div>
          <div className="col-md-6 col-xl-3">
            <h6>Contact Me</h6>
            <ContactForm isFooter={true} />
          </div>
        </div>
        <p className="right">
          &#169;&nbsp;
          <span className="copyright-year"></span> All Rights Reserved
        </p>
      </div>
    </footer>
  );
};

export default Footer;
