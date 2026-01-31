import { Badge } from '@/app/components/ui/badge';
import { Progress } from '@/app/components/ui/progress';
import { Card } from '@/app/components/ui/card';
import { getMatchScoreColor, getMatchScoreLabel, formatPercentage } from '@/utils/helpers';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { Match } from '@/types/models';

interface MatchScoreCardProps {
  match: Match;
  onClick?: () => void;
}

export function MatchScoreCard({ match, onClick }: MatchScoreCardProps) {
  const scoreColor = getMatchScoreColor(match.overallScore);
  const scoreLabel = getMatchScoreLabel(match.overallScore);

  return (
    <Card
      className="p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      {/* Overall Score */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-3xl font-bold">
            {formatPercentage(match.overallScore, 0)}
          </div>
          <Badge className={scoreColor}>{scoreLabel} Match</Badge>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">Match Score</div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="space-y-3">
        <ScoreBar
          label="Skills"
          score={match.skillScore}
          icon={<CheckCircle className="size-4" />}
        />
        <ScoreBar
          label="Experience"
          score={match.experienceScore}
          icon={<AlertCircle className="size-4" />}
        />
        <ScoreBar
          label="Semantic"
          score={match.semanticScore}
          icon={<CheckCircle className="size-4" />}
        />
      </div>

      {/* Skills Overview */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1 text-green-600">
            <CheckCircle className="size-4" />
            <span>{match.matchedSkills.length} matched</span>
          </div>
          <div className="flex items-center gap-1 text-red-600">
            <XCircle className="size-4" />
            <span>{match.missingSkills.length} missing</span>
          </div>
        </div>
      </div>
    </Card>
  );
}

interface ScoreBarProps {
  label: string;
  score: number;
  icon?: React.ReactNode;
}

function ScoreBar({ label, score, icon }: ScoreBarProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2 text-sm">
          {icon}
          <span className="font-medium">{label}</span>
        </div>
        <span className="text-sm text-gray-600">
          {formatPercentage(score, 0)}
        </span>
      </div>
      <Progress value={score * 100} className="h-2" />
    </div>
  );
}
