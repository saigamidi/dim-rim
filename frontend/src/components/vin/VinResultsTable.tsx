import { useState } from 'react';
import { CircleCheck, CircleX, Copy, ListIcon } from 'lucide-react';
import { Chip } from '../shared/Chip';

interface VinRecord {
  id: string;
  normalized_vin: string | null;
  raw_vin: string | null;
  validation_status?: 'valid' | 'invalid';
  failure_reason_code?: string | null;
  failure_reason_detail?: string | null;
  checksum_passed?: boolean;
  is_duplicate_within_case: boolean;
  validated_at_utc?: string;
}

interface VinResultsTableProps {
  records: VinRecord[];
  onSelectRecord?: (record: VinRecord) => void;
  selectedRecordId?: string;
}

type FilterType = 'all' | 'valid' | 'invalid' | 'wrong_length' | 'invalid_character' | 'checksum_failure' | 'empty_value' | 'duplicate_in_case';

export function VinResultsTable({ records, onSelectRecord, selectedRecordId }: VinResultsTableProps) {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');

  const filteredRecords = records.filter(record => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'valid') return record.validation_status === 'valid';
    if (activeFilter === 'invalid') return record.validation_status === 'invalid';
    if (activeFilter === 'duplicate_in_case') return record.is_duplicate_within_case;
    return record.failure_reason_code === activeFilter;
  });

  const handleRowClick = (record: VinRecord) => {
    if (onSelectRecord) {
      onSelectRecord(record);
    }
  };

  return (
    <section className="card" aria-labelledby="res-h">
      <div className="card-h">
        <h3 id="res-h">Per-VIN results · lineage view</h3>
        <span className="muted" style={{ fontSize: '13px' }}>
          Sample rows in source order; every failure code is represented
        </span>
      </div>
      <div
        className="card-b"
        style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', borderBottom: '1px solid var(--line-2)' }}
      >
        <span
          className={`filter ${activeFilter === 'all' ? 'on' : ''}`}
          onClick={() => setActiveFilter('all')}
          style={{ cursor: 'pointer' }}
        >
          <ListIcon style={{ width: '16px', height: '16px' }} />
          All
        </span>
        <span
          className={`filter ${activeFilter === 'valid' ? 'on' : ''}`}
          onClick={() => setActiveFilter('valid')}
          style={{ cursor: 'pointer' }}
        >
          <CircleCheck style={{ width: '16px', height: '16px' }} />
          Valid
        </span>
        <span
          className={`filter ${activeFilter === 'invalid' ? 'on' : ''}`}
          onClick={() => setActiveFilter('invalid')}
          style={{ cursor: 'pointer' }}
        >
          <CircleX style={{ width: '16px', height: '16px' }} />
          Invalid
        </span>
        <span
          className={`filter ${activeFilter === 'wrong_length' ? 'on' : ''}`}
          onClick={() => setActiveFilter('wrong_length')}
          style={{ cursor: 'pointer' }}
        >
          wrong_length
        </span>
        <span
          className={`filter ${activeFilter === 'invalid_character' ? 'on' : ''}`}
          onClick={() => setActiveFilter('invalid_character')}
          style={{ cursor: 'pointer' }}
        >
          invalid_character
        </span>
        <span
          className={`filter ${activeFilter === 'checksum_failure' ? 'on' : ''}`}
          onClick={() => setActiveFilter('checksum_failure')}
          style={{ cursor: 'pointer' }}
        >
          checksum_failure
        </span>
        <span
          className={`filter ${activeFilter === 'empty_value' ? 'on' : ''}`}
          onClick={() => setActiveFilter('empty_value')}
          style={{ cursor: 'pointer' }}
        >
          empty_value
        </span>
        <span
          className={`filter ${activeFilter === 'duplicate_in_case' ? 'on' : ''}`}
          onClick={() => setActiveFilter('duplicate_in_case')}
          style={{ cursor: 'pointer' }}
        >
          duplicate_in_case
        </span>
      </div>
      <div className="tw">
        <table className="dt">
          <thead>
            <tr>
              <th scope="col">Normalized VIN</th>
              <th scope="col">Raw value</th>
              <th scope="col">Validation</th>
              <th scope="col">Failure reason code</th>
              <th scope="col">Failure detail</th>
              <th scope="col">Checksum passed</th>
              <th scope="col">Duplicate in case</th>
              <th scope="col">Validated (UTC)</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: 'var(--s5)', color: 'var(--muted)' }}>
                  No VIN records match the current filter
                </td>
              </tr>
            ) : (
              filteredRecords.map(record => (
                <tr
                  key={record.id}
                  className={selectedRecordId === record.id ? 'sel' : ''}
                  onClick={() => handleRowClick(record)}
                  style={{ cursor: onSelectRecord ? 'pointer' : 'default' }}
                >
                  <td className="mono">{record.normalized_vin}</td>
                  <td className="mono">{record.raw_vin}</td>
                  <td>
                    {record.validation_status === 'valid' ? (
                      <Chip variant="ok" icon="CircleCheck">Valid</Chip>
                    ) : record.validation_status === 'invalid' ? (
                      <Chip variant="err" icon="CircleX">Invalid</Chip>
                    ) : (
                      <span className="muted">—</span>
                    )}
                  </td>
                  <td className={record.failure_reason_code ? 'mono' : 'muted'}>
                    {record.failure_reason_code || '—'}
                  </td>
                  <td className={record.failure_reason_detail ? '' : 'muted'}>
                    {record.failure_reason_detail || '—'}
                  </td>
                  <td>{record.checksum_passed !== undefined ? (record.checksum_passed ? 'Yes' : 'No') : '—'}</td>
                  <td>
                    {record.is_duplicate_within_case ? (
                      <Chip variant="warn" icon="Copy">Yes</Chip>
                    ) : (
                      'No'
                    )}
                  </td>
                  <td className="mono">
                    {record.validated_at_utc 
                      ? new Date(record.validated_at_utc).toLocaleTimeString('en-GB', { 
                          hour: '2-digit', 
                          minute: '2-digit', 
                          second: '2-digit',
                          hour12: false 
                        })
                      : '—'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="pager">
        <span>Showing {filteredRecords.length} of {records.length} · VIN drill-down loads in ≤ 2 s target</span>
        <span className="muted">Page 1 · {filteredRecords.length} rows per page</span>
      </div>
    </section>
  );
}
