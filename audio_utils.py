import os
import speech_recognition as sr
import edge_tts
import uuid
from pathlib import Path

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

from pydub import AudioSegment

TEMP_DIR = Path(__file__).parent / "temp_audio"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def normalize_audio(self, input_path: str) -> str:
        """
        Browser MediaRecorder always sends webm/opus data regardless of
        the filename extension we give it. So we ALWAYS run it through
        pydub/ffmpeg to produce a clean 16-kHz mono WAV that Google STT
        can read. We only skip conversion if it truly is a valid WAV.
        """
        output_path = input_path.rsplit('.', 1)[0] + "_clean.wav"
        try:
            # Let ffmpeg auto-detect the real container format
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            audio.export(output_path, format="wav")
            print(f"[AUDIO] Converted to clean WAV: {output_path} ({len(audio)}ms)")
            return output_path
        except Exception as e:
            print(f"[ERROR] Audio conversion failed: {e}")
            return input_path

    def speech_to_text(self, audio_file_path: str) -> str:
        clean_path = self.normalize_audio(audio_file_path)
        try:
            with sr.AudioFile(clean_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language="ta-IN")
                return text
        except sr.UnknownValueError:
            print("[STT] Google could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"[ERROR] STT Connection Error: {e}")
            return ""
        except Exception as e:
            print(f"[ERROR] STT Crash: {e}")
            return ""
        finally:
            for path in set([audio_file_path, clean_path]):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass

    async def text_to_speech(self, text: str) -> str:
        output_filename = f"response_{uuid.uuid4()}.mp3"
        output_path = str(TEMP_DIR / output_filename)
        try:
            communicate = edge_tts.Communicate(text, "ta-IN-PallaviNeural")
            await communicate.save(output_path)
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                print("[ERROR] TTS produced empty file")
                return ""
            return output_path
        except Exception as e:
            print(f"[ERROR] TTS Failed: {e}")
            return ""
