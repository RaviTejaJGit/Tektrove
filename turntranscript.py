import os
import whisper
from tqdm import tqdm

# Load the Whisper model
model = whisper.load_model("base")

# Define the folder containing the videos and the folder to save transcripts
video_folder = "assets/videos"
transcript_folder = "srts"

# Create the transcript folder if it doesn't exist
os.makedirs(transcript_folder, exist_ok=True)

# Function to convert seconds to SRT timestamp format
def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"


# Function to transcribe, save SRT file, and create a PDF for a given video
def transcribe_and_save(video_path):
    print(f"Turntranscript.py '{video_path}'...")
    # Define the SRT file path in the transcript folder
    base_name = os.path.basename(video_path)
    name, _ = os.path.splitext(base_name)
    srt_file_path = os.path.join(transcript_folder, f"{name}.srt")

    # Skip transcription if the SRT file already exists
    if os.path.exists(srt_file_path):
        print(f"SRT file already exists for '{video_path}'. Skipping...")
        return
    
    # Transcribe the video with time stamps
    result = model.transcribe(video_path, language='en', task='transcribe',fp16=False)
    
    # Prepare the content for SRT
    srt_content = ""
    
    for i, segment in enumerate(result['segments']):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        
        srt_content += f"{i + 1}\n"
        srt_content += f"{start} --> {end}\n"
        srt_content += f"{text}\n\n"
    
    # Save SRT file
    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        srt_file.write(srt_content)
    
    print(f"Transcription saved as '{srt_file_path}'")
'''
# Get the list of video files in the specified folder
video_files = [f for f in os.listdir(video_folder) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]

# Process each video in the specified folder
for file_name in tqdm(video_files, desc="Processing videos"):
        video_path = os.path.join(video_folder, file_name)
        transcribe_and_save(video_path)

print("All transcriptions completed.")
'''
