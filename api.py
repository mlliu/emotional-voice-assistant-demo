import os
import torch
import gradio as gr
from openai import OpenAI

from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
import whisper


def get_tts(path='openvoice/ckpts/', device='cuda'):
    ckpt_base = f'{path}/base_speakers/EN'
    ckpt_converter =  f'{path}/converter'    
    base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
    base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    return base_speaker_tts, tone_color_converter


def fake_chatgpt(text, history):
    return 'It is a fake chat!', 'sad'


def chatgpt(history):
    chat_completion = client.chat.completions.create(
        messages=history,
        model="gpt-3.5-turbo",
        temperature=0.7,
        # presence_penalty=0.6,
    )
    result = chat_completion.choices[0].message.content
    return result


def reformat(input_string, expected_keys=['content', 'emotion'], emotion_list=['sad', 'cheerful', 'whisper', 'default', 'friendly']):
    # Split the input string by new lines to separate the different parts
    parts = input_string.split("\n")
    # Create a dictionary to store the items
    result = {}
    # Process each part to split key and value, then add them to the dictionary
    for part in parts:
        key, value = part.split(": ")
        result[key.strip()] = value.strip().lower()
    if all(key in result for key in expected_keys) and all(key in expected_keys for key in result):
        if result['emotion'] not in emotion_list:
            result['emotion'] = 'default'
        return result['content'], result['emotion']
    else:
        return None


def chatbot(user, audio):
    if user == 'random':
        global user_id
        user_id += 1
        user = f'usr_{user_id}'
        
    global all_chats
    try:
        all_chats[user]
    except:
        all_chats[user] = None
        
    my_dict = all_chats[user]
    if my_dict is None:

        my_dict = [{'role': 'user',
                    'content': 'You are a chatgot for emotional therapy. Now, you need to answer user input by few sentence. '
                               'You need to reply in this format: "content: your reply content. \n emotion: the emotion will be used for the tts model. You should change it based on the conversation scene.\n'
                               'here are emotions you can use: [sad, cheerful, whisper, default, friendly]\n Let me know whenyou are ready.'},
                   {'role': 'assistant', 'content': 'I am ready now.'},
                   {'role': 'user', 'content': 'This is a test. Reply anything with default emotion.'},
                   {'role': 'assistant', 'content': 'content: yes. \n emotion: default.'}]
    if audio is not None:
        asr_result = whisper_model.transcribe(audio)['text']
        # print(asr_result)
    
        my_dict.append({'role': 'user', 'content': f'{asr_result}'})
    
        result_tts = None
    
        while result_tts is None:
            result = chatgpt(my_dict)
            print(result)
            result_tts = reformat(result)
        print(my_dict)
            
        my_dict.append({'role': 'assistant', 'content': f'{result}'})
        reply, emotion = result_tts
    
        base_speaker_tts.tts(reply, f'cache/reply_{user}.wav', speaker=emotion, language='English', speed=1.0)

        return f'cache/reply_{user}.wav', reply, None, asr_result, user
    else:
        return None, None, None, 'Please record your voice and try again.', user


if __name__ == '__main__':
    base_speaker_tts, tone_color_converter = get_tts(path='ckpts/tts_ckpts')
    whisper_model = whisper.load_model("ckpts/medium.pt")
    os.makedirs('cache', exist_ok=True)
    api_key = 'use your api here'
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=api_key,
    )
    all_chats = {}
    
    user_id = 0
    
    with gr.Blocks() as demo:
        with gr.Row():
            # column for inputs
            with gr.Column():
                user_key =  gr.Textbox(value='random', label="Your user id.", interactive=True)
                recorder = gr.Audio(label="Input Audio", sources=["microphone"], type="filepath",format="wav")
                submit_button = gr.Button("Submit")
                asr_result = gr.Textbox(label="Your speech transcription", interactive=False, show_copy_button=True)
            with gr.Column():
                player = gr.Audio(label="Output Audio", type='filepath', autoplay=True)
                text_output = gr.Textbox(label="Chatbot reply", interactive=False, show_copy_button=True)

        # audio2 = gr.Audio(label="Reference Audio", type='filepath')
        inputs = [user_key, recorder]
        outputs = [player, text_output, recorder, asr_result, user_key]
        submit_button.click(
                fn=chatbot,
                inputs=inputs,
                outputs=outputs)

    demo.launch(share=True)