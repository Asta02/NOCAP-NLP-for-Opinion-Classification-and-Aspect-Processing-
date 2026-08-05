'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { Menu, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CompanyHeaderProps {
  onMenuClick: () => void;
  sidebarCollapsed: boolean;
  companyName?: string;
}

const pageTitles: Record<string, string> = {
  '/dashboard': 'Decision Support Dashboard',
  '/new-review': 'Submit New Review',
  '/review-history': 'Review History',
};

export function CompanyHeader({ onMenuClick, sidebarCollapsed, companyName }: CompanyHeaderProps) {
  const pathname = usePathname();
  const pageTitle = pageTitles[pathname] || 'Dashboard';

  return (
    <header
      className="fixed top-0 right-0 h-16 bg-white/80 backdrop-blur-sm border-b border-neutral-200 z-30 flex items-center justify-between px-4 lg:px-6"
      style={{ left: sidebarCollapsed ? 80 : 260 }}
    >
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-lg font-semibold text-neutral-900">{pageTitle}</h1>
          {companyName && (
            <p className="text-sm text-neutral-500 flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5" />
              {companyName}
            </p>
          )}
        </div>
      </div>
    </header>
  );
}
