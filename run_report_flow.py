import pathlib
import requests

base = pathlib.Path(__file__).resolve().parent
img_path = base / 'artifacts' / 'input_screenshots' / 'sample.png'
img_path.parent.mkdir(parents=True, exist_ok=True)
img_path.write_bytes(b'\x89PNG\r\n\x1a\nfake-image-bytes')

files = {'file': ('sample.png', img_path.read_bytes(), 'image/png')}

response = requests.post('http://127.0.0.1:8000/upload', files=files, params={'screen_name': 'Sample Screen'}, timeout=30)
print('UPLOAD', response.status_code, response.text)
payload = response.json()

gen = requests.post('http://127.0.0.1:8000/generate', json={'screen_name': payload['screen_name']}, timeout=30)
print('GENERATE', gen.status_code, gen.text)

generate_payload = gen.json()
review = requests.post('http://127.0.0.1:8000/review', json={'script': generate_payload['script'], 'app_name': 'Demo App'}, timeout=30)
print('REVIEW', review.status_code, review.text)

execute = requests.post('http://127.0.0.1:8000/execute', json={'script': generate_payload['script'], 'app_name': 'Demo App'}, timeout=30)
print('EXECUTE', execute.status_code, execute.text)

reports_dir = base / 'artifacts' / 'reports'
print('REPORTS', [p.name for p in reports_dir.glob('*')])
