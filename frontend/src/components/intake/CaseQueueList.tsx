/**
 * Case queue list component showing intake cases
 */

import { IntakeCaseOut } from '../../types/intake';
import { Chip, ChipVariant } from '../shared/Chip';
import * as LucideIcons from 'lucide-react';

interface CaseQueueListProps {
  cases: IntakeCaseOut[];
  selectedCaseId: string | null;
  onSelectCase: (caseId: string) => void;
}

function getStatusChipConfig(status: string): { variant: ChipVariant; icon: keyof typeof LucideIcons; label: string } {
  switch (status) {
    case 'parsed':
      return { variant: 'ok', icon: 'CircleCheck', label: 'parsed' };
    case 'classification_pending_review':
      return { variant: 'warn', icon: 'Hourglass', label: 'classification_pending_review' };
    case 'classification_decided':
      return { variant: 'ok', icon: 'CircleCheck', label: 'classification_decided' };
    case 'vin_validated':
      return { variant: 'ok', icon: 'CircleCheck', label: 'vin_validated' };
    case 'parse_failed':
      return { variant: 'err', icon: 'CircleX', label: 'parse_failed' };
    case 'received':
      return { variant: 'neutral', icon: 'Circle', label: 'received' };
    default:
      return { variant: 'neutral', icon: 'Circle', label: status };
  }
}

export function CaseQueueList({ cases, selectedCaseId, onSelectCase }: CaseQueueListProps) {
  const ClockIcon = LucideIcons.Clock;
  const PaperclipIcon = LucideIcons.Paperclip;

  return (
    <ul className="list-none m-0 p-0">
      {cases.map((caseItem, index) => {
        const isSelected = caseItem.id === selectedCaseId;
        const statusConfig = getStatusChipConfig(caseItem.intake_status);
        const isLastItem = index === cases.length - 1;

        return (
          <li
            key={caseItem.id}
            className={`p-3 px-4 grid gap-1.5 cursor-pointer ${
              isSelected ? 'bg-accent-soft shadow-[inset_5px_0_0_var(--accent)]' : ''
            } ${!isLastItem ? 'border-b border-line-2' : ''}`}
            onClick={() => onSelectCase(caseItem.id)}
            aria-current={isSelected ? 'true' : undefined}
          >
            <div className="flex justify-between items-center gap-2">
              <span className="font-mono font-semibold text-[13px]">{caseItem.case_key}</span>
              <Chip variant={statusConfig.variant} icon={statusConfig.icon}>
                {statusConfig.label}
              </Chip>
            </div>
            <div className="whitespace-nowrap overflow-hidden text-ellipsis font-medium">
              {caseItem.subject}
            </div>
            <div className="flex gap-4 text-xs text-muted items-center">
              <span className="inline-flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                {new Date(caseItem.received_at_utc).toLocaleString('en-US', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  timeZone: 'UTC',
                  timeZoneName: 'short'
                })}
              </span>
              <span className="inline-flex items-center gap-1">
                <PaperclipIcon className="w-4 h-4" />
                {caseItem.attachments.length} attachment{caseItem.attachments.length !== 1 ? 's' : ''}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
