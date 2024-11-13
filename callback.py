import os
import time
import subprocess
from urllib.parse import unquote,quote
from dash import html, Input, Output, State
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from turntranscript import transcribe_and_save
from pdf_to_txt import generate_text_from_pdf


from chromadex import process_query

#These functions dont HAVE CALLBACKS

def validate_and_move_file(src_path, dest_path, file_name):
    # Validate the MP4 file using ffmpeg

    if(file_name.endswith(('.mp4'))):
        result = subprocess.run(['ffmpeg', '-v', 'error', '-i', src_path, '-f', 'null', '-'], capture_output=True, text=True)
        if result.returncode == 0:
            transcribe_and_save(src_path)
            dest_path = os.path.join('assets', 'videos', file_name)
            # Check if the file already exists at the destination
            if os.path.exists(dest_path):
                print(f"File {file_name} already exists in the destination. Skipping move.")
            else:
                os.rename(src_path, dest_path)
                print(f"Moved file {file_name} to assets/videos")
        else:
            print(f"Validation failed for {file_name}")

    elif file_name.endswith(('.txt', '.srt')):
        print(f"Ending with txt or srt: {file_name}")
        dest_path = os.path.join('srts', file_name)
        # Check if the file already exists at the destination
        if os.path.exists(dest_path):
            print(f"File {file_name} already exists in 'srts'. Skipping move.")
        else:
            os.rename(src_path, dest_path)
            print(f"Moved file {file_name} to srts")

    else:
        if(file_name.endswith(('.pdf'))):
            generate_text_from_pdf(file_name)        

def monitor_folder(folder_path):
    # Ensure 'assets/videos' folder exists
    os.makedirs('assets/videos', exist_ok=True)

    # Move any existing files initially
    existing_files = set(os.listdir(folder_path))
    for file in existing_files:
        if file.endswith(('.mp4', '.srt', '.txt', '.pdf')):
            src_path = os.path.join(folder_path, file)
            dest_path = os.path.join('assets', 'videos', file)
            validate_and_move_file(src_path, dest_path,file)
        
    # Monitor for new files
    existing_files = set(os.listdir(folder_path))
    while True:
        time.sleep(5)  # Check every 5 seconds
        current_files = set(os.listdir(folder_path))
        new_files = current_files - existing_files
        if new_files:
            for new_file in new_files:
                if file.endswith(('.mp4', '.srt', '.txt', '.pdf')):  # Only process video files
                    src_path = os.path.join(folder_path, new_file)
                    dest_path = os.path.join('assets', 'videos', new_file)
                    validate_and_move_file(src_path, dest_path,new_file)
            # Update the list of existing files after moving
            existing_files = set(os.listdir(folder_path))

def load_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    return srt_content

def get_video_content(file_name, videos_folder):
    #print(f"14 . Checking file name: {file_name}")  # Debugging line
    mp4_file_name = file_name.replace('.srt', '.mp4')
    video_url = f'assets/videos/{quote(mp4_file_name)}'  # Update this line
    file_path = os.path.join(videos_folder, mp4_file_name)
    #print(f"Checking file path: {file_path}")  # Debugging line
    
    if os.path.exists(file_path):
        #print(f"Video URL: {video_url}{file_path}")  # Debugging line
        video_file_name = video_url.split('/')[-1]
        video_div = html.Div([
            #print("debug line 66: ",video_url),
            html.Video(src=video_url, controls=True, style={'width': '100%', 'border-radius': '0.5rem'}),
            html.A(  # Wrap only the file name in an anchor tag
                html.P(unquote(video_file_name),className='file-name-box'),
                href=f'/Synopsis/{(video_file_name)}',  # URL to redirect to when clicked
                #target='_blank',  # Opens the link in a new tab
                style={'textDecoration': 'none'}  # Remove underline from the link
            )
        ], className='video-file')
        
        return video_div
    else:
        file_nonvideo_url = f'srts/{file_name}'
        #print(f"Video file does NOT exist but: {file_nonvideo_url}")

        video_div = html.Div([
            #print("debug line 82: ",video_url),
            #html.Video(src=file_nonvideo_url, controls=True, style={'width': '100%', 'border-radius': '0.5rem'}),
            html.A(  # Wrap only the file name in an anchor tag
                html.P(file_name,className='file-name-box'),
                href=f'/Synopsis/{quote(file_name)}',  # URL to redirect to when clicked
                #target='_blank',  # Opens the link in a new tab
                style={'textDecoration': 'none'}  # Remove underline from the link
            )
        ], className='video-file')
        
        return video_div
        print(f"Video file does NOT exist but: {file_nonvideo_url}")  # Debugging line
    return None

