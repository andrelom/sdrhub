import webrtcvad

def detect_voice(pcm_audio, sample_rate):
    vad = webrtcvad.Vad(3)
    AUDIO_FRAME_MS = 30
    frame_size = int(sample_rate * AUDIO_FRAME_MS / 1000)
    for i in range(0, len(pcm_audio) - frame_size + 1, frame_size):
        frame = pcm_audio[i:i+frame_size].tobytes()
        if vad.is_speech(frame, sample_rate):
            return True
    return False
