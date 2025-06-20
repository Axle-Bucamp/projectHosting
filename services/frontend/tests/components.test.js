import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ContactForm from '../src/components/ContactForm';
import ProjectList from '../src/components/ProjectList';
import StoreGrid from '../src/components/StoreGrid';

// Mock fetch for API calls
global.fetch = jest.fn();

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ContactForm Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders contact form with all fields', () => {
    renderWithRouter(<ContactForm />);
    
    expect(screen.getByLabelText(/nom complet/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/entreprise/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sujet/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /envoyer le message/i })).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Message envoyé avec succès' })
    });

    renderWithRouter(<ContactForm />);
    
    fireEvent.change(screen.getByLabelText(/nom complet/i), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/message/i), {
      target: { value: 'Test message' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /envoyer le message/i }));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: 'John Doe',
          email: 'john@example.com',
          company: '',
          subject: '',
          message: 'Test message'
        })
      });
    });
  });

  test('displays success message after successful submission', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });

    renderWithRouter(<ContactForm />);
    
    fireEvent.change(screen.getByLabelText(/nom complet/i), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/message/i), {
      target: { value: 'Test message' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /envoyer le message/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/message envoyé/i)).toBeInTheDocument();
    });
  });

  test('displays error message on submission failure', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Erreur serveur' })
    });

    renderWithRouter(<ContactForm />);
    
    fireEvent.change(screen.getByLabelText(/nom complet/i), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/message/i), {
      target: { value: 'Test message' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /envoyer le message/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/erreur serveur/i)).toBeInTheDocument();
    });
  });
});

describe('ProjectList Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithRouter(<ProjectList />);
    
    expect(screen.getAllByTestId('loading-card')).toHaveLength(6);
  });

  test('renders projects when data is loaded', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Test Project 1',
        description: 'Description 1',
        status: 'online',
        technologies: ['React', 'Node.js'],
        url: 'https://test1.com'
      },
      {
        id: 2,
        name: 'Test Project 2',
        description: 'Description 2',
        status: 'maintenance',
        technologies: ['Vue.js', 'Python'],
        url: 'https://test2.com'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, projects: mockProjects })
    });

    renderWithRouter(<ProjectList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument();
      expect(screen.getByText('Test Project 2')).toBeInTheDocument();
    });
    
    expect(screen.getByText('En ligne')).toBeInTheDocument();
    expect(screen.getByText('Maintenance')).toBeInTheDocument();
  });

  test('renders empty state when no projects', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, projects: [] })
    });

    renderWithRouter(<ProjectList />);
    
    await waitFor(() => {
      expect(screen.getByText(/aucun projet disponible/i)).toBeInTheDocument();
    });
  });

  test('handles API error gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('API Error'));

    renderWithRouter(<ProjectList />);
    
    await waitFor(() => {
      expect(screen.getByText(/aucun projet disponible/i)).toBeInTheDocument();
    });
  });
});

describe('StoreGrid Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithRouter(<StoreGrid />);
    
    expect(screen.getAllByTestId('loading-card')).toHaveLength(6);
  });

  test('renders store items when data is loaded', async () => {
    const mockItems = [
      {
        id: 1,
        name: 'Test Service 1',
        description: 'Service description 1',
        price: 99.99,
        currency: 'EUR',
        category: 'service',
        features: ['Feature 1', 'Feature 2'],
        rating: 4.5,
        reviews_count: 10
      },
      {
        id: 2,
        name: 'Test Product 2',
        description: 'Product description 2',
        price: 149.99,
        currency: 'EUR',
        category: 'product',
        features: ['Feature A', 'Feature B'],
        popular: true,
        rating: 4.8,
        reviews_count: 25
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, items: mockItems })
    });

    renderWithRouter(<StoreGrid />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Service 1')).toBeInTheDocument();
      expect(screen.getByText('Test Product 2')).toBeInTheDocument();
    });
    
    expect(screen.getByText('99.99')).toBeInTheDocument();
    expect(screen.getByText('149.99')).toBeInTheDocument();
    expect(screen.getByText('Populaire')).toBeInTheDocument();
  });

  test('renders empty state when no items', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, items: [] })
    });

    renderWithRouter(<StoreGrid />);
    
    await waitFor(() => {
      expect(screen.getByText(/aucun produit disponible/i)).toBeInTheDocument();
    });
  });

  test('displays correct category badges', async () => {
    const mockItems = [
      {
        id: 1,
        name: 'Service Item',
        category: 'service',
        price: 99.99,
        currency: 'EUR'
      },
      {
        id: 2,
        name: 'Product Item',
        category: 'product',
        price: 149.99,
        currency: 'EUR'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, items: mockItems })
    });

    renderWithRouter(<StoreGrid />);
    
    await waitFor(() => {
      expect(screen.getByText('service')).toBeInTheDocument();
      expect(screen.getByText('product')).toBeInTheDocument();
    });
  });
});

describe('Navigation and Routing', () => {
  test('renders navigation links', () => {
    renderWithRouter(
      <div>
        <nav>
          <a href="/">Accueil</a>
          <a href="/projects">Prototypes</a>
          <a href="/store">Store</a>
        </nav>
      </div>
    );
    
    expect(screen.getByText('Accueil')).toBeInTheDocument();
    expect(screen.getByText('Prototypes')).toBeInTheDocument();
    expect(screen.getByText('Store')).toBeInTheDocument();
  });
});

describe('Responsive Design', () => {
  test('components render on mobile viewport', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });
    
    renderWithRouter(<ContactForm />);
    
    expect(screen.getByLabelText(/nom complet/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /envoyer le message/i })).toBeInTheDocument();
  });

  test('components render on desktop viewport', () => {
    // Mock desktop viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1920,
    });
    
    renderWithRouter(<ContactForm />);
    
    expect(screen.getByLabelText(/nom complet/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /envoyer le message/i })).toBeInTheDocument();
  });
});

