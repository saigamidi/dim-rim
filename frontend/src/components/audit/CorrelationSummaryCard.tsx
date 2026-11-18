import { CircleCheck, Copy, Hash } from 'lucide-react';
import { Chip } from '../shared/Chip';

interface CorrelationSummaryCardProps {
  caseId: string;
  correlationId: string;
  firstEventUtc: string;
  lastEventUtc: string;
  finalClassification: string;
  eventCount: number;
  requirementCounts: {
    'FR-001': number;
    'FR-002': number;
    'FR-003': number;
    'FR-004': number;
    'FR-005': number;
  };
}

export function CorrelationSummaryCard({
  caseId,
  correlationId,
  firstEventUtc,
  lastEventUtc,
  finalClassification,
  eventCount,
  requirementCounts
}: CorrelationSummaryCardProps) {
  const handleCopyCorrelationId = () => {
    navigator.clipboard.writeText(correlationId);
  };

  return (
    <div className="summ">
      <section className="card" aria-labelledby="corr-h">
        <div className="card-h">
          <h3 id="corr-h">Case correlation summary</h3>
          <Chip variant="info" icon="Hash">{eventCount} events</Chip>
        </div>
        <div className="card-b">
          <dl className="kv" style={{ gridTemplateColumns: '150px 1fr 150px 1fr' }}>
            <dt>case_id</dt>
            <dd className="mono">{caseId}</dd>
            <dt>Correlation ID</dt>
            <dd>
              <span className="mono">{correlationId}</span>{' '}
              <span className="copy" onClick={handleCopyCorrelationId} style={{ cursor: 'pointer' }}>
                <Copy style={{ width: '14px', height: '14px' }} />
                Copy
              </span>
            </dd>
            <dt>First event (UTC)</dt>
            <dd className="mono">{firstEventUtc}</dd>
            <dt>Last event (UTC)</dt>
            <dd className="mono">{lastEventUtc}</dd>
            <dt>Final classification</dt>
            <dd>
              <Chip variant="ok" icon="CircleCheck">{finalClassification}</Chip>
            </dd>
            <dt>Event count</dt>
            <dd>{eventCount} (11 tagged to FR-001 to FR-005, 1 status change)</dd>
          </dl>
        </div>
      </section>
      <section className="card" aria-labelledby="cov-h">
        <div className="card-h">
          <h3 id="cov-h">Requirement coverage</h3>
          <span className="muted" style={{ fontSize: '12px' }}>Evidence only — not a workflow</span>
        </div>
        <div className="card-b cov">
          <div className="covchip">
            <b>{requirementCounts['FR-001']}</b>
            <span>FR-001<br />Intake</span>
          </div>
          <div className="covchip">
            <b>{requirementCounts['FR-002']}</b>
            <span>FR-002<br />Parse</span>
          </div>
          <div className="covchip">
            <b>{requirementCounts['FR-003']}</b>
            <span>FR-003<br />Classification</span>
          </div>
          <div className="covchip">
            <b>{requirementCounts['FR-004']}</b>
            <span>FR-004<br />Extraction</span>
          </div>
          <div className="covchip">
            <b>{requirementCounts['FR-005']}</b>
            <span>FR-005<br />BR-01 validation</span>
          </div>
        </div>
      </section>
    </div>
  );
}
