'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  ColumnDef,
  flexRender,
} from '@tanstack/react-table';
import { Plus, Search, SlidersHorizontal, Building2, Loader2 } from 'lucide-react';
import { companyService } from '@/services';
import { Company, CompanyStatus } from '@/types/company';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import { CompanyFormModal } from '@/components/companies/company-form-modal';
import { ConfirmDialog } from '@/components/shared/confirm-dialog';
import { toast } from 'sonner';

const statusColors: Record<CompanyStatus, string> = {
  active: 'bg-success-50 text-success-700',
  inactive: 'bg-neutral-100 text-neutral-600',
  pending: 'bg-warning-50 text-warning-700',
};

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [industryFilter, setIndustryFilter] = useState<string>('all');
  const [industries, setIndustries] = useState<string[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingCompany, setDeletingCompany] = useState<Company | null>(null);

  const fetchCompanies = useCallback(async () => {
    setLoading(true);
    try {
      const result = await companyService.getAll({
        page,
        limit: 10,
        search: search || undefined,
        status: statusFilter !== 'all' ? (statusFilter as CompanyStatus) : undefined,
        industry: industryFilter !== 'all' ? industryFilter : undefined,
      });
      setCompanies(result.companies);
      setTotal(result.total);
    } catch (error) {
      toast.error('Failed to load companies');
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter, industryFilter]);

  useEffect(() => {
    const fetchIndustries = async () => {
      try {
        const result = await companyService.getIndustries();
        setIndustries(result);
      } catch (error) {
        console.error('Failed to load industries');
      }
    };
    fetchIndustries();
  }, []);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const handleCreate = () => {
    setEditingCompany(null);
    setModalOpen(true);
  };

  const handleEdit = (company: Company) => {
    setEditingCompany(company);
    setModalOpen(true);
  };

  const handleDelete = (company: Company) => {
    setDeletingCompany(company);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!deletingCompany) return;
    try {
      await companyService.delete(deletingCompany.company_id);
      toast.success('Company deleted successfully');
      fetchCompanies();
    } catch (error) {
      toast.error('Failed to delete company');
    } finally {
      setDeleteDialogOpen(false);
      setDeletingCompany(null);
    }
  };

  const handleFormSuccess = () => {
    setModalOpen(false);
    setEditingCompany(null);
    fetchCompanies();
    toast.success(editingCompany ? 'Company updated successfully' : 'Company created successfully');
  };

  const columns: ColumnDef<Company>[] = [
    {
      accessorKey: 'company_name',
      header: 'Company',
      cell: ({ row }) => {
        const company = row.original;
        return (
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarImage src={company.logo_url || ''} alt={company.company_name} />
              <AvatarFallback className="bg-primary-50 text-primary-600">
                {company.company_name.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium text-neutral-900">{company.company_name}</p>
              <p className="text-sm text-neutral-500">{company.email}</p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'industry',
      header: 'Industry',
      cell: ({ row }) => (
        <span className="text-neutral-600">{row.getValue('industry')}</span>
      ),
    },
    {
      accessorKey: 'username',
      header: 'Username',
      cell: ({ row }) => (
        <code className="px-2 py-1 rounded bg-neutral-100 text-sm text-neutral-600">
          {row.getValue('username')}
        </code>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const status = row.getValue('status') as CompanyStatus;
        return (
          <Badge className={statusColors[status]}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Created',
      cell: ({ row }) => (
        <span className="text-neutral-500">
          {new Date(row.getValue('created_at')).toLocaleDateString()}
        </span>
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => {
        const company = row.original;
        return (
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleEdit(company)}
              className="text-primary hover:text-primary-700 hover:bg-primary-50"
            >
              Edit
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleDelete(company)}
              className="text-error hover:text-error-600 hover:bg-error-50"
            >
              Delete
            </Button>
          </div>
        );
      },
    },
  ];

  const totalPages = Math.ceil(total / 10);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader className="pb-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <CardTitle className="text-lg font-semibold">Companies Management</CardTitle>
            <Button onClick={handleCreate} className="bg-primary hover:bg-primary-700">
              <Plus className="w-4 h-4 mr-2" />
              Add Company
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <Input
                placeholder="Search companies..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Select value={industryFilter} onValueChange={(v) => { setIndustryFilter(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Industries</SelectItem>
                {industries.map((industry) => (
                  <SelectItem key={industry} value={industry}>
                    {industry}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-16 rounded-lg" />
              ))}
            </div>
          ) : companies.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Building2 className="w-12 h-12 text-neutral-300 mb-4" />
              <h3 className="text-lg font-medium text-neutral-900">No companies found</h3>
              <p className="text-neutral-500 mt-1">
                {search || statusFilter !== 'all' || industryFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Get started by adding your first company'}
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-lg border border-neutral-200 overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-neutral-50">
                      {columns.map((column, idx) => (
                        <TableHead key={column.id || `col-${idx}`} className="font-medium">
                          {column.header as string}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {companies.map((company) => (
                      <TableRow key={company.company_id} className="hover:bg-neutral-50">
                        {columns.map((column, idx) => (
                          <TableCell key={column.id || `col-${idx}`}>
                            {flexRender(column.cell, { row: { original: company, getValue: (key: string) => company[key as keyof Company] } } as any)}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-neutral-500">
                  Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, total)} of {total} companies
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                      const pageNum = i + 1;
                      return (
                        <Button
                          key={pageNum}
                          variant={page === pageNum ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setPage(pageNum)}
                          className={page === pageNum ? 'bg-primary' : ''}
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                    {totalPages > 5 && <span className="px-2">...</span>}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page >= totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <CompanyFormModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        company={editingCompany}
        onSuccess={handleFormSuccess}
      />

      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title="Delete Company"
        description={`Are you sure you want to delete "${deletingCompany?.company_name}"? This action cannot be undone.`}
        onConfirm={confirmDelete}
        confirmText="Delete"
        variant="destructive"
      />
    </motion.div>
  );
}
