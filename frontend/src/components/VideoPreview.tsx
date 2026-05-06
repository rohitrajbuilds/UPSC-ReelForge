import type { JobStatus } from "../types";

interface VideoPreviewProps {
  job: JobStatus | null;
  downloadUrl?: string | null;
}

export function VideoPreview({ job, downloadUrl }: VideoPreviewProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-panel/80 p-6 shadow-soft">
      <div className="mb-5">
        <h3 className="text-xl font-semibold text-white">Vertical Preview</h3>
        <p className="mt-1 text-sm text-slate-400">The final download appears here when video assembly is complete.</p>
      </div>
      <div className="mx-auto flex aspect-[9/16] max-w-[280px] items-center justify-center rounded-[32px] border border-white/10 bg-[linear-gradient(180deg,rgba(142,197,255,0.18),rgba(9,17,31,0.95))] p-6">
        {job?.status === "completed" && downloadUrl ? (
          <div className="text-center">
            <p className="text-sm text-slate-200">Video ready for review</p>
            <a href={downloadUrl} className="mt-4 inline-flex rounded-2xl bg-accent px-4 py-3 font-medium text-ink">
              Download MP4
            </a>
          </div>
        ) : job?.status === "failed" ? (
          <p className="text-center text-sm text-rose-200">{job.error ?? "The job failed during assembly."}</p>
        ) : (
          <p className="text-center text-sm text-slate-300">A 9:16 preview card will activate once the backend completes the job.</p>
        )}
      </div>
    </section>
  );
}
