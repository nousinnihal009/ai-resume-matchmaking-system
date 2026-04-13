import { useMemo } from 'react';

interface ScoreGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export function ScoreGauge({
  score,
  size = 140,
  strokeWidth = 12,
}: ScoreGaugeProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = useMemo(
    () => circumference - (score / 100) * circumference,
    [score, circumference]
  );

  const color = score >= 75
    ? '#22c55e'   // green-500
    : score >= 50
    ? '#f59e0b'   // amber-500
    : '#ef4444';  // red-500

  const label = score >= 75 ? 'Great' : score >= 50 ? 'Good' : 'Needs Work';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative flex items-center justify-center">
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s ease' }}
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span
            className="text-4xl font-bold"
            style={{ color }}
          >
            {score}
          </span>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            out of 100
          </span>
        </div>
      </div>
      <span
        className="text-sm font-semibold"
        style={{ color }}
      >
        {label}
      </span>
    </div>
  );
}
