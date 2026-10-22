import subprocess
import imageio_ffmpeg
import os
import re

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

scenes = ['scene1', 'scene2', 'scene3', 'scene4', 'scene5', 'scene6', 'scene7', 'scene8']
durations = []

for s in scenes:
    f = f'public/urubo-bella-flor/images/vo_{s}.mp3'
    res = subprocess.run([ffmpeg, '-i', f], capture_output=True, text=True)
    m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', res.stderr)
    if m:
        dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
        durations.append(dur)
    else:
        durations.append(6.0)

print('Durations:', durations)
print('Total:', sum(durations))

# Create concat list for ffmpeg
with open('scripts/audio_concat.txt', 'w', encoding='utf-8') as f:
    for s in scenes:
        f.write(f"file '../public/urubo-bella-flor/images/vo_{s}.mp3'\n")

cmd = [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', 'scripts/audio_concat.txt', '-c', 'copy', 'public/urubo-bella-flor/images/full_voiceover.mp3']
subprocess.run(cmd, check=True)
print('full_voiceover.mp3 created!')
