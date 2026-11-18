/**
 * Intake Cases Page (Wireframe 1)
 * Shows case queue and case detail with receipt metadata, attachment status, and candidate rows
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { Stepper } from '../components/layout/Stepper';
import { CaseQueueList } from '../components/intake/CaseQueueList';
import { CaseDetailCard } from '../components/intake/CaseDetailCard';
import { ReceiptMetadataCard } from '../components/intake/ReceiptMetadataCard';
import { AttachmentStatusCard } from '../components/intake/AttachmentStatusCard';
import { CandidateRowTable } from '../components/intake/CandidateRowTable';
import { IntakeCaseOut, CandidateRowOut } from '../types/intake';
import { api } from '../lib/api-client';
import * as LucideIcons from 'lucide-react';

export function IntakeCasesPage() {
  const navigate = useNavigate();
  const [cases, setCases] = useState<IntakeCaseOut[]>([]);
  const [selectedCase, setSelectedCase] = useState<IntakeCaseOut | null>(null);
  const [candidateRows, setCandidateRows] = useState<CandidateRowOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ArrowRightIcon = LucideIcons.ArrowRight;

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For MVP, fetch both seed cases
      // In production, this would be a list endpoint
      try {
        const case1 = await api.get<IntakeCaseOut>('/intake/cases/CASE-2026-001');
        const case2 = await api.get<IntakeCaseOut>('/intake/cases/CASE-2026-002');
        const loadedCases = [case1, case2];
        setCases(loadedCases);
        
        // Select first case by default
        const defaultCase = loadedCases[0];
        setSelectedCase(defaultCase);
        
        // Load candidate rows if case is parsed
        if (defaultCase.intake_status === 'parsed' && defaultCase.id) {
          try {
            const rows = await api.get<CandidateRowOut[]>(`/parsing/cases/${defaultCase.id}/rows`);
            setCandidateRows(rows);
          } catch (rowError) {
            console.error('Failed to load candidate rows:', rowError);
            // Non-critical error, continue without rows
          }
        }
      } catch (caseError) {
        // If specific cases fail, try to load at least one
        console.error('Failed to load all cases:', caseError);
        try {
          const case1 = await api.get<IntakeCaseOut>('/intake/cases/CASE-2026-001');
          setCases([case1]);
          setSelectedCase(case1);
        } catch {
          throw new Error('Failed to load any cases');
        }
      }
    } catch (err) {
      console.error('Failed to load intake cases:', err);
      setError('Failed to load intake cases. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCase = async (caseId: string) => {
    const selected = cases.find((c) => c.id === caseId);
    if (selected) {
      setSelectedCase(selected);
      
      // Load candidate rows for selected case
      if (selected.intake_status === 'parsed') {
        try {
          const rows = await api.get<CandidateRowOut[]>(`/parsing/cases/${selected.id}/rows`);
          setCandidateRows(rows);
        } catch (err) {
          console.error('Failed to load candidate rows:', err);
          setCandidateRows([]);
        }
      } else {
        setCandidateRows([]);
      }
    }
  };

  const handleGoToClassification = () => {
    if (selectedCase) {
      navigate(`/cases/${selectedCase.case_key}/classification`);
    }
  };

  const getStepperSteps = () => {
    if (!selectedCase) return [];
    
    const status = selectedCase.intake_status;
    const parsedStatus: 'done' | 'current' | 'todo' = 
      status === 'parsed' ? 'current' : 
      status === 'received' ? 'todo' : 'done';
    
    return [
      {
        label: 'Received',
        statusText: 'Done',
        status: 'done' as const,
      },
      {
        label: 'Parsed',
        statusText: status === 'parsed' ? 'Current · ready for review' : 'Done',
        status: parsedStatus,
      },
      {
        label: 'Classification review',
        statusText: 'Upcoming',
        status: 'todo' as const,
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
      <Layout currentPage="intake">
        <div className="flex items-center justify-center min-h-[400px]">
          <p className="text-muted">Loading cases...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout currentPage="intake">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-err mb-4">{error}</p>
            <button
              onClick={loadCases}
              className="inline-flex items-center gap-2 min-h-9 px-4 py-2 rounded border border-accent bg-accent text-white font-semibold text-sm"
              type="button"
            >
              Retry
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPage="intake" caseContext={selectedCase ? { caseKey: selectedCase.case_key, status: selectedCase.intake_status } : undefined}>
      <div>
        <h1 className="font-head font-bold text-[30px] m-0 tracking-tight leading-tight">Intake Cases</h1>
      </div>

      {selectedCase && <Stepper steps={getStepperSteps()} ariaLabel={`Case progress for ${selectedCase.case_key}`} />}

      <div className="grid grid-cols-[2fr_3fr] gap-6 items-start">
        {/* Case queue */}
        <section className="bg-surface border border-line rounded-md" aria-labelledby="queue-h">
          <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
            <h3 id="queue-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
              Case queue
            </h3>
            <span className="text-muted text-[13px]">{cases.length} submission{cases.length !== 1 ? 's' : ''} today</span>
          </div>
          <CaseQueueList
            cases={cases}
            selectedCaseId={selectedCase?.id || null}
            onSelectCase={handleSelectCase}
          />
          <div className="flex justify-between items-center p-3 px-4 border-t border-line-2 text-sm text-muted">
            <span>Showing 1-{cases.length} of {cases.length}</span>
          </div>
        </section>

        {/* Case detail */}
        {selectedCase && (
          <div className="flex flex-col gap-4">
            <CaseDetailCard intakeCase={selectedCase} />
            <ReceiptMetadataCard intakeCase={selectedCase} />
            {selectedCase.attachments.length > 0 && (
              <AttachmentStatusCard
                attachment={selectedCase.attachments[0]}
                rowCount={candidateRows.length}
              />
            )}
          </div>
        )}
      </div>

      {/* Candidate rows table */}
      {selectedCase && candidateRows.length > 0 && (
        <CandidateRowTable
          rows={candidateRows}
          filename={selectedCase.attachments[0]?.filename || 'attachment'}
        />
      )}

      {/* Next step bar */}
      {selectedCase && selectedCase.intake_status === 'parsed' && (
        <div className="flex justify-between items-center gap-5 p-4 px-5 mt-5 bg-ink text-white rounded-md">
          <p className="m-0 text-[#D5DFE8] text-sm">
            <strong className="text-white">Next step.</strong> Event binding needs your explicit decision before VIN
            processing continues.
          </p>
          <button
            onClick={handleGoToClassification}
            className="inline-flex items-center gap-2 min-h-9 px-4 py-2 rounded border border-white bg-white text-[#12405F] font-semibold text-sm flex-shrink-0"
            type="button"
          >
            Go to classification review
            <ArrowRightIcon className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Footer */}
      <div className="flex justify-between gap-5 mt-5 pt-3 border-t border-line text-xs text-muted">
        <span>TOL1 inbox and TOL2 parser are mocked in this demo.</span>
      </div>
    </Layout>
  );
}
