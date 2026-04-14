import { CheckCircle, Shield } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

interface Template {
  name: string;
  description: string;
  best_for: string;
  ats_friendly: boolean;
}

interface TemplateShowcaseProps {
  templates: Template[];
}

// Visual preview patterns for each template type
const TEMPLATE_PREVIEWS: Record<string, string[][]> = {
  'Double Column': [
    ['bg-blue-600 h-3 w-3/4 rounded', 'bg-blue-400 h-2 w-1/2 rounded'],
    ['bg-gray-300 h-1.5 w-full rounded', 'bg-gray-200 h-1.5 w-5/6 rounded'],
    ['bg-gray-300 h-1.5 w-4/5 rounded', 'bg-gray-200 h-1.5 w-3/4 rounded'],
  ],
  'Ivy League': [
    ['bg-gray-800 h-3 w-2/3 rounded mx-auto'],
    ['bg-gray-400 h-px w-full'],
    ['bg-gray-300 h-1.5 w-full rounded', 'bg-gray-200 h-1.5 w-5/6 rounded'],
    ['bg-gray-300 h-1.5 w-4/5 rounded'],
  ],
  'Elegant': [
    ['bg-purple-700 h-4 w-1/2 rounded'],
    ['bg-purple-300 h-0.5 w-full'],
    ['bg-gray-300 h-1.5 w-full rounded', 'bg-gray-200 h-1.5 w-4/5 rounded'],
  ],
  'Executive': [
    ['bg-gray-900 h-5 w-full rounded-t'],
    ['bg-gray-300 h-1.5 w-3/4 rounded', 'bg-gray-200 h-1.5 w-full rounded'],
    ['bg-gray-300 h-1.5 w-5/6 rounded'],
  ],
};

export function TemplateShowcase({ templates }: TemplateShowcaseProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {templates.map((tpl, i) => {
        const preview = TEMPLATE_PREVIEWS[tpl.name] || [];
        return (
          <div
            key={i}
            className={cn(
              'border border-gray-200 rounded-xl overflow-hidden',
              'hover:border-blue-400 hover:shadow-md transition-all',
              'cursor-pointer group'
            )}
          >
            {/* Mini resume preview */}
            <div className="bg-white p-3 h-28 flex flex-col gap-1.5 justify-center">
              {preview.map((row, ri) => (
                <div key={ri} className="flex gap-1">
                  {row.map((cls, ci) => (
                    <div key={ci} className={cls} />
                  ))}
                </div>
              ))}
              {preview.length === 0 && (
                <div className="flex flex-col gap-1.5">
                  <div className="bg-gray-700 h-3 w-2/3 rounded" />
                  <div className="bg-gray-300 h-1.5 w-full rounded" />
                  <div className="bg-gray-200 h-1.5 w-4/5 rounded" />
                  <div className="bg-gray-300 h-1.5 w-5/6 rounded" />
                </div>
              )}
            </div>

            {/* Info */}
            <div className="p-3 bg-gray-50 border-t border-gray-100">
              <div className="flex items-start justify-between gap-1 mb-1">
                <p className="text-xs font-semibold text-gray-800 leading-tight">
                  {tpl.name}
                </p>
                {tpl.ats_friendly && (
                  <Shield className="w-3 h-3 text-green-500 flex-shrink-0 mt-0.5" />
                )}
              </div>
              <p className="text-xs text-gray-500 leading-tight">
                {tpl.best_for}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
