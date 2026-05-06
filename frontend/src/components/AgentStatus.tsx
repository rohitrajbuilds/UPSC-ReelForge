import type { AgentStatus as AgentStatusType } from "../types";

interface Props {
  status: AgentStatusType | null;
  loading: boolean;
  onRun: () => void;
}

export function AgentStatus({ status, loading, onRun }: Props) {
  const cards = [
    { label: "Videos Per Day", value: status?.topics_per_day ?? "-" },
    { label: "Generated Today", value: status?.generated_today ?? "-" },
    { label: "Last Run", value: status?.last_run ? new Date(status.last_run).toLocaleString() : "Not yet" },
    { label: "Next Run", value: status?.next_run ? new Date(status.next_run).toLocaleString() : "Scheduling..." },
  ];

  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">Daily Agent</h3>
          <p className="mt-1 text-sm text-slate-400">Autonomous topic selection and scheduled generation from the internal queue.</p>
        </div>
        <span className="rounded-full bg-emerald-400/20 px-4 py-2 text-xs uppercase tracking-[0.24em] text-emerald-100">
          {status?.enabled ? "Enabled" : "Disabled"}
        </span>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {cards.map((card) => (
          <div key={card.label} className="rounded-2xl bg-white/5 px-4 py-4">
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{card.label}</div>
            <div className="mt-2 text-sm font-medium text-white">{card.value}</div>
          </div>
        ))}
      </div>
      <button
        onClick={onRun}
        disabled={loading}
        className="mt-6 rounded-2xl bg-gradient-to-r from-mint to-skyline px-5 py-3 font-medium text-ink disabled:opacity-60"
      >
        {loading ? "Running..." : "Run Agent Once"}
      </button>
    </section>
  );
}
