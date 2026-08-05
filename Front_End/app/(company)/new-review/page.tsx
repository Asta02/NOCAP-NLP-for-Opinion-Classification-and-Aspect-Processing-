'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Save, X, Loader2, Calendar, Briefcase, User, Star, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { reviewService } from '@/services';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { toast } from 'sonner';

const reviewSchema = z.object({
  review_date: z.string().min(1, 'Review date is required'),
  employment_status: z.enum(['Current Employee', 'Former Employee']),
  job_title: z.string().min(1, 'Job title is required'),
  summary: z.string().min(10, 'Summary must be at least 10 characters'),
  review_text: z.string().min(50, 'Review must be at least 50 characters'),
  work_life_balance: z.number().min(1).max(5),
  culture_values: z.number().min(1).max(5),
  career_opportunities: z.number().min(1).max(5),
  compensation_benefits: z.number().min(1).max(5),
  senior_management: z.number().min(1).max(5),
});

type ReviewFormData = z.infer<typeof reviewSchema>;

const ratingCategories = [
  { key: 'work_life_balance', label: 'Work-Life Balance', description: 'Balance between work and personal life' },
  { key: 'culture_values', label: 'Culture & Values', description: 'Company culture and core values' },
  { key: 'career_opportunities', label: 'Career Opportunities', description: 'Growth and advancement prospects' },
  { key: 'compensation_benefits', label: 'Compensation & Benefits', description: 'Salary, perks, and benefits package' },
  { key: 'senior_management', label: 'Senior Management', description: 'Leadership quality and transparency' },
];

