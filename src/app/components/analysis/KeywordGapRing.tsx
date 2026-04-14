interface KeywordGapRingProps {
  score: number;
  size?: number;
}

export function KeywordGapRing({ score, size = 120 }: KeywordGapRingProps) {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color = score >= 70
    ? '#22c55e'
    : score >= 45
    ? '#f59e0b'
    : '#ef4444';

  const label = score >= 70
    ? 'Strong Fit'
    : score >= 45
    ? 'Moderate Fit'
    : 'Weak Fit';

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative flex items-center justify-center">
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke="#f3f4f6" strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={color} strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-2xl font-bold" style={{ color }}>
            {score}%
          </span>
          <span className="text-xs text-gray-400">fit</span>
        </div>
      </div>
      <span className="text-xs font-semibold" style={{ color }}>
        {label}
      </span>
    </div>
  );
}
