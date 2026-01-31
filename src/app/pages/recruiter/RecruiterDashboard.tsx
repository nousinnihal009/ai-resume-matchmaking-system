import { useState } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '@/contexts/AuthContext';
import { useJobs, useMatches } from '@/hooks/useData';
import { Button } from '@/app/components/ui/button';
import { Card } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Textarea } from '@/app/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { SkillBadgeList } from '@/app/components/SkillBadgeList';
import { MatchScoreCard } from '@/app/components/MatchScoreCard';
import {
  Plus,
  Briefcase,
  Users,
  TrendingUp,
  LogOut,
  BrainCircuit,
  Loader2,
  MapPin,
  Building,
  Calendar,
  FileText,
  Mail,
} from 'lucide-react';
import { formatDate, formatSalary } from '@/utils/helpers';
import { toast } from 'sonner';
import type { Job, Match, JobPostingForm, Resume } from '@/types/models';
import { dataStore } from '@/services/api/mockData';

export function RecruiterDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { jobs, isLoading: jobsLoading, createJob } = useJobs(user?.id);
  const { matches, isLoading: matchesLoading, matchJob } = useMatches(user?.id, 'recruiter');
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getResumeById = (resumeId: string): Resume | undefined => {
    return dataStore.resumes.get(resumeId);
  };

  const getUserById = (userId: string) => {
    return dataStore.users.get(userId);
  };

  const stats = {
    activeJobs: jobs.filter(j => j.status === 'active').length,
    totalCandidates: matches.length,
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
                <div className="text-3xl font-bold">{stats.activeJobs}</div>
                <div className="text-gray-600">Active Jobs</div>
              </div>
              <Briefcase className="size-8 text-blue-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold">{stats.totalCandidates}</div>
                <div className="text-gray-600">Total Candidates</div>
              </div>
              <Users className="size-8 text-green-600" />
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

        <Tabs defaultValue="jobs" className="space-y-6">
          <TabsList>
            <TabsTrigger value="jobs">My Jobs ({jobs.length})</TabsTrigger>
            <TabsTrigger value="candidates">Candidates ({matches.length})</TabsTrigger>
          </TabsList>

          {/* Jobs Tab */}
          <TabsContent value="jobs">
            <div className="mb-4">
              <Button onClick={() => setIsCreatingJob(true)}>
                <Plus className="size-4 mr-2" />
                Post New Job
              </Button>
            </div>

            {jobsLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="size-8 animate-spin text-gray-400" />
              </div>
            ) : jobs.length === 0 ? (
              <Card className="p-12 text-center">
                <Briefcase className="size-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-semibold mb-2">No jobs posted yet</h3>
                <p className="text-gray-600 mb-4">
                  Create your first job posting to find candidates
                </p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 gap-6">
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onViewCandidates={() => setSelectedJob(job)}
                    onFindMatches={() => matchJob(job.id)}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Candidates Tab */}
          <TabsContent value="candidates">
            {matchesLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="size-8 animate-spin text-gray-400" />
              </div>
            ) : matches.length === 0 ? (
              <Card className="p-12 text-center">
                <Users className="size-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-semibold mb-2">No candidates yet</h3>
                <p className="text-gray-600">
                  Post a job and find matches to see candidates here
                </p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {matches
                  .sort((a, b) => b.overallScore - a.overallScore)
                  .map((match) => {
                    const resume = getResumeById(match.resumeId);
                    const student = getUserById(match.studentId);
                    const job = dataStore.jobs.get(match.jobId);
                    
                    return (
                      <div key={match.id}>
                        <Card className="p-4 mb-3">
                          <h3 className="font-semibold text-lg mb-1">{student?.name}</h3>
                          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                            <Mail className="size-4" />
                            {student?.email}
                          </div>
                          <div className="text-sm text-gray-600 mb-3">
                            <span className="font-medium">Applied for:</span> {job?.title}
                          </div>
                          {resume && (
                            <div className="text-sm">
                              <SkillBadgeList skills={resume.extractedSkills} maxDisplay={5} />
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
        </Tabs>
      </div>

      {/* Create Job Dialog */}
      {isCreatingJob && (
        <CreateJobDialog
          onClose={() => setIsCreatingJob(false)}
          onCreate={async (data) => {
            const result = await createJob(data);
            if (result.success && result.data) {
              setIsCreatingJob(false);
              // Auto-match
              await matchJob(result.data.id);
            }
          }}
        />
      )}

      {/* Candidate Detail Dialog */}
      {selectedMatch && (
        <CandidateDetailDialog
          match={selectedMatch}
          resume={getResumeById(selectedMatch.resumeId)}
          student={getUserById(selectedMatch.studentId)}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  );
}

function JobCard({
  job,
  onViewCandidates,
  onFindMatches,
}: {
  job: Job;
  onViewCandidates: () => void;
  onFindMatches: () => void;
}) {
  const matches = Array.from(dataStore.matches.values()).filter(m => m.jobId === job.id);

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-2">{job.title}</h3>
          <div className="space-y-1 text-sm text-gray-600 mb-3">
            <div className="flex items-center gap-2">
              <Building className="size-4" />
              {job.company}
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="size-4" />
              {job.location} • {job.locationType}
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="size-4" />
              Posted {formatDate(job.postedAt)}
            </div>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm font-medium mb-2">Required Skills:</div>
        <SkillBadgeList skills={job.requiredSkills} maxDisplay={6} />
      </div>

      <div className="flex items-center justify-between pt-4 border-t">
        <div className="text-sm text-gray-600">
          {matches.length} {matches.length === 1 ? 'candidate' : 'candidates'}
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={onFindMatches}>
            Find Matches
          </Button>
          {matches.length > 0 && (
            <Button size="sm" onClick={onViewCandidates}>
              View Candidates
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}

function CreateJobDialog({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (data: JobPostingForm) => Promise<void>;
}) {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<JobPostingForm>({
    title: '',
    company: (user as any)?.company || '',
    description: '',
    requiredSkills: [],
    preferredSkills: [],
    experienceLevel: 'internship',
    location: '',
    locationType: 'hybrid',
    salaryCurrency: 'USD',
  });
  const [skillInput, setSkillInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    await onCreate(formData);
    setIsLoading(false);
  };

  const addSkill = () => {
    if (skillInput.trim()) {
      setFormData(prev => ({
        ...prev,
        requiredSkills: [...prev.requiredSkills, skillInput.trim()],
      }));
      setSkillInput('');
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Post New Job</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div>
            <Label htmlFor="title">Job Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="e.g., Software Engineering Intern"
              required
            />
          </div>

          <div>
            <Label htmlFor="company">Company</Label>
            <Input
              id="company"
              value={formData.company}
              onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
              placeholder="Company name"
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Job Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the role, responsibilities, and requirements..."
              rows={6}
              required
            />
          </div>

          <div>
            <Label htmlFor="skills">Required Skills</Label>
            <div className="flex gap-2 mb-2">
              <Input
                id="skills"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Add a skill and press Enter"
              />
              <Button type="button" onClick={addSkill}>Add</Button>
            </div>
            <SkillBadgeList skills={formData.requiredSkills} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="level">Experience Level</Label>
              <Select
                value={formData.experienceLevel}
                onValueChange={(v: any) => setFormData(prev => ({ ...prev, experienceLevel: v }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="internship">Internship</SelectItem>
                  <SelectItem value="entry">Entry Level</SelectItem>
                  <SelectItem value="mid">Mid Level</SelectItem>
                  <SelectItem value="senior">Senior Level</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="locationType">Location Type</Label>
              <Select
                value={formData.locationType}
                onValueChange={(v: any) => setFormData(prev => ({ ...prev, locationType: v }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="onsite">Onsite</SelectItem>
                  <SelectItem value="remote">Remote</SelectItem>
                  <SelectItem value="hybrid">Hybrid</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
              placeholder="e.g., San Francisco, CA"
              required
            />
          </div>

          <div className="flex gap-4 pt-4">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" className="flex-1" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 size-4 animate-spin" />}
              Post Job
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function CandidateDetailDialog({
  match,
  resume,
  student,
  onClose,
}: {
  match: Match;
  resume?: Resume;
  student?: any;
  onClose: () => void;
}) {
  if (!resume || !student) return null;

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">{student.name}</DialogTitle>
          <div className="text-sm text-gray-600 mt-2">
            {student.email}
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Match Summary */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Match Summary</h3>
            <p className="text-sm">{match.explanation.summary}</p>
          </div>

          {/* Skills */}
          <div>
            <h3 className="font-semibold mb-3">Skills</h3>
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

          {/* Resume Extract */}
          <div>
            <h3 className="font-semibold mb-2">Resume Summary</h3>
            <p className="text-sm text-gray-700 line-clamp-10">
              {resume.extractedText.substring(0, 500)}...
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
