import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Card } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { BrainCircuit, Loader2 } from 'lucide-react';
import { validateEmail, validatePassword } from '@/utils/validation';

export function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState<'student' | 'recruiter'>('student');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    setErrors(prev => ({ ...prev, [field]: '' }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!validateEmail(formData.email)) {
      newErrors.email = 'Invalid email address';
    }

    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.errors[0];
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setIsLoading(true);

    const result = await signup({
      name: formData.name,
      email: formData.email,
      password: formData.password,
      confirmPassword: formData.confirmPassword,
      role,
    });

    if (result.success) {
      navigate(role === 'student' ? '/student' : '/recruiter');
    } else {
      setErrors({ form: result.error || 'Signup failed' });
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 to-white px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <BrainCircuit className="size-10 text-blue-600" />
          <span className="font-bold text-2xl">AI Resume Matcher</span>
        </div>

        <Card className="p-6">
          <h1 className="text-2xl font-bold mb-6 text-center">Create Account</h1>

          <Tabs value={role} onValueChange={(v) => setRole(v as any)} className="mb-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="student">Student</TabsTrigger>
              <TabsTrigger value="recruiter">Recruiter</TabsTrigger>
            </TabsList>

            <TabsContent value="student" className="mt-4">
              <p className="text-sm text-gray-600 text-center">
                Upload your resume and find matching internships
              </p>
            </TabsContent>

            <TabsContent value="recruiter" className="mt-4">
              <p className="text-sm text-gray-600 text-center">
                Post jobs and find qualified candidates
              </p>
            </TabsContent>
          </Tabs>

          <form onSubmit={handleSignup} className="space-y-4">
            {errors.form && (
              <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">
                {errors.form}
              </div>
            )}

            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="John Doe"
                required
              />
              {errors.name && (
                <p className="text-sm text-red-600 mt-1">{errors.name}</p>
              )}
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="your.email@example.com"
                required
              />
              {errors.email && (
                <p className="text-sm text-red-600 mt-1">{errors.email}</p>
              )}
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="••••••••"
                required
              />
              {errors.password && (
                <p className="text-sm text-red-600 mt-1">{errors.password}</p>
              )}
              <p className="text-xs text-gray-500 mt-1">
                Must be 8+ characters with uppercase, lowercase, and number
              </p>
            </div>

            <div>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                placeholder="••••••••"
                required
              />
              {errors.confirmPassword && (
                <p className="text-sm text-red-600 mt-1">{errors.confirmPassword}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 size-4 animate-spin" />}
              Create Account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:underline">
              Sign in
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
