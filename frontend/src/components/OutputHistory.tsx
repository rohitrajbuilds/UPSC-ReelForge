import type { HistoryItem } from "../types";
import { api } from "../api";

interface OutputHistoryProps {
  items: HistoryItem[];
}

export function OutputHistory({ items }: OutputHistoryProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5">
        <h3 className="text-xl font-semibold text-white">Output History</h3>
        <p className="mt-1 text-sm text-slate-400">Generated assets and processing outcomes from local JSON history.</p>
      </div>
      {items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-400">
          No videos generated yet.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm text-slate-200">
            <thead className="text-xs uppercase tracking-[0.22em] text-slate-400">
              <tr>
                <th className="pb-3">Date</th>
                <th className="pb-3">Topic</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Mode</th>
                <th className="pb-3">Download</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.job_id} className="border-t border-white/5">
                  <td className="py-3">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="py-3">{item.topic}</td>
                  <td className="py-3">{item.category}</td>
                  <td className="py-3">{item.status}</td>
                  <td className="py-3">{item.repeated_topic ? "Recycled" : "Fresh"}</td>
                  <td className="py-3">
                    {item.status === "completed" ? (
                      <a href={api.downloadUrl(item.job_id)} className="rounded-full bg-white/10 px-3 py-2 text-xs text-white">
                        Download
                      </a>
                    ) : (
                      <span className="text-slate-500">Unavailable</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
