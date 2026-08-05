'use client';

import { useAuth } from '@/hooks/use-auth';
import { usePathname } from 'next/navigation';
import { Menu, LogOut, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface AdminHeaderProps {
  onMenuClick: () => void;
  sidebarCollapsed: boolean;
}

const pageTitles: Record<string, string> = {
  '/admin/dashboard': 'Dashboard',
  '/admin/companies': 'Companies',
  '/admin/reviews': 'Reviews',
  '/admin/ai-processing': 'AI Processing',
};

export function AdminHeader({ onMenuClick, sidebarCollapsed }: AdminHeaderProps) {
  const pathname = usePathname();
  const pageTitle = pageTitles[pathname] || 'Admin';

  const { logout } = useAuth();

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
        <h1 className="text-lg font-semibold text-neutral-900">{pageTitle}</h1>
      </div>

      <div className="flex items-center gap-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-10 w-10 rounded-full">
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-primary text-white text-sm font-medium">
                  A
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium text-neutral-900">Administrator</p>
                <p className="text-xs text-neutral-500">admin@system.local</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="text-error focus:text-error">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
