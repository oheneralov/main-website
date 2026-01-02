import React, { useState } from 'react';
import axios from 'axios';

interface ContactFormProps {
  isFooter?: boolean;
}

const ContactForm: React.FC<ContactFormProps> = ({ isFooter = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);
    setError('');

    try {
      const response = await axios.post('/contacts', formData);

      if (response.data.success) {
        setSuccess(true);
        setFormData({ name: '', email: '', message: '' });
        setTimeout(() => setSuccess(false), 5000);
      } else {
        setError(response.data.message || 'Failed to send message');
      }
    } catch (err) {
      setError('Error sending message. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formClasses = isFooter
    ? 'rd-mailform rd-mailform-sm'
    : 'rd-mailform rd-mailform-lg';

  return (
    <div>
      <form className={formClasses} onSubmit={handleSubmit}>
        <div className="form-wrap form-wrap-validation">
          <input
            className="form-input"
            id={`form-${isFooter ? 'footer' : 'main'}-name`}
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder=" "
          />
          <label
            className="form-label"
            htmlFor={`form-${isFooter ? 'footer' : 'main'}-name`}
          >
            Name
          </label>
        </div>
        <div className="form-wrap form-wrap-validation">
          <input
            className="form-input"
            id={`form-${isFooter ? 'footer' : 'main'}-email`}
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder=" "
          />
          <label
            className="form-label"
            htmlFor={`form-${isFooter ? 'footer' : 'main'}-email`}
          >
            E-mail
          </label>
        </div>
        <div className="form-wrap form-wrap-validation">
          <label
            className="form-label"
            htmlFor={`form-${isFooter ? 'footer' : 'main'}-message`}
          >
            Message
          </label>
          <textarea
            className="form-input"
            id={`form-${isFooter ? 'footer' : 'main'}-message`}
            name="message"
            value={formData.message}
            onChange={handleChange}
            required
            placeholder=" "
          ></textarea>
        </div>
        {success && (
          <div className="alert alert-success" role="alert">
            Message sent successfully!
          </div>
        )}
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}
        <div className="form-button">
          <button
            className="button button-sm button-primary"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Sending...' : 'Send message'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ContactForm;
