export type StageStatus = "pending" | "processing" | "completed" | "failed" | "skipped";

export interface TopicItem {
  id: string;
  title: string;
  category: string;
  difficulty: string;
  keywords: string[];
}

export interface PipelineProgress {
  script: StageStatus;
  voice: StageStatus;
  animation: StageStatus;
  subtitles: StageStatus;
  video: StageStatus;
}

export interface GenerateRequest {
  topic: string;
  category: string;
  duration_seconds: number;
  voice: string;
  include_music: boolean;
  include_subtitles: boolean;
}

export interface GenerateResponse {
  job_id: string;
  status: string;
  topic: string;
  progress: PipelineProgress;
}

export interface JobStatus {
  job_id: string;
  topic: string;
  status: string;
  progress: PipelineProgress;
  output_path?: string | null;
  download_url?: string | null;
  error?: string | null;
}

export interface AgentStatus {
  enabled: boolean;
  topics_per_day: number;
  generated_today: number;
  last_run?: string | null;
  next_run?: string | null;
}

export interface AppConfig {
  videos_per_day: number;
  max_retries: number;
  default_duration_seconds: number;
  output_width: number;
  output_height: number;
  voice_engine: string;
  include_subtitles: boolean;
  include_music: boolean;
  recycle_topics: boolean;
}

export interface HistoryItem {
  job_id: string;
  topic: string;
  category: string;
  created_at: string;
  status: string;
  output_path?: string | null;
  repeated_topic: boolean;
}
