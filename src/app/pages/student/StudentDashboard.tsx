import { useState, useRef } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '@/contexts/AuthContext';
import { useResumes, useMatches } from '@/hooks/useData';
import { Button } from '@/app/components/ui/button';
import { Card } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { SkillBadgeList } from '@/app/components/SkillBadgeList';
import { MatchScoreCard } from '@/app/components/MatchScoreCard';
import {
  Upload,
  FileText,
  LogOut,
  Briefcase,
  TrendingUp,
  Loader2,
  BrainCircuit,
  ExternalLink,
  MapPin,
  Building,
  DollarSign,
} from 'lucide-react';
import { validateResumeFile } from '@/utils/validation';
import { formatDate, formatFileSize, formatSalary } from '@/utils/helpers';
import { toast } from 'sonner';
import type { Match, Job, Resume } from '@/types/models';
import { dataStore } from '@/services/api/mockData';

export function StudentDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { resumes, isLoading: resumesLoading, uploadResume } = useResumes(user?.id);
  const { matches, isLoading: matchesLoading, matchResume } = useMatches(user?.id, 'student');
  const [isUploading, setIsUploading] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file
    const validation = validateResumeFile(file);
    if (!validation.isValid) {
      toast.error(validation.error || 'Invalid file');
      return;
    }

    setIsUploading(true);
    const result = await uploadResume(file);

    if (result.success && result.data) {
      // Automatically trigger matching
      await matchResume(result.data.id);
    }

    setIsUploading(false);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  // Get jobs for displaying match details
  const getJobById = (jobId: string): Job | undefined => {
    return dataStore.jobs.get(jobId);
  };

  const stats = {
    resumesCount: resumes.length,
    matchesCount: matches.length,
    avgScore: matches.length > 0
      ? matches.reduce((sum, m) => sum + m.overallScore, 0) / matches.length
      : 0,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BrainCircuit className="size-8 text-blue-600" />
            <span className="font-bold text-xl">AI Resume Matcher</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, {user?.name}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="size-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold">{stats.resumesCount}</div>
                <div className="text-gray-600">Resumes Uploaded</div>
              </div>
              <FileText className="size-8 text-blue-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold">{stats.matchesCount}</div>
                <div className="text-gray-600">Matches Found</div>
              </div>
              <Briefcase className="size-8 text-green-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold">
                  {(stats.avgScore * 100).toFixed(0)}%
                </div>
                <div className="text-gray-600">Avg Match Score</div>
              </div>
              <TrendingUp className="size-8 text-purple-600" />
            </div>
          </Card>
        </div>

        <Tabs defaultValue="upload" className="space-y-6">
          <TabsList>
            <TabsTrigger value="upload">Upload Resume</TabsTrigger>
            <TabsTrigger value="matches">My Matches ({matches.length})</TabsTrigger>
            <TabsTrigger value="resumes">My Resumes ({resumes.length})</TabsTrigger>
          </TabsList>

          {/* Upload Tab */}
          <TabsContent value="upload">
            <Card className="p-8">
              <div className="text-center">
                <Upload className="size-16 mx-auto mb-4 text-gray-400" />
                <h2 className="text-2xl font-bold mb-2">Upload Your Resume</h2>
                <p className="text-gray-600 mb-6">
                  Our AI will analyze your resume and find matching internships instantly
                </p>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileSelect}
                  className="hidden"
                />

                <Button
                  size="lg"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  {isUploading && <Loader2 className="mr-2 size-4 animate-spin" />}
                  {isUploading ? 'Processing...' : 'Choose File'}
                </Button>

                <p className="text-sm text-gray-500 mt-4">
                  Supported formats: PDF, DOC, DOCX (Max 5MB)
                </p>
              </div>
            </Card>
          </TabsContent>

          {/* Matches Tab */}
          <TabsContent value="matches">
            {matchesLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="size-8 animate-spin text-gray-400" />
              </div>
            ) : matches.length === 0 ? (
              <Card className="p-12 text-center">
                <Briefcase className="size-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-semibold mb-2">No matches yet</h3>
                <p className="text-gray-600 mb-4">
                  Upload your resume to find matching internships
                </p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {matches
                  .sort((a, b) => b.overallScore - a.overallScore)
                  .map((match) => {
                    const job = getJobById(match.jobId);
                    return (
                      <div key={match.id}>
                        <Card className="p-4 mb-3">
                          <h3 className="font-semibold text-lg mb-1">{job?.title}</h3>
                          <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                            <Building className="size-4" />
                            {job?.company}
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                            <MapPin className="size-4" />
                            {job?.location} • {job?.locationType}
                          </div>
                          {job?.salary && (
                            <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                              <DollarSign className="size-4" />
                              {formatSalary(job.salary.min, job.salary.max, job.salary.currency)}
                            </div>
                          )}
                        </Card>
                        <MatchScoreCard
                          match={match}
                          onClick={() => setSelectedMatch(match)}
                        />
                      </div>
                    );
                  })}
              </div>
            )}
          </TabsContent>

          {/* Resumes Tab */}
          <TabsContent value="resumes">
            {resumesLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="size-8 animate-spin text-gray-400" />
              </div>
            ) : resumes.length === 0 ? (
              <Card className="p-12 text-center">
                <FileText className="size-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-semibold mb-2">No resumes uploaded</h3>
                <p className="text-gray-600">Get started by uploading your resume</p>
              </Card>
            ) : (
              <div className="space-y-4">
                {resumes.map((resume) => (
                  <ResumeCard key={resume.id} resume={resume} />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Match Detail Dialog */}
      {selectedMatch && (
        <MatchDetailDialog
          match={selectedMatch}
          job={getJobById(selectedMatch.jobId)}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  );
}

function ResumeCard({ resume }: { resume: Resume }) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="size-5 text-blue-600" />
            <h3 className="font-semibold">{resume.fileName}</h3>
          </div>
          <div className="text-sm text-gray-600 mb-4">
            Uploaded {formatDate(resume.uploadedAt)} • {formatFileSize(resume.fileSize)}
          </div>

          <div>
            <div className="text-sm font-medium mb-2">Extracted Skills:</div>
            <SkillBadgeList skills={resume.extractedSkills} maxDisplay={10} />
          </div>
        </div>
      </div>
    </Card>
  );
}

function MatchDetailDialog({
  match,
  job,
  onClose,
}: {
  match: Match;
  job?: Job;
  onClose: () => void;
}) {
  if (!job) return null;

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">{job.title}</DialogTitle>
          <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
            <div className="flex items-center gap-1">
              <Building className="size-4" />
              {job.company}
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="size-4" />
              {job.location}
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Match Summary */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Match Summary</h3>
            <p className="text-sm">{match.explanation.summary}</p>
          </div>

          {/* Strengths */}
          {match.explanation.strengths.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <span className="text-green-600">✓</span> Strengths
              </h3>
              <ul className="space-y-1 text-sm">
                {match.explanation.strengths.map((strength, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-green-600 mt-0.5">•</span>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Gaps */}
          {match.explanation.gaps.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <span className="text-red-600">!</span> Areas to Improve
              </h3>
              <ul className="space-y-1 text-sm">
                {match.explanation.gaps.map((gap, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>{gap}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Skills Breakdown */}
          <div>
            <h3 className="font-semibold mb-3">Skills Breakdown</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm font-medium text-green-700 mb-2">
                  Matched Skills ({match.matchedSkills.length})
                </div>
                <SkillBadgeList skills={match.matchedSkills} variant="success" />
              </div>
              {match.missingSkills.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-red-700 mb-2">
                    Missing Skills ({match.missingSkills.length})
                  </div>
                  <SkillBadgeList skills={match.missingSkills} variant="danger" />
                </div>
              )}
            </div>
          </div>

          {/* Job Description */}
          <div>
            <h3 className="font-semibold mb-2">Job Description</h3>
            <p className="text-sm text-gray-700 whitespace-pre-line">{job.description}</p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
