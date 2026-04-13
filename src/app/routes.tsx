import { createBrowserRouter } from 'react-router';
import { lazy, Suspense } from 'react';
import { RootLayout } from '@/app/layouts/RootLayout';
import { LandingPage } from '@/app/pages/LandingPage';
import { StudentDashboard } from '@/app/pages/student/StudentDashboard';
import { RecruiterDashboard } from '@/app/pages/recruiter/RecruiterDashboard';
import { LoginPage } from '@/app/pages/auth/LoginPage';
import { SignupPage } from '@/app/pages/auth/SignupPage';
import { NotFoundPage } from '@/app/pages/NotFoundPage';

const ResumeAnalysisPage = lazy(() => import('@/app/pages/student/ResumeAnalysisPage'));

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
        path: 'student/resume/:resumeId/analysis',
        element: (
          <Suspense fallback={
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
          }>
            <ResumeAnalysisPage />
          </Suspense>
        ),
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
