/**
 * Candidate row table showing parsed VIN candidates
 */

import { CandidateRowOut } from '../../types/intake';
import { Chip } from '../shared/Chip';

interface CandidateRowTableProps {
  rows: CandidateRowOut[];
  filename: string;
}

export function CandidateRowTable({ rows, filename }: CandidateRowTableProps) {
  const displayRows = rows.slice(0, 8);
  
  return (
    <section className="bg-surface border border-line rounded-md mt-5" aria-labelledby="rows-h">
      <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
        <div className="flex items-center gap-3">
          <h3 id="rows-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
            Canonical candidate-row preview
          </h3>
          <span className="text-muted text-[13px]">Parse stage only — VIN validity is checked later</span>
        </div>
        <span className="text-muted text-[13px]">GET /parsing/cases/{'{id}'}/rows</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              <th className="bg-surface-2 text-left font-semibold text-ink-2 p-2.5 px-3 border-b-2 border-line whitespace-nowrap">
                Source file
              </th>
              <th className="bg-surface-2 text-left font-semibold text-ink-2 p-2.5 px-3 border-b-2 border-line whitespace-nowrap">
                Sheet / Row #
              </th>
              <th className="bg-surface-2 text-left font-semibold text-ink-2 p-2.5 px-3 border-b-2 border-line whitespace-nowrap">
                Raw value
              </th>
              <th className="bg-surface-2 text-left font-semibold text-ink-2 p-2.5 px-3 border-b-2 border-line whitespace-nowrap">
                Canonical VIN candidate
              </th>
              <th className="bg-surface-2 text-left font-semibold text-ink-2 p-2.5 px-3 border-b-2 border-line whitespace-nowrap">
                Row status
              </th>
              <th className="bg-surface-2 text-left font-semibold text-ink-2 p-2.5 px-3 border-b-2 border-line whitespace-nowrap">
                Lineage ref
              </th>
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row) => {
              let rawRow: { vin?: string } = {};
              try {
                rawRow = JSON.parse(row.raw_row_json);
              } catch {
                // Fallback for unparseable JSON
              }
              const rawValue = rawRow.vin || row.canonical_vin_candidate || '(empty cell)';
              const isBlank = !row.canonical_vin_candidate;

              return (
                <tr key={row.id}>
                  <td className="p-2 px-3 border-b border-line-2 align-middle">{filename}</td>
                  <td className="p-2 px-3 border-b border-line-2 align-middle">
                    Affected · {row.source_row_number}
                  </td>
                  <td className="p-2 px-3 border-b border-line-2 align-middle font-mono text-xs">
                    {rawValue}
                  </td>
                  <td className="p-2 px-3 border-b border-line-2 align-middle font-mono text-xs">
                    {row.canonical_vin_candidate || '—'}
                  </td>
                  <td className="p-2 px-3 border-b border-line-2 align-middle">
                    {isBlank ? (
                      <Chip variant="neutral" icon="CircleMinus">
                        blank
                      </Chip>
                    ) : (
                      <Chip variant="ok" icon="CircleCheck">
                        ok
                      </Chip>
                    )}
                  </td>
                  <td className="p-2 px-3 border-b border-line-2 align-middle font-mono text-xs">
                    {row.lineage_ref}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="flex justify-between items-center p-3 px-4 border-t border-line-2 text-sm text-muted">
        <span>
          Showing 1-{displayRows.length} of {rows.length.toLocaleString()} rows
        </span>
        <span>Page 1 of {Math.ceil(rows.length / 8)} · 8 rows per page</span>
      </div>
    </section>
  );
}
