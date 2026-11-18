/**
 * Classification recommendation card with AI-assisted recommendation display
 */

import { ClassificationRecommendationOut } from '../../types/classification';
import { Chip } from '../shared/Chip';
import * as LucideIcons from 'lucide-react';

interface ClassificationRecommendationCardProps {
  recommendation: ClassificationRecommendationOut;
  onRegenerate?: () => void;
}

export function ClassificationRecommendationCard({
  recommendation,
  onRegenerate,
}: ClassificationRecommendationCardProps) {
  const RefreshCwIcon = LucideIcons.RefreshCw;
  const confidence = recommendation.confidence_score;
  const confidencePercent = Math.round(confidence * 100);
  const isHighConfidence = confidence >= 0.70;

  return (
    <section className="bg-surface border border-line rounded-md" aria-labelledby="rec-h">
      <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
        <div className="flex items-center gap-3">
          <h3 id="rec-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
            AGN1 recommendation
          </h3>
          <Chip variant="info" icon="Sparkles">
            AI-assisted
          </Chip>
        </div>
        {onRegenerate && (
          <button
            className="inline-flex items-center gap-2 min-h-7 px-2 py-1 rounded border-transparent bg-transparent text-accent font-semibold text-sm"
            type="button"
            onClick={onRegenerate}
          >
            <RefreshCwIcon className="w-4 h-4" />
            Regenerate recommendation
          </button>
        )}
      </div>
      <div className="p-4">
        <dl className="grid grid-cols-[200px_1fr] gap-3 gap-x-4 m-0">
          <dt className="text-muted text-sm pt-0.5">Disruption type</dt>
          <dd className="m-0 font-semibold">{recommendation.suggested_disruption_type}</dd>

          <dt className="text-muted text-sm pt-0.5">Subtype</dt>
          <dd className="m-0 font-semibold">{recommendation.suggested_disruption_subtype || '—'}</dd>

          <dt className="text-muted text-sm pt-0.5">Event reference</dt>
          <dd className="m-0 font-semibold">
            {recommendation.suggested_event_ref ? (
              <>
                <span className="font-mono text-sm">{recommendation.suggested_event_ref}</span>
                {recommendation.suggested_disruption_subtype && (
                  <span className="text-muted"> — {recommendation.suggested_disruption_subtype}</span>
                )}
              </>
            ) : (
              '—'
            )}
          </dd>

          <dt className="text-muted text-sm pt-0.5">Confidence</dt>
          <dd className="m-0">
            <div className="flex items-center gap-3">
              <span className="text-xl font-head font-bold">{confidence.toFixed(2)}</span>
              <span
                className="relative w-[260px] h-3.5 bg-neutral-bg border border-[#8794A1] rounded"
                role="img"
                aria-label={`Confidence ${confidence.toFixed(2)} out of 1.00`}
              >
                <span
                  className="absolute left-0 top-0 bottom-0 bg-accent rounded-l"
                  style={{ width: `${confidencePercent}%` }}
                />
                <span className="absolute top-[-4px] bottom-[-4px] w-0.5 bg-ink" style={{ left: '70%' }} />
              </span>
              <Chip variant={isHighConfidence ? 'ok' : 'warn'} icon="Gauge">
                {isHighConfidence ? 'High confidence' : 'Low confidence'}
              </Chip>
              <span className="text-muted font-normal text-xs">tick = 0.70 review threshold</span>
            </div>
          </dd>

          <dt className="text-muted text-sm pt-0.5">Requires human decision</dt>
          <dd className="m-0">
            <Chip variant="warn" icon="UserCheck">
              true
            </Chip>
          </dd>
        </dl>
        <div className="mt-4 p-4 bg-surface-2 border border-line-2 rounded">
          <h4 className="m-0 mb-1.5 text-xs uppercase tracking-wider text-muted">Explanation</h4>
          <p className="m-0">
            The subject and body cite a disruption event. The sender domain and attachment structure are
            consistent with a disruption-list submission.
          </p>
        </div>
      </div>
    </section>
  );
}
