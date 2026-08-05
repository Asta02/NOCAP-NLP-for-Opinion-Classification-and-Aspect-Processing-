'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/hooks/use-auth';
import {
  LayoutDashboard,
  PlusCircle,
  History,
  LogOut,
  ChevronLeft,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface CompanySidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  companyName?: string;
}

const menuItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'New Review',
    href: '/new-review',
    icon: PlusCircle,
  },
  {
    title: 'Review History',
    href: '/review-history',
    icon: History,
  },
];

export function CompanySidebar({
  collapsed,
  onToggle,
  companyName,
}: CompanySidebarProps) {
  const pathname = usePathname();
  const { logout } = useAuth(); // ✅ Hook inside component

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 80 : 260 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-screen bg-white border-r border-neutral-200 z-40 flex flex-col"
    >
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-neutral-100">
        <AnimatePresence mode="wait">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="flex items-center gap-2"
            >
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-white" />
              </div>

              <div className="flex flex-col">
                <span className="text-xs font-semibold text-neutral-900 truncate max-w-[150px]">
                  {companyName || 'Company'}
                </span>
                <span className="text-[10px] text-neutral-400">
                  Decision Support
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {collapsed && (
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center mx-auto">
            <BarChart3 className="w-4 h-4 text-white" />
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 overflow-y-auto scrollbar-thin">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'sidebar-link',
                    isActive && 'sidebar-link-active',
                    collapsed && 'justify-center px-0'
                  )}
                  title={collapsed ? item.title : undefined}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />

                  <AnimatePresence mode="wait">
                    {!collapsed && (
                      <motion.span
                        initial={{ opacity: 0, x: -5 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -5 }}
                        transition={{ duration: 0.2 }}
                      >
                        {item.title}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-neutral-100">
        <button
          onClick={logout} // ✅ Actually calls logout
          className={cn(
            'sidebar-link w-full text-error hover:bg-error-50',
            collapsed && 'justify-center px-0'
          )}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />

          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>

      {/* Collapse */}
      <div className="p-3 border-t border-neutral-100">
        <button
          onClick={onToggle}
          className={cn(
            'sidebar-link w-full',
            collapsed && 'justify-center px-0'
          )}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft
            className={cn('w-5 h-5', collapsed && 'rotate-180')}
          />

          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Collapse
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
}