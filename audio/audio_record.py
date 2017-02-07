import pyaudio, wave

BUFFER_SIZE = 256
REC_SECONDS = 5
RATE = 44100
WAV_FILENAME = 'test.wav'
FORMAT = pyaudio.paInt16

#init sound stream
pa = pyaudio.PyAudio()
stream = pa.open(
    format = FORMAT,
    input = True,
    channels = 1,
    rate = RATE,
    input_device_index = 2,
    frames_per_buffer = BUFFER_SIZE
)

#run recording
print('Recording...')
data_frames = []
for f in range(0, RATE/BUFFER_SIZE * REC_SECONDS):
    data = stream.read(BUFFER_SIZE)
    data_frames.append(data)
print('Finished recording...')
stream.stop_stream()
stream.close()
pa.terminate()

wf = wave.open(WAV_FILENAME, 'wb')
wf.setnchannels(1)
wf.setsampwidth(pa.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(data_frames))
wf.close()
