/**
 * Header component matching wireframe design.
 * Shows brand, environment tag, user info, role, and sign out.
 */

import { Radar, User as UserIcon, ShieldCheck, LogOut } from 'lucide-react';
import { useAuth } from '../../lib/auth-context';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between min-h-[60px] px-s5 bg-[#0F1923] text-white border-b-[3px] border-accent">
      <div className="flex items-center gap-s3">
        <span className="w-[34px] h-[34px] rounded-md bg-accent flex items-center justify-center" aria-hidden="true">
          <Radar className="w-5 h-5" />
        </span>
        <span className="font-head font-bold text-xl tracking-wider">Disruption Manager RIM</span>
        <span className="ml-s3 px-[10px] py-[2px] border border-[#6F8397] rounded text-xs text-[#D5DFE8]">
          MVP demo · mocked integrations
        </span>
      </div>
      <div className="flex items-center gap-s4 text-sm">
        <span className="flex items-center gap-2">
          <UserIcon className="w-4 h-4" />
          {user?.full_name || user?.email}
        </span>
        <span className="inline-flex items-center gap-[6px] px-[10px] py-[3px] rounded bg-[#E4EEF7] text-[#12405F] font-semibold text-xs">
          <ShieldCheck className="w-[14px] h-[14px]" />
          {user?.role}
        </span>
        <button
          onClick={logout}
          className="inline-flex items-center gap-[6px] px-3 py-[6px] border border-[#6F8397] rounded bg-transparent text-white text-sm"
          type="button"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </header>
  );
}
