import { useState, ReactNode } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

interface SectionCardProps {
  id: string;
  title: string;
  score: number;
  issueCount: number;
  icon: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function SectionCard({
  id,
  title,
  score,
  issueCount,
  icon,
  children,
  defaultOpen = false,
}: SectionCardProps) {
  const [open, setOpen] = useState(defaultOpen);

  const headerColor = issueCount === 0
    ? 'border-l-green-500'
    : issueCount <= 2
    ? 'border-l-amber-500'
    : 'border-l-red-500';

  return (
    <div
      id={id}
      className={cn(
        'bg-white rounded-xl border border-gray-200 border-l-4',
        'shadow-sm overflow-hidden',
        headerColor
      )}
    >
      <button
        className="w-full flex items-center justify-between p-5 text-left hover:bg-gray-50 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-3">
          <span className="text-gray-600">{icon}</span>
          <div>
            <h3 className="text-base font-semibold text-gray-800">
              {title}
            </h3>
            <p className="text-sm text-gray-500">
              Score: <span className="font-medium">{score}/100</span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {issueCount === 0 ? (
            <span className="text-xs bg-green-100 text-green-700 px-2.5 py-1 rounded-full font-medium">
              ✓ No issues
            </span>
          ) : (
            <span className="text-xs bg-red-100 text-red-700 px-2.5 py-1 rounded-full font-medium">
              {issueCount} {issueCount === 1 ? 'issue' : 'issues'} found
            </span>
          )}
          {open
            ? <ChevronUp className="w-4 h-4 text-gray-400" />
            : <ChevronDown className="w-4 h-4 text-gray-400" />
          }
        </div>
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-gray-100">
          {children}
        </div>
      )}
    </div>
  );
}
