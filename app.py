import os
import dash_auth
from urllib.parse import unquote
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback

#user defined functions
from callback import *                  
import threading
import time

# Define valid username-password pairs
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin123'
}

# Create the Dash app
app = Dash(__name__, external_stylesheets=['/assets/styles.css'], suppress_callback_exceptions=True)
app.server.secret_key = os.urandom(24)

# Add Basic Authentication to the app
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-data'),  # Store for user-specific data
    html.Div(id='page-content')  # Dynamic page content
])

# Home layout (Initial layout)
home_layout = html.Div([
    # Logo and Textarea
    html.Img(
            src='/assets/tektronix.png',
            className='tektronix-logo-left'
    ),
    html.Img(
        src='/assets/logo.png',
        className='tektronix-logomain'
    ),
    dcc.Textarea(
        id='my-input',
        value='',
        className='textareamain'
    ),
    dbc.Button(
        'Submit',
        id='submit-button',
        n_clicks=0,
        className='buttonmain'
    )
    #html.Div(id='output')  # Placeholder for displaying results
], className='container')

# Results layout
results_layout = html.Div([
    html.Div([
        dcc.Link(  # Wrap the logo in a link to navigate back to home
            html.Img(
                src='/assets/logo.png',
                className='tektronix-logoresult',
            ),
            href='/'  # This will redirect to the home page
        ),
        html.Div([
            dcc.Textarea(
                id='my-input-results',
                value='',
                className='textarea',
            ),
            dbc.Button(
                'Submit',
                id='submit-button-results',
                n_clicks=0,
                className='button'
            ),
            html.Img(
                src='/assets/profile_icon.png',
                className='logo'
            )
        ], className='search-area'),
    ], className='top-section'),

    # Bottom section
    html.Div(
        dcc.Loading(  # Loading component wrapping the entire bottom section
            html.Div(
                className='bottom-section',
                children=[
                    html.Div(id='left-section', className='left-section'),
                    html.Div(id='right-section', className='right-section')
                ]
            ),
            className="loading"  # Optional loading class for styling
        )
    )
])


# Video layout
video_layout = html.Div([
    dcc.Link(  # Wrap the logo in a link to navigate back to home
        html.Img(
            src='/assets/logo.png',
            className='tektronix-logoresult'
        ),
        href='/'
        # This will redirect to the home page
    ),
    dcc.Loading(  # Loading component wrapping the entire video layout
        html.Div([
            html.Div(id='video-header', className='video-header'),  # Placeholder for video controls or title
            html.Div(id='video-content', className='video-content'),  # Placeholder for the video content
            html.Div(id='response-text', className='response-text')  # Placeholder for displaying command output
        ], className='video-layout-content'),
        className="loading"  # Optional loading class for styling
    )
  # Placeholder for displaying command output
], className='video-layout')


# Callback to dynamically render different pages based on the URL
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-data', 'data')  # Get user data
)
def display_page(pathname, user_data):
    if pathname == '/results':
        return results_layout
    elif pathname.startswith('/Synopsis/'):  # Check if the URL is for a video
        video_file_name = pathname.split('/')[-1]  # Extract the file name from the URL
        video_file_name = unquote(video_file_name)
        #print(f'Line 128 Video file name: {pathname}{video_file_name}')  # Debugging line
        return video_layout  # Return the video layout
    else:
        return home_layout

# Client-side callback for main input
app.clientside_callback(
    """
    function(value) {
        // Wait for the document to fully load/render before interacting with it
        setTimeout(function() {
            // Get the current pathname (URL path)
            const pathname = window.location.pathname;
            console.log("Current Pathname:", pathname);

            let textarea, button;

            if (pathname === '/results') {
                textarea = document.getElementById('my-input-results');
                button = document.getElementById('submit-button-results');
            } else {
                textarea = document.getElementById('my-input');
                button = document.getElementById('submit-button');
            }

            console.log("Textarea:", textarea);
            console.log("Button:", button);

            if (textarea && button) {
                textarea.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter' && event.shiftKey) {
                        // Allow new line with Shift+Enter
                        return;
                    } else if (event.key === 'Enter') {
                        // Prevent new line and trigger the button click
                        event.preventDefault();
                        button.click();
                    }
                });
            }
        }, 500);  // Add a timeout of 500ms to ensure the page is loaded
        return value;
    }
    """,
    Output('my-input', 'value'),
    Input('my-input', 'value')
)


# Register all callbacks
register_callbacks(app)

# Run the app
# Run the app
if __name__ == '__main__':

    # Define folder path and start the monitoring thread
    folder_path = 'Upload_here'
    monitor_thread = threading.Thread(target=monitor_folder, args=(folder_path,))
    monitor_thread.daemon = True
    monitor_thread.start()

    #planning to create a monitoring system to .srt also

    # Start the application (assuming it's a Dash or Flask app)
    app.run_server(debug=False, host='0.0.0.0', port=2222)
