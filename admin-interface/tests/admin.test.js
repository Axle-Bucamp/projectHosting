import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Login from '../src/pages/Login';
import Dashboard from '../src/pages/Dashboard';
import Projects from '../src/pages/Projects';

// Mock contexts
const mockAuthContext = {
  user: { id: 1, email: 'admin@test.com', role: 'admin' },
  login: jest.fn(),
  logout: jest.fn(),
  isAuthenticated: true
};

const mockApiContext = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn()
};

jest.mock('../src/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext
}));

jest.mock('../src/contexts/ApiContext', () => ({
  useApi: () => mockApiContext
}));

global.fetch = jest.fn();

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form', () => {
    renderWithRouter(<Login />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  test('handles login form submission', async () => {
    mockAuthContext.login.mockResolvedValueOnce({ success: true });
    
    renderWithRouter(<Login />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'admin@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/mot de passe/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /se connecter/i }));
    
    await waitFor(() => {
      expect(mockAuthContext.login).toHaveBeenCalledWith('admin@test.com', 'password123');
    });
  });

  test('displays error message on login failure', async () => {
    mockAuthContext.login.mockRejectedValueOnce(new Error('Invalid credentials'));
    
    renderWithRouter(<Login />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'admin@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/mot de passe/i), {
      target: { value: 'wrongpassword' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /se connecter/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/erreur de connexion/i)).toBeInTheDocument();
    });
  });
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApiContext.get.mockResolvedValue({
      projects: 5,
      contacts: 12,
      storeItems: 8,
      systemMetrics: {
        cpu: 45,
        memory: 67,
        disk: 23
      }
    });
  });

  test('renders dashboard with metrics', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
    });
    
    expect(mockApiContext.get).toHaveBeenCalledWith('/api/admin/dashboard');
  });

  test('displays system metrics', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('45%')).toBeInTheDocument(); // CPU
      expect(screen.getByText('67%')).toBeInTheDocument(); // Memory
      expect(screen.getByText('23%')).toBeInTheDocument(); // Disk
    });
  });

  test('displays project count', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument(); // Projects count
    });
  });
});

describe('Admin Projects Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders projects list', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Test Project 1',
        status: 'online',
        created_at: '2025-01-01T00:00:00Z'
      },
      {
        id: 2,
        name: 'Test Project 2',
        status: 'maintenance',
        created_at: '2025-01-02T00:00:00Z'
      }
    ];

    mockApiContext.get.mockResolvedValueOnce({ projects: mockProjects });
    
    renderWithRouter(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument();
      expect(screen.getByText('Test Project 2')).toBeInTheDocument();
    });
  });

  test('handles project creation', async () => {
    mockApiContext.get.mockResolvedValueOnce({ projects: [] });
    mockApiContext.post.mockResolvedValueOnce({
      success: true,
      project: { id: 3, name: 'New Project', status: 'online' }
    });
    
    renderWithRouter(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /ajouter un projet/i })).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByRole('button', { name: /ajouter un projet/i }));
    
    // Fill form (assuming modal opens)
    await waitFor(() => {
      const nameInput = screen.getByLabelText(/nom du projet/i);
      if (nameInput) {
        fireEvent.change(nameInput, { target: { value: 'New Project' } });
        
        const submitButton = screen.getByRole('button', { name: /créer/i });
        fireEvent.click(submitButton);
        
        expect(mockApiContext.post).toHaveBeenCalledWith('/api/projects', expect.any(Object));
      }
    });
  });

  test('handles project deletion', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Test Project 1',
        status: 'online',
        created_at: '2025-01-01T00:00:00Z'
      }
    ];

    mockApiContext.get.mockResolvedValueOnce({ projects: mockProjects });
    mockApiContext.delete.mockResolvedValueOnce({ success: true });
    
    renderWithRouter(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument();
    });
    
    // Find and click delete button
    const deleteButton = screen.getByRole('button', { name: /supprimer/i });
    fireEvent.click(deleteButton);
    
    // Confirm deletion
    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: /confirmer/i });
      if (confirmButton) {
        fireEvent.click(confirmButton);
        expect(mockApiContext.delete).toHaveBeenCalledWith('/api/projects/1');
      }
    });
  });

  test('handles project status update', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Test Project 1',
        status: 'online',
        created_at: '2025-01-01T00:00:00Z'
      }
    ];

    mockApiContext.get.mockResolvedValueOnce({ projects: mockProjects });
    mockApiContext.put.mockResolvedValueOnce({
      success: true,
      project: { id: 1, name: 'Test Project 1', status: 'maintenance' }
    });
    
    renderWithRouter(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project 1')).toBeInTheDocument();
    });
    
    // Find and click status toggle
    const statusButton = screen.getByRole('button', { name: /en ligne/i });
    fireEvent.click(statusButton);
    
    await waitFor(() => {
      expect(mockApiContext.put).toHaveBeenCalledWith('/api/projects/1', expect.any(Object));
    });
  });
});

describe('Authentication Flow', () => {
  test('redirects to login when not authenticated', () => {
    const unauthenticatedContext = {
      ...mockAuthContext,
      isAuthenticated: false,
      user: null
    };
    
    jest.doMock('../src/contexts/AuthContext', () => ({
      useAuth: () => unauthenticatedContext
    }));
    
    renderWithRouter(<Dashboard />);
    
    // Should redirect to login or show login form
    expect(screen.getByText(/connexion/i) || screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  test('shows dashboard when authenticated', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/tableau de bord/i)).toBeInTheDocument();
    });
  });
});

describe('Error Handling', () => {
  test('handles API errors gracefully', async () => {
    mockApiContext.get.mockRejectedValueOnce(new Error('Network error'));
    
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/erreur de chargement/i) || screen.getByText(/erreur/i)).toBeInTheDocument();
    });
  });

  test('shows loading states', () => {
    mockApiContext.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithRouter(<Dashboard />);
    
    expect(screen.getByText(/chargement/i) || screen.getByTestId('loading')).toBeInTheDocument();
  });
});

describe('Form Validation', () => {
  test('validates required fields in project form', async () => {
    mockApiContext.get.mockResolvedValueOnce({ projects: [] });
    
    renderWithRouter(<Projects />);
    
    await waitFor(() => {
      const addButton = screen.getByRole('button', { name: /ajouter un projet/i });
      fireEvent.click(addButton);
    });
    
    // Try to submit empty form
    await waitFor(() => {
      const submitButton = screen.getByRole('button', { name: /créer/i });
      if (submitButton) {
        fireEvent.click(submitButton);
        
        // Should show validation errors
        expect(screen.getByText(/nom requis/i) || screen.getByText(/champ obligatoire/i)).toBeInTheDocument();
      }
    });
  });
});

