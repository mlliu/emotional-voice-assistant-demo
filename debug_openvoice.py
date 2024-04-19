import os
import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
import whisper


def get_tts(path='openvoice/ckpts/'):
    ckpt_base = f'{path}/base_speakers/EN'
    ckpt_converter =  f'{path}/converter'
    
    device="cuda:0" if torch.cuda.is_available() else "cpu"
    
    base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
    base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')
    
    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    return base_speaker_tts, tone_color_converter


if __name__ == "__main__":
    base_speaker_tts, tone_color_converter = get_tts(path='openvoice/ckpts/')

    text = "I know how are you feeling now."
    src_path = f'test.wav'
    base_speaker_tts.tts(text, src_path, speaker='sad', language='English', speed=0.9)