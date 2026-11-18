/**
 * Classification decision form with confirm/revise/reject options
 */

import { useState } from 'react';
import { ClassificationDecisionIn } from '../../types/classification';
import * as LucideIcons from 'lucide-react';

interface DecisionFormProps {
  onSubmit: (decision: ClassificationDecisionIn) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export function DecisionForm({ onSubmit, onCancel, isSubmitting = false }: DecisionFormProps) {
  const [selectedAction, setSelectedAction] = useState<'confirm' | 'revise' | 'reject'>('revise');
  const [finalType, setFinalType] = useState('');
  const [finalSubtype, setFinalSubtype] = useState('');
  const [finalEventRef, setFinalEventRef] = useState('');
  const [reviewerComment, setReviewerComment] = useState('');
  const [showValidationError, setShowValidationError] = useState(false);

  const CheckIcon = LucideIcons.Check;
  const PencilIcon = LucideIcons.Pencil;
  const XIcon = LucideIcons.X;
  const SendIcon = LucideIcons.Send;
  const InfoIcon = LucideIcons.Info;
  const CircleAlertIcon = LucideIcons.CircleAlert;
  const ChevronDownIcon = LucideIcons.ChevronDown;
  const SearchIcon = LucideIcons.Search;

  const canSubmit = () => {
    if (selectedAction === 'revise') {
      return finalType.trim().length > 0 || finalSubtype.trim().length > 0 || finalEventRef.trim().length > 0;
    }
    return true;
  };

  const handleSubmit = () => {
    if (!canSubmit()) {
      setShowValidationError(true);
      return;
    }

    const decision: ClassificationDecisionIn = {
      reviewer_decision: selectedAction,
      final_disruption_type: selectedAction === 'revise' && finalType ? finalType : null,
      final_disruption_subtype: selectedAction === 'revise' && finalSubtype ? finalSubtype : null,
      final_event_ref: selectedAction === 'revise' && finalEventRef ? finalEventRef : null,
      reviewer_comment: reviewerComment || null,
    };

    onSubmit(decision);
  };

  return (
    <section className="bg-surface border border-line rounded-md mt-5" aria-labelledby="dec-h">
      <div className="flex justify-between items-center gap-3 p-3 px-4 border-b border-line-2">
        <h3 id="dec-h" className="font-head font-semibold text-base m-0 uppercase tracking-wider text-ink-2">
          Your decision
        </h3>
        <span className="text-muted text-xs flex items-center gap-1.5">
          <LucideIcons.Shield className="w-3.5 h-3.5" />
          Requires reviewer role (403 otherwise)
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4" role="radiogroup" aria-label="Decision action">
        <div
          className={`flex gap-3 p-3 px-4 border-2 rounded-md bg-surface cursor-pointer ${
            selectedAction === 'confirm' ? 'border-accent bg-accent-soft' : 'border-line'
          }`}
          role="radio"
          aria-checked={selectedAction === 'confirm'}
          onClick={() => setSelectedAction('confirm')}
        >
          <span
            className={`w-[18px] h-[18px] rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center ${
              selectedAction === 'confirm' ? 'border-accent' : 'border-ink-2'
            }`}
          >
            {selectedAction === 'confirm' && <span className="w-2 h-2 rounded-full bg-accent" />}
          </span>
          <div>
            <strong className="flex items-center gap-1.5">
              <CheckIcon className="w-4 h-4" />
              Confirm
            </strong>
            <span className="block text-sm text-ink-2">
              Commit the AI suggestion as the final classification and event binding.
            </span>
          </div>
        </div>

        <div
          className={`flex gap-3 p-3 px-4 border-2 rounded-md bg-surface cursor-pointer ${
            selectedAction === 'revise' ? 'border-accent bg-accent-soft' : 'border-line'
          }`}
          role="radio"
          aria-checked={selectedAction === 'revise'}
          onClick={() => setSelectedAction('revise')}
        >
          <span
            className={`w-[18px] h-[18px] rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center ${
              selectedAction === 'revise' ? 'border-accent' : 'border-ink-2'
            }`}
          >
            {selectedAction === 'revise' && <span className="w-2 h-2 rounded-full bg-accent" />}
          </span>
          <div>
            <strong className="flex items-center gap-1.5">
              <PencilIcon className="w-4 h-4" />
              Revise
            </strong>
            <span className="block text-sm text-ink-2">
              Commit your own overrides for type, subtype or event reference.
            </span>
          </div>
        </div>

        <div
          className={`flex gap-3 p-3 px-4 border-2 rounded-md bg-surface cursor-pointer ${
            selectedAction === 'reject' ? 'border-accent bg-accent-soft' : 'border-line'
          }`}
          role="radio"
          aria-checked={selectedAction === 'reject'}
          onClick={() => setSelectedAction('reject')}
        >
          <span
            className={`w-[18px] h-[18px] rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center ${
              selectedAction === 'reject' ? 'border-accent' : 'border-ink-2'
            }`}
          >
            {selectedAction === 'reject' && <span className="w-2 h-2 rounded-full bg-accent" />}
          </span>
          <div>
            <strong className="flex items-center gap-1.5">
              <XIcon className="w-4 h-4" />
              Reject
            </strong>
            <span className="block text-sm text-ink-2">
              Clear any binding commitment; the case stays open for another recommendation.
            </span>
          </div>
        </div>
      </div>

      {selectedAction === 'revise' && (
        <div className="mx-4 mb-4 p-4 border border-[#9DBFD8] rounded-md bg-[#F3F8FC]" aria-label="Revise overrides">
          <div className="grid grid-cols-3 gap-4">
            <div className="fld">
              <label htmlFor="f-type" className="block font-semibold text-sm mb-1.5">
                Final disruption type
              </label>
              <div
                className="flex items-center justify-between min-h-10 px-3 py-2 border border-[#6F7E8D] rounded bg-surface text-sm text-muted"
                id="f-type"
              >
                <input
                  type="text"
                  value={finalType}
                  onChange={(e) => setFinalType(e.target.value)}
                  placeholder="Select a type…"
                  className="bg-transparent border-none outline-none w-full text-ink"
                />
                <ChevronDownIcon className="w-4 h-4 flex-shrink-0" />
              </div>
            </div>
            <div className="fld">
              <label htmlFor="f-sub" className="block font-semibold text-sm mb-1.5">
                Final subtype
              </label>
              <div
                className="flex items-center justify-between min-h-10 px-3 py-2 border border-[#6F7E8D] rounded bg-surface text-sm text-muted"
                id="f-sub"
              >
                <input
                  type="text"
                  value={finalSubtype}
                  onChange={(e) => setFinalSubtype(e.target.value)}
                  placeholder="Select a subtype…"
                  className="bg-transparent border-none outline-none w-full text-ink"
                />
                <ChevronDownIcon className="w-4 h-4 flex-shrink-0" />
              </div>
            </div>
            <div className="fld">
              <label htmlFor="f-ref" className="block font-semibold text-sm mb-1.5">
                Final event reference
              </label>
              <div
                className="flex items-center justify-between min-h-10 px-3 py-2 border border-[#6F7E8D] rounded bg-surface text-sm"
                id="f-ref"
              >
                <SearchIcon className="w-4 h-4 text-muted flex-shrink-0" />
                <input
                  type="text"
                  value={finalEventRef}
                  onChange={(e) => setFinalEventRef(e.target.value)}
                  placeholder="Search events, e.g. EVT-2026-…"
                  className="bg-transparent border-none outline-none w-full text-ink ml-2"
                />
              </div>
            </div>
          </div>
          <div className="fld mt-4">
            <label htmlFor="f-cmt" className="block font-semibold text-sm mb-1.5">
              Reviewer comment
            </label>
            <textarea
              id="f-cmt"
              value={reviewerComment}
              onChange={(e) => setReviewerComment(e.target.value)}
              placeholder='Add the reason for your override, for example "Event is a quality hold, not a shortage."'
              className="flex items-start justify-between min-h-[84px] w-full px-3 py-2 border border-[#6F7E8D] rounded bg-surface text-sm text-ink resize-none"
              rows={3}
            />
          </div>
          <p className="text-xs text-muted mt-1.5">Revise requires at least one override.</p>
          {showValidationError && (
            <div className="flex items-center gap-1.5 mt-1.5 text-sm text-err font-semibold" role="alert">
              <CircleAlertIcon className="w-4 h-4" />
              Validation example: choose at least one override (type, subtype or event reference) before submitting a
              revision.
            </div>
          )}
        </div>
      )}

      <div className="flex justify-between items-center gap-5 p-4 border-t border-line-2 flex-wrap">
        <span className="text-muted text-[13px] flex items-center gap-1.5">
          <InfoIcon className="w-4 h-4" />
          Select an action and complete its fields to enable submission.
        </span>
        <div className="flex gap-3 items-center">
          <button
            className="inline-flex items-center gap-2 min-h-9 px-4 py-2 rounded border border-accent bg-surface text-accent font-semibold text-sm"
            type="button"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            className={`inline-flex items-center gap-2 min-h-9 px-4 py-2 rounded border font-semibold text-sm ${
              canSubmit() && !isSubmitting
                ? 'border-accent bg-accent text-white'
                : 'bg-[#DDE3E9] border-[#B7C2CD] text-[#4A5663] cursor-not-allowed'
            }`}
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit() || isSubmitting}
            aria-disabled={!canSubmit() || isSubmitting}
          >
            <SendIcon className="w-4 h-4" />
            {isSubmitting ? 'Submitting...' : 'Submit decision'}
          </button>
        </div>
      </div>
      <ul className="list-none m-0 p-3 px-4 pb-4 grid gap-1.5 text-sm text-ink-2">
        <li className="flex gap-2 items-start">
          <CheckIcon className="w-4 h-4 flex-shrink-0" />
          <span>
            <strong>Confirm</strong> commits the AI suggestion.
          </span>
        </li>
        <li className="flex gap-2 items-start">
          <PencilIcon className="w-4 h-4 flex-shrink-0" />
          <span>
            <strong>Revise</strong> commits your overrides.
          </span>
        </li>
        <li className="flex gap-2 items-start">
          <XIcon className="w-4 h-4 flex-shrink-0" />
          <span>
            <strong>Reject</strong> clears binding commitment and keeps the case available for another recommendation.
          </span>
        </li>
      </ul>
    </section>
  );
}
