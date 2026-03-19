/**
 * Custom render utility for tests.
 *
 * Wraps components with all providers required by the application:
 * MemoryRouter (for React Router), AuthProvider (for auth state).
 * Add any additional providers here if the app requires them.
 *
 * Usage:
 *   import { render, screen } from '../utils';
 *   render(<LoginPage />);
 *   render(<StudentDashboard />, { initialRoute: '/student' });
 */
import React from 'react';
import { render as tlRender, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialRoute?: string;
}

function TestProviders({
  children,
  initialRoute = '/',
}: {
  children: React.ReactNode;
  initialRoute?: string;
}) {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </MemoryRouter>
  );
}

function customRender(
  ui: React.ReactElement,
  options: CustomRenderOptions = {}
) {
  const { initialRoute, ...renderOptions } = options;
  return tlRender(ui, {
    wrapper: ({ children }) => (
      <TestProviders initialRoute={initialRoute}>{children}</TestProviders>
    ),
    ...renderOptions,
  });
}

// Re-export everything from @testing-library/react so tests only
// need to import from this file
export * from '@testing-library/react';
export { customRender as render };

// Helper: simulate an authenticated session in localStorage
// before rendering a protected component
export function setAuthSession(user = {
  id: 'user-student-001',
  email: 'student@test.com',
  name: 'Test Student',
  role: 'student',
  createdAt: new Date('2026-01-01T00:00:00Z'),
  updatedAt: new Date('2026-01-01T00:00:00Z'),
}) {
  localStorage.setItem('access_token', 'mock-jwt-token-for-testing-only');
  localStorage.setItem('current_user', JSON.stringify(user));
}

// Helper: clear auth session
export function clearAuthSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('current_user');
}
