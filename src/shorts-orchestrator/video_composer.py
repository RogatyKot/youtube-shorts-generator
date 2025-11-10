from pathlib import Path
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from gtts import gTTS
import uuid

def tts_to_file(text, path, lang='en'):
    t = gTTS(text=text, lang=lang)
    t.save(str(path))

def compose_short(title, script_text, duration=10, out_dir='/generated'):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    width, height = 720, 1280
    bg = ColorClip(size=(width, height), color=(20,20,20)).set_duration(duration)
    txt = TextClip(title, fontsize=60, color='white', size=(width-40, None), method='caption').set_position(('center', 50)).set_duration(5)
    body = TextClip(script_text, fontsize=40, color='white', size=(width-40, None), method='caption').set_position(('center', 300)).set_duration(duration-2)
    out_audio_path = out_dir / f"{uuid.uuid4().hex}.mp3"
    tts_to_file(script_text, out_audio_path)
    audio = AudioFileClip(str(out_audio_path))
    clip = CompositeVideoClip([bg, txt, body]).set_duration(audio.duration)
    clip = clip.set_audio(audio)
    out_path = out_dir / f"{uuid.uuid4().hex}.mp4"
    clip.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac', threads=0, verbose=False, logger=None)
    try:
        out_audio_path.unlink()
    except Exception:
        pass
    return str(out_path)
