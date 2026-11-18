import { CircleCheck, CircleX, Cpu, ShieldCheck } from 'lucide-react';

interface ValidationOutcomeCardProps {
  validCount: number;
  invalidCount: number;
  totalCount: number;
  failureBreakdown: {
    wrong_length?: number;
    invalid_character?: number;
    checksum_failure?: number;
    empty_value?: number;
    duplicate_in_case?: number;
  };
  validatedAt?: string;
}

export function ValidationOutcomeCard({
  validCount,
  invalidCount,
  totalCount,
  failureBreakdown,
  validatedAt
}: ValidationOutcomeCardProps) {
  const validPercent = totalCount > 0 ? (validCount / totalCount) * 100 : 0;

  return (
    <>
      <h2 style={{ marginBottom: 'var(--s3)' }}>
        BR-01 validation{' '}
        <span className="chip info" style={{ verticalAlign: 'middle', marginLeft: '8px' }}>
          <ShieldCheck style={{ width: '14px', height: '14px' }} />
          FR-005
        </span>{' '}
        <span className="chip neutral" style={{ verticalAlign: 'middle', marginLeft: '4px' }}>
          <Cpu style={{ width: '14px', height: '14px' }} />
          Deterministic · no AI involved
        </span>
      </h2>
      <div className="two">
        <section className="card" aria-labelledby="out-h">
          <div className="card-h">
            <h3 id="out-h">Outcome and failure reasons</h3>
            <span className="muted" style={{ fontSize: '13px' }}>
              {validatedAt ? `Validated ${validatedAt} UTC · ` : ''}run_status completed
            </span>
          </div>
          <div className="card-b">
            <div className="sumline">
              <span>
                <CircleCheck style={{ color: 'var(--ok)', width: '16px', height: '16px' }} />
                {' '}Valid <b>{validCount.toLocaleString()}</b>
              </span>
              <span>
                <CircleX style={{ color: 'var(--err)', width: '16px', height: '16px' }} />
                {' '}Invalid <b>{invalidCount.toLocaleString()}</b>
              </span>
              <span className="muted">of {totalCount.toLocaleString()} unique VIN records</span>
            </div>
            <div
              className="outbar"
              role="img"
              aria-label={`${validCount} valid and ${invalidCount} invalid out of ${totalCount}`}
            >
              <span className="v" style={{ width: `${validPercent}%` }}>
                <CircleCheck style={{ width: '16px', height: '16px' }} />
                {' '}Valid {validCount.toLocaleString()}
              </span>
              <span className="i">{invalidCount}</span>
            </div>
            <div className="tw" style={{ marginTop: 'var(--s4)' }}>
              <table className="dt">
                <caption className="muted" style={{ textAlign: 'left', fontSize: '12px', paddingBottom: '6px' }}>
                  Failure-reason breakdown
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Reason code</th>
                    <th scope="col" className="num">Count</th>
                    <th scope="col">Meaning</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="mono">wrong_length</td>
                    <td className="num">{failureBreakdown.wrong_length || 0}</td>
                    <td>Length is not 17</td>
                  </tr>
                  <tr>
                    <td className="mono">invalid_character</td>
                    <td className="num">{failureBreakdown.invalid_character || 0}</td>
                    <td>Contains I, O, Q or non-alphanumeric characters</td>
                  </tr>
                  <tr>
                    <td className="mono">checksum_failure</td>
                    <td className="num">{failureBreakdown.checksum_failure || 0}</td>
                    <td>ISO 3779 check digit at position 9 does not match</td>
                  </tr>
                  <tr>
                    <td className="mono">
                      empty_value{' '}
                      <span className="stagetag">
                        <i data-lucide="filter" />
                        extraction stage
                      </span>
                    </td>
                    <td className="num">{failureBreakdown.empty_value || 0}</td>
                    <td>Blank VIN cell — rejected at extraction</td>
                  </tr>
                  <tr>
                    <td className="mono">
                      duplicate_in_case{' '}
                      <span className="stagetag">
                        <i data-lucide="filter" />
                        extraction stage
                      </span>
                    </td>
                    <td className="num">{failureBreakdown.duplicate_in_case || 0}</td>
                    <td>Duplicate within submission — kept once, lineage preserved</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="muted" style={{ fontSize: '12px', margin: 'var(--s3) 0 0' }}>
              {(failureBreakdown.wrong_length || 0) + (failureBreakdown.invalid_character || 0) + (failureBreakdown.checksum_failure || 0)} = {invalidCount} invalid. The two extraction-stage codes are shown for completeness and are not counted in the {invalidCount}.
            </p>
          </div>
        </section>
      </div>
    </>
  );
}
