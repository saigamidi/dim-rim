import { useState } from 'react';
import { 
  Bot, 
  Calendar, 
  ChevronDown, 
  ChevronRight, 
  CircleCheck, 
  CircleX, 
  FileSpreadsheet, 
  Loader, 
  ListIcon, 
  ListFilter, 
  Mail, 
  Scale, 
  Server, 
  ShieldCheck, 
  UserCheck 
} from 'lucide-react';
import { Chip } from '../shared/Chip';

interface AuditEvent {
  id: string;
  occurred_at_utc: string;
  actor_type: string;
  actor_id: string;
  action_type: string;
  entity_type: string;
  entity_id: string;
  outcome: string;
  correlation_id: string;
  metadata_json?: string;
}

interface AuditEventsTableProps {
  events: AuditEvent[];
}

type ActionFilterType = 'all' | 'intake' | 'parse' | 'classification' | 'extraction' | 'validation';
type ActorFilterType = 'all' | 'agent' | 'system' | 'human';

export function AuditEventsTable({ events }: AuditEventsTableProps) {
  const [actionFilter, setActionFilter] = useState<ActionFilterType>('all');
  const [actorFilter, setActorFilter] = useState<ActorFilterType>('all');
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  const filteredEvents = events.filter(event => {
    // Action type filter
    if (actionFilter !== 'all') {
      const actionLower = event.action_type.toLowerCase();
      if (actionFilter === 'intake' && !actionLower.includes('intake') && !actionLower.includes('attachment_registered')) {
        return false;
      }
      if (actionFilter === 'parse' && !actionLower.includes('parse')) {
        return false;
      }
      if (actionFilter === 'classification' && !actionLower.includes('classification') && !actionLower.includes('recommendation')) {
        return false;
      }
      if (actionFilter === 'extraction' && !actionLower.includes('extraction')) {
        return false;
      }
      if (actionFilter === 'validation' && !actionLower.includes('validation') && !actionLower.includes('br01')) {
        return false;
      }
    }

    // Actor type filter
    if (actorFilter !== 'all') {
      const actorLower = event.actor_type.toLowerCase();
      if (actorFilter === 'agent' && !actorLower.includes('agent')) {
        return false;
      }
      if (actorFilter === 'system' && !actorLower.includes('system')) {
        return false;
      }
      if (actorFilter === 'human' && !actorLower.includes('user')) {
        return false;
      }
    }

    return true;
  });

  const toggleExpand = (eventId: string) => {
    setExpandedEventId(expandedEventId === eventId ? null : eventId);
  };

  const getActionIcon = (actionType: string) => {
    const lower = actionType.toLowerCase();
    if (lower.includes('intake') || lower.includes('attachment')) return Mail;
    if (lower.includes('parse')) return FileSpreadsheet;
    if (lower.includes('classification') || lower.includes('recommendation')) return Scale;
    if (lower.includes('extraction')) return ListFilter;
    if (lower.includes('validation') || lower.includes('br01')) return ShieldCheck;
    return Server;
  };

  const getActorIcon = (actorType: string) => {
    const lower = actorType.toLowerCase();
    if (lower.includes('agent')) return Bot;
    if (lower.includes('user')) return UserCheck;
    return Server;
  };

  const formatTime = (utcString: string) => {
    return new Date(utcString).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  const truncateCorrelationId = (id: string) => {
    return id.substring(0, 8) + '…' + id.substring(id.length - 4);
  };

  return (
    <section className="card" aria-labelledby="tbl-h">
      <div className="card-h">
        <h3 id="tbl-h">Audit events</h3>
        <span className="muted" style={{ fontSize: '13px' }}>
          GET /audit/cases/{'{id}'} · newest last
        </span>
      </div>
      <div className="fbar">
        <div className="fgroup">
          <span className="lab">Action type</span>
          <span
            className={`filter ${actionFilter === 'all' ? 'on' : ''}`}
            onClick={() => setActionFilter('all')}
            style={{ cursor: 'pointer' }}
          >
            <ListIcon style={{ width: '16px', height: '16px' }} />
            All
          </span>
          <span
            className={`filter ${actionFilter === 'intake' ? 'on' : ''}`}
            onClick={() => setActionFilter('intake')}
            style={{ cursor: 'pointer' }}
          >
            <Mail style={{ width: '16px', height: '16px' }} />
            Intake
          </span>
          <span
            className={`filter ${actionFilter === 'parse' ? 'on' : ''}`}
            onClick={() => setActionFilter('parse')}
            style={{ cursor: 'pointer' }}
          >
            <FileSpreadsheet style={{ width: '16px', height: '16px' }} />
            Parse
          </span>
          <span
            className={`filter ${actionFilter === 'classification' ? 'on' : ''}`}
            onClick={() => setActionFilter('classification')}
            style={{ cursor: 'pointer' }}
          >
            <Scale style={{ width: '16px', height: '16px' }} />
            Classification
          </span>
          <span
            className={`filter ${actionFilter === 'extraction' ? 'on' : ''}`}
            onClick={() => setActionFilter('extraction')}
            style={{ cursor: 'pointer' }}
          >
            <ListFilter style={{ width: '16px', height: '16px' }} />
            Extraction
          </span>
          <span
            className={`filter ${actionFilter === 'validation' ? 'on' : ''}`}
            onClick={() => setActionFilter('validation')}
            style={{ cursor: 'pointer' }}
          >
            <ShieldCheck style={{ width: '16px', height: '16px' }} />
            Validation
          </span>
        </div>
        <div className="fgroup">
          <span className="lab">Actor</span>
          <span
            className={`filter ${actorFilter === 'all' ? 'on' : ''}`}
            onClick={() => setActorFilter('all')}
            style={{ cursor: 'pointer' }}
          >
            All
          </span>
          <span
            className={`filter ${actorFilter === 'agent' ? 'on' : ''}`}
            onClick={() => setActorFilter('agent')}
            style={{ cursor: 'pointer' }}
          >
            <Bot style={{ width: '16px', height: '16px' }} />
            Agent
          </span>
          <span
            className={`filter ${actorFilter === 'system' ? 'on' : ''}`}
            onClick={() => setActorFilter('system')}
            style={{ cursor: 'pointer' }}
          >
            <Server style={{ width: '16px', height: '16px' }} />
            System
          </span>
          <span
            className={`filter ${actorFilter === 'human' ? 'on' : ''}`}
            onClick={() => setActorFilter('human')}
            style={{ cursor: 'pointer' }}
          >
            <UserCheck style={{ width: '16px', height: '16px' }} />
            Human reviewer
          </span>
        </div>
        <div className="fgroup">
          <span className="lab">Time range</span>
          <span className="filter">
            <Calendar style={{ width: '16px', height: '16px' }} />
            {events.length > 0 
              ? `${formatTime(events[0].occurred_at_utc)} → ${formatTime(events[events.length - 1].occurred_at_utc)} UTC`
              : 'No events'}
          </span>
        </div>
      </div>
      <div className="tw">
        <table className="dt">
          <thead>
            <tr>
              <th scope="col">Time (UTC)</th>
              <th scope="col">Actor</th>
              <th scope="col">Action type</th>
              <th scope="col">Entity</th>
              <th scope="col">Outcome</th>
              <th scope="col">Correlation ID</th>
              <th scope="col">Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: 'var(--s5)', color: 'var(--muted)' }}>
                  No audit events match the current filter
                </td>
              </tr>
            ) : (
              filteredEvents.map(event => {
                const ActionIcon = getActionIcon(event.action_type);
                const ActorIcon = getActorIcon(event.actor_type);
                const isExpanded = expandedEventId === event.id;
                const hasMetadata = event.metadata_json && event.metadata_json !== '{}';

                return (
                  <>
                    <tr key={event.id} className={isExpanded ? 'open' : ''}>
                      <td className="mono">{formatTime(event.occurred_at_utc)}</td>
                      <td>
                        <ActorIcon style={{ width: '16px', height: '16px', verticalAlign: '-3px' }} />
                        {' '}{event.actor_id}
                      </td>
                      <td>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          {event.action_type}
                          <Chip variant="info">
                            <ActionIcon style={{ width: '12px', height: '12px' }} />
                            {/* Extract FR requirement if present in action type metadata */}
                          </Chip>
                        </span>
                      </td>
                      <td className="mono">{event.entity_type} · {event.entity_id}</td>
                      <td>
                        {event.outcome === 'success' ? (
                          <Chip variant="ok" icon="CircleCheck">success</Chip>
                        ) : event.outcome === 'failure' ? (
                          <Chip variant="err" icon="CircleX">failure</Chip>
                        ) : event.outcome === 'pending' ? (
                          <Chip variant="neutral" icon="Loader">pending</Chip>
                        ) : (
                          <span className="muted">{event.outcome}</span>
                        )}
                      </td>
                      <td className="mono">{truncateCorrelationId(event.correlation_id)}</td>
                      <td>
                        {hasMetadata ? (
                          <a
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              toggleExpand(event.id);
                            }}
                            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                          >
                            {isExpanded ? (
                              <>
                                <ChevronDown style={{ width: '16px', height: '16px' }} />
                                Hide
                              </>
                            ) : (
                              <>
                                <ChevronRight style={{ width: '16px', height: '16px' }} />
                                Show
                              </>
                            )}
                          </a>
                        ) : (
                          <span className="muted">—</span>
                        )}
                      </td>
                    </tr>
                    {isExpanded && hasMetadata && (
                      <tr className="expand">
                        <td colSpan={7}>
                          <pre className="mj">{JSON.stringify(JSON.parse(event.metadata_json || '{}'), null, 2)}</pre>
                        </td>
                      </tr>
                    )}
                  </>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      <div className="pager">
        <span>Showing {filteredEvents.length} of {events.length}</span>
        <span className="muted">
          Failure outcomes carry an explicit reason; append-only audit trail
        </span>
      </div>
    </section>
  );
}
