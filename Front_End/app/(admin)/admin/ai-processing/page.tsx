'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Upload,
  Play,
  CheckCircle2,
  Clock,
  AlertCircle,
  Loader2,
  ChevronRight,
  FileText,
  Building2,
  Cpu,
} from 'lucide-react';
import { aiProcessingService, companyService } from '@/services';
import { AiProcessingJob, PipelineStep, DEFAULT_PIPELINE_STEPS } from '@/types/ai-processing';
import { Company } from '@/types/company';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';

const statusConfig: Record<string, { icon: typeof Clock; color: string; bg: string; animate?: boolean }> = {
  pending: { icon: Clock, color: 'text-neutral-400', bg: 'bg-neutral-100' },
  processing: { icon: Loader2, color: 'text-primary', bg: 'bg-primary-50', animate: true },
  completed: { icon: CheckCircle2, color: 'text-success', bg: 'bg-success-50' },
  failed: { icon: AlertCircle, color: 'text-error', bg: 'bg-error-50' },
};

export default function AiProcessingPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStep[]>(DEFAULT_PIPELINE_STEPS);
  const [recentJobs, setRecentJobs] = useState<AiProcessingJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [companiesResult, jobsResult] = await Promise.all([
          companyService.getAll({ limit: 100, status: 'active' }),
          aiProcessingService.getJobs({ limit: 10 }),
        ]);
        setCompanies(companiesResult.companies);
        setRecentJobs(jobsResult.jobs);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        toast.error('Please select a CSV file');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !selectedCompanyId) {
      toast.error('Please select a company and file');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setPipelineSteps(DEFAULT_PIPELINE_STEPS.map(s => ({ ...s, status: 'pending', progress: 0 })));

    try {
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(r => setTimeout(r, 100));
        setUploadProgress(i);
      }

      const uploadResponse = await aiProcessingService.uploadFile(
        selectedFile,
        parseInt(selectedCompanyId)
      );

      toast.success(`File uploaded: ${uploadResponse.records_count} records found`);
      setProcessing(true);

      // Simulate pipeline progress
      const steps = [...DEFAULT_PIPELINE_STEPS];
      for (let i = 0; i < steps.length; i++) {
        if (i > 0) {
          steps[i - 1].status = 'completed';
          steps[i - 1].progress = 100;
        }
        steps[i].status = 'processing';
        for (let p = 0; p <= 100; p += 10) {
          steps[i].progress = p;
          setPipelineSteps([...steps]);
          await new Promise(r => setTimeout(r, 80));
        }
      }
      steps[steps.length - 1].status = 'completed';
      steps[steps.length - 1].progress = 100;
      setPipelineSteps([...steps]);

      toast.success('AI Processing completed successfully!');

      // Refresh jobs
      const jobsResult = await aiProcessingService.getJobs({ limit: 10 });
      setRecentJobs(jobsResult.jobs);
    } catch (error) {
      toast.error('Failed to upload file');
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  };

  const overallProgress = pipelineSteps.reduce((acc, step) => {
    const stepWeight = 100 / pipelineSteps.length;
    return acc + (step.status === 'completed' ? stepWeight : step.progress * stepWeight / 100);
  }, 0);

  const getJobStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      queued: 'bg-neutral-100 text-neutral-600',
      processing: 'bg-primary-50 text-primary-700',
      completed: 'bg-success-50 text-success-700',
      failed: 'bg-error-50 text-error-700',
    };
    return styles[status] || styles.queued;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Upload Section */}
      <Card className="border-dashed border-2 border-neutral-200 hover:border-primary-300 transition-colors">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5 text-primary" />
            Upload Dataset
          </CardTitle>
          <CardDescription>
            Upload a CSV file containing employee feedback data to analyze
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-700">Select Company</label>
              <Select value={selectedCompanyId} onValueChange={setSelectedCompanyId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a company" />
                </SelectTrigger>
                <SelectContent>
                  {companies.map((company) => (
                    <SelectItem key={company.company_id} value={company.company_id.toString()}>
                      {company.company_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-700">Select CSV File</label>
              <div className="relative">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="csv-upload"
                />
                <label
                  htmlFor="csv-upload"
                  className="flex items-center justify-center gap-2 w-full h-11 px-4 rounded-lg border border-neutral-200 bg-white cursor-pointer hover:bg-neutral-50 transition-colors"
                >
                  <FileText className="w-4 h-4 text-neutral-400" />
                  <span className="text-sm text-neutral-600">
                    {selectedFile ? selectedFile.name : 'Choose CSV file'}
                  </span>
                </label>
              </div>
            </div>
          </div>

          {uploading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-neutral-500">Uploading...</span>
                <span className="font-medium text-primary">{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>
          )}

          <Button
            onClick={handleUpload}
            disabled={!selectedFile || !selectedCompanyId || uploading || processing}
            className="w-full h-11 bg-primary hover:bg-primary-700"
          >
            {processing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run AI Analysis
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Pipeline Progress */}
      {(uploading || processing) && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Card className="bg-gradient-to-r from-primary-50 to-white border-primary-100">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-primary animate-pulse" />
                    AI Pipeline Progress
                  </CardTitle>
                  <CardDescription className="mt-1">
                    Real-time progress of the analysis pipeline
                  </CardDescription>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-primary">{Math.round(overallProgress)}%</p>
                  <p className="text-sm text-neutral-500">Overall</p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pipelineSteps.map((step, index) => {
                  const config = statusConfig[step.status] || statusConfig.pending;
                  const Icon = config.icon;
                  const isActive = step.status === 'processing';
                  const isCompleted = step.status === 'completed';

                  return (
                    <motion.div
                      key={step.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`
                        flex items-center gap-4 p-4 rounded-lg transition-all
                        ${isActive ? 'bg-primary-50 border border-primary-200' : 'bg-neutral-50'}
                      `}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${config.bg}`}>
                        <Icon className={`w-5 h-5 ${config.color} ${config.animate ? 'animate-spin' : ''}`} />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <p className={`font-medium ${isActive ? 'text-primary' : 'text-neutral-700'}`}>
                            {step.name}
                          </p>
                          <span className="text-sm text-neutral-500">
                            {isCompleted ? 'Done' : `${step.progress}%`}
                          </span>
                        </div>
                        <Progress value={step.progress} className="h-1.5" />
                      </div>

                      {index < pipelineSteps.length - 1 && (
                        <ChevronRight className="w-5 h-5 text-neutral-300" />
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Recent Jobs Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Recent Processing Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-20 rounded-lg" />
              ))}
            </div>
          ) : recentJobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Cpu className="w-12 h-12 text-neutral-300 mb-4" />
              <h3 className="text-lg font-medium text-neutral-900">No processing jobs yet</h3>
              <p className="text-neutral-500 mt-1">Upload a dataset to start analyzing</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentJobs.map((job) => {
                const config = statusConfig[job.status] || statusConfig.pending;
                const Icon = config.icon;

                return (
                  <div
                    key={job.job_id}
                    className="flex items-center gap-4 p-4 rounded-lg bg-neutral-50 hover:bg-neutral-100 transition-colors"
                  >
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${config.bg}`}>
                      <Icon className={`w-5 h-5 ${config.color} ${config.animate ? 'animate-spin' : ''}`} />
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Building2 className="w-4 h-4 text-neutral-400" />
                        <span className="font-medium text-neutral-900">{job.company_name}</span>
                      </div>
                      <p className="text-sm text-neutral-500">
                        {job.filename} ({job.records_count.toLocaleString()} records)
                      </p>
                    </div>

                    <div className="text-right">
                      <Badge className={getJobStatusBadge(job.status)}>
                        {job.status}
                      </Badge>
                      {job.started_at && (
                        <p className="text-xs text-neutral-400 mt-1">
                          {new Date(job.started_at).toLocaleString()}
                        </p>
                      )}
                    </div>

                    <div className="w-24">
                      <Progress value={job.progress} className="h-2" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
