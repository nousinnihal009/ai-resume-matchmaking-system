import { Link } from 'react-router';
import { Button } from '@/app/components/ui/button';
import { AlertCircle } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <AlertCircle className="size-16 text-gray-400 mx-auto mb-4" />
        <h1 className="text-4xl font-bold mb-2">404</h1>
        <p className="text-xl text-gray-600 mb-6">Page not found</p>
        <Link to="/">
          <Button>Go Home</Button>
        </Link>
      </div>
    </div>
  );
}
