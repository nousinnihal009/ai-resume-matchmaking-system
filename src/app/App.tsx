import { RouterProvider } from 'react-router';
import { router } from '@/app/routes';
import { Toaster } from '@/app/components/ui/sonner';
import { AuthProvider } from '@/contexts/AuthContext';

export default function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
      <Toaster />
    </AuthProvider>
  );
}