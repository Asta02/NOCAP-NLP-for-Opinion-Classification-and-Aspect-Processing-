'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, MessageSquareText, Eye, X } from 'lucide-react';
import { reviewService } from '@/services';
import { Review, SentimentType } from '@/types/review';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';

const sentimentColors: Record<SentimentType, string> = {
  Positive: 'bg-success-50 text-success-700',
  Neutral: 'bg-warning-50 text-warning-700',
  Negative: 'bg-error-50 text-error-700',
};

const statusColors: Record<string, string> = {
  analyzed: 'bg-success-50 text-success-700',
  pending: 'bg-warning-50 text-warning-700',
  imported: 'bg-primary-50 text-primary-700',
};

const ratingLabels: Record<string, string> = {
  overall_rating: 'Overall Rating',
  work_life_balance: 'Work-Life Balance',
  culture_values: 'Culture & Values',
  career_opportunities: 'Career Opportunities',
  compensation_benefits: 'Compensation & Benefits',
  senior_management: 'Senior Management',
};

export default function AdminReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    try {
      const result = await reviewService.getAdminAll({
        page,
        limit: 15,
        search: search || undefined,
        sentiment: sentimentFilter !== 'all' ? (sentimentFilter as SentimentType) : undefined,
      });
      setReviews(result.reviews);
      setTotal(result.total);
    } catch (error) {
      console.error('Failed to load reviews');
    } finally {
      setLoading(false);
    }
  }, [page, search, sentimentFilter]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  const handleViewDetails = (review: Review) => {
    setSelectedReview(review);
    setDetailsOpen(true);
  };

  const totalPages = Math.ceil(total / 15);

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-4 h-4 ${star <= rating ? 'text-warning fill-warning' : 'text-neutral-200'}`}
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M10 15l-5.878 3.09 1.123-6.542L2.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.638 1.123 6.542z" />
          </svg>
        ))}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold">All Reviews</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <Input
                placeholder="Search by company, job title, or summary..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="pl-10"
              />
            </div>
            <Select value={sentimentFilter} onValueChange={(v) => { setSentimentFilter(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Sentiment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sentiments</SelectItem>
                <SelectItem value="Positive">Positive</SelectItem>
                <SelectItem value="Neutral">Neutral</SelectItem>
                <SelectItem value="Negative">Negative</SelectItem>
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
          ) : reviews.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <MessageSquareText className="w-12 h-12 text-neutral-300 mb-4" />
              <h3 className="text-lg font-medium text-neutral-900">No reviews found</h3>
              <p className="text-neutral-500 mt-1">
                {search || sentimentFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'No reviews have been submitted yet'}
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-lg border border-neutral-200 overflow-hidden">
                <table className="w-full">
                  <thead className="bg-neutral-50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Company</th>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Date</th>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Job Title</th>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Summary</th>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Rating</th>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Sentiment</th>
                      <th className="text-left px-4 py-3 font-medium text-sm text-neutral-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100">
                    {reviews.map((review) => (
                      <tr key={review.review_id} className="hover:bg-neutral-50">
                        <td className="px-4 py-3">
                          <span className="font-medium text-neutral-900">{review.company_name}</span>
                        </td>
                        <td className="px-4 py-3 text-neutral-500">
                          {new Date(review.review_date).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 text-neutral-600">{review.job_title}</td>
                        <td className="px-4 py-3 max-w-xs">
                          <p className="text-sm text-neutral-600 truncate">{review.summary}</p>
                        </td>
                        <td className="px-4 py-3">{renderStars(review.overall_rating)}</td>
                        <td className="px-4 py-3">
                          <Badge className={sentimentColors[review.sentiment]}>
                            {review.sentiment}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewDetails(review)}
                            className="text-primary hover:text-primary-700 hover:bg-primary-50"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-neutral-500">
                  Showing {(page - 1) * 15 + 1} to {Math.min(page * 15, total)} of {total} reviews
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

      {/* Review Details Dialog */}
      <Dialog open={detailsOpen} onOpenChange={setDetailsOpen}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold">Review Details</DialogTitle>
          </DialogHeader>

          {selectedReview && (
            <div className="space-y-6 mt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Company</p>
                  <p className="font-medium text-neutral-900">{selectedReview.company_name}</p>
                </div>
                <Badge className={sentimentColors[selectedReview.sentiment]}>
                  {selectedReview.sentiment}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-neutral-500">Review Date</p>
                  <p className="font-medium text-neutral-900">
                    {new Date(selectedReview.review_date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Job Title</p>
                  <p className="font-medium text-neutral-900">{selectedReview.job_title}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Employment Status</p>
                  <p className="font-medium text-neutral-900">{selectedReview.employment_status}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Status</p>
                  <Badge className={statusColors[selectedReview.status]}>
                    {selectedReview.status}
                  </Badge>
                </div>
              </div>

              <Separator />

              <div>
                <p className="text-sm text-neutral-500 mb-2">Summary</p>
                <p className="text-neutral-900">{selectedReview.summary}</p>
              </div>

              <div>
                <p className="text-sm text-neutral-500 mb-2">Full Review</p>
                <p className="text-neutral-900 whitespace-pre-wrap">{selectedReview.review_text}</p>
              </div>

              <Separator />

              <div>
                <p className="text-sm text-neutral-500 mb-3">Ratings</p>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(ratingLabels).map(([key, label]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-neutral-600">{label}</span>
                      <div className="flex items-center gap-2">
                        {renderStars(selectedReview[key as keyof Review] as number)}
                        <span className="text-neutral-900 font-medium">
                          {selectedReview[key as keyof Review]}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
