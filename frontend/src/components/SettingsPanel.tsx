import type { AppConfig } from "../types";

interface Props {
  config: AppConfig | null;
  saving: boolean;
  onChange: (patch: Partial<AppConfig>) => void;
  onSave: () => void;
}

export function SettingsPanel({ config, saving, onChange, onSave }: Props) {
  if (!config) {
    return <div className="rounded-[28px] border border-white/10 bg-panel/80 p-6 text-slate-300">Loading settings...</div>;
  }

  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5">
        <h3 className="text-xl font-semibold text-white">Settings</h3>
        <p className="mt-1 text-sm text-slate-400">Update local JSON configuration for the manual and agent flows.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2">
          <span className="text-sm text-slate-300">Videos per day</span>
          <input
            type="number"
            value={config.videos_per_day}
            onChange={(event) => onChange({ videos_per_day: Number(event.target.value) })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          />
        </label>
        <label className="space-y-2">
          <span className="text-sm text-slate-300">Default duration</span>
          <input
            type="number"
            value={config.default_duration_seconds}
            onChange={(event) => onChange({ default_duration_seconds: Number(event.target.value) })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          />
        </label>
        <label className="space-y-2">
          <span className="text-sm text-slate-300">Voice engine</span>
          <select
            value={config.voice_engine}
            onChange={(event) => onChange({ voice_engine: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          >
            <option value="gtts" className="bg-slate-900">gTTS</option>
            <option value="pyttsx3" className="bg-slate-900">pyttsx3</option>
          </select>
        </label>
        <label className="space-y-2">
          <span className="text-sm text-slate-300">Max retries</span>
          <input
            type="number"
            value={config.max_retries}
            onChange={(event) => onChange({ max_retries: Number(event.target.value) })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          />
        </label>
        <label className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
          <span>Include subtitles</span>
          <input type="checkbox" checked={config.include_subtitles} onChange={(event) => onChange({ include_subtitles: event.target.checked })} />
        </label>
        <label className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
          <span>Include music</span>
          <input type="checkbox" checked={config.include_music} onChange={(event) => onChange({ include_music: event.target.checked })} />
        </label>
      </div>
      <button onClick={onSave} disabled={saving} className="mt-6 rounded-2xl bg-white px-5 py-3 font-medium text-ink disabled:opacity-60">
        {saving ? "Saving..." : "Save settings"}
      </button>
    </section>
  );
}
