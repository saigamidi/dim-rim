/**
 * Stepper component showing workflow stages matching wireframe design.
 */

import { CircleCheck, CircleDot, Circle } from 'lucide-react';
import { cn } from '../../lib/utils';

interface Step {
  label: string;
  status: 'done' | 'current' | 'todo';
  statusText: string;
}

interface StepperProps {
  steps: Step[];
  ariaLabel?: string;
}

export function Stepper({ steps, ariaLabel }: StepperProps) {
  return (
    <ol
      className="flex list-none m-0 mb-s5 p-0 bg-surface border border-line rounded-md"
      aria-label={ariaLabel}
    >
      {steps.map((step, index) => {
        const Icon =
          step.status === 'done'
            ? CircleCheck
            : step.status === 'current'
            ? CircleDot
            : Circle;

        return (
          <li
            key={index}
            className={cn(
              'flex-1 flex items-center gap-s2 px-s3 py-[10px] border-r border-line-2 text-sm',
              step.status === 'done' && 'text-ok',
              step.status === 'current' && 'bg-accent-soft text-[#12405F] shadow-[inset_0_-4px_0_var(--accent)]',
              step.status === 'todo' && 'text-muted',
              index === steps.length - 1 && 'border-r-0'
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span className="flex flex-col">
              <span className="font-semibold">{step.label}</span>
              <span
                className={cn(
                  'block text-[11px] uppercase tracking-wider',
                  step.status === 'current' ? 'text-[#12405F]' : 'text-muted'
                )}
              >
                {step.statusText}
              </span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
