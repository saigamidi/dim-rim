/**
 * Chip component with variants matching wireframe design
 */

import * as LucideIcons from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type ChipVariant = 'ok' | 'err' | 'warn' | 'info' | 'neutral';

interface ChipProps {
  variant: ChipVariant;
  icon?: keyof typeof LucideIcons;
  children: React.ReactNode;
  className?: string;
}

export function Chip({ variant, icon, children, className = '' }: ChipProps) {
  const Icon = icon ? (LucideIcons[icon] as LucideIcon) : null;
  
  const variantClasses = {
    ok: 'bg-ok-bg text-ok border-[#A9D3B5]',
    err: 'bg-err-bg text-err border-[#E3A9A5]',
    warn: 'bg-warn-bg text-warn border-warn-line',
    info: 'bg-accent-soft text-[#12405F] border-[#9DBFD8]',
    neutral: 'bg-neutral-bg text-ink-2 border-[#B7C2CD]',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 pl-2 rounded-xl text-xs font-semibold whitespace-nowrap border ${variantClasses[variant]} ${className}`}
    >
      {Icon && <Icon className="w-3.5 h-3.5" strokeWidth={2} />}
      {children}
    </span>
  );
}
