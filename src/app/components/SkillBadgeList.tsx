import { Badge } from '@/app/components/ui/badge';

interface SkillBadgeListProps {
  skills: string[];
  variant?: 'default' | 'success' | 'danger' | 'warning';
  maxDisplay?: number;
}

export function SkillBadgeList({ skills, variant = 'default', maxDisplay }: SkillBadgeListProps) {
  const displaySkills = maxDisplay ? skills.slice(0, maxDisplay) : skills;
  const remaining = maxDisplay && skills.length > maxDisplay ? skills.length - maxDisplay : 0;

  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    danger: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <div className="flex flex-wrap gap-2">
      {displaySkills.map((skill, index) => (
        <Badge key={index} variant="secondary" className={variantClasses[variant]}>
          {skill}
        </Badge>
      ))}
      {remaining > 0 && (
        <Badge variant="secondary" className="bg-gray-200 text-gray-600">
          +{remaining} more
        </Badge>
      )}
    </div>
  );
}
