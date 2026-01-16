import React from 'react';

const Home: React.FC = () => {
  return (
    <section className="section bg-gray-darker text-center" id="home">
      <div
        className="section-xl bg-vide"
        style={{
          backgroundImage: 'url(/video/office-day)',
          backgroundPosition: '0% 50%',
          backgroundSize: 'cover',
        }}
      >
        <div className="container container-wide">
          <div className="row row-50 justify-content-md-center">
            <div className="col-md-10 col-xl-9">
              <h1>Modern IT technologies</h1>
              <p className="big">
                Modern IT technologies are shaping how businesses operate and how people interact with technology. It is various innovative technologies that make your work not only easier but more productive without unnecessary coding.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Home;
