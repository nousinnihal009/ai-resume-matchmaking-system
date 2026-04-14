import { useState } from 'react';
import { Copy, CheckCheck, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/app/components/ui/utils';

interface TailoredSummaryCardProps {
  summary: string;
}

export function TailoredSummaryCard({ summary }: TailoredSummaryCardProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(summary);
    setCopied(true);
    toast.success('Tailored summary copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="border border-blue-200 rounded-xl overflow-hidden shadow-sm">

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-white" />
          <span className="text-sm font-semibold text-white">
            AI-Tailored Professional Summary
          </span>
        </div>
        <button
          onClick={handleCopy}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
            copied
              ? 'bg-green-500 text-white'
              : 'bg-white/20 text-white hover:bg-white/30'
          )}
        >
          {copied
            ? <><CheckCheck className="w-3 h-3" /> Copied!</>
            : <><Copy className="w-3 h-3" /> Copy to clipboard</>
          }
        </button>
      </div>

      {/* Summary content */}
      <div className="p-5 bg-white">
        <p className="text-sm text-gray-700 leading-relaxed">
          {summary}
        </p>
      </div>

      {/* Usage hint */}
      <div className="px-4 py-2.5 bg-blue-50 border-t border-blue-100">
        <p className="text-xs text-blue-600">
          💡 Replace your current summary with this version when applying
          to this role. It uses the job's exact keywords for better ATS matching.
        </p>
      </div>
    </div>
  );
}
