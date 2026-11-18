/**
 * Classification Review Page (Wireframe 2)
 * Shows AI-assisted recommendation and human-gated decision form
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { Stepper } from '../components/layout/Stepper';
import { ClassificationRecommendationCard } from '../components/classification/ClassificationRecommendationCard';
import { DecisionForm } from '../components/classification/DecisionForm';
import { IntakeCaseOut } from '../types/intake';
import { ClassificationRecommendationOut, ClassificationDecisionIn } from '../types/classification';
import { api } from '../lib/api-client';
import * as LucideIcons from 'lucide-react';

export function ClassificationReviewPage() {
  const { caseId: caseKeyOrId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [intakeCase, setIntakeCase] = useState<IntakeCaseOut | null>(null);
  const [recommendation, setRecommendation] = useState<ClassificationRecommendationOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const HandIcon = LucideIcons.Hand;
  const OctagonAlertIcon = LucideIcons.OctagonAlert;
  const FileSpreadsheetIcon = LucideIcons.FileSpreadsheet;
  const HistoryIcon = LucideIcons.History;
  const ArrowRightIcon = LucideIcons.ArrowRight;

  useEffect(() => {
    if (caseKeyOrId) {
      loadCaseAndRecommendation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseKeyOrId]);

  const loadCaseAndRecommendation = async () => {
    if (!caseKeyOrId) return;

    try {
      setLoading(true);
      setError(null);

      // Load intake case (API accepts case_key)
      const caseResponse = await api.get<IntakeCaseOut>(`/intake/cases/${caseKeyOrId}`);
      setIntakeCase(caseResponse);

      // Generate or load recommendation
      try {
        const recommendationResponse = await api.post<ClassificationRecommendationOut>(
          `/classification/cases/${caseResponse.id}/recommendation`
        );
        setRecommendation(recommendationResponse);
      } catch (recError) {
        console.error('Failed to generate recommendation:', recError);
        setError('Failed to generate classification recommendation.');
      }
    } catch (err) {
      console.error('Failed to load case:', err);
      setError('Failed to load case details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitDecision = async (decision: ClassificationDecisionIn) => {
    if (!intakeCase || !recommendation) return;

    try {
      setSubmitting(true);
      setError(null);

      await api.post(`/classification/cases/${intakeCase.id}/decision`, decision);

      // Navigate to audit or success page
      navigate('/');
    } catch (err) {
      console.error('Failed to submit decision:', err);
      setError('Failed to submit decision. Please check your permissions and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate('/');
  };

  const getStepperSteps = () => {
    if (!intakeCase) return [];

    return [
      {
        label: 'Received',
        statusText: 'Done',
        status: 'done' as const,
      },
      {
        label: 'Parsed',
        statusText: 'Done',
        status: 'done' as const,
      },
      {
        label: 'Classification review',
        statusText: 'Current · awaiting your decision',
        status: 'current' as const,
      },
      {
        label: 'VIN extracted',
        statusText: 'Upcoming',
        status: 'todo' as const,
      },
      {
        label: 'VIN validated',
        statusText: 'Upcoming',
        status: 'todo' as const,
      },
    ];
  };

  if (loading) {
    return (
      <Layout currentPage="classification">
        <div className="flex items-center justify-center min-h-[400px]">
          <p className="text-muted">Loading case and recommendation...</p>
        </div>
      </Layout>
    );
  }

  if (error || !intakeCase) {
    return (
      <Layout currentPage="classification">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-err mb-4">{error || 'Case not found'}</p>
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center gap-2 min-h-9 px-4 py-2 rounded border border-accent bg-accent text-white font-semibold text-sm"
              type="button"
            >
              Back to Cases
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout
      currentPage="classification"
      caseContext={{ caseKey: intakeCase.case_key, status: intakeCase.intake_status }}
    >
      <div className="flex justify-between items-end gap-5 mb-4">
        <div>
          <h1 className="font-head font-bold text-[30px] m-0 tracking-tight leading-tight">Classification Review</h1>
          <div className="flex items-center gap-3 mt-2">
            <span className="font-mono text-[13px] font-semibold">{intakeCase.case_key}</span>
          </div>
        </div>
      </div>

      <Stepper steps={getStepperSteps()} ariaLabel={`Case progress for ${intakeCase.case_key}`} />

      {/* AMBER gate callout */}
      <div
        className="flex gap-3 p-4 px-5 rounded-md border border-[#D99A00] border-l-[6px] bg-warn-bg items-center"
        role="status"
      >
        <HandIcon className="w-[30px] h-[30px] flex-shrink-0" strokeWidth={2} />
        <div>
          <p className="font-head text-xl font-bold m-0 mb-0.5">Requires human decision</p>
          <p className="m-0">
            No event binding is committed until you confirm, revise or reject.{' '}
            <span className="font-semibold">AI-assisted recommendation (AGN1 Intake &amp; Triage).</span>
          </p>
        </div>
        <span className="ml-auto inline-flex items-center gap-1.5 px-3 py-1 border-2 border-[#4A2E00] rounded bg-[#FFE08A] font-bold text-xs tracking-wider text-[#4A2E00] whitespace-nowrap flex-shrink-0">
          <OctagonAlertIcon className="w-4 h-4" />
          AMBER GATE · BR-06
        </span>
      </div>

      <div className="grid grid-cols-[35fr_65fr] gap-6 mt-5 items-start">
        {/* Case evidence */}
        <section className="bg-surface border border-line rounded-md" aria-labelledby="ev-h">
          <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
            <h3 id="ev-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
              Case evidence
            </h3>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 pl-2 rounded-xl text-xs font-semibold border bg-neutral-bg text-ink-2 border-[#B7C2CD]">
              <LucideIcons.Lock className="w-3.5 h-3.5" />
              Read-only
            </span>
          </div>
          <div className="p-4">
            <dl className="grid grid-cols-[110px_1fr] gap-2 gap-x-4 m-0">
              <dt className="text-muted text-sm">Subject</dt>
              <dd className="m-0 overflow-wrap-anywhere">{intakeCase.subject}</dd>

              <dt className="text-muted text-sm">Sender</dt>
              <dd className="m-0 overflow-wrap-anywhere">{intakeCase.source_address}</dd>

              <dt className="text-muted text-sm">Received</dt>
              <dd className="m-0 overflow-wrap-anywhere">
                {new Date(intakeCase.received_at_utc).toLocaleString('en-US', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                  timeZone: 'UTC',
                  timeZoneName: 'short',
                })}
              </dd>

              {intakeCase.attachments.length > 0 && (
                <>
                  <dt className="text-muted text-sm">Attachment</dt>
                  <dd className="m-0 overflow-wrap-anywhere flex items-center gap-2">
                    <FileSpreadsheetIcon className="w-4 h-4" />
                    {intakeCase.attachments[0].filename}
                  </dd>
                </>
              )}
            </dl>
            <p className="mt-4 p-3 px-4 bg-surface-2 border-l-4 border-line text-sm text-ink-2">
              <strong>Email body excerpt</strong>
              <br />
              "Disruption event detected. Affected VINs are in the attached sheet; please confirm the vehicles in scope."
            </p>
          </div>
        </section>

        {/* Recommendation */}
        {recommendation && (
          <ClassificationRecommendationCard
            recommendation={recommendation}
            onRegenerate={loadCaseAndRecommendation}
          />
        )}
      </div>

      {/* Decision form */}
      {recommendation && (
        <DecisionForm
          onSubmit={handleSubmitDecision}
          onCancel={handleCancel}
          isSubmitting={submitting}
        />
      )}

      {/* Decision history */}
      <div className="flex justify-between items-center mt-5 p-3 px-4 bg-surface border border-line rounded-md text-sm">
        <span className="flex items-center gap-2">
          <HistoryIcon className="w-4 h-4" />
          <strong>No decision recorded yet.</strong> Last recommendation generated{' '}
          {recommendation
            ? new Date(recommendation.created_at).toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZone: 'UTC',
              })
            : 'recently'}{' '}
          (confidence {recommendation ? recommendation.confidence_score.toFixed(2) : '0.00'}). After submission an Audit
          event ID is shown here.
        </span>
        <a href={`/cases/${intakeCase.case_key}/audit`} className="flex items-center gap-1.5 text-accent">
          View audit trail
          <ArrowRightIcon className="w-4 h-4" />
        </a>
      </div>

      {/* Footer */}
      <div className="flex justify-between gap-5 mt-5 pt-3 border-t border-line text-xs text-muted">
        <span>TOL1 inbox and TOL2 parser are mocked in this demo.</span>
      </div>
    </Layout>
  );
}
