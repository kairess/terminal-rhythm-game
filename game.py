from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import make_chunks
import pyaudio
import librosa
from pyfiglet import figlet_format
import time
import warnings
warnings.filterwarnings('ignore')
from KBHit import KBHit

song_path = 'songs/Powerup! - Jeremy Blake.mp3'
w, h = 50, 50
chunk_size = 20 # ms
map_empty = ' '
map_line = '-'
map_note = '='
bar_thickness = 3
margin = 20

print('\x1b[2J', end='')
print(figlet_format('LOADING...', font='starwars'))

y, sr = librosa.load(song_path, duration=None)

tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False, units='time')
beats = beats * 1000 # s to ms

avg_gap = (beats[1:] - beats[:-1]).mean()

# ready for playing
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
for i in range(3):
    print(figlet_format('%s' % (3-i), font='starwars'))
    time.sleep(1)
    print('\x1b[2J', end='')
print(figlet_format('START!', font='starwars'))
time.sleep(1)
print('\x1b[2J', end='')

try:
    time_counter = 0

    for chunk in make_chunks(song, chunk_size):
        time_counter += chunk_size

        stream.write(chunk._data)

        map = []
        for y in range(h):
            row = []
            for x in range(w + margin * 2):
                if y == 0 or y == h - 1:
                    row.append(map_line)
                else:
                    row.append(map_empty)
            map.append(row)

        if len(beats) > 0:
            index = max(h - int((beats[0] - time_counter) / avg_gap * h), 0)

            for y in range(h):
                if y == index:
                    for x in range(margin, w + margin):
                        for d in range(bar_thickness):
                            try:
                                map[y+d][x] = map_note
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
