"""
Full tailoring results display.

Layout (4 sections, visually separated):
  1. HEADER — fit score ring + fit label + explanation + reset button
  2. KEYWORD ANALYSIS — gap ring + keyword cloud (missing vs present)
  3. REWRITES — bullet rewrite cards (before/after side by side)
  4. SUMMARY & TEMPLATES — tailored summary + template showcase
"""
import { RotateCcw } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Separator } from '@/app/components/ui/separator';
import type { TailoringReport } from '@/types/models';
import { KeywordGapRing } from './KeywordGapRing';
import { KeywordCloud } from './KeywordCloud';
import { BulletRewriteCard } from './BulletRewriteCard';
import { TemplateShowcase } from './TemplateShowcase';
import { TailoredSummaryCard } from './TailoredSummaryCard';
import { GapAnalysisBar } from './GapAnalysisBar';
import { cn } from '@/app/components/ui/utils';

interface TailoringResultsProps {
  tailoring: TailoringReport;
  templateSuggestions?: Array<{
    name: string;
    description: string;
    best_for: string;
    ats_friendly: boolean;
  }>;
  onReset: () => void;
}

export function TailoringResults({
  tailoring,
  templateSuggestions = [],
  onReset,
}: TailoringResultsProps) {

  const fitBgColor = tailoring.overall_fit === 'strong'
    ? 'bg-green-50 border-green-200'
    : tailoring.overall_fit === 'moderate'
    ? 'bg-amber-50 border-amber-200'
    : 'bg-red-50 border-red-200';

  const fitTextColor = tailoring.overall_fit === 'strong'
    ? 'text-green-700'
    : tailoring.overall_fit === 'moderate'
    ? 'text-amber-700'
    : 'text-red-700';

  return (
    <div className="flex flex-col gap-8">

      {/* ── SECTION 1: Header / Fit Score ──────────────────────── */}
      <div className={cn(
        'flex flex-col sm:flex-row items-center gap-6 p-5 rounded-xl border',
        fitBgColor
      )}>
        <KeywordGapRing score={tailoring.tailoring_score} size={110} />
        <div className="flex-1 text-center sm:text-left">
          <p className={cn(
            'text-lg font-bold capitalize mb-1',
            fitTextColor
          )}>
            {tailoring.overall_fit} Match
          </p>
          <p className="text-sm text-gray-600 leading-relaxed">
            {tailoring.fit_explanation}
          </p>
          {tailoring.source === 'rule_based' && (
            <p className="text-xs text-gray-400 mt-2 italic">
              ℹ Analysis powered by keyword matching.
              Add GEMINI_API_KEY for deep AI analysis.
            </p>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={onReset}
          className="flex-shrink-0 gap-2"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Try Another Job
        </Button>
      </div>

      {/* ── SECTION 2: Critical Gaps ────────────────────────────── */}
      {tailoring.top_3_gaps?.length > 0 && (
        <div>
          <GapAnalysisBar gaps={tailoring.top_3_gaps} />
        </div>
      )}

      {/* ── SECTION 3: Keyword Analysis ─────────────────────────── */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <span className="w-1 h-4 bg-blue-500 rounded-full inline-block" />
          Keyword Gap Analysis
        </h4>
        <KeywordCloud
          missing={tailoring.missing_keywords || []}
          present={tailoring.keywords_present || []}
        />
      </div>

      <Separator />

      {/* ── SECTION 4: Bullet Rewrites ──────────────────────────── */}
      {tailoring.bullet_rewrites?.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span className="w-1 h-4 bg-purple-500 rounded-full inline-block" />
            Suggested Bullet Rewrites
            <span className="text-xs font-normal text-gray-400">
              ({tailoring.bullet_rewrites.length} suggestion
              {tailoring.bullet_rewrites.length !== 1 ? 's' : ''})
            </span>
          </h4>
          <div className="flex flex-col gap-4">
            {tailoring.bullet_rewrites.slice(0, 5).map((rewrite, i) => (
              <BulletRewriteCard
                key={i}
                index={i}
                original={rewrite.original}
                rewritten={rewrite.rewritten}
                reason={rewrite.reason}
              />
            ))}
          </div>
        </div>
      )}

      {/* ── SECTION 5: Skills to Highlight ──────────────────────── */}
      {tailoring.skills_to_highlight?.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span className="w-1 h-4 bg-green-500 rounded-full inline-block" />
            Skills to Highlight More Prominently
          </h4>
          <div className="flex flex-wrap gap-2">
            {tailoring.skills_to_highlight.map((skill, i) => (
              <span
                key={i}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-green-100 text-green-800 border border-green-200"
              >
                ↑ {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── SECTION 6: Sections to Add ──────────────────────────── */}
      {tailoring.sections_to_add?.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span className="w-1 h-4 bg-amber-500 rounded-full inline-block" />
            Sections to Add
          </h4>
          <div className="flex flex-col gap-2">
            {tailoring.sections_to_add.map((section, i) => (
              <p
                key={i}
                className="text-sm text-amber-800 bg-amber-50 border border-amber-200 p-3 rounded-lg"
              >
                + {section}
              </p>
            ))}
          </div>
        </div>
      )}

      <Separator />

      {/* ── SECTION 7: Tailored Summary ─────────────────────────── */}
      {tailoring.summary_rewrite && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span className="w-1 h-4 bg-indigo-500 rounded-full inline-block" />
            Tailored Professional Summary
          </h4>
          <TailoredSummaryCard summary={tailoring.summary_rewrite} />
        </div>
      )}

      {/* ── SECTION 8: Template Recommendations ─────────────────── */}
      {templateSuggestions.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span className="w-1 h-4 bg-gray-500 rounded-full inline-block" />
            Recommended Templates for This Role
          </h4>
          <TemplateShowcase templates={templateSuggestions} />
        </div>
      )}

    </div>
  );
}
