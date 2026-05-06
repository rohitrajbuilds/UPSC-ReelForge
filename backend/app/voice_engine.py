from __future__ import annotations

import wave
from pathlib import Path


class VoiceEngine:
    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries

    def _build_silent_wav(self, path: Path, duration_seconds: int) -> Path:
        frame_rate = 22050
        total_frames = max(duration_seconds, 1) * frame_rate
        with wave.open(str(path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(frame_rate)
            wav_file.writeframes(b"\x00\x00" * total_frames)
        return path

    def generate(self, script_text: str, output_dir: Path, engine_name: str = "gtts") -> dict:
        duration_seconds = max(30, min(300, int(len(script_text.split()) / 2.4)))
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                if engine_name == "gtts":
                    try:
                        from gtts import gTTS  # type: ignore

                        output_path = output_dir / "voice.mp3"
                        gTTS(script_text, lang="en").save(str(output_path))
                        return {
                            "engine": "gtts",
                            "audio_path": str(output_path),
                            "duration_seconds": duration_seconds,
                            "attempt": attempt + 1,
                        }
                    except Exception as exc:
                        last_error = exc
                if engine_name == "pyttsx3":
                    try:
                        import pyttsx3  # type: ignore

                        output_path = output_dir / "voice.wav"
                        engine = pyttsx3.init()
                        engine.save_to_file(script_text, str(output_path))
                        engine.runAndWait()
                        return {
                            "engine": "pyttsx3",
                            "audio_path": str(output_path),
                            "duration_seconds": duration_seconds,
                            "attempt": attempt + 1,
                        }
                    except Exception as exc:
                        last_error = exc

                output_path = output_dir / "voice.wav"
                self._build_silent_wav(output_path, duration_seconds)
                return {
                    "engine": "silent-fallback",
                    "audio_path": str(output_path),
                    "duration_seconds": duration_seconds,
                    "attempt": attempt + 1,
                    "warning": f"Voice fallback used after error: {last_error}" if last_error else "Voice fallback used.",
                }
            except Exception as exc:  # pragma: no cover
                last_error = exc
        raise RuntimeError(f"Voice generation failed after retries: {last_error}")
