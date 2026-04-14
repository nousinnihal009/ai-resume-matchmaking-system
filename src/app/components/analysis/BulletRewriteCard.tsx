import { Copy, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

interface BulletRewriteCardProps {
  original: string;
  rewritten: string;
  reason: string;
  index: number;
}

export function BulletRewriteCard({
  original,
  rewritten,
  reason,
  index,
}: BulletRewriteCardProps) {
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">

      {/* Header */}
      <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          Bullet {index + 1}
        </span>
        <button
          onClick={() => {
            navigator.clipboard.writeText(rewritten);
            toast.success('Rewritten bullet copied!');
          }}
          className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
        >
          <Copy className="w-3 h-3" />
          Copy improved
        </button>
      </div>

      {/* Before / After */}
      <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-gray-200">

        {/* Before */}
        <div className="p-4 bg-red-50">
          <p className="text-xs font-semibold text-red-600 mb-2 uppercase tracking-wide">
            Before
          </p>
          <p className="text-sm text-red-800 leading-relaxed line-through decoration-red-300">
            {original}
          </p>
        </div>

        {/* After */}
        <div className="p-4 bg-green-50">
          <p className="text-xs font-semibold text-green-600 mb-2 uppercase tracking-wide">
            After
          </p>
          <p className="text-sm text-green-800 leading-relaxed font-medium">
            {rewritten}
          </p>
        </div>
      </div>

      {/* Reason */}
      <div className="px-4 py-2.5 bg-blue-50 border-t border-blue-100">
        <p className="text-xs text-blue-700">
          <span className="font-semibold">Why: </span>
          {reason}
        </p>
      </div>
    </div>
  );
}
