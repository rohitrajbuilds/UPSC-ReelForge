export function Header() {
  return (
    <header className="rounded-[28px] border border-white/10 bg-[radial-gradient(circle_at_top_left,_rgba(245,158,11,0.35),_transparent_40%),linear-gradient(135deg,rgba(16,27,45,0.95),rgba(9,17,31,0.98))] p-6 shadow-soft">
      <p className="text-xs uppercase tracking-[0.3em] text-skyline/70">Internal Studio</p>
      <div className="mt-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-white">UPSC ReelForge</h1>
          <p className="mt-2 text-sm text-slate-300">AI-powered educational vertical video generator</p>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm text-slate-200">
          <div className="rounded-2xl bg-white/5 px-4 py-3">
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Format</div>
            <div className="mt-1 font-medium">1080 × 1920</div>
          </div>
          <div className="rounded-2xl bg-white/5 px-4 py-3">
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Mode</div>
            <div className="mt-1 font-medium">Manual + Agent</div>
          </div>
        </div>
      </div>
    </header>
  );
}
