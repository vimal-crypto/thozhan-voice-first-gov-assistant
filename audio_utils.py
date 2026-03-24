import os
import speech_recognition as sr
import edge_tts
import uuid
import asyncio
from pathlib import Path

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    print("[audio_utils] FFMPEG paths configured via static-ffmpeg")
except ImportError:
    print("[audio_utils] WARNING: static-ffmpeg not found")

from pydub import AudioSegment

TEMP_DIR = Path(__file__).parent / "voice_agent" / "temp_audio"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def normalize_audio(self, input_path: str) -> str:
        print(f"   [STEP 2.1] Normalizing: {os.path.basename(input_path)}")
        import wave

        try:
            with wave.open(input_path, 'rb') as s_read:
                n_channels = s_read.getnchannels()
                framerate = s_read.getframerate()
                print(f"   [INFO] WAV Detected: {n_channels}ch, {framerate}Hz")
            return input_path
        except wave.Error as e:
            print(f"   [WARN] Not a valid WAV ({e}). Converting to WAV...")
        except Exception as e:
            print(f"   [WARN] File check failed ({e}). Attempting conversion...")

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
            print(f"   [SUCCESS] Converted to: {os.path.basename(output_path)}")
            return output_path
        except Exception as e:
            print(f"   [ERROR] Conversion failed: {e}")
            return input_path

    def speech_to_text(self, audio_file_path: str) -> str:
        print(f"\n[STEP 1] Receiving Audio File: {audio_file_path}")
        clean_path = self.normalize_audio(audio_file_path)

        # Cleanup converted temp file if different from input
        try:
            print(f"   [STEP 2.2] Sending to Google Speech API...")
            with sr.AudioFile(clean_path) as source:
                audio_data = self.recognizer.record(source)
                print(f"   [STEP 2.3] Transcribing...")
                text = self.recognizer.recognize_google(audio_data, language="ta-IN")
                print(f"   [SUCCESS] User said: (Tamil text - {len(text)} chars)")
                return text
        except sr.UnknownValueError:
            print("   [ERROR] STT: Audio was unclear (UnknownValueError).")
            return ""
        except sr.RequestError as e:
            print(f"   [ERROR] STT Connection Error: {e}")
            return ""
        except Exception as e:
            import traceback
            print(f"   [CRITICAL] STT Crash: {e}")
            traceback.print_exc()
            return ""
        finally:
            # Cleanup input and converted files after processing
            for path in set([audio_file_path, clean_path]):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        print(f"   [CLEANUP] Deleted: {os.path.basename(path)}")
                except Exception:
                    pass

    async def text_to_speech(self, text: str) -> str:
        print(f"\n[STEP 4] Generating TTS for: (Tamil text - {len(text)} chars)")
        output_filename = f"response_{uuid.uuid4()}.mp3"
        output_path = str(TEMP_DIR / output_filename)

        try:
            voice = "ta-IN-PallaviNeural"
            print(f"   [STEP 4.1] Calling EdgeTTS ({voice})...")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            print(f"   [SUCCESS] Audio saved: {output_path}")
            return output_path
        except Exception as e:
            print(f"   [ERROR] TTS Failed: {e}")
            return ""
