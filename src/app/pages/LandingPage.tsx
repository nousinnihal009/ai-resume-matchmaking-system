import { Link } from 'react-router';
import { Button } from '@/app/components/ui/button';
import { BrainCircuit, Users, Target, Zap, Shield, TrendingUp } from 'lucide-react';

export function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BrainCircuit className="size-8 text-blue-600" />
            <span className="font-bold text-xl">AI Resume Matcher</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link to="/signup">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-b from-blue-50 to-white">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            AI-Powered Resume & Internship Matching
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Connect talented students with leading companies using advanced machine learning
            and semantic matching technology. Find your perfect match in seconds.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/signup">
              <Button size="lg" className="px-8">
                Start Matching
              </Button>
            </Link>
            <Button size="lg" variant="outline">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Intelligent Matching Technology
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<BrainCircuit className="size-8 text-blue-600" />}
              title="AI-Powered Analysis"
              description="Advanced NLP extracts skills, experience, and qualifications from resumes and job descriptions automatically."
            />
            <FeatureCard
              icon={<Target className="size-8 text-green-600" />}
              title="Semantic Matching"
              description="Vector embeddings find the best candidate-role matches beyond simple keyword matching."
            />
            <FeatureCard
              icon={<Zap className="size-8 text-yellow-600" />}
              title="Real-Time Results"
              description="Get instant match scores and explanations powered by our high-performance ML pipeline."
            />
            <FeatureCard
              icon={<Shield className="size-8 text-purple-600" />}
              title="Secure & Private"
              description="Enterprise-grade security with role-based access control and data encryption."
            />
            <FeatureCard
              icon={<Users className="size-8 text-indigo-600" />}
              title="Dual Dashboard"
              description="Separate optimized experiences for students and recruiters with intuitive interfaces."
            />
            <FeatureCard
              icon={<TrendingUp className="size-8 text-red-600" />}
              title="Analytics & Insights"
              description="Track matching performance, skill trends, and hiring metrics with detailed analytics."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-2 gap-12">
            {/* For Students */}
            <div className="bg-white p-8 rounded-lg shadow-sm">
              <h3 className="text-2xl font-bold mb-6">For Students</h3>
              <ol className="space-y-4">
                <li className="flex gap-4">
                  <span className="flex-shrink-0 size-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                    1
                  </span>
                  <div>
                    <p className="font-semibold">Upload Your Resume</p>
                    <p className="text-gray-600">Upload your resume in PDF or DOCX format</p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 size-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                    2
                  </span>
                  <div>
                    <p className="font-semibold">AI Analyzes Your Profile</p>
                    <p className="text-gray-600">Our ML pipeline extracts skills and experience</p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 size-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                    3
                  </span>
                  <div>
                    <p className="font-semibold">Get Matched Opportunities</p>
                    <p className="text-gray-600">See ranked internships with match scores</p>
                  </div>
                </li>
              </ol>
            </div>

            {/* For Recruiters */}
            <div className="bg-white p-8 rounded-lg shadow-sm">
              <h3 className="text-2xl font-bold mb-6">For Recruiters</h3>
              <ol className="space-y-4">
                <li className="flex gap-4">
                  <span className="flex-shrink-0 size-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold">
                    1
                  </span>
                  <div>
                    <p className="font-semibold">Post Job Descriptions</p>
                    <p className="text-gray-600">Create detailed internship postings</p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 size-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold">
                    2
                  </span>
                  <div>
                    <p className="font-semibold">AI Matches Candidates</p>
                    <p className="text-gray-600">Automatic semantic matching with all resumes</p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 size-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold">
                    3
                  </span>
                  <div>
                    <p className="font-semibold">Review Top Candidates</p>
                    <p className="text-gray-600">Get ranked candidates with detailed explanations</p>
                  </div>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Transform Your Hiring Process?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join hundreds of students and recruiters using AI to find perfect matches.
          </p>
          <Link to="/signup">
            <Button size="lg" variant="secondary" className="px-8">
              Get Started Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <BrainCircuit className="size-6" />
                <span className="font-bold">AI Resume Matcher</span>
              </div>
              <p className="text-gray-400 text-sm">
                Production-ready ML platform for intelligent resume and job matching.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Features</li>
                <li>Pricing</li>
                <li>Demo</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>About</li>
                <li>Careers</li>
                <li>Contact</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Documentation</li>
                <li>API</li>
                <li>Support</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2025 AI Resume Matcher. Built for placements and technical interviews.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
