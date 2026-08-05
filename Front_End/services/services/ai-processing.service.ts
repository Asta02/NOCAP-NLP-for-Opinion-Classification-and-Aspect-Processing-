import { AiProcessingJob, JobsListParams, JobsListResponse, ProcessRequest, ProcessResponse, UploadResponse } from '@/types/ai-processing';
import { mockJobs } from '@/services/mock/mock-data';

export interface IAiProcessingService {
  uploadFile(file: File, companyId: number, onProgress?: (progress: number) => void): Promise<UploadResponse>;
  process(request: ProcessRequest): Promise<ProcessResponse>;
  getJobs(params?: JobsListParams): Promise<JobsListResponse>;
  getJobById(jobId: number): Promise<AiProcessingJob>;
}

export class MockAiProcessingService implements IAiProcessingService {
  private jobs: AiProcessingJob[] = [...mockJobs];
  private uploadId = 5;
  private jobId = 5;

  async uploadFile(file: File, companyId: number, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    for (let i = 0; i <= 100; i += 10) {
      await this.simulateDelay(100);
      if (onProgress) {
        onProgress(i);
      }
    }

    return {
      upload_id: this.uploadId++,
      filename: file.name,
      records_count: Math.floor(Math.random() * 500) + 50,
      message: 'File uploaded successfully',
    };
  }

  async process(request: ProcessRequest): Promise<ProcessResponse> {
    await this.simulateDelay(500);

    return {
      job_id: this.jobId++,
      message: 'Processing job started successfully',
    };
  }

  async getJobs(params?: JobsListParams): Promise<JobsListResponse> {
    await this.simulateDelay();

    let filtered = [...this.jobs];

    if (params?.company_id) {
      filtered = filtered.filter((j) => j.company_id === params.company_id);
    }

    if (params?.status) {
      filtered = filtered.filter((j) => j.status === params.status);
    }

    filtered.sort((a, b) =>
      (b.started_at ? new Date(b.started_at).getTime() : 0) -
      (a.started_at ? new Date(a.started_at).getTime() : 0)
    );

    const page = params?.page || 1;
    const limit = params?.limit || 10;
    const total = filtered.length;
    const start = (page - 1) * limit;
    const paginatedData = filtered.slice(start, start + limit);

    return {
      jobs: paginatedData,
      total,
      page,
      limit,
    };
  }

  async getJobById(jobId: number): Promise<AiProcessingJob> {
    await this.simulateDelay();

    const job = this.jobs.find((j) => j.job_id === jobId);
    if (!job) {
      throw new Error('Job not found');
    }
    return job;
  }

  private simulateDelay(ms?: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms || Math.random() * 300 + 200));
  }
}

export class RealAiProcessingService implements IAiProcessingService {
  async uploadFile(file: File, companyId: number, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    const { apiUpload } = await import('@/services/api');
    return apiUpload<UploadResponse>(`/admin/upload?company_id=${companyId}`, file, onProgress);
  }

  async process(request: ProcessRequest): Promise<ProcessResponse> {
    const { apiPost } = await import('@/services/api');
    return apiPost<ProcessResponse>('/admin/process', request);
  }

  async getJobs(params?: JobsListParams): Promise<JobsListResponse> {
    const { apiGet } = await import('@/services/api');
    return apiGet<JobsListResponse>('/admin/jobs', { params });
  }

  async getJobById(jobId: number): Promise<AiProcessingJob> {
    const { apiGet } = await import('@/services/api');
    return apiGet<AiProcessingJob>(`/admin/jobs/${jobId}`);
  }
}
