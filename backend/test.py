import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

if __name__ == "__main__":
    audio_path = '/path/to/your/audio/file.wav'  # Replace this with the actual path to your audio file
    transcription = transcribe_audio(audio_path)
    if transcription:
        print("Transcription successful!")
        print("Transcribed text:")
        print(transcription)
    else:
        print("Failed to transcribe the audio.")







