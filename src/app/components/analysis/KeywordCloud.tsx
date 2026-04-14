interface KeywordCloudProps {
  missing: string[];
  present: string[];
}

export function KeywordCloud({ missing, present }: KeywordCloudProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

      {/* Missing keywords */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
            Missing Keywords ({missing.length})
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {missing.length === 0 ? (
            <p className="text-xs text-gray-400 italic">None — great coverage!</p>
          ) : (
            missing.slice(0, 20).map((kw, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-100"
              >
                + {kw}
              </span>
            ))
          )}
        </div>
      </div>

      {/* Present keywords */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
            Already Present ({present.length})
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {present.length === 0 ? (
            <p className="text-xs text-gray-400 italic">No matches found yet.</p>
          ) : (
            present.slice(0, 15).map((kw, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-100"
              >
                ✓ {kw}
              </span>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
