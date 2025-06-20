import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Menu, X, Github, Linkedin, Twitter } from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <span className="font-bold text-xl">Startup</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className="text-foreground/80 hover:text-foreground transition-colors duration-200"
            >
              Accueil
            </Link>
            <Link 
              to="/projects" 
              className="text-foreground/80 hover:text-foreground transition-colors duration-200"
            >
              Prototypes
            </Link>
            <Link 
              to="/store" 
              className="text-foreground/80 hover:text-foreground transition-colors duration-200"
            >
              Store
            </Link>
          </nav>

          {/* Social Links & CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-foreground/60 hover:text-foreground transition-colors duration-200"
            >
              <Github className="h-5 w-5" />
            </a>
            <a 
              href="https://linkedin.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-foreground/60 hover:text-foreground transition-colors duration-200"
            >
              <Linkedin className="h-5 w-5" />
            </a>
            <a 
              href="https://twitter.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-foreground/60 hover:text-foreground transition-colors duration-200"
            >
              <Twitter className="h-5 w-5" />
            </a>
            <Button className="ml-4">
              Contactez-nous
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden p-2 rounded-md hover:bg-accent transition-colors duration-200"
          >
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <nav className="flex flex-col space-y-4">
              <Link 
                to="/" 
                className="text-foreground/80 hover:text-foreground transition-colors duration-200 py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Accueil
              </Link>
              <Link 
                to="/projects" 
                className="text-foreground/80 hover:text-foreground transition-colors duration-200 py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Prototypes
              </Link>
              <Link 
                to="/store" 
                className="text-foreground/80 hover:text-foreground transition-colors duration-200 py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Store
              </Link>
              <div className="flex items-center space-x-4 pt-4">
                <a 
                  href="https://github.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-foreground/60 hover:text-foreground transition-colors duration-200"
                >
                  <Github className="h-5 w-5" />
                </a>
                <a 
                  href="https://linkedin.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-foreground/60 hover:text-foreground transition-colors duration-200"
                >
                  <Linkedin className="h-5 w-5" />
                </a>
                <a 
                  href="https://twitter.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-foreground/60 hover:text-foreground transition-colors duration-200"
                >
                  <Twitter className="h-5 w-5" />
                </a>
              </div>
              <Button className="w-full mt-4">
                Contactez-nous
              </Button>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;

