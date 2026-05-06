from __future__ import annotations

from pathlib import Path


class VideoAssemblyError(RuntimeError):
    """Raised when final video assembly fails."""


class VideoEngine:
    def assemble(
        self,
        output_dir: Path,
        animation_path: str,
        audio_path: str,
        include_music: bool,
        subtitles_path: str | None = None,
    ) -> dict:
        final_path = output_dir / "final_video.mp4"
        try:
            from moviepy import AudioFileClip, ColorClip, VideoFileClip  # type: ignore

            base_clip = None
            source = Path(animation_path)
            if source.exists() and source.stat().st_size > 0:
                base_clip = VideoFileClip(str(source))
            else:
                base_clip = ColorClip(size=(540, 960), color=(12, 18, 28), duration=5)

            audio_clip = AudioFileClip(audio_path)
            duration = min(base_clip.duration or audio_clip.duration, audio_clip.duration)
            final_clip = base_clip.with_duration(duration).with_audio(audio_clip)
            final_clip.write_videofile(str(final_path), codec="libx264", audio_codec="aac", fps=24, logger=None)
            final_clip.close()
            audio_clip.close()
            base_clip.close()
            return {
                "final_video_path": str(final_path),
                "include_music": include_music,
                "subtitles_path": subtitles_path,
            }
        except Exception as exc:
            raise VideoAssemblyError(
                f"Video assembly failed while preserving intermediate assets: {exc}"
            ) from exc
