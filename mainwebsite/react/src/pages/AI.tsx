import React from 'react';

interface GalleryItem {
  src: string;
  alt: string;
  title: string;
}

const AI: React.FC = () => {
  const galleryItems: GalleryItem[] = [
    {
      src: '/images/neural-network.webp',
      alt: 'Neural Network',
      title: 'Neural Network',
    },
    {
      src: '/images/cnn.webp',
      alt: 'Convolutional Neural Network',
      title: 'Convolutional Neural Network',
    },
    {
      src: '/images/gan.webp',
      alt: 'GAN',
      title: 'GAN',
    },
    {
      src: '/images/feedforward.webp',
      alt: 'Feedforward neural network',
      title: 'Feedforward neural network',
    },
    {
      src: '/images/recurrent.webp',
      alt: 'Recurrent Neural Network',
      title: 'Recurrent Neural Network',
    },
    {
      src: '/images/ml.webp',
      alt: 'Machine Learning',
      title: 'Machine Learning',
    },
  ];

  return (
    <section className="section section-lg text-center bg-default" id="ai">
      <div className="container container-bigger">
        <h3>AI</h3>
        <div className="row row-50" data-lightgallery="group">
          {galleryItems.map((item, index) => (
            <div key={index} className="col-sm-12 col-md-6 col-lg-4">
              <a
                className="gallery-item titled-gallery-item"
                href={item.src}
                data-lightgallery="item"
              >
                <div className="gallery-item-image">
                  <figure>
                    <img
                      src={item.src}
                      alt={item.alt}
                      width="570"
                      height="380"
                      loading="lazy"
                    />
                  </figure>
                  <div className="caption"></div>
                </div>
              </a>
              <div className="titled-gallery-caption">
                <a href="#ai">{item.title}</a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AI;
