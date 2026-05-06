import type { PipelineProgress } from "../types";

interface ProgressPanelProps {
  progress: PipelineProgress | null;
  status?: string;
}

const labels: Array<keyof PipelineProgress> = ["script", "voice", "animation", "subtitles", "video"];

function badge(status: string) {
  if (status === "completed") return "bg-emerald-400/20 text-emerald-200";
  if (status === "processing") return "bg-amber-400/20 text-amber-100";
  if (status === "failed") return "bg-rose-500/20 text-rose-100";
  if (status === "skipped") return "bg-slate-400/20 text-slate-200";
  return "bg-white/5 text-slate-300";
}

export function ProgressPanel({ progress, status }: ProgressPanelProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">Pipeline Progress</h3>
          <p className="mt-1 text-sm text-slate-400">Track each production stage from script to final MP4.</p>
        </div>
        <span className="rounded-full bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-slate-300">{status ?? "idle"}</span>
      </div>
      <div className="space-y-3">
        {labels.map((label) => (
          <div key={label} className="flex items-center justify-between rounded-2xl bg-white/5 px-4 py-3">
            <span className="capitalize text-slate-200">{label}</span>
            <span className={`rounded-full px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] ${badge(progress?.[label] ?? "pending")}`}>
              {progress?.[label] ?? "pending"}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
