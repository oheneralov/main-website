import React from 'react';

const About: React.FC = () => {
  return (
    <section className="section section-lg bg-default" id="about-me">
      <div className="container container-bigger">
        <div className="row row-50 justify-content-md-center align-items-lg-center justify-content-xl-between flex-lg-row-reverse">
          <div className="col-md-9 col-lg-5 col-xl-5">
            <h3>About Me</h3>
            <div className="divider divider-default"></div>
            <p className="heading-5">
              I am a senior fullstack ReactJS/NodeJS developer with a solid experience in DevOps (AWS and GCP). I am an expert bringing you innovative web and IT solutions that combine DevOps, AI and flawless functionality in every project.
            </p>
            <p className="text-spacing-sm">
              I provide IT services for companies all over the world. I operate on a managed services model that offers proactive outsourced IT services as well as design, development, and management services at affordable, consistent rates.
            </p>
          </div>
          <div className="col-md-9 col-lg-6">
            <img
              src="/images/video-poster.jpg"
              alt="Video poster"
              width="720"
              height="459"
              loading="lazy"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
