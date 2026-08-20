@st.cache_data(show_spinner=False)
def load_data():
    import requests

    # rfm and journey are in the repo directly
    rfm     = pd.read_csv('golootlo_rfm.csv',     low_memory=False)
    journey = pd.read_csv('golootlo_journey.csv', low_memory=False)

    # scored is too large for GitHub — load from Drive
    if not os.path.exists('scored.csv') or os.path.getsize('scored.csv') < 1000000:
        session = requests.Session()
        file_id = '1rk40X6Kqcntr5mk7eheZ0z7UdDfybT2Z'
        url = f'https://drive.google.com/uc?id={file_id}&export=download&confirm=t'
        response = session.get(url, stream=True)
        token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                token = value
        if token:
            url = f'https://drive.google.com/uc?id={file_id}&export=download&confirm={token}'
            response = session.get(url, stream=True)
        with open('scored.csv', 'wb') as f:
            for chunk in response.iter_content(32768):
                if chunk:
                    f.write(chunk)

    scored = pd.read_csv('scored.csv', low_memory=False)
    scored['DATE'] = pd.to_datetime(scored['DATE'], errors='coerce')
    return scored, rfm, journey
