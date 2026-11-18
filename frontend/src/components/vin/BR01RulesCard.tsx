import { Cpu } from 'lucide-react';

export function BR01RulesCard() {
  return (
    <section className="card" aria-labelledby="rules-h">
      <div className="card-h">
        <h3 id="rules-h">BR-01 rule reference</h3>
        <span className="chip neutral">
          <Cpu style={{ width: '14px', height: '14px' }} />
          Deterministic · no AI involved
        </span>
      </div>
      <div className="card-b">
        <ol className="rules">
          <li>Normalize to uppercase and remove whitespace and control characters.</li>
          <li>Reject empty values.</li>
          <li>Enforce exact length 17.</li>
          <li>Reject the characters I, O, Q and any non-alphanumeric character.</li>
          <li>Compute the ISO 3779 check digit.</li>
          <li>Persist one validation outcome per VIN record.</li>
          <li>Keep invalid VINs stored for auditability, marked as blocked from any future lookup or load path.</li>
        </ol>
      </div>
    </section>
  );
}
