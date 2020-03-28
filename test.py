from requests import get, post, delete, patch
import json
import datetime

# ID не существует
print(patch('http://127.0.0.1:5000/api/jobs/500', json={'collaborators': '1, 4, 3'}).json())

# Нет такой колонки в таблице(bad_attr)
print(patch('http://127.0.0.1:5000/api/jobs/13', json={'bad_attr': 'No', 'collaborators': '1, 4, 3'}).json())

print(patch('http://127.0.0.1:5000/api/jobs/13', json={'collaborators': '1, 4, 3'}).json())
print(json.dumps(get('http://127.0.0.1:5000/api/jobs').json(), indent=2))
