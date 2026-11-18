import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Clock, Info, Lock } from 'lucide-react';
import { Layout } from '../components/layout/Layout';
import { Stepper } from '../components/layout/Stepper';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';
import { Chip } from '../components/shared/Chip';
import { CorrelationSummaryCard } from '../components/audit/CorrelationSummaryCard';
import { AuditEventsTable } from '../components/audit/AuditEventsTable';
import { api } from '../lib/api-client';
import { IntakeCaseOut } from '../types/intake';
import { AuditEventOut } from '../types/audit';

export function AuditTrailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [intakeCase, setIntakeCase] = useState<IntakeCaseOut | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEventOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load intake case
      const caseData = await api.get<IntakeCaseOut>(`/intake/cases/${caseId}`);
      setIntakeCase(caseData);

      // Load audit events
      const events = await api.get<AuditEventOut[]>(`/audit/cases/${caseData.id}/events`);
      setAuditEvents(Array.isArray(events) ? events : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit data');
      console.error('Error loading audit data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div style={{ padding: 'var(--s5)', textAlign: 'center' }}>
          <p className="muted">Loading audit trail...</p>
        </div>
      </Layout>
    );
  }

  if (error || !intakeCase) {
    return (
      <Layout>
        <div style={{ padding: 'var(--s5)' }}>
          <div className="callout err">
            <Info style={{ width: '20px', height: '20px' }} />
            <div>
              <strong>Error loading audit trail</strong>
              <p style={{ margin: '4px 0 0' }}>{error || 'Case not found'}</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Calculate requirement counts from audit events
  const requirementCounts = {
    'FR-001': auditEvents.filter(e => 
      e.action_type.includes('intake') || e.action_type.includes('attachment_registered')
    ).length,
    'FR-002': auditEvents.filter(e => e.action_type.includes('parse')).length,
    'FR-003': auditEvents.filter(e => 
      e.action_type.includes('classification') || e.action_type.includes('recommendation')
    ).length,
    'FR-004': auditEvents.filter(e => e.action_type.includes('extraction')).length,
    'FR-005': auditEvents.filter(e => 
      e.action_type.includes('validation') || e.action_type.includes('br01')
    ).length
  };

  const firstEvent = auditEvents[0];
  const lastEvent = auditEvents[auditEvents.length - 1];

  const formatDateTime = (isoString: string) => {
    return new Date(isoString).toISOString().slice(0, 19).replace('T', ' ');
  };

  return (
    <Layout>
      <main className="main">
        <Breadcrumbs
          items={[
            { label: 'Cases', href: '/intake' },
            { label: intakeCase.case_key, href: `/intake/${caseId}` },
            { label: 'Audit' }
          ]}
        />

        <div className="pagehead">
          <div>
            <h1>Audit Trail</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px', flexWrap: 'wrap' }}>
              <span className="mono" style={{ fontSize: '13px', fontWeight: 600 }}>
                {intakeCase.case_key}
              </span>
              <Chip variant="ok" icon="Clock">
                {intakeCase.intake_status}
              </Chip>
            </div>
          </div>
          <div className="meta">
            <span className="appendonly">
              <Lock style={{ width: '16px', height: '16px' }} />
              Append-only: entries cannot be edited or deleted
            </span>
            <span>
              <Clock style={{ width: '16px', height: '16px' }} />
              {' '}Last refreshed {new Date().toISOString().slice(0, 19).replace('T', ' ')} UTC
            </span>
          </div>
        </div>

        <Stepper
          steps={[
            { label: 'Received', status: 'done', statusText: 'Done' },
            { label: 'Parsed', status: 'done', statusText: 'Done' },
            { label: 'Classification review', status: 'done', statusText: 'Done · Confirmed' },
            { label: 'VIN extracted', status: 'done', statusText: 'Done' },
            { label: 'VIN validated', status: 'current', statusText: 'Current' }
          ]}
        />

        {firstEvent && lastEvent && (
          <CorrelationSummaryCard
            caseId={intakeCase.id}
            correlationId={intakeCase.correlation_id}
            firstEventUtc={formatDateTime(firstEvent.occurred_at_utc)}
            lastEventUtc={formatDateTime(lastEvent.occurred_at_utc)}
            finalClassification="Confirmed — EVT-2026-1187"
            eventCount={auditEvents.length}
            requirementCounts={requirementCounts}
          />
        )}

        <AuditEventsTable events={auditEvents} />

        <div className="seam">
          <Info style={{ width: '16px', height: '16px' }} />
          Downstream marker emission (AGN5 / TOL7) is not active in this MVP.
        </div>

        <div className="foot">
          <span>
            <i data-lucide="hash" />
            Correlation ID shown on each action; copy for support.
          </span>
          <span>TOL1 inbox and TOL2 parser are mocked in this demo.</span>
        </div>
      </main>
    </Layout>
  );
}
