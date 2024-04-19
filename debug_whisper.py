import whisper


if __name__ == "__main__":
    model = whisper.load_model("whisper/medium.pt")
    # options = DecodingOptions(language='en', temperature=1.0)
    result = model.transcribe("cache/recorded.wav")
    print(result["text"])