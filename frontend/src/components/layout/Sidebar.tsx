/**
 * Sidebar navigation component matching wireframe design.
 * Shows main navigation links and case context panel.
 */

import { NavLink } from 'react-router-dom';
import * as LucideIcons from 'lucide-react';
import { Chip } from '../shared/Chip';

interface SidebarProps {
  currentPage?: string;
  caseContext?: {
    caseKey: string;
    status: string;
  };
}

export function Sidebar({ currentPage, caseContext }: SidebarProps) {
  const InboxIcon = LucideIcons.Inbox;
  const ScaleIcon = LucideIcons.Scale;
  const ListChecksIcon = LucideIcons.ListChecks;
  const HistoryIcon = LucideIcons.History;

  // Use case context if available, otherwise use placeholder for case-specific nav links
  const caseKey = caseContext?.caseKey || 'CASE-2026-001';

  // Navigation links for all implemented screens
  // /intake is case-independent; others are case-specific but with base route fallbacks
  const navLinks = [
    { id: 'intake', to: '/intake', icon: InboxIcon, label: 'Intake Cases' },
    { id: 'classification', to: caseContext ? `/cases/${caseKey}/classification` : '/classification', icon: ScaleIcon, label: 'Classification Review' },
    { id: 'vin-review', to: caseContext ? `/cases/${caseKey}/vins` : '/vin-review', icon: ListChecksIcon, label: 'VIN Review' },
    { id: 'audit', to: caseContext ? `/cases/${caseKey}/audit` : '/audit', icon: HistoryIcon, label: 'Audit Trail' },
  ];

  return (
    <aside className="bg-side text-side-ink py-6" aria-label="Primary">
      <nav>
        <ul className="list-none m-0 p-0">
          {navLinks.map((link) => {
            const isActive = currentPage === link.id;
            const Icon = link.icon;

            return (
              <li key={link.id}>
                <NavLink
                  to={link.to}
                  className={`flex items-center gap-3 px-6 py-3 text-side-ink no-underline font-semibold border-l-4 ${
                    isActive ? 'bg-side-active border-l-[#5FA8DC] text-white' : 'border-transparent'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {caseContext && (
        <div className="mt-8 mx-4 p-3 border border-[#33465A] rounded-md text-xs text-side-muted">
          Case context
          <b className="block text-white font-mono text-xs mt-1 mb-1.5">{caseContext.caseKey}</b>
          <Chip variant="ok" icon="CircleCheck">
            {caseContext.status}
          </Chip>
        </div>
      )}
    </aside>
  );
}
