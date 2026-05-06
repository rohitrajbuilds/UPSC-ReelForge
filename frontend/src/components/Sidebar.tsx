interface SidebarProps {
  page: string;
  onSelect: (page: string) => void;
}

const items = ["Generate Video", "Daily Agent", "Output History", "Topic Library", "Settings"];

export function Sidebar({ page, onSelect }: SidebarProps) {
  return (
    <aside className="rounded-[28px] border border-white/10 bg-panel/80 p-5 shadow-soft backdrop-blur">
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.3em] text-skyline/70">Control Center</p>
        <h2 className="mt-2 text-xl font-semibold text-white">Operations</h2>
      </div>
      <nav className="space-y-2">
        {items.map((item) => (
          <button
            key={item}
            onClick={() => onSelect(item)}
            className={`w-full rounded-2xl px-4 py-3 text-left text-sm transition ${
              page === item
                ? "bg-gradient-to-r from-accent to-amber-300 text-ink"
                : "bg-white/5 text-slate-200 hover:bg-white/10"
            }`}
          >
            {item}
          </button>
        ))}
      </nav>
    </aside>
  );
}
