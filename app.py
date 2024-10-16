from flask import Flask, render_template, request
import requests
import autopy

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_data = None
    error_message = None
    
    if request.method == 'POST':
        username = request.form['username']
        user_response = requests.get(f'https://users.roblox.com/v1/users/search?keyword={username}')
        user_data_response = user_response.json()
        
        if 'errors' in user_data_response:
            for error in user_data_response['errors']:
                if error['message'] == 'Too many requests':
                    return render_template('loading.html')
        elif 'data' in user_data_response and len(user_data_response['data']) > 0:
            user_id = user_data_response['data'][0]['id']
            display_name = user_data_response['data'][0]['displayName']

            # Step 2: Get full user details
            user_details_response = requests.get(f'https://users.roblox.com/v1/users/{user_id}')
            user_details = user_details_response.json()
            join_date = user_details['created']

            # Step 3: Get friends count
            friends_response = requests.get(f'https://friends.roblox.com/v1/users/{user_id}/friends/count')
            friends_count = friends_response.json()['count']

            # Step 4: Get followers count
            followers_response = requests.get(f'https://friends.roblox.com/v1/users/{user_id}/followers/count')
            followers_count = followers_response.json()['count']

            # Step 5: Get following count
            following_response = requests.get(f'https://friends.roblox.com/v1/users/{user_id}/followings/count')
            following_count = following_response.json()['count']

            # Step 6: Get full-body avatar thumbnail
            avatar_response = requests.get(f'https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false')
            avatar_data = avatar_response.json()
            full_body_thumbnail = avatar_data['data'][0]['imageUrl']

            # Step 7: Get user groups
            groups_response = requests.get(f'https://groups.roblox.com/v1/users/{user_id}/groups/roles')
            groups_data = groups_response.json()

            # Process group data
            groups = []
            if 'data' in groups_data:
                for group in groups_data['data']:

                    groups.append({
                        'name': group['group']['name'],
                        'id': group['group']['id'],
                        'role': group['role']['name'],
                        'rank': group['role']['rank']
                    })

            user_data = {
                'userid': user_id,
                'username': username,
                'displayName': display_name,
                'joinDate': join_date,
                'friends': friends_count,
                'followers': followers_count,
                'following': following_count,
                'fullBodyAvatarThumbnail': full_body_thumbnail,
                'groups': groups,
            }
            pass
        else:
            error_message = "User not found or no data returned."

    return render_template('index.html', user_data=user_data, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
