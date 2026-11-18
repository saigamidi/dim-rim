/**
 * Attachment status card showing parse status and metadata
 */

import { AttachmentOut } from '../../types/intake';
import { Chip } from '../shared/Chip';
import * as LucideIcons from 'lucide-react';

interface AttachmentStatusCardProps {
  attachment: AttachmentOut;
  rowCount?: number;
}

export function AttachmentStatusCard({ attachment, rowCount = 0 }: AttachmentStatusCardProps) {
  const FileSpreadsheetIcon = LucideIcons.FileSpreadsheet;
  const RefreshCwIcon = LucideIcons.RefreshCw;
  
  const isParsed = attachment.parse_status === 'parsed';
  const statusConfig = isParsed
    ? { variant: 'ok' as const, icon: 'CircleCheck' as const }
    : { variant: 'err' as const, icon: 'CircleX' as const };

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${Math.round(bytes / (1024 * 1024))} MB`;
  };

  return (
    <section className="bg-surface border border-line rounded-md" aria-labelledby="att-h">
      <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
        <h3 id="att-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
          Attachment and parse status
        </h3>
        <Chip variant={statusConfig.variant} icon={statusConfig.icon}>
          {attachment.parse_status}
        </Chip>
      </div>
      <div className="p-4">
        <dl className="grid grid-cols-[170px_1fr] gap-2 gap-x-4 m-0">
          <dt className="text-muted text-sm">Filename</dt>
          <dd className="m-0 overflow-wrap-anywhere flex items-center gap-2">
            <FileSpreadsheetIcon className="w-4 h-4" />
            {attachment.filename}
          </dd>

          <dt className="text-muted text-sm">Media type</dt>
          <dd className="m-0 overflow-wrap-anywhere font-mono text-xs">{attachment.media_type}</dd>

          <dt className="text-muted text-sm">Size</dt>
          <dd className="m-0 overflow-wrap-anywhere">{formatBytes(attachment.byte_size)}</dd>

          {isParsed && rowCount > 0 && (
            <>
              <dt className="text-muted text-sm">Rows parsed</dt>
              <dd className="m-0 overflow-wrap-anywhere">
                <strong>{rowCount.toLocaleString()}</strong> data rows
              </dd>
            </>
          )}

          <dt className="text-muted text-sm">Parse failures</dt>
          <dd className="m-0 overflow-wrap-anywhere">0</dd>

          <dt className="text-muted text-sm">Accepted formats</dt>
          <dd className="m-0 overflow-wrap-anywhere">Excel (.xlsx, .xls) and CSV accepted</dd>
        </dl>
        <div className="mt-4">
          <button className="inline-flex items-center gap-2 min-h-7 px-2.5 py-1 rounded border border-accent bg-surface text-accent font-semibold text-sm" type="button">
            <RefreshCwIcon className="w-4 h-4" />
            Re-parse (force_reparse)
          </button>
        </div>
      </div>
    </section>
  );
}
