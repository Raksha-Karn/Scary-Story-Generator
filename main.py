import praw 
from dotenv import load_dotenv
import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import time


load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET_KEY"),
    password=os.getenv("PASSWORD"),
    user_agent=os.getenv("USER_AGENT"),
    username=os.getenv("USERNAME"),
)

print("-" * 40)
print("WELCOME TO THE SCARY STORY GENERATOR! 👻")
print("-" * 40 + "\n")
post_url = input("Enter the URL of the reddit post: ")


def divide_into_sections(text):
    llm = OllamaLLM(model="gemma2:2b")
    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a scary story editor who analyzes a scary story,
                        Above story is a very scary story that needs to be divided into three paragraphs, which are introduction, build up, and climax. Please split the story into these sections, ensuring that each one builds suspense and maintains a cohesive narrative flow. Do not write any section names in the response just divide them into sections. Do not write title just story.
                        The sections should seamlessly transition from one to the next, with each part intensifying the horror and contributing to the overall frightening atmosphere.
                        Make sure it sounds spooky not simple, bland or cringe dont generate anything else than story just return the story dividing into section separated by new line'''),
        ("user", "{input}")
    ])
    
    chain = prompt | llm 
    out = chain.invoke({"input": text})

    sections = out.split("\n")
    
    filtered_sections = []
    
    for section in sections:
        if section.strip() != "":
            filtered_sections.append(section)
            
    return filtered_sections[1:]


def create_audio_files(sections, title):
    audio_files = []
    for index, section in enumerate(sections):
        tts = gTTS(section, lang='en')
        file_name = f"{index+1}_{title}.mp3"
        tts.save(file_name)
        audio_files.append(file_name)
    return audio_files


def apply_scary_effects(audio):
    lowered = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * 0.9)
    })
    
    filtered = lowered.low_pass_filter(3000).high_pass_filter(300)
    
    reverb = filtered.reverse().reverse()
    
    louder = reverb + 3
    
    return louder


def load_wind_sound(file_path, volume=1):
    wind = AudioSegment.from_mp3(file_path)
    
    wind = wind + volume
    
    return wind


def combine_audio_files(audio_files, wind_file_path, pause_duration_ms=2000):
    combined = AudioSegment.empty()
    pause = AudioSegment.silent(duration=pause_duration_ms)
    
    wind = load_wind_sound(wind_file_path)
    
    total_duration = sum(AudioSegment.from_file(file).duration_seconds for file in audio_files) * 1000 + len(audio_files) * pause_duration_ms
    
    looped_wind = wind * (int(total_duration / len(wind)) + 1)
    looped_wind = looped_wind[:int(total_duration)]
    
    wind_position = 0
    for file in audio_files:
        audio = AudioSegment.from_file(file)
        scary_audio = apply_scary_effects(audio)
        
        segment_with_wind = scary_audio.overlay(looped_wind[wind_position:wind_position+len(scary_audio)])
        
        combined += segment_with_wind + pause
        
        wind_position += len(scary_audio) + pause_duration_ms
    
    return combined
        

try:    
    submission = reddit.submission(url=post_url)
    print("GETTING YOUR STORY...")
    
    title = submission.title
    
    body = submission.selftext
    
    input_text = f"Title: {title}\n\n{body}"
    print(f"ANALYZING {title}...")

    divided_sections = divide_into_sections(input_text)
        
    with open(f"{title}.txt", "w") as file:
        file.write("\n".join(divided_sections))
    
    print("CONVERTING STORY TO SCARY VOICE...")
        
    audio_files = create_audio_files(divided_sections, title)
    
    combined_audio = combine_audio_files(audio_files, "wind.mp3")
    
    for file in audio_files:
        os.remove(file)
    
    output_file = f"{title}.mp3"
    combined_audio.export(output_file, format="mp3")
    
    print(f"Audio file saved to {output_file}")
    
    intro = f"Story {submission.title} by {submission.author.name}"
    tts1 = gTTS(intro, lang='en')
    tts1.save("intro.mp3")
    play(AudioSegment.from_file("intro.mp3"))
    
    time.sleep(2)
    
    play(AudioSegment.from_mp3(output_file))
    
    time.sleep(2)
    
    ending = "The end"
    tts2 = gTTS(ending, lang='en')
    tts2.save("ending.mp3")
    play(AudioSegment.from_file("ending.mp3"))
    
    os.remove("intro.mp3")
    os.remove("ending.mp3")
    
    print("THE END!")


except Exception as e:
    print(e)