export default function NewReviewPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ReviewFormData>({
    resolver: zodResolver(reviewSchema),
    defaultValues: {
      review_date: new Date().toISOString().split('T')[0],
      employment_status: 'Current Employee',
      job_title: '',
      summary: '',
      review_text: '',
      work_life_balance: 3,
      culture_values: 3,
      career_opportunities: 3,
      compensation_benefits: 3,
      senior_management: 3,
    },
  });

  const workLifeBalance = watch('work_life_balance');
  const cultureValues = watch('culture_values');
  const careerOpportunities = watch('career_opportunities');
  const compensationBenefits = watch('compensation_benefits');
  const seniorManagement = watch('senior_management');
  const employmentStatus = watch('employment_status');

  // Calculate overall rating as average of category ratings
  const overallRating = (
    (workLifeBalance + cultureValues + careerOpportunities + compensationBenefits + seniorManagement) / 5
  ).toFixed(1);

  const ratingValues: Record<string, number> = {
    work_life_balance: workLifeBalance,
    culture_values: cultureValues,
    career_opportunities: careerOpportunities,
    compensation_benefits: compensationBenefits,
    senior_management: seniorManagement,
  };

  const onSubmit = async (data: ReviewFormData) => {
    setIsSubmitting(true);
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const companyId = user.company?.company_id;

      if (!companyId) {
        toast.error('Company ID not found. Please log in again.');
        return;
      }

      // Calculate overall rating
      const calculatedOverallRating = Math.round(
        (data.work_life_balance + data.culture_values + data.career_opportunities +
         data.compensation_benefits + data.senior_management) / 5
      );

      await reviewService.create({
        review_date: data.review_date,
        employment_status: data.employment_status,
        job_title: data.job_title,
        summary: data.summary,
        review_text: data.review_text,
        overall_rating: calculatedOverallRating,
        work_life_balance: Math.round(data.work_life_balance),
        culture_values: Math.round(data.culture_values),
        career_opportunities: Math.round(data.career_opportunities),
        compensation_benefits: Math.round(data.compensation_benefits),
        senior_management: Math.round(data.senior_management),
      }, companyId);

      toast.success('Review submitted successfully');
      router.replace('/review-history');
    } catch (error) {
      toast.error('Failed to submit review');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStars = (rating: number, size: 'sm' | 'lg' = 'sm') => {
    const starSize = size === 'lg' ? 'w-8 h-8' : 'w-4 h-4';
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${starSize} ${star <= rating ? 'text-amber-400 fill-amber-400' : 'text-neutral-200'}`}
          />
        ))}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-3xl mx-auto"
    >
      <Card className="shadow-xl border-0 overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-primary to-primary-700 text-white pb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <CardTitle className="text-2xl font-bold">Share Your Experience</CardTitle>
          </div>
          <CardDescription className="text-primary-100 text-base">
            Your honest feedback helps improve workplace culture for everyone
          </CardDescription>
        </CardHeader>

        <CardContent className="p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-10">
            {/* Employment Details */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 pb-3 border-b border-neutral-100">
                <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
                  <User className="w-4 h-4 text-primary" />
                </div>
                <h3 className="font-semibold text-neutral-900 text-lg">Employment Details</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="review_date" className="text-sm font-medium text-neutral-700">Review Date</Label>
                  <Input
                    id="review_date"
                    type="date"
                    className="h-12"
                    {...register('review_date')}
                  />
                  {errors.review_date && (
                    <p className="text-xs text-red-500">{errors.review_date.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="employment_status" className="text-sm font-medium text-neutral-700">Status</Label>
                  <Select
                    value={employmentStatus}
                    onValueChange={(v) => setValue('employment_status', v as 'Current Employee' | 'Former Employee')}
                  >
                    <SelectTrigger className="h-12">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Current Employee">Current Employee</SelectItem>
                      <SelectItem value="Former Employee">Former Employee</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="job_title" className="text-sm font-medium text-neutral-700">Job Title</Label>
                  <Input
                    id="job_title"
                    placeholder="e.g. Software Engineer"
                    className="h-12"
                    {...register('job_title')}
                  />
                  {errors.job_title && (
                    <p className="text-xs text-red-500">{errors.job_title.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Your Feedback */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 pb-3 border-b border-neutral-100">
                <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
                  <Briefcase className="w-4 h-4 text-primary" />
                </div>
                <h3 className="font-semibold text-neutral-900 text-lg">Your Feedback</h3>
              </div>

              <div className="space-y-2">
                <Label htmlFor="summary" className="text-sm font-medium text-neutral-700">Summary</Label>
                <Input
                  id="summary"
                  placeholder="Brief summary of your experience"
                  className="h-12 text-base"
                  {...register('summary')}
                />
                {errors.summary && (
                  <p className="text-xs text-red-500">{errors.summary.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="review_text" className="text-sm font-medium text-neutral-700">Detailed Review</Label>
                <Textarea
                  id="review_text"
                  placeholder="Share your detailed experience. What did you enjoy? What could be improved?"
                  rows={6}
                  className="text-base resize-none"
                  {...register('review_text')}
                />
                {errors.review_text && (
                  <p className="text-xs text-red-500">{errors.review_text.message}</p>
                )}
              </div>
            </div>

            {/* Category Ratings */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 pb-3 border-b border-neutral-100">
                <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center">
                  <Star className="w-4 h-4 text-amber-500" />
                </div>
                <h3 className="font-semibold text-neutral-900 text-lg">Category Ratings</h3>
              </div>

              {/* Overall Rating Display */}
              <div className="bg-gradient-to-r from-amber-50 to-primary-50 rounded-xl p-6 border border-amber-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600">Overall Rating</p>
                    <p className="text-xs text-neutral-400 mt-1">Automatically calculated from categories below</p>
                  </div>
                  <div className="flex items-center gap-4">
                    {renderStars(parseFloat(overallRating), 'lg')}
                    <span className="text-4xl font-bold text-primary">{overallRating}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-8">
                {ratingCategories.map((cat) => (
                  <div key={cat.key} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-sm font-medium text-neutral-700">{cat.label}</Label>
                        <p className="text-xs text-neutral-400">{cat.description}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        {renderStars(ratingValues[cat.key])}
                        <span className="text-lg font-semibold text-neutral-800 w-8 text-right">
                          {ratingValues[cat.key].toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <Slider
                      value={[ratingValues[cat.key]]}
                      onValueChange={(vals) => setValue(cat.key as keyof ReviewFormData, vals[0] as number)}
                      min={1}
                      max={5}
                      step={1}
                      className="py-2"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-4 pt-6 border-t border-neutral-100">
              <Button
                type="button"
                variant="outline"
                size="lg"
                onClick={() => router.back()}
                className="px-8"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
                size="lg"
                className="bg-primary hover:bg-primary-700 px-8"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Submit Review
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
