from huggingface_hub import InferenceClient

client = InferenceClient(token="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")

def transcribe_audio(file_path: str) -> str:
    output = client.automatic_speech_recognition(
        file_path,
        model="boumehdi/wav2vec2-large-xlsr-moroccan-darija"
    )
    return output.get("text", "")
