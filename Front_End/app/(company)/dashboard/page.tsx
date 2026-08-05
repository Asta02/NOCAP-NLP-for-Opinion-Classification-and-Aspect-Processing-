'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Star,
  ThumbsUp,
  Smile,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Loader2,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Target,
  Zap,
  MessageSquare,
} from 'lucide-react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { dashboardService } from '@/services';
import { DashboardData } from '@/types/dashboard';
import { DecisionSupportData, getHealthCategory } from '@/types/decision-support';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

const COLORS = {
  Positive: '#10B981',
  Neutral: '#F59E0B',
  Negative: '#EF4444',
  primary: '#2563EB',
};

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function CompanyDashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [decisionData, setDecisionData] = useState<DecisionSupportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const companyId = user.company?.company_id || 1;

        const [dashboard, decision] = await Promise.all([
          dashboardService.getCompanyDashboard(companyId),
          dashboardService.getDecisionSupport(companyId),
        ]);

        setDashboardData(dashboard);
        setDecisionData(decision);
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-56 rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  if (error || !dashboardData || !decisionData) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-error">{error || 'No data available'}</p>
      </div>
    );
  }

  const healthCategory = getHealthCategory(decisionData.organization_health);

  const employeeMoodData = [
    { name: 'Positive', value: dashboardData.employee_mood.positive, color: COLORS.Positive },
    { name: 'Neutral', value: dashboardData.employee_mood.neutral, color: COLORS.Neutral },
    { name: 'Negative', value: dashboardData.employee_mood.negative, color: COLORS.Negative },
  ];

  const priorityConfig = {
    HIGH: { bg: 'bg-gradient-to-br from-error-50 to-error-100/50', text: 'text-error-700', border: 'border-error-200', icon: Zap },
    MEDIUM: { bg: 'bg-gradient-to-br from-warning-50 to-warning-100/50', text: 'text-warning-700', border: 'border-warning-200', icon: Target },
    LOW: { bg: 'bg-gradient-to-br from-success-50 to-success-100/50', text: 'text-success-700', border: 'border-success-200', icon: CheckCircle2 },
  };

  const renderStars = (rating: number) => (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`w-4 h-4 ${star <= rating ? 'text-amber-400 fill-amber-400' : 'text-neutral-200'}`}
        />
      ))}
    </div>
  );

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Decision Support Panel - Main Feature */}
      <motion.div variants={item}>
        <Card className="bg-gradient-to-br from-primary-700 via-primary-800 to-darkblue-900 text-white border-0 shadow-2xl overflow-hidden">
          <CardContent className="p-0">
            <div className="flex flex-col lg:flex-row">
              {/* Left: Health Score */}
              <div className="lg:w-72 flex-shrink-0 p-8 bg-white/5">
                <div className="flex items-center gap-2 mb-6">
                  <Activity className="w-5 h-5 text-primary-200" />
                  <span className="text-primary-100 text-sm font-medium">Organization Health</span>
                </div>
                <div className="relative w-44 h-44 mx-auto">
                  <svg className="absolute w-full h-full transform -rotate-90">
                    <circle cx="88" cy="88" r="78" stroke="rgba(255,255,255,0.15)" strokeWidth="14" fill="none" />
                    <circle
                      cx="88" cy="88" r="78"
                      stroke={healthCategory.color}
                      strokeWidth="14"
                      fill="none"
                      strokeDasharray={`${decisionData.organization_health * 4.9} 490`}
                      strokeLinecap="round"
                      className="drop-shadow-lg"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-5xl font-bold tracking-tight">{decisionData.organization_health}%</span>
                    <span className="text-lg font-medium mt-1" style={{ color: healthCategory.color }}>
                      {healthCategory.label}
                    </span>
                  </div>
                </div>
                <div className="mt-6 flex items-center justify-center gap-2">
                  {decisionData.employee_satisfaction === 'High' ? (
                    <TrendingUp className="w-4 h-4 text-success-400" />
                  ) : decisionData.employee_satisfaction === 'Low' ? (
                    <TrendingDown className="w-4 h-4 text-error-400" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-warning-400" />
                  )}
                  <span className="text-primary-200 text-sm">
                    Satisfaction: <span className="text-white font-semibold">{decisionData.employee_satisfaction}</span>
                  </span>
                </div>
              </div>

              {/* Right: Summary & Insights */}
              <div className="flex-1 p-8">
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">AI Executive Summary</h2>
                    <p className="text-xs text-primary-200">Real-time insights from employee feedback</p>
                  </div>
                </div>
                <p className="text-base leading-relaxed text-white/90 mb-8">
                  {decisionData.executive_summary}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Strengths */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-success-400">
                      <CheckCircle2 className="w-4 h-4" />
                      <span className="text-sm font-medium">Key Strengths</span>
                    </div>
                    <div className="space-y-2">
                      {decisionData.strengths.slice(0, 3).map((strength, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-success-500/10 text-white/90 text-sm"
                        >
                          <ArrowUpRight className="w-3.5 h-3.5 text-success-400 flex-shrink-0" />
                          {strength}
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Issues */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-warning-400">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-sm font-medium">Areas for Improvement</span>
                    </div>
                    <div className="space-y-2">
                      {decisionData.critical_issues.slice(0, 3).map((issue, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-warning-500/10 text-white/90 text-sm"
                        >
                          <ArrowDownRight className="w-3.5 h-3.5 text-warning-400 flex-shrink-0" />
                          {issue}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Priority Recommendations */}
      <motion.div variants={item}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
            <Lightbulb className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-900">Priority Recommendations</h3>
            <p className="text-xs text-neutral-500">AI-generated actionable insights</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {decisionData.recommendations.map((rec, index) => {
            const config = priorityConfig[rec.priority];
            const Icon = config.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-5 rounded-xl border ${config.bg} ${config.border}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-4 h-4 ${config.text}`} />
                    <Badge className={`${config.bg} ${config.text} border ${config.border}`} variant="outline">
                      {rec.priority}
                    </Badge>
                  </div>
                </div>
                <h4 className="font-semibold text-neutral-900 mb-1">{rec.title}</h4>
                <p className="text-sm text-neutral-600 leading-relaxed">{rec.description}</p>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* KPI Cards */}
      <motion.div variants={container} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: 'Total Reviews', value: dashboardData.overview.total_reviews.toLocaleString(), icon: MessageSquare, color: 'primary' },
          { label: 'Avg. Rating', value: dashboardData.overview.average_rating.toFixed(1), icon: Star, color: 'warning', rating: true },
          { label: 'Positive', value: dashboardData.overview.positive_reviews.toLocaleString(), icon: ThumbsUp, color: 'success', border: 'success' },
          { label: 'Neutral', value: dashboardData.overview.neutral_reviews.toLocaleString(), icon: Smile, color: 'warning', border: 'warning' },
          { label: 'Negative', value: dashboardData.overview.negative_reviews.toLocaleString(), icon: AlertTriangle, color: 'error', border: 'error' },
        ].map((kpi, idx) => (
          <motion.div key={idx} variants={item}>
            <Card className={`group hover:shadow-lg transition-all duration-300 ${kpi.border ? `border-l-4 border-l-${kpi.border}` : ''}`}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide">{kpi.label}</p>
                    <div className="flex items-baseline gap-2 mt-1">
                      <p className="text-2xl font-bold text-neutral-900">{kpi.value}</p>
                      {kpi.rating && renderStars(Math.round(dashboardData.overview.average_rating))}
                    </div>
                  </div>
                  <div className={`w-10 h-10 rounded-xl bg-${kpi.color}-50 flex items-center justify-center group-hover:scale-110 transition-transform`}>
                    <kpi.icon className={`w-5 h-5 text-${kpi.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Employee Mood Pie Chart */}
        <motion.div variants={item}>
          <Card className="shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold">Employee Mood Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={employeeMoodData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {employeeMoodData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0' }} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Monthly Sentiment Trend */}
        <motion.div variants={item}>
          <Card className="shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold">Monthly Sentiment Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={dashboardData.monthly_sentiment}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0' }} />
                  <Legend iconType="circle" iconSize={8} />
                  <Line type="monotone" dataKey="positive" stroke="#10B981" strokeWidth={2.5} name="Positive" dot={false} />
                  <Line type="monotone" dataKey="neutral" stroke="#F59E0B" strokeWidth={2.5} name="Neutral" dot={false} />
                  <Line type="monotone" dataKey="negative" stroke="#EF4444" strokeWidth={2.5} name="Negative" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Rating Distribution */}
        <motion.div variants={item}>
          <Card className="shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold">Rating Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={dashboardData.rating_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="rating" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0' }} />
                  <Bar dataKey="count" fill="#2563EB" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Top Topics */}
        <motion.div variants={item}>
          <Card className="shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold">Most Discussed Topics</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={dashboardData.top_topics} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                  <XAxis type="number" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="topic" tick={{ fill: '#64748B', fontSize: 11 }} width={90} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0' }} />
                  <Bar dataKey="count" fill="#2563EB" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Keywords */}
      <motion.div variants={item}>
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold">Trending Keywords</CardTitle>
            <CardDescription className="text-xs">Key terms from employee feedback</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {dashboardData.keywords.map((kw, index) => {
                const size = Math.min(14 + kw.score * 10, 18);
                return (
                  <motion.span
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.03 }}
                    className="px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 font-medium hover:bg-primary-100 transition-colors cursor-default"
                    style={{ fontSize: `${size}px` }}
                  >
                    {kw.keyword}
                  </motion.span>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Reviews */}
      <motion.div variants={item}>
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold">Recent Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboardData.recent_reviews.map((review, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-4 p-4 rounded-xl bg-neutral-50 hover:bg-neutral-100 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center flex-wrap gap-2 mb-2">
                      <span className="font-medium text-neutral-900">{review.job_title}</span>
                      <span className="text-xs text-neutral-400">{review.date}</span>
                      <Badge
                        className={`text-xs ${
                          review.sentiment === 'Positive'
                            ? 'bg-success-50 text-success-700 hover:bg-success-50'
                            : review.sentiment === 'Negative'
                            ? 'bg-error-50 text-error-700 hover:bg-error-50'
                            : 'bg-warning-50 text-warning-700 hover:bg-warning-50'
                        }`}
                      >
                        {review.sentiment}
                      </Badge>
                    </div>
                    <p className="text-sm text-neutral-600 line-clamp-2">{review.summary}</p>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                    <span className="font-semibold text-neutral-900">{review.rating}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}

function Activity({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  );
}
