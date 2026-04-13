interface IssueChipProps {
  count: number;
  label?: string;
}

export function IssueChip({ count, label }: IssueChipProps) {
  if (count === 0) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
        <span>✓</span>
        {label || 'No issues'}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
      {count} {count === 1 ? 'issue' : 'issues'}
    </span>
  );
}
