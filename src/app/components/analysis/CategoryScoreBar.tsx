import { cn } from '@/app/components/ui/utils';

interface CategoryScoreBarProps {
  label: string;
  score: number;
  weight: number;
  onClick?: () => void;
  active?: boolean;
}

export function CategoryScoreBar({
  label,
  score,
  weight,
  onClick,
  active = false,
}: CategoryScoreBarProps) {
  const color = score >= 75
    ? 'bg-green-500'
    : score >= 50
    ? 'bg-amber-500'
    : 'bg-red-500';

  const textColor = score >= 75
    ? 'text-green-600'
    : score >= 50
    ? 'text-amber-600'
    : 'text-red-600';

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left p-3 rounded-lg transition-all',
        'hover:bg-gray-50 cursor-pointer',
        active && 'bg-blue-50 ring-1 ring-blue-200'
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-700 capitalize">
          {label.replace(/_/g, ' ')}
        </span>
        <div className="flex items-center gap-2">
          <span className={cn('text-sm font-bold', textColor)}>
            {score}%
          </span>
          <span className="text-xs text-gray-400">
            {weight}%
          </span>
        </div>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className={cn('h-2 rounded-full transition-all duration-700', color)}
          style={{ width: `${score}%` }}
        />
      </div>
    </button>
  );
}
