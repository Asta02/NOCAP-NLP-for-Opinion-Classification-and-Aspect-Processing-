'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { CompanySidebar } from '@/components/layout/company-sidebar';
import { CompanyHeader } from '@/components/layout/company-header';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { Loader2 } from 'lucide-react';

export default function CompanyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const companyName = user?.company?.company_name || '';

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }

    if (user?.role !== 'company') {
      router.replace('/admin/dashboard');
      return;
    }
  }, [isLoading, isAuthenticated, user, router]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setSidebarCollapsed(true);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (isLoading || !isAuthenticated || user?.role !== 'company') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-neutral-50 via-white to-primary-50/30">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-primary mx-auto" />
          <p className="mt-4 text-neutral-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-white to-primary-50/30">
      <div className="hidden lg:block">
        <CompanySidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          companyName={companyName}
        />
      </div>

      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="left" className="p-0 w-64">
          <CompanySidebar
            collapsed={false}
            onToggle={() => setMobileMenuOpen(false)}
            companyName={companyName}
          />
        </SheetContent>
      </Sheet>

      <CompanyHeader
        onMenuClick={() => setMobileMenuOpen(true)}
        sidebarCollapsed={sidebarCollapsed}
        companyName={companyName}
      />

      <main
        className="pt-16 min-h-screen transition-all duration-300"
        style={{ paddingLeft: sidebarCollapsed ? 80 : 260 }}
      >
        <div className="p-4 lg:p-6">{children}</div>
      </main>
    </div>
  );
}
