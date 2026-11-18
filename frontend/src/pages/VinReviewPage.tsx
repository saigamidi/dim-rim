import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Clock, Info, Repeat, ShieldCheck } from 'lucide-react';
import { Layout } from '../components/layout/Layout';
import { Stepper } from '../components/layout/Stepper';
import { Breadcrumbs } from '../components/layout/Breadcrumbs';
import { Chip } from '../components/shared/Chip';
import { ExtractionSummaryTiles } from '../components/vin/ExtractionSummaryTiles';
import { ValidationOutcomeCard } from '../components/vin/ValidationOutcomeCard';
import { BR01RulesCard } from '../components/vin/BR01RulesCard';
import { VinResultsTable } from '../components/vin/VinResultsTable';
import { api } from '../lib/api-client';
import { IntakeCaseOut } from '../types/intake';
import { VinValidationSummaryOut, VinRecordOut, VinValidationResultOut } from '../types/vin';

interface VinRecordWithValidation extends VinRecordOut {
  validation_result?: VinValidationResultOut;
}

export function VinReviewPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [intakeCase, setIntakeCase] = useState<IntakeCaseOut | null>(null);
  const [vinSummary, setVinSummary] = useState<VinValidationSummaryOut | null>(null);
  const [vinRecords, setVinRecords] = useState<VinRecordWithValidation[]>([]);
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

      // Load VIN summary
      const summary = await api.get<VinValidationSummaryOut>(`/vins/cases/${caseData.id}/summary`);
      setVinSummary(summary);

      // Load VIN records (from extraction)
      // Backend returns array of VIN records
      const records = await api.get<VinRecordWithValidation[]>(`/vins/cases/${caseData.id}/records`);
      setVinRecords(records || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load VIN data');
      console.error('Error loading VIN data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReRunExtraction = async () => {
    if (!intakeCase) return;
    try {
      await api.post(`/vins/cases/${intakeCase.id}/extract`);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to re-run extraction');
    }
  };

  const handleReRunValidation = async () => {
    if (!intakeCase) return;
    try {
      await api.post(`/vins/cases/${intakeCase.id}/validate`);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to re-run validation');
    }
  };

  if (loading) {
    return (
      <Layout>
        <div style={{ padding: 'var(--s5)', textAlign: 'center' }}>
          <p className="muted">Loading VIN review data...</p>
        </div>
      </Layout>
    );
  }

  if (error || !intakeCase || !vinSummary) {
    return (
      <Layout>
        <div style={{ padding: 'var(--s5)' }}>
          <div className="callout err">
            <Info style={{ width: '20px', height: '20px' }} />
            <div>
              <strong>Error loading VIN review</strong>
              <p style={{ margin: '4px 0 0' }}>{error || 'Case or VIN data not found'}</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const totalVins = vinSummary.extracted - vinSummary.deduplicated;
  const validCount = vinSummary.valid || 0;
  const invalidCount = vinSummary.invalid || 0;

  // Map VIN records to table format
  const tableRecords = vinRecords.map(record => ({
    id: record.id,
    normalized_vin: record.normalized_vin,
    raw_vin: record.raw_vin,
    validation_status: record.validation_result?.validation_status as 'valid' | 'invalid' | undefined,
    failure_reason_code: record.validation_result?.failure_reason_code,
    failure_reason_detail: record.validation_result?.failure_reason_detail,
    checksum_passed: record.validation_result?.checksum_passed,
    is_duplicate_within_case: record.is_duplicate_within_case,
    validated_at_utc: record.validation_result?.validated_at_utc
  }));

  return (
    <Layout>
      <main className="main">
        <Breadcrumbs
          items={[
            { label: 'Cases', href: '/intake' },
            { label: intakeCase.case_key, href: `/intake/${caseId}` },
            { label: 'VIN Review' }
          ]}
        />

        <div className="pagehead">
          <div>
            <h1>VIN Review</h1>
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
            <span>
              <ShieldCheck style={{ width: '16px', height: '16px' }} />
              {' '}BR-01 validation enforced
            </span>
          </div>
        </div>

        <Stepper
          steps={[
            { label: 'Received', statusText: 'Done', status: 'done' },
            { label: 'Parsed', statusText: 'Done', status: 'done' },
            { label: 'Classified', statusText: 'Done', status: 'done' },
            { label: 'VIN Extracted', statusText: 'Done', status: 'done' },
            { label: 'VIN Validated', statusText: 'Done', status: 'current' }
          ]}
        />

        {/* Extraction Summary */}
        <section>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2>Extraction Summary</h2>
            <button 
              onClick={handleReRunExtraction} 
              className="btn secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Repeat style={{ width: '16px', height: '16px' }} />
              Re-run extraction
            </button>
          </div>

          <ExtractionSummaryTiles
            rowsParsed={vinSummary.extracted + vinSummary.rejected}
            extracted={vinSummary.extracted}
            deduplicated={vinSummary.deduplicated}
            rejected={vinSummary.rejected}
          />
        </section>

        {/* Validation Outcome */}
        <section style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2>Validation Outcome (BR-01)</h2>
            <button 
              onClick={handleReRunValidation} 
              className="btn secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Repeat style={{ width: '16px', height: '16px' }} />
              Re-run validation
            </button>
          </div>

          <ValidationOutcomeCard
            totalCount={totalVins}
            validCount={validCount}
            invalidCount={invalidCount}
            failureBreakdown={vinSummary.failure_reason_breakdown || {}}
          />
        </section>

        {/* BR-01 Rules Reference */}
        <section style={{ marginTop: '24px' }}>
          <h2>BR-01 Rules Reference</h2>
          <BR01RulesCard />
        </section>

        {/* VIN Records Table */}
        <section style={{ marginTop: '24px' }}>
          <h2>VIN Records ({tableRecords.length})</h2>
          <VinResultsTable records={tableRecords} />
        </section>

        {/* Footer */}
        <div className="flex justify-between gap-5 mt-5 pt-3 border-t border-line text-xs text-muted">
          <span>VIN extraction and BR-01 validation running in this demo.</span>
        </div>
      </main>
    </Layout>
  );
}
