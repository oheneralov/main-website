import React from 'react';

const Contact: React.FC = () => {
  return (
    <section className="section section-lg bg-default text-center" id="get-in-touch">
      <div className="container container-bigger">
        <h3>Get In Touch</h3>
        <hr className="divider divider-default" />
        <div className="row row-50 justify-content-center">
          <div className="col-md-6 col-lg-3">
            <div className="team-classic">
              <div className="team-classic-image">
                <figure>
                  <img
                    src="/images/me.webp"
                    alt="Profile"
                    width="270"
                    height="270"
                    loading="lazy"
                  />
                </figure>
                <div className="team-classic-image-caption">
                  <ul className="list-inline list-team">
                    <li>
                      <a
                        className="icon icon-sm-bigger icon-white mdi mdi-twitter"
                        href="https://x.com/alex_oheneralov"
                        aria-label="Twitter"
                      ></a>
                    </li>
                    <li>
                      <a
                        className="icon icon-sm-bigger icon-white mdi mdi-instagram"
                        href="https://www.linkedin.com/in/oleksandr-heneralov-82389640/"
                        aria-label="LinkedIn"
                      ></a>
                    </li>
                    <li>
                      <a
                        className="icon icon-sm-bigger icon-white mdi mdi-linkedin"
                        href="https://www.linkedin.com/in/oleksandr-heneralov-82389640/"
                        aria-label="LinkedIn"
                      ></a>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="team-classic-caption">
                <h5>
                  <a
                    className="team-classic-title"
                    href="https://www.linkedin.com/in/oleksandr-heneralov-82389640/"
                  >
                    Oleksandr Generalov
                  </a>
                </h5>
                <p className="team-classic-job-position">Fullstack Developer</p>
                <a
                  className="button button-xs button-default-outline"
                  href="https://www.linkedin.com/in/oleksandr-heneralov-82389640/"
                >
                  get in touch
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
