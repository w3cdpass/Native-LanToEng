from flask import Flask, render_template, request
from pathlib import Path
import pyaudio
import wave
import openai
import os
import tempfile

app = Flask(__name__)

# Initialize the OpenAI client with the provided API key
client = openai.OpenAI(api_key='your api key')

def record_audio_and_transcribe(model="whisper-1", seconds=5, frames_per_buffer=3200, format=pyaudio.paInt16, channels=1, rate=16000):
    # Create a temporary WAV file to save the recorded audio
    output_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

    # Recording audio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=frames_per_buffer
    )

    print("Start recording...")
    frames = []
    for _ in range(0, int(rate / frames_per_buffer * seconds)):
        data = stream.read(frames_per_buffer)
        frames.append(data)

    print("Recording stopped")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Saving recorded audio to the temporary WAV file
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcribing audio using the OpenAI API
    with open(output_file, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            language="en"  # Specify the language as English
        )
    transcription_text = response.text
    print("Transcription:", transcription_text)  # Print the transcription

    # Clean up the temporary WAV file
    os.remove(output_file)

    return transcription_text  # Return the transcription text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if request.method == 'POST':
        transcription_text = record_audio_and_transcribe()
        return render_template('index.html', transcription_text=transcription_text)

if __name__ == '__main__':
    app.run(debug=True)
