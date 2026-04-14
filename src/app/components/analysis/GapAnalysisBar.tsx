import { AlertTriangle } from 'lucide-react';

interface GapAnalysisBarProps {
  gaps: string[];
}

export function GapAnalysisBar({ gaps }: GapAnalysisBarProps) {
  if (!gaps || gaps.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className="w-4 h-4 text-red-500" />
        <h4 className="text-sm font-semibold text-red-700">
          Critical Gaps — Address These First
        </h4>
      </div>
      <div className="flex flex-col gap-2">
        {gaps.map((gap, i) => (
          <div
            key={i}
            className="flex items-start gap-3 p-3 bg-white rounded-lg border border-red-100"
          >
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 text-xs font-bold flex items-center justify-center mt-0.5">
              {i + 1}
            </span>
            <p className="text-sm text-gray-700">{gap}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
