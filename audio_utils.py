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
        import wave
        try:
            with wave.open(input_path, 'rb'):
                return input_path
        except Exception:
            pass
        try:
            output_path = input_path.rsplit('.', 1)[0] + "_converted.wav"
            ext = input_path.rsplit('.', 1)[-1].lower()
            if ext == 'webm':
                audio = AudioSegment.from_file(input_path, format="webm")
            elif ext == 'mp3':
                audio = AudioSegment.from_mp3(input_path)
            elif ext == 'ogg':
                audio = AudioSegment.from_ogg(input_path)
            else:
                audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(output_path, format="wav")
            return output_path
        except Exception as e:
            print(f"[ERROR] Audio conversion failed: {e}")
            return input_path

    def speech_to_text(self, audio_file_path: str) -> str:
        clean_path = self.normalize_audio(audio_file_path)
        try:
            with sr.AudioFile(clean_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language="ta-IN")
                return text
        except sr.UnknownValueError:
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
            return output_path
        except Exception as e:
            print(f"[ERROR] TTS Failed: {e}")
            return ""
