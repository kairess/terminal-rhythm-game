from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import make_chunks
import pyaudio
import librosa
import sys
from KBHit import KBHit

song_path = 'songs/Powerup! - Jeremy Blake.mp3'
w, h = 50, 50
chunk_size = 20 # ms
map_empty = ' '
map_note = '='
bar_thickness = 3
left_margin = 20

y, sr = librosa.load(song_path, duration=None)

tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False, units='time')
beats = beats * 1000 # s to ms
print(tempo) # 83 beats per second == 1380 ms per beat (83/60*1000)
print(beats)

max_gap = 0
for i in range(len(beats)):
    if i + 1 >= len(beats):
        break

    gap = beats[i+1] - beats[i]
    if gap > max_gap:
        max_gap = gap

# ready for playing
time_counter = 0

song = AudioSegment.from_file(song_path)

p = pyaudio.PyAudio()

stream = p.open(
    format=p.get_format_from_width(song.sample_width),
    channels=song.channels,
    rate=song.frame_rate,
    output=True
)

# render
print('\x1b[2J', end='')

try:
    for chunk in make_chunks(song, chunk_size):
        time_counter += chunk_size

        stream.write(chunk._data)

        map = []
        for y in range(h):
            row = []
            for x in range(w + left_margin):
                row.append(map_empty)
            map.append(row)

        if len(beats) > 0:
            index = max(h - int((beats[0] - time_counter) / max_gap * h), 0)

            for y, row in enumerate(map):
                if y == index:
                    for x, el in enumerate(row):
                        for d in range(bar_thickness):
                            try:
                                map[y+d][x+left_margin] = map_note
                            except:
                                pass

            # remove the beat passed by
            if time_counter <= beats[0] < time_counter + chunk_size:
                beats = beats[1:]
                KBHit().getch()

        # print the map
        print('\x1b[H', end='')
        for row in map:
            for el in row:
                print(el, end='')
            print()
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()