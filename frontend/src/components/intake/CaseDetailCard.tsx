/**
 * Case detail card showing case metadata
 */

import { IntakeCaseOut } from '../../types/intake';
import { Chip } from '../shared/Chip';
import * as LucideIcons from 'lucide-react';

interface CaseDetailCardProps {
  intakeCase: IntakeCaseOut;
}

export function CaseDetailCard({ intakeCase }: CaseDetailCardProps) {
  const CopyIcon = LucideIcons.Copy;
  const statusConfig =
    intakeCase.intake_status === 'parsed'
      ? { variant: 'ok' as const, icon: 'CircleCheck' as const }
      : { variant: 'warn' as const, icon: 'Hourglass' as const };

  const handleCopyCorrelationId = () => {
    navigator.clipboard.writeText(intakeCase.correlation_id);
  };

  return (
    <section className="bg-surface border border-line rounded-md" aria-labelledby="detail-h">
      <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2 flex-wrap">
        <div className="flex items-center gap-3">
          <h2 id="detail-h" className="font-head font-semibold text-xl m-0 leading-tight">
            {intakeCase.case_key}
          </h2>
          <Chip variant={statusConfig.variant} icon={statusConfig.icon}>
            {intakeCase.intake_status}
          </Chip>
        </div>
        <div className="flex items-center gap-2 text-[13px]">
          <span className="text-muted">Correlation ID</span>
          <span className="font-mono text-xs">{intakeCase.correlation_id}</span>
          <button
            onClick={handleCopyCorrelationId}
            className="inline-flex items-center gap-1.5 px-2 py-0.5 border border-line rounded bg-surface text-xs text-accent font-semibold"
            type="button"
          >
            <CopyIcon className="w-3.5 h-3.5" />
            Copy
          </button>
        </div>
      </div>
    </section>
  );
}
