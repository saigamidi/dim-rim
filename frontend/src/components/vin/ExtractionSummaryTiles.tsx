import { FileSpreadsheet } from 'lucide-react';

interface ExtractionSummaryTilesProps {
  rowsParsed: number;
  extracted: number;
  deduplicated: number;
  rejected: number;
  attachmentFilename?: string;
}

export function ExtractionSummaryTiles({
  rowsParsed,
  extracted,
  deduplicated,
  rejected,
  attachmentFilename = 'attachment file'
}: ExtractionSummaryTilesProps) {
  return (
    <>
      <h2 style={{ marginBottom: 'var(--s3)' }}>
        Extraction summary{' '}
        <span className="chip info" style={{ verticalAlign: 'middle', marginLeft: '8px' }}>
          <FileSpreadsheet style={{ width: '14px', height: '14px' }} />
          FR-004
        </span>
      </h2>
      <div className="tiles">
        <div className="tile">
          <div className="n">{rowsParsed.toLocaleString()}</div>
          <div className="l">Rows parsed</div>
          <div className="d">{attachmentFilename}</div>
        </div>
        <div className="tile">
          <div className="n">{extracted.toLocaleString()}</div>
          <div className="l">Extracted candidates</div>
          <div className="d">{rowsParsed} − {rejected} blank cells</div>
        </div>
        <div className="tile dup">
          <div className="n">{deduplicated.toLocaleString()}</div>
          <div className="l">Deduplicated (duplicates removed)</div>
          <div className="d">First occurrence kept; lineage preserved</div>
        </div>
        <div className="tile rej">
          <div className="n">{rejected.toLocaleString()}</div>
          <div className="l">Rejected as empty</div>
          <div className="d">Blank VIN cells</div>
        </div>
      </div>
      <div className="recon">
        <i data-lucide="equal" />
        Reconciliation:{' '}
        <span className="mono">{extracted} − {deduplicated} = {extracted - deduplicated}</span>{' '}
        unique VIN records
      </div>
    </>
  );
}
