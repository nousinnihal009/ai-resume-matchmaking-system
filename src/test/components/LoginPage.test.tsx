/**
 * Tests for the LoginPage component.
 *
 * Tests cover: field rendering, validation, successful login flow,
 * failed login error display, and token storage side effects.
 */
import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, setAuthSession, clearAuthSession } from '../utils';
import { LoginPage } from '@/app/pages/auth/LoginPage';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

const API_BASE = 'http://localhost:8000/api/v1';

describe('LoginPage', () => {

  // ── Rendering ──────────────────────────────────────────────────────

  describe('rendering', () => {

    it('renders email input field', () => {
      render(<LoginPage />);
      expect(
        screen.getByRole('textbox', { name: /email/i }) ??
        screen.getByPlaceholderText(/email/i) ??
        screen.getByLabelText(/email/i)
      ).toBeInTheDocument();
    });

    it('renders password input field', () => {
      render(<LoginPage />);
      expect(
        screen.getByLabelText(/password/i) ??
        screen.getByPlaceholderText(/password/i)
      ).toBeInTheDocument();
    });

    it('renders a submit button', () => {
      render(<LoginPage />);
      expect(
        screen.getByRole('button', { name: /sign in|log in|login|submit/i })
      ).toBeInTheDocument();
    });

    it('renders a link to the signup page', () => {
      render(<LoginPage />);
      expect(
        screen.getByRole('link', { name: /sign up|register|create account/i }) ??
        screen.getByText(/sign up|register|create account/i)
      ).toBeInTheDocument();
    });

  });

  // ── Validation ─────────────────────────────────────────────────────

  describe('validation', () => {

    it('shows validation feedback when submitted with empty fields', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);
      await user.click(
        screen.getByRole('button', { name: /sign in|log in|login|submit/i })
      );
      await waitFor(() => {
        // Accept any validation feedback: aria-invalid, error text, or toast
        const hasError =
          document.querySelector(':invalid') !== null ||
          document.querySelector('[aria-invalid="true"]') !== null ||
          screen.queryByText(/required|invalid|enter your/i) !== null;
        expect(hasError).toBe(true);
      });
    });

  });

  // ── Successful login ───────────────────────────────────────────────

  describe('successful login', () => {

    it('stores access_token in localStorage after successful login', async () => {
      clearAuthSession();
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailField =
        screen.queryByLabelText(/email/i) ??
        screen.queryByPlaceholderText(/email/i) as HTMLElement;
      const passwordField =
        screen.queryByLabelText(/password/i) ??
        screen.queryByPlaceholderText(/password/i) as HTMLElement;

      if (emailField) await user.type(emailField, 'student@test.com');
      if (passwordField) await user.type(passwordField, 'TestPassword123!');

      await user.click(
        screen.getByRole('button', { name: /sign in|log in|login|submit/i })
      );

      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe(
          'mock-jwt-token-for-testing-only'
        );
      });
    });

  });

  // ── Failed login ───────────────────────────────────────────────────

  describe('failed login', () => {

    it('shows error feedback when login returns 401', async () => {
      server.use(
        http.post(`${API_BASE}/auth/login`, () =>
          HttpResponse.json(
            { success: false, error: 'Invalid credentials' },
            { status: 401 }
          )
        )
      );
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailField =
        screen.queryByLabelText(/email/i) ??
        screen.queryByPlaceholderText(/email/i) as HTMLElement;
      const passwordField =
        screen.queryByLabelText(/password/i) ??
        screen.queryByPlaceholderText(/password/i) as HTMLElement;

      if (emailField) await user.type(emailField, 'wrong@test.com');
      if (passwordField) await user.type(passwordField, 'WrongPass!');

      await user.click(
        screen.getByRole('button', { name: /sign in|log in|login|submit/i })
      );

      await waitFor(() => {
        const hasError =
          screen.queryByText(/invalid|error|failed|incorrect|wrong/i) !==
            null ||
          screen.queryByRole('alert') !== null;
        expect(hasError).toBe(true);
      });
    });

    it('does not store token when login fails', async () => {
      server.use(
        http.post(`${API_BASE}/auth/login`, () =>
          HttpResponse.json(
            { success: false, error: 'Invalid credentials' },
            { status: 401 }
          )
        )
      );
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailField =
        screen.queryByLabelText(/email/i) ??
        screen.queryByPlaceholderText(/email/i) as HTMLElement;
      const passwordField =
        screen.queryByLabelText(/password/i) ??
        screen.queryByPlaceholderText(/password/i) as HTMLElement;

      if (emailField) await user.type(emailField, 'wrong@test.com');
      if (passwordField) await user.type(passwordField, 'WrongPass!');

      await user.click(
        screen.getByRole('button', { name: /sign in|log in|login|submit/i })
      );

      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBeNull();
      });
    });

  });

});
