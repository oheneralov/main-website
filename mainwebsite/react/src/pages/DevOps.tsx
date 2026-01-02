import React from 'react';

interface ServiceCard {
  icon: string;
  title: string;
  description: string;
}

const DevOps: React.FC = () => {
  const services: ServiceCard[] = [
    {
      icon: 'mdi mdi-cellphone-android',
      title: 'Kubernetes',
      description:
        'Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It helps ensure high availability and efficient resource utilization across clusters of hosts.',
    },
    {
      icon: 'mdi mdi-television-guide',
      title: 'Amazon Web Services',
      description:
        'A comprehensive cloud platform that provides a wide range of services, including computing power, storage, databases, and machine learning, on a pay-as-you-go basis. It enables businesses to build and scale applications globally with reliability, security, and performance.',
    },
    {
      icon: 'mdi mdi-headset',
      title: 'Google Cloud Platform',
      description:
        'It offers a suite of cloud computing services that run on the same infrastructure Google uses for its products, like Search and YouTube. It provides solutions for computing, data analytics, machine learning, and scalable storage.',
    },
    {
      icon: 'mdi mdi-web',
      title: 'Helm Charts',
      description:
        'Package managers for Kubernetes, simplifying the deployment and management of applications by bundling together all necessary resources into a single, reusable package. They allow users to version, share, and configure applications easily',
    },
  ];

  return (
    <section className="section section-lg bg-gray-lighter text-center" id="devops">
      <div className="container-wide">
        <div className="text-center">
          <h3>DevOps</h3>
          <div className="divider divider-default"></div>
        </div>
        <div className="row row-50 justify-content-sm-center offset-custom-2">
          {services.map((service, index) => (
            <div
              key={index}
              className="col-sm-10 col-md-6 col-lg-4 col-xl-3"
            >
              <div className="thumbnail-classic flex-md-row flex-lg-column flex-column thumbnail-classic-primary">
                <div className="thumbnail-classic-icon">
                  <span className={`icon ${service.icon}`}></span>
                </div>
                <div className="thumbnail-classic-caption">
                  <h6 className="thumbnail-classic-title">{service.title}</h6>
                  <hr className="divider divider-default divider-sm" />
                  <p className="thumbnail-classic-text">{service.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default DevOps;
