import type { AgentStatus, AppConfig, GenerateRequest, GenerateResponse, HistoryItem, JobStatus, TopicItem } from "./types";

const API_BASE = "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  getTopics: () => request<TopicItem[]>("/api/topics"),
  generate: (payload: GenerateRequest) =>
    request<GenerateResponse>("/api/generate", { method: "POST", body: JSON.stringify(payload) }),
  getJob: (jobId: string) => request<JobStatus>(`/api/jobs/${jobId}`),
  getAgentStatus: () => request<AgentStatus>("/api/agent/status"),
  runAgentOnce: () => request<{ status: string; job_ids: string[] }>("/api/agent/run-once", { method: "POST" }),
  getHistory: () => request<HistoryItem[]>("/api/history"),
  getConfig: () => request<AppConfig>("/api/config"),
  updateConfig: (payload: AppConfig) =>
    request<AppConfig>("/api/config", { method: "POST", body: JSON.stringify(payload) }),
  downloadUrl: (jobId: string) => `${API_BASE}/api/download/${jobId}`,
};
