export type PipelineStepStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface PipelineStep {
  id: string;
  name: string;
  description: string;
  status: PipelineStepStatus;
  progress: number;
  error?: string;
}

export interface AiProcessingJob {
  job_id: number;
  company_id: number;
  company_name: string;
  filename: string;
  records_count: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  pipeline_steps: PipelineStep[];
  started_at: string | null;
  completed_at: string | null;
  error_message?: string;
}

export interface UploadResponse {
  upload_id: number;
  filename: string;
  records_count: number;
  message: string;
}

export interface ProcessRequest {
  upload_id: number;
  company_id: number;
}

export interface ProcessResponse {
  job_id: number;
  message: string;
}

export interface JobsListParams {
  company_id?: number;
  status?: string;
  page?: number;
  limit?: number;
}

export interface JobsListResponse {
  jobs: AiProcessingJob[];
  total: number;
  page: number;
  limit: number;
}

export const DEFAULT_PIPELINE_STEPS: PipelineStep[] = [
  {
    id: 'upload',
    name: 'CSV Uploaded',
    description: 'Dataset successfully uploaded to the system',
    status: 'pending',
    progress: 0,
  },
  {
    id: 'preprocessing',
    name: 'Preprocessing',
    description: 'Cleaning and normalizing text data',
    status: 'pending',
    progress: 0,
  },
  {
    id: 'sentiment',
    name: 'Sentiment Analysis',
    description: 'Analyzing employee sentiment using NLP models',
    status: 'pending',
    progress: 0,
  },
  {
    id: 'topic',
    name: 'Topic Modeling',
    description: 'Identifying key themes and topics in feedback',
    status: 'pending',
    progress: 0,
  },
  {
    id: 'keyword',
    name: 'Keyword Extraction',
    description: 'Extracting important keywords and phrases',
    status: 'pending',
    progress: 0,
  },
  {
    id: 'recommendations',
    name: 'Recommendation Generation',
    description: 'Generating actionable recommendations',
    status: 'pending',
    progress: 0,
  },
  {
    id: 'completed',
    name: 'Completed',
    description: 'AI analysis pipeline completed successfully',
    status: 'pending',
    progress: 0,
  },
];
