import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Card } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { BrainCircuit, Loader2 } from 'lucide-react';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState<'student' | 'recruiter'>('student');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const result = await login({ email, password, role });

    if (result.success) {
      navigate(role === 'student' ? '/student' : '/recruiter');
    } else {
      setError(result.error || 'Login failed');
    }

    setIsLoading(false);
  };

  const handleDemoLogin = async (demoRole: 'student' | 'recruiter') => {
    setRole(demoRole);
    setEmail(
      demoRole === 'student' 
        ? 'john.doe@university.edu' 
        : 'jane.recruiter@google.com'
    );
    setPassword('demo123');
    
    // Auto-submit after a short delay
    setTimeout(() => {
      const form = document.getElementById('login-form') as HTMLFormElement;
      form?.requestSubmit();
    }, 100);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 to-white px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <BrainCircuit className="size-10 text-blue-600" />
          <span className="font-bold text-2xl">AI Resume Matcher</span>
        </div>

        <Card className="p-6">
          <h1 className="text-2xl font-bold mb-6 text-center">Sign In</h1>

          <Tabs value={role} onValueChange={(v) => setRole(v as any)} className="mb-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="student">Student</TabsTrigger>
              <TabsTrigger value="recruiter">Recruiter</TabsTrigger>
            </TabsList>

            <TabsContent value="student" className="mt-4">
              <p className="text-sm text-gray-600 text-center">
                Find your perfect internship match
              </p>
            </TabsContent>

            <TabsContent value="recruiter" className="mt-4">
              <p className="text-sm text-gray-600 text-center">
                Discover top candidates for your roles
              </p>
            </TabsContent>
          </Tabs>

          <form id="login-form" onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">
                {error}
              </div>
            )}

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                required
              />
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 size-4 animate-spin" />}
              Sign In
            </Button>
          </form>

          {/* Demo Login */}
          <div className="mt-6 pt-6 border-t">
            <p className="text-sm text-gray-600 text-center mb-3">Quick Demo Access:</p>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDemoLogin('student')}
                disabled={isLoading}
              >
                Demo Student
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDemoLogin('recruiter')}
                disabled={isLoading}
              >
                Demo Recruiter
              </Button>
            </div>
          </div>

          <p className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-600 hover:underline">
              Sign up
            </Link>
          </p>
        </Card>

        <p className="mt-4 text-center text-xs text-gray-500">
          <Link to="/" className="hover:underline">
            ← Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}
