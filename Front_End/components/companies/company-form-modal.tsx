'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2, Upload, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { companyService } from '@/services';
import { Company, CompanyStatus } from '@/types/company';

const companySchema = z.object({
  company_name: z.string().min(1, 'Company name is required'),
  industry: z.string().min(1, 'Industry is required'),
  email: z.string().email('Valid email is required'),
  username: z.string().min(1, 'Username is required'),
  password: z.string().optional(),
  logo_url: z.string().optional(),
  status: z.enum(['active', 'inactive', 'pending']),
});

type CompanyFormData = z.infer<typeof companySchema>;

const industries = [
  'Technology',
  'E-Commerce',
  'Financial Services',
  'Healthcare',
  'Manufacturing',
  'Retail',
  'Consulting',
  'Media & Entertainment',
  'Automotive',
  'Telecommunications',
];

interface CompanyFormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  company: Company | null;
  onSuccess: () => void;
}

export function CompanyFormModal({ open, onOpenChange, company, onSuccess }: CompanyFormModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isEditing = !!company;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<CompanyFormData>({
    resolver: zodResolver(companySchema),
    defaultValues: company
      ? {
          company_name: company.company_name,
          industry: company.industry,
          email: company.email,
          username: company.username,
          password: '',
          logo_url: company.logo_url || '',
          status: company.status,
        }
      : {
          company_name: '',
          industry: '',
          email: '',
          username: '',
          password: '',
          logo_url: '',
          status: 'pending',
        },
  });

  React.useEffect(() => {
    if (company) {
      reset({
        company_name: company.company_name,
        industry: company.industry,
        email: company.email,
        username: company.username,
        password: '',
        logo_url: company.logo_url || '',
        status: company.status,
      });
    } else {
      reset({
        company_name: '',
        industry: '',
        email: '',
        username: '',
        password: '',
        logo_url: '',
        status: 'pending',
      });
    }
  }, [company, reset]);

  const onSubmit = async (data: CompanyFormData) => {
    setIsSubmitting(true);
    try {
      if (isEditing) {
        await companyService.update(company.company_id, {
          company_name: data.company_name,
          industry: data.industry,
          email: data.email,
          username: data.username,
          password: data.password || undefined,
          logo_url: data.logo_url || undefined,
          status: data.status,
        });
      } else {
        if (!data.password) {
          throw new Error('Password is required for new companies');
        }
        await companyService.create({
          company_name: data.company_name,
          industry: data.industry,
          email: data.email,
          username: data.username,
          password: data.password,
          logo_url: data.logo_url || undefined,
        });
      }
      onSuccess();
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const status = watch('status');
  const industry = watch('industry');

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">
            {isEditing ? 'Edit Company' : 'Add New Company'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 mt-4">
          <div className="space-y-2">
            <Label htmlFor="company_name">Company Name *</Label>
            <Input
              id="company_name"
              placeholder="Enter company name"
              {...register('company_name')}
            />
            {errors.company_name && (
              <p className="text-xs text-error">{errors.company_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="industry">Industry *</Label>
            <Select value={industry} onValueChange={(v) => setValue('industry', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select industry" />
              </SelectTrigger>
              <SelectContent>
                {industries.map((ind) => (
                  <SelectItem key={ind} value={ind}>
                    {ind}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.industry && (
              <p className="text-xs text-error">{errors.industry.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                placeholder="company@example.com"
                {...register('email')}
              />
              {errors.email && (
                <p className="text-xs text-error">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">Username *</Label>
              <Input
                id="username"
                placeholder="Enter username"
                {...register('username')}
              />
              {errors.username && (
                <p className="text-xs text-error">{errors.username.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">
              Password {isEditing ? '(leave empty to keep current)' : '*'}
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter password"
              {...register('password')}
            />
            {errors.password && (
              <p className="text-xs text-error">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="logo_url">Logo URL (optional)</Label>
            <Input
              id="logo_url"
              placeholder="https://example.com/logo.png"
              {...register('logo_url')}
            />
          </div>

          {isEditing && (
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={status} onValueChange={(v) => setValue('status', v as CompanyStatus)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-primary hover:bg-primary-700"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {isEditing ? 'Updating...' : 'Creating...'}
                </>
              ) : (
                isEditing ? 'Update Company' : 'Create Company'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
