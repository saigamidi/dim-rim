/**
 * Receipt metadata card displaying intake case details
 */

import { IntakeCaseOut } from '../../types/intake';
import { Chip } from '../shared/Chip';

interface ReceiptMetadataCardProps {
  intakeCase: IntakeCaseOut;
}

export function ReceiptMetadataCard({ intakeCase }: ReceiptMetadataCardProps) {
  return (
    <section className="bg-surface border border-line rounded-md" aria-labelledby="rcpt-h">
      <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
        <h3 id="rcpt-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
          Receipt metadata
        </h3>
        <Chip variant="info" icon="MailCheck">
          Disruption-list candidate
        </Chip>
      </div>
      <div className="p-4">
        <dl className="grid grid-cols-[170px_1fr] gap-2 gap-x-4 m-0">
          <dt className="text-muted text-sm">Source address</dt>
          <dd className="m-0 overflow-wrap-anywhere">{intakeCase.source_address}</dd>

          <dt className="text-muted text-sm">Received (UTC)</dt>
          <dd className="m-0 overflow-wrap-anywhere">
            {new Date(intakeCase.received_at_utc).toLocaleString('en-US', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              timeZone: 'UTC',
            })}
          </dd>

          <dt className="text-muted text-sm">Subject</dt>
          <dd className="m-0 overflow-wrap-anywhere">{intakeCase.subject}</dd>

          <dt className="text-muted text-sm">Attachment present</dt>
          <dd className="m-0 overflow-wrap-anywhere">
            {intakeCase.attachments.length > 0
              ? `Yes — ${intakeCase.attachments.length} file${intakeCase.attachments.length > 1 ? 's' : ''}`
              : 'No'}
          </dd>

          <dt className="text-muted text-sm">source_email_id</dt>
          <dd className="m-0 overflow-wrap-anywhere font-mono text-xs">{intakeCase.source_email_id}</dd>

          <dt className="text-muted text-sm">case_id</dt>
          <dd className="m-0 overflow-wrap-anywhere font-mono text-xs">{intakeCase.id}</dd>
        </dl>
      </div>
    </section>
  );
}
