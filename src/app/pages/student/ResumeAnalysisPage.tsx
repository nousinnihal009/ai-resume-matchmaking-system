/**
 * Full-page resume analysis at /student/resume/:resumeId/analysis
 *
 * Layout:
 *   ┌─────────────────────────────────────────────────────┐
 *   │  ← Back to Dashboard        Resume Analysis         │
 *   ├──────────────┬──────────────────────────────────────┤
 *   │              │                                       │
 *   │  SCORE CARD  │  CONTENT          (expandable card)  │
 *   │    140px     │  SECTIONS         (expandable card)  │
 *   │   circular   │  ATS ESSENTIALS   (expandable card)  │
 *   │   gauge      │  DESIGN           (expandable card)  │
 *   │              │  SKILLS           (expandable card)  │
 *   │  CATEGORY    │  TAILORING        (interactive card) │
 *   │  BREAKDOWN   │                                       │
 *   │  (bars)      │                                       │
 *   │              │                                       │
 *   │  Re-analyze  │                                       │
 *   │  button      │                                       │
 *   └──────────────┴──────────────────────────────────────┘
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import {
  ArrowLeft, RefreshCw, FileText, Shield,
  Layout, Zap, Target, Briefcase,
  CheckCircle, XCircle, AlertCircle,
  Copy, ChevronRight,
} from 'lucide-react';
import { toast } from 'sonner';
import { resumeAnalysisAPI } from '@/services/api/apiService';
import type { ResumeAnalysisReport, TailoringReport } from '@/types/models';
import {
  ScoreGauge,
  CategoryScoreBar,
  SectionCard,
} from '@/app/components/analysis';
import { TailoringResults } from '@/app/components/analysis/TailoringResults';
import { Button } from '@/app/components/ui/button';
import { Textarea } from '@/app/components/ui/textarea';
import { Badge } from '@/app/components/ui/badge';
import { Separator } from '@/app/components/ui/separator';
import { cn } from '@/app/components/ui/utils';

export default function ResumeAnalysisPage() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  const [report, setReport] = useState<ResumeAnalysisReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('content');

  // Tailoring state
  const [jobDescription, setJobDescription] = useState('');
  const [tailoring, setTailoring] = useState<TailoringReport | null>(null);
  const [isTailoring, setIsTailoring] = useState(false);

  // Load existing report on mount
  useEffect(() => {
    if (!resumeId) return;
    loadReport();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumeId]);

  async function loadReport() {
    setIsLoading(true);
    setError(null);
    try {
      // Try to get cached report first
      const result = await resumeAnalysisAPI.getReport(resumeId!);
      if (result.success && result.data) {
        setReport(result.data);
      } else {
        // No report yet — trigger analysis automatically
        await runAnalysis(false);
      }
    } catch {
      await runAnalysis(false);
    } finally {
      setIsLoading(false);
    }
  }

  async function runAnalysis(forceRefresh: boolean) {
    setIsAnalyzing(true);
    setError(null);
    try {
      const result = await resumeAnalysisAPI.runAnalysis(
        resumeId!, forceRefresh
      );
      if (result.success && result.data) {
        setReport(result.data);
        if (forceRefresh) {
          toast.success('Analysis refreshed successfully');
        }
      } else {
        setError(result.error || 'Analysis failed. Please try again.');
      }
    } catch {
      setError('Unable to run analysis. Check your connection.');
    } finally {
      setIsAnalyzing(false);
      setIsLoading(false);
    }
  }

  async function handleTailor() {
    if (!jobDescription.trim() || jobDescription.length < 50) {
      toast.error('Please paste a job description (minimum 50 characters)');
      return;
    }
    setIsTailoring(true);
    try {
      const result = await resumeAnalysisAPI.tailorResume(
        resumeId!, jobDescription
      );
      if (result.success && result.data) {
        setTailoring(result.data);
        toast.success('Tailoring analysis complete!');
      } else {
        toast.error(result.error || 'Tailoring failed. Try again.');
      }
    } catch {
      toast.error('Tailoring service unavailable. Try again.');
    } finally {
      setIsTailoring(false);
    }
  }

  function scrollToSection(id: string) {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }

  // ── Loading state ──────────────────────────────────────────────────
  if (isLoading || isAnalyzing) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-4">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-600 font-medium">
          {isAnalyzing
            ? 'Analyzing your resume with AI...'
            : 'Loading analysis...'}
        </p>
        <p className="text-sm text-gray-400">
          This may take 10-15 seconds on first run
        </p>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────────────
  if (error && !report) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-4">
        <XCircle className="w-12 h-12 text-red-500" />
        <p className="text-gray-800 font-semibold">{error}</p>
        <Button onClick={() => runAnalysis(false)}>
          Try Again
        </Button>
        <Button variant="ghost" onClick={() => navigate(-1)}>
          ← Back
        </Button>
      </div>
    );
  }

  if (!report) return null;

  const categories = Object.entries(report.score_breakdown || {});

  // ── Main layout ────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50">

      {/* Top bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          <button
            onClick={() => navigate('/student')}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-sm font-semibold text-gray-800">
            Resume Analysis
          </h1>
          <Button
            size="sm"
            variant="outline"
            onClick={() => runAnalysis(true)}
            disabled={isAnalyzing}
            className="gap-2"
          >
            <RefreshCw className={cn(
              'w-3.5 h-3.5',
              isAnalyzing && 'animate-spin'
            )} />
            Re-analyze
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8 items-start">

          {/* ── LEFT SIDEBAR (sticky) ────────────────────────────── */}
          <aside className="w-72 flex-shrink-0 sticky top-20 hidden lg:block">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 flex flex-col gap-5">

              {/* Score gauge */}
              <div className="flex flex-col items-center gap-1">
                <ScoreGauge score={report.overall_score} />
                <p className="text-sm text-gray-500 mt-2 text-center">
                  {report.total_issues} issue{report.total_issues !== 1 ? 's' : ''} found
                </p>
              </div>

              <Separator />

              {/* Category breakdown */}
              <div className="flex flex-col gap-1">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                  Score Breakdown
                </p>
                {categories.map(([key, cat]) => (
                  <CategoryScoreBar
                    key={key}
                    label={key}
                    score={cat.score}
                    weight={cat.weight}
                    active={activeSection === key}
                    onClick={() => scrollToSection(key)}
                  />
                ))}
              </div>

              <Separator />

              {/* Analyzed at */}
              <p className="text-xs text-gray-400 text-center">
                Analyzed {new Date(report.analyzed_at).toLocaleDateString()}
              </p>
            </div>
          </aside>

          {/* ── RIGHT PANEL ──────────────────────────────────────── */}
          <main className="flex-1 min-w-0 flex flex-col gap-5">

            {/* ── CONTENT SECTION ──────────────────────────────── */}
            <SectionCard
              id="content"
              title="Content"
              score={report.content?.score ?? 0}
              issueCount={
                (report.content?.repetition?.issue_count ?? 0) +
                (report.content?.spelling_grammar?.spelling_errors?.length ?? 0) +
                (report.content?.spelling_grammar?.grammar_errors?.length ?? 0)
              }
              icon={<FileText className="w-5 h-5" />}
              defaultOpen={true}
            >
              <div className="flex flex-col gap-6 pt-4">

                {/* ATS Parse Rate */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">
                      ATS Parse Rate
                    </span>
                    <span className={cn(
                      'text-sm font-bold',
                      (report.content?.ats_parse_rate ?? 0) >= 85
                        ? 'text-green-600' : 'text-amber-600'
                    )}>
                      {report.content?.ats_parse_rate ?? 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div
                      className={cn(
                        'h-3 rounded-full transition-all duration-700',
                        (report.content?.ats_parse_rate ?? 0) >= 85
                          ? 'bg-green-500' : 'bg-amber-500'
                      )}
                      style={{
                        width: `${report.content?.ats_parse_rate ?? 0}%`
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {(report.content?.ats_parse_rate ?? 0) >= 85
                      ? '✓ Great! Most ATS systems can parse your resume.'
                      : 'Consider simplifying formatting for better ATS compatibility.'}
                  </p>
                </div>

                {/* Quantifying Impact */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">
                      Quantifying Impact
                    </span>
                    {report.content?.quantification?.has_impact_metrics
                      ? <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">No issues</span>
                      : <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">Needs improvement</span>
                    }
                  </div>
                  {(report.content?.quantification?.quantified_achievements?.length ?? 0) > 0 && (
                    <div className="space-y-1 mb-2">
                      {report.content!.quantification.quantified_achievements
                        .slice(0, 3).map((a, i) => (
                        <p key={i} className="text-xs text-gray-600 bg-green-50 p-2 rounded flex gap-2">
                          <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0 mt-0.5" />
                          {a}
                        </p>
                      ))}
                    </div>
                  )}
                  {report.content?.quantification?.suggestion && (
                    <p className="text-xs text-amber-700 bg-amber-50 p-2 rounded">
                      💡 {report.content.quantification.suggestion}
                    </p>
                  )}
                </div>

                {/* Repetition */}
                {(report.content?.repetition?.issue_count ?? 0) > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-gray-700">
                        Repetition
                      </span>
                      <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                        {report.content!.repetition.issue_count} issues
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mb-3">
                      Using the same words repeatedly can be perceived as poor
                      language skills. Try synonyms instead.
                    </p>
                    <div className="flex flex-col gap-2">
                      {report.content!.repetition.issues.map((issue, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-3 p-3 bg-red-50 rounded-lg"
                        >
                          <div className="flex-1">
                            <span className="text-sm font-medium text-red-800">
                              {issue.count}x: &quot;{issue.word}&quot;
                            </span>
                            {issue.suggestions.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                <span className="text-xs text-gray-500">
                                  try replacing with:
                                </span>
                                {issue.suggestions.map((s, j) => (
                                  <span
                                    key={j}
                                    className="text-xs bg-white border border-gray-200 text-gray-700 px-2 py-0.5 rounded cursor-pointer hover:bg-gray-50"
                                    onClick={() => {
                                      navigator.clipboard.writeText(s);
                                      toast.success(`Copied "${s}"`);
                                    }}
                                  >
                                    {s}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Spelling & Grammar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">
                      Spelling & Grammar
                    </span>
                    {(report.content?.spelling_grammar?.spelling_errors?.length ?? 0) === 0
                      ? <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">No issues</span>
                      : <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                          {report.content!.spelling_grammar.spelling_errors.length} errors
                        </span>
                    }
                  </div>
                  {report.content?.spelling_grammar?.language_feedback && (
                    <p className="text-xs text-gray-500 mb-2">
                      {report.content.spelling_grammar.language_feedback}
                    </p>
                  )}
                  {report.content?.spelling_grammar?.spelling_errors?.map((err, i) => (
                    <div key={i} className="flex items-center gap-2 p-2 bg-red-50 rounded mb-1">
                      <XCircle className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
                      <span className="text-xs text-red-800 line-through">{err.word}</span>
                      <ChevronRight className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-green-700 font-medium">{err.suggestion}</span>
                    </div>
                  ))}
                </div>

                {/* AI Content Quality */}
                {(report.content?.content_quality?.strengths?.length ?? 0) > 0 && (
                  <div>
                    <span className="text-sm font-semibold text-gray-700 block mb-2">
                      AI Content Assessment
                    </span>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs font-medium text-green-700 mb-1">
                          ✓ Strengths
                        </p>
                        {report.content!.content_quality.strengths.map((s, i) => (
                          <p key={i} className="text-xs text-gray-600 mb-1">• {s}</p>
                        ))}
                      </div>
                      <div>
                        <p className="text-xs font-medium text-red-700 mb-1">
                          ✗ Weaknesses
                        </p>
                        {report.content!.content_quality.weaknesses.map((w, i) => (
                          <p key={i} className="text-xs text-gray-600 mb-1">• {w}</p>
                        ))}
                      </div>
                    </div>
                    {report.content!.content_quality.suggestions?.map((s, i) => (
                      <p key={i} className="text-xs text-blue-700 bg-blue-50 p-2 rounded mt-2">
                        💡 {s}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </SectionCard>

            {/* ── SECTIONS SECTION ─────────────────────────────── */}
            <SectionCard
              id="sections"
              title="Sections"
              score={report.score_breakdown?.sections?.score ?? 0}
              issueCount={report.sections?.missing?.length ?? 0}
              icon={<Layout className="w-5 h-5" />}
            >
              <div className="pt-4">
                <p className="text-sm text-gray-500 mb-4">
                  Essential sections help recruiters and ATS systems
                  navigate your resume quickly.
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {['experience', 'education', 'skills', 'summary', 'contact'].map(
                    section => {
                      const present = report.sections?.present?.includes(section);
                      return (
                        <div
                          key={section}
                          className={cn(
                            'flex items-center gap-2 p-3 rounded-lg',
                            present ? 'bg-green-50' : 'bg-red-50'
                          )}
                        >
                          {present
                            ? <CheckCircle className="w-4 h-4 text-green-500" />
                            : <XCircle className="w-4 h-4 text-red-500" />
                          }
                          <span className={cn(
                            'text-sm font-medium capitalize',
                            present ? 'text-green-800' : 'text-red-800'
                          )}>
                            {section}
                          </span>
                        </div>
                      );
                    }
                  )}
                </div>
                {(report.sections?.optional_present?.length ?? 0) > 0 && (
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 mb-2 font-medium">
                      Optional sections found:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {report.sections!.optional_present.map(s => (
                        <Badge key={s} variant="secondary" className="capitalize text-xs">
                          {s}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </SectionCard>

            {/* ── ATS ESSENTIALS SECTION ───────────────────────── */}
            <SectionCard
              id="ats_essentials"
              title="ATS Essentials"
              score={report.ats_essentials?.score ?? 0}
              issueCount={
                (report.ats_essentials?.file_analysis?.issues?.length ?? 0) +
                (report.ats_essentials?.contact_info?.missing?.length ?? 0)
              }
              icon={<Shield className="w-5 h-5" />}
            >
              <div className="flex flex-col gap-5 pt-4">

                {/* File Format */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">
                    File Format & Size
                  </h4>
                  <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-800">
                        {report.ats_essentials?.file_analysis?.format || 'Unknown'} format
                      </p>
                      <p className="text-xs text-gray-500">
                        {report.ats_essentials?.file_analysis?.size_kb}KB
                      </p>
                    </div>
                    {report.ats_essentials?.file_analysis?.ats_compatible
                      ? <CheckCircle className="w-5 h-5 text-green-500" />
                      : <AlertCircle className="w-5 h-5 text-amber-500" />
                    }
                  </div>
                  {report.ats_essentials?.file_analysis?.issues?.map((issue, i) => (
                    <p key={i} className="text-xs text-amber-700 bg-amber-50 p-2 rounded mt-2">
                      ⚠ {issue}
                    </p>
                  ))}
                  <p className="text-xs text-gray-500 mt-2 italic">
                    {report.ats_essentials?.file_analysis?.recommendation}
                  </p>
                </div>

                {/* Contact Information */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">
                    Contact Information
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(
                      report.ats_essentials?.contact_info?.found ?? {}
                    ).map(([field, info]) => (
                      <div
                        key={field}
                        className={cn(
                          'flex items-center gap-2 p-2.5 rounded-lg text-xs',
                          info.present ? 'bg-green-50' : 'bg-gray-50'
                        )}
                      >
                        {info.present
                          ? <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
                          : <XCircle className="w-3.5 h-3.5 text-gray-300 flex-shrink-0" />
                        }
                        <div>
                          <p className={cn(
                            'font-medium capitalize',
                            info.present ? 'text-green-800' : 'text-gray-400'
                          )}>
                            {field}
                          </p>
                          {info.present && (info.masked || info.value) && (
                            <p className="text-gray-500 truncate max-w-24">
                              {info.masked || info.value}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </SectionCard>

            {/* ── DESIGN SECTION ───────────────────────────────── */}
            <SectionCard
              id="design"
              title="Design & Layout"
              score={report.design?.score ?? 0}
              issueCount={report.design?.feedback?.length ?? 0}
              icon={<Zap className="w-5 h-5" />}
            >
              <div className="flex flex-col gap-5 pt-4">
                {report.design?.feedback?.map((fb, i) => (
                  <p key={i} className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                    💡 {fb}
                  </p>
                ))}

                {/* Template suggestions */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">
                    Recommended Templates
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {report.design?.template_suggestions?.map((tpl, i) => (
                      <div
                        key={i}
                        className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
                      >
                        <div className="flex items-start justify-between mb-1">
                          <p className="text-sm font-semibold text-gray-800">
                            {tpl.name}
                          </p>
                          {tpl.ats_friendly && (
                            <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded text-nowrap">
                              ATS ✓
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mb-1">
                          {tpl.description}
                        </p>
                        <p className="text-xs text-blue-600">
                          Best for: {tpl.best_for}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </SectionCard>

            {/* ── SKILLS SECTION ───────────────────────────────── */}
            <SectionCard
              id="skills"
              title="Skills"
              score={report.skills_analysis?.score ?? 0}
              issueCount={
                (report.skills_analysis?.score ?? 0) < 60 ? 1 : 0
              }
              icon={<Target className="w-5 h-5" />}
            >
              <div className="pt-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-semibold text-gray-700">
                      Technical Skill Density
                    </p>
                    <p className="text-xs text-gray-500">
                      {report.skills_analysis?.density} distinct technical
                      skills detected
                    </p>
                  </div>
                  <span className={cn(
                    'text-2xl font-bold',
                    (report.skills_analysis?.score ?? 0) >= 75
                      ? 'text-green-600'
                      : (report.skills_analysis?.score ?? 0) >= 50
                      ? 'text-amber-600'
                      : 'text-red-600'
                  )}>
                    {report.skills_analysis?.score}/100
                  </span>
                </div>
                {(report.skills_analysis?.density ?? 0) < 8 && (
                  <p className="text-xs text-amber-700 bg-amber-50 p-3 rounded-lg mt-3">
                    💡 Add more technical skills to your resume. Aim for
                    10-15 relevant technologies, frameworks, and tools
                    for your target role.
                  </p>
                )}
              </div>
            </SectionCard>

            {/* ── TAILORING SECTION ────────────────────────────── */}
            <SectionCard
              id="tailoring"
              title="Resume Tailoring"
              score={tailoring?.tailoring_score ?? 0}
              issueCount={tailoring?.top_3_gaps?.length ?? 0}
              icon={<Briefcase className="w-5 h-5" />}
              defaultOpen={true}
            >
              <div className="flex flex-col gap-5 pt-4">
                {!tailoring ? (
                  <div className="flex flex-col gap-5 pt-4">
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
                      <h4 className="text-sm font-semibold text-gray-800 mb-1">
                        Tailor Your Resume for a Specific Job
                      </h4>
                      <p className="text-sm text-gray-500 mb-4">
                        Paste the job description below. Our AI will analyze the fit,
                        identify missing keywords, suggest bullet rewrites, and
                        generate a tailored professional summary — all specific to
                        this role.
                      </p>
                      <Textarea
                        placeholder="Paste the full job description here...&#10;(e.g. We are looking for a Senior Python Engineer with experience in&#10;FastAPI, PostgreSQL, and microservices architecture...)"
                        value={jobDescription}
                        onChange={e => setJobDescription(e.target.value)}
                        className="min-h-40 text-sm resize-none bg-white mb-3"
                      />
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-gray-400">
                          {jobDescription.length} characters
                          {jobDescription.length < 50 && jobDescription.length > 0
                            ? ' — need at least 50'
                            : ''}
                        </p>
                        <Button
                          onClick={handleTailor}
                          disabled={isTailoring || jobDescription.length < 50}
                          className="gap-2"
                        >
                          {isTailoring ? (
                            <>
                              <RefreshCw className="w-4 h-4 animate-spin" />
                              Analyzing fit...
                            </>
                          ) : (
                            <>
                              <Zap className="w-4 h-4" />
                              Get Tailored Insights
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="pt-4">
                    <TailoringResults
                      tailoring={tailoring}
                      templateSuggestions={
                        report?.design?.template_suggestions ?? []
                      }
                      onReset={() => {
                        setTailoring(null);
                        setJobDescription('');
                      }}
                    />
                  </div>
                )}
              </div>
            </SectionCard>

          </main>
        </div>
      </div>
    </div>
  );
}

