import { createBrowserRouter } from 'react-router';
import { RootLayout } from '@/app/layouts/RootLayout';
import { LandingPage } from '@/app/pages/LandingPage';
import { StudentDashboard } from '@/app/pages/student/StudentDashboard';
import { RecruiterDashboard } from '@/app/pages/recruiter/RecruiterDashboard';
import { LoginPage } from '@/app/pages/auth/LoginPage';
import { SignupPage } from '@/app/pages/auth/SignupPage';
import { NotFoundPage } from '@/app/pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: RootLayout,
    children: [
      {
        index: true,
        Component: LandingPage,
      },
      {
        path: 'login',
        Component: LoginPage,
      },
      {
        path: 'signup',
        Component: SignupPage,
      },
      {
        path: 'student',
        Component: StudentDashboard,
      },
      {
        path: 'recruiter',
        Component: RecruiterDashboard,
      },
      {
        path: '*',
        Component: NotFoundPage,
      },
    ],
  },
]);
