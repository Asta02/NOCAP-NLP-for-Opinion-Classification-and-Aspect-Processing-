'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  MessageSquareText,
  Clock,
  CheckCircle2,
  TrendingUp,
  Upload,
} from 'lucide-react';
import { dashboardService } from '@/services';
import { AdminDashboardData } from '@/types/dashboard';
import { Loader2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';

const COLORS = ['#2563EB', '#10B981', '#F59E0B', '#EF4444'];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function AdminDashboardPage() {
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const result = await dashboardService.getAdminDashboard();
        setData(result);
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-error">{error || 'No data available'}</p>
      </div>
    );
  }

  const processingStatusData = [
    { name: 'Pending', value: data.processing_status.pending, color: '#F59E0B' },
    { name: 'Processing', value: data.processing_status.processing, color: '#2563EB' },
    { name: 'Completed', value: data.processing_status.completed, color: '#10B981' },
    { name: 'Failed', value: data.processing_status.failed, color: '#EF4444' },
  ];

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* KPI Cards */}
      <motion.div
        variants={container}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <motion.div variants={item}>
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-500">Total Companies</p>
                  <h3 className="text-3xl font-bold text-neutral-900 mt-1">
                    {data.total_companies}
                  </h3>
                </div>
                <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-500">Total Reviews</p>
                  <h3 className="text-3xl font-bold text-neutral-900 mt-1">
                    {data.total_reviews.toLocaleString()}
                  </h3>
                </div>
                <div className="w-12 h-12 rounded-xl bg-success-50 flex items-center justify-center">
                  <MessageSquareText className="w-6 h-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-500">Pending Jobs</p>
                  <h3 className="text-3xl font-bold text-neutral-900 mt-1">
                    {data.pending_jobs}
                  </h3>
                </div>
                <div className="w-12 h-12 rounded-xl bg-warning-50 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-warning" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-500">Completed Analysis</p>
                  <h3 className="text-3xl font-bold text-neutral-900 mt-1">
                    {data.completed_analysis.toLocaleString()}
                  </h3>
                </div>
                <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={item}>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Reviews Per Company</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data.reviews_per_company.slice(0, 6)} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis type="number" tick={{ fill: '#64748B', fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="company_name"
                    tick={{ fill: '#64748B', fontSize: 12 }}
                    width={100}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Processing Status</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={processingStatusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {processingStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-4">
                {processingStatusData.map((entry) => (
                  <div key={entry.name} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-sm text-neutral-600">{entry.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Monthly Imports Chart */}
      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Monthly Imported Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.monthly_imports}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis
                  dataKey="month"
                  tick={{ fill: '#64748B', fontSize: 12 }}
                />
                <YAxis tick={{ fill: '#64748B', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#2563EB"
                  strokeWidth={2}
                  dot={{ fill: '#2563EB', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, fill: '#2563EB' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </motion.div>

      {/* Latest Upload Activity */}
      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Latest Upload Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.latest_uploads.map((upload) => (
                <div
                  key={upload.upload_id}
                  className="flex items-center justify-between p-4 rounded-lg bg-neutral-50 hover:bg-neutral-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-white border border-neutral-200 flex items-center justify-center">
                      <Upload className="w-5 h-5 text-neutral-400" />
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900">{upload.company_name}</p>
                      <p className="text-sm text-neutral-500">
                        {upload.filename} ({upload.records} records)
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge
                      variant={
                        upload.status === 'completed'
                          ? 'default'
                          : upload.status === 'processing'
                          ? 'secondary'
                          : 'destructive'
                      }
                      className={
                        upload.status === 'completed'
                          ? 'bg-success-50 text-success-700 hover:bg-success-50'
                          : upload.status === 'processing'
                          ? 'bg-primary-50 text-primary-700 hover:bg-primary-50'
                          : 'bg-error-50 text-error-700 hover:bg-error-50'
                      }
                    >
                      {upload.status}
                    </Badge>
                    <span className="text-sm text-neutral-400">
                      {new Date(upload.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
