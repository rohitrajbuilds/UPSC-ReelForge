import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { AgentStatus } from "./components/AgentStatus";
import { Header } from "./components/Header";
import { OutputHistory } from "./components/OutputHistory";
import { ProgressPanel } from "./components/ProgressPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { Sidebar } from "./components/Sidebar";
import { TopicForm } from "./components/TopicForm";
import { VideoPreview } from "./components/VideoPreview";
import type { AppConfig, GenerateRequest, HistoryItem, JobStatus, TopicItem } from "./types";

const defaultForm: GenerateRequest = {
  topic: "Directive Principles of State Policy",
  category: "Polity",
  duration_seconds: 180,
  voice: "gtts",
  include_music: true,
  include_subtitles: true,
};

const pages = ["Generate Video", "Daily Agent", "Output History", "Topic Library", "Settings"] as const;

function TopicLibrary({ topics }: { topics: TopicItem[] }) {
  const [query, setQuery] = useState("");
  const filtered = topics.filter((topic) => topic.title.toLowerCase().includes(query.toLowerCase()));

  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">Topic Library</h3>
          <p className="mt-1 text-sm text-slate-400">Search locally curated UPSC-ready placeholder topics.</p>
        </div>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search topics"
          className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map((topic) => (
          <div key={topic.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-start justify-between gap-3">
              <h4 className="font-medium text-white">{topic.title}</h4>
              <span className="rounded-full bg-accent/20 px-3 py-1 text-xs text-amber-100">{topic.category}</span>
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
              <span>{topic.difficulty}</span>
              <span>{topic.keywords.join(", ")}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null;
  return <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{message}</div>;
}

export default function App() {
  const [page, setPage] = useState<(typeof pages)[number]>("Generate Video");
  const [form, setForm] = useState<GenerateRequest>(defaultForm);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [agentStatus, setAgentStatus] = useState<import("./types").AgentStatus | null>(null);
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [runningAgent, setRunningAgent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const categories = Array.from(new Set(topics.map((topic) => topic.category)));

  async function bootstrap() {
    try {
      const [topicData, historyData, configData, agentData] = await Promise.all([
        api.getTopics(),
        api.getHistory(),
        api.getConfig(),
        api.getAgentStatus(),
      ]);
      setTopics(topicData);
      setHistory(historyData);
      setConfig(configData);
      setAgentStatus(agentData);
      setForm((current) => ({
        ...current,
        category: topicData[0]?.category ?? current.category,
        duration_seconds: configData.default_duration_seconds,
        voice: configData.voice_engine,
        include_music: configData.include_music,
        include_subtitles: configData.include_subtitles,
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard data.");
    }
  }

  useEffect(() => {
    void bootstrap();
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  async function refreshHistoryAndAgent() {
    const [historyData, agentData] = await Promise.all([api.getHistory(), api.getAgentStatus()]);
    setHistory(historyData);
    setAgentStatus(agentData);
  }

  function startPolling(jobId: string) {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      const latest = await api.getJob(jobId);
      setJob(latest);
      if (latest.status === "completed" || latest.status === "failed") {
        if (pollRef.current) window.clearInterval(pollRef.current);
        await refreshHistoryAndAgent();
      }
    }, 1500);
  }

  async function handleGenerate() {
    setLoadingGenerate(true);
    setError(null);
    try {
      const response = await api.generate(form);
      setJob({
        job_id: response.job_id,
        topic: response.topic,
        status: response.status,
        progress: response.progress,
      });
      startPolling(response.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation request failed.");
    } finally {
      setLoadingGenerate(false);
    }
  }

  async function handleRunAgent() {
    setRunningAgent(true);
    setError(null);
    try {
      await api.runAgentOnce();
      await refreshHistoryAndAgent();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent run failed.");
    } finally {
      setRunningAgent(false);
    }
  }

  async function handleSaveSettings() {
    if (!config) return;
    setSavingSettings(true);
    setError(null);
    try {
      const saved = await api.updateConfig(config);
      setConfig(saved);
      await refreshHistoryAndAgent();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saving settings failed.");
    } finally {
      setSavingSettings(false);
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(245,158,11,0.16),transparent_22%),radial-gradient(circle_at_bottom_right,_rgba(110,231,183,0.1),transparent_30%),linear-gradient(180deg,#07101d,#0b1626_45%,#050c16)] p-4 md:p-6">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[280px,1fr]">
        <Sidebar page={page} onSelect={(next) => setPage(next as (typeof pages)[number])} />
        <main className="space-y-6">
          <Header />
          <ErrorBanner message={error} />

          {page === "Generate Video" && (
            <div className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
              <div className="space-y-6">
                <TopicForm
                  form={form}
                  categories={categories.length ? categories : ["Polity"]}
                  loading={loadingGenerate}
                  onChange={(patch) => setForm((current) => ({ ...current, ...patch }))}
                  onSubmit={handleGenerate}
                />
                <VideoPreview job={job} downloadUrl={job ? api.downloadUrl(job.job_id) : null} />
              </div>
              <ProgressPanel progress={job?.progress ?? null} status={job?.status} />
            </div>
          )}

          {page === "Daily Agent" && <AgentStatus status={agentStatus} loading={runningAgent} onRun={handleRunAgent} />}
          {page === "Output History" && <OutputHistory items={history} />}
          {page === "Topic Library" && <TopicLibrary topics={topics} />}
          {page === "Settings" && (
            <SettingsPanel
              config={config}
              saving={savingSettings}
              onChange={(patch) => setConfig((current) => (current ? { ...current, ...patch } : current))}
              onSave={handleSaveSettings}
            />
          )}
        </main>
      </div>
    </div>
  );
}
