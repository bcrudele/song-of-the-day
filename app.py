from flask import Flask, render_template, request, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Spotify API credentials
SPOTIFY_CLIENT_ID = 'Not Needed'
SPOTIFY_CLIENT_SECRET = 'Not Needed'
SPOTIFY_REDIRECT_URI = 'http://localhost:5000/callback'
SPOTIFY_SCOPE = 'user-library-read'

# Google Sheets credentials
# There are big issues when using google sheets as a storage, maybe look into clouded storage devices in the future, but for now this will do.
GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1Og5onhL1DU9396gB_SVpxreyhExtli5vviAJVTRR6VI/edit?usp=sharing'
GOOGLE_CREDENTIALS_FILE = 'credentials.json'  # DO NOT SHARE, contains keys

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    track_name = request.form['track_name']
    my_name = request.form['my_name']

    # Authenticate with Spotify
    sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                            client_secret=SPOTIFY_CLIENT_SECRET,
                            redirect_uri=SPOTIFY_REDIRECT_URI,
                            scope=SPOTIFY_SCOPE)
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    # Search for the track
    search_results = sp.search(track_name, type='track', limit=1)
    selected_track = search_results['tracks']['items'][0]

    # Authenticate with Google Sheets
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, ['https://spreadsheets.google.com/feeds'])
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open_by_url(GOOGLE_SHEET_URL)
    worksheet = sheet.get_worksheet(0)

    # Update Google Sheet with track information
    worksheet.append_row([my_name, selected_track['name'], selected_track['artists'][0]['name'], selected_track['album']['name'], selected_track['external_urls']['spotify']])
    return render_template('search_results.html', track_info=selected_track)

if __name__ == '__main__':
    app.run(debug=False)
