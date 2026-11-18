/**
 * Main layout component wrapping authenticated pages.
 * Combines Header, Sidebar, and main content area.
 */

import { ReactNode } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: ReactNode;
  currentPage?: string;
  caseContext?: {
    caseKey: string;
    status: string;
  };
}

export function Layout({ children, currentPage, caseContext }: LayoutProps) {
  return (
    <div className="min-h-screen bg-canvas">
      <Header />
      <div className="grid grid-cols-[240px_1fr] items-stretch w-full">
        <Sidebar currentPage={currentPage} caseContext={caseContext} />
        <main className="p-6 pb-8 min-w-0">{children}</main>
      </div>
    </div>
  );
}