#This function has CALLBACKS
def register_callbacks(app):

    # Callback for handling query submission on home page Page 1
    @app.callback(
        Output('user-data', 'data'),  # Store both query and result
        Output('url', 'pathname'),     # Change the URL to '/results'
        Input('submit-button', 'n_clicks'),
        State('my-input', 'value')
    )
    def handle_home_query(n_clicks, input_value):
        #print(f'Button clicked: {n_clicks}, Input value: "{input_value}"')  # Debug statement
        if n_clicks > 0:
            if input_value:
                return {'query': input_value}, '/results'
        return "",""

    # Callback for handling query submission on results page Page 2
    @app.callback(
        Output('left-section', 'children'),
        Output('right-section', 'children'),
        Output('my-input-results', 'value'),
        Input('submit-button-results', 'n_clicks'),
        State('my-input-results', 'value'),
        State('user-data', 'data')
    )
    def handle_results_query(n_clicks ,input_value, user_data):
        right_section_content = []  # List to hold the content for the right section

        if n_clicks > 0 and input_value:
            # Process the new query
            result, unique_file_names = process_query(input_value)
            #print(unique_file_names)  # Debugging line
            videos_folder = 'assets/videos/'  # Accessing the videos folder

            # Check for videos corresponding to the results
            for file_name in unique_file_names:
                video_content = get_video_content(file_name, videos_folder)
                if video_content:
                    right_section_content.append(video_content)
                else:
                    print("No video content found")

            return html.Div(f'{result}', className='response-text'), right_section_content, input_value

        # Load the query and result from user data when page loads
        if user_data:
            query = user_data.get('query', '')
            result, unique_file_names = process_query(query)
            videos_folder = 'assets/videos/'

            # Check for videos corresponding to the results
            for file_name in unique_file_names:
                video_content = get_video_content(file_name, videos_folder)
                if video_content:
                    right_section_content.append(video_content)

            return html.Div(f'{result}', className='response-text'), right_section_content, query

        return "", "", ""

    # Callback for displaying the video on the video page Page 3
    @app.callback(
        Output('video-header', 'children'),  # Update video-header to include the video element
        Output('video-content', 'children'),  # Update response-text with command output #may b put response-text in video-content
        Input('url', 'pathname'),
        State('user-data', 'data')  # Get user data
    )
    def display_video_summary(pathname, user_data):
        if pathname.startswith('/Synopsis/'):

            video_file_name = pathname.split('/')[-1]  # Extract the file name from the URL
            video_file_name = unquote(video_file_name)
            #print("debug line 100",video_file_name)

            video_url = f'/assets/videos/{quote(video_file_name.replace(".srt", ".mp4"))}'  # Assuming the video is in MP4 format
            video_path = os.path.join('assets/videos', video_file_name.replace(".srt", ".mp4"))
            
            if os.path.exists(video_path):
                #print(f"130.Video URL: {video_path}{video_url}")  # Debugging line
                video_element = html.Video(src=video_url, controls=True, className='video-header video')
            else:
                #print(f"141.Video URL: {video_path}{video_url}")
                document_path = os.path.join('srts', video_file_name.replace('.mp4', '.srt'))
                srt_content = load_srt(document_path)
                video_element = html.Pre(srt_content,className='video-header pre')

            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            doc_file_name = video_file_name.replace('.mp4', '.srt')
            #print(f"Document file name: {doc_file_name}")
            command = f"Get-Content -Path '{current_dir}\\srts\\{doc_file_name}' | fabric --pattern summarize"
            #print(command)  # Debugging line

            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)             # Run the PowerShell command

            # Get the output
            command_output = result.stdout if result.stdout else "No output or error occurred."
            return video_element, html.Div(command_output, className='response-text')  # Return both video element and command output
        return "", ""