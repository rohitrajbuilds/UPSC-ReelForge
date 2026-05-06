import type { GenerateRequest } from "../types";

interface TopicFormProps {
  form: GenerateRequest;
  categories: string[];
  loading: boolean;
  onChange: (patch: Partial<GenerateRequest>) => void;
  onSubmit: () => void;
}

export function TopicForm({ form, categories, loading, onChange, onSubmit }: TopicFormProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">Generate Video</h3>
          <p className="mt-1 text-sm text-slate-400">Trigger the modular production pipeline from a single topic brief.</p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 md:col-span-2">
          <span className="text-sm text-slate-300">Topic</span>
          <input
            value={form.topic}
            onChange={(event) => onChange({ topic: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500"
            placeholder="Directive Principles of State Policy"
          />
        </label>

        <label className="space-y-2">
          <span className="text-sm text-slate-300">Category</span>
          <select
            value={form.category}
            onChange={(event) => onChange({ category: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          >
            {categories.map((category) => (
              <option key={category} value={category} className="bg-slate-900">
                {category}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm text-slate-300">Duration</span>
          <select
            value={form.duration_seconds}
            onChange={(event) => onChange({ duration_seconds: Number(event.target.value) })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          >
            {[90, 120, 180, 240].map((duration) => (
              <option key={duration} value={duration} className="bg-slate-900">
                {duration} sec
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm text-slate-300">Voice Engine</span>
          <select
            value={form.voice}
            onChange={(event) => onChange({ voice: event.target.value })}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
          >
            <option value="gtts" className="bg-slate-900">gTTS</option>
            <option value="pyttsx3" className="bg-slate-900">pyttsx3</option>
          </select>
        </label>

        <div className="grid grid-cols-2 gap-3">
          <label className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
            <span>Subtitles</span>
            <input type="checkbox" checked={form.include_subtitles} onChange={(event) => onChange({ include_subtitles: event.target.checked })} />
          </label>
          <label className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
            <span>Music</span>
            <input type="checkbox" checked={form.include_music} onChange={(event) => onChange({ include_music: event.target.checked })} />
          </label>
        </div>
      </div>
      <button
        onClick={onSubmit}
        disabled={loading}
        className="mt-6 rounded-2xl bg-gradient-to-r from-accent to-amber-300 px-5 py-3 font-medium text-ink transition hover:brightness-105 disabled:opacity-60"
      >
        {loading ? "Queueing..." : "Generate Video"}
      </button>
    </section>
  );
}
