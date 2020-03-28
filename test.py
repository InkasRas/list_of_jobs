from requests import get, post, patch
import json

get_all_users = get('http://127.0.0.1:5000/api/users')
print(json.dumps(get_all_users.json(), indent=2))
print('\n')
get_user = get('http://127.0.0.1:5000/api/users/2')
print(json.dumps(get_user.json(), indent=2))
add_user = post('http://127.0.0.1:5000/api/users', json={'surname': 'AHHA',
                                                         'name': 'KJHDSK',
                                                         'age': 23,
                                                         'position': 'ffffff',
                                                         'speciality': 'klsdjfld',
                                                         'address': 'lkdjlfjs',
                                                         'email': 'herl@mail.ddj',
                                                         'username': 'ushdhsjd',
                                                         'password': 'herty'})
print(add_user.json())
edit_user = patch('http://127.0.0.1:5000/api/users/10', json={'surname': 'HHHHH', 'age': 50})
print(edit_user.json())
