import React from 'react';
import ProjectList from '../components/ProjectList';
import ContactForm from '../components/ContactForm';

const Projects = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Nos <span className="text-blue-600">Prototypes</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Découvrez nos projets innovants et solutions technologiques. 
              Chaque prototype démontre notre expertise dans les technologies modernes.
            </p>
          </div>
        </div>
      </section>

      {/* Projects Grid */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Projets en cours
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Statut en temps réel de nos différents prototypes et applications
            </p>
          </div>
          
          <ProjectList />
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Un projet en tête ?
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Contactez-nous pour discuter de votre projet et voir comment nous pouvons vous aider
            </p>
          </div>
          
          <ContactForm />
        </div>
      </section>
    </div>
  );
};

export default Projects;

