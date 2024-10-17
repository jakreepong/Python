from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_data = None
    error_message = None
    current_year = datetime.now().year
    
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

            # Step 7: Get avatar items (assets)
            avatar_items_response = requests.get(f'https://avatar.roblox.com/v1/users/{user_id}/avatar')
            avatar_items = avatar_items_response.json()

            # Get user groups
            groups_response = requests.get(f'https://groups.roblox.com/v1/users/{user_id}/groups/roles')
            groups_data = groups_response.json()

            def get_group_details(group_id):
                url = f'https://groups.roblox.com/v1/groups/{group_id}'
                response = requests.get(url)
                data = response.json()
                return data

            #Get asset thumbnail
            def get_asset_thumbnail(item_id):
                url = f'https://thumbnails.roblox.com/v1/assets?assetIds={item_id}&size=150x150&format=Png'
                response = requests.get(url)
                data = response.json()

                if 'data' in data and len(data['data']) > 0:
                    return data['data'][0]['imageUrl']
                return None

            # Get group thumbnail
            def get_group_thumbnail(group_id):
                url = f'https://thumbnails.roblox.com/v1/groups/icons?groupIds={group_id}&size=150x150&format=Png'
                response = requests.get(url)
                data = response.json()

                if 'data' in data and len(data['data']) > 0:
                    return data['data'][0]['imageUrl']
                return None
            
            avatar_items_list = []
            if 'assets' in avatar_items:
                for item in avatar_items['assets']:
                    asset_thumbnail = get_asset_thumbnail(item['id'])
                    avatar_items_list.append({
                        'name': item['name'],
                        'assetType': item['assetType'],
                        'id': item['id'],
                        'imageUrl': asset_thumbnail
                    })

            groups = []
            if 'data' in groups_data:
                for group in groups_data['data']:
                    group_id = group['group']['id']
                    group_details = get_group_details(group_id)
        
                    group_name = group_details.get('name', 'Unknown Group')
                    group_description = group_details.get('description', 'No Description Available')
                    group_owner = group_details.get('owner', {})
                    owner_username = group_owner.get('username', 'Unknown Owner')
                    owner_display_name = group_owner.get('displayName', 'Unknown Owner Display Name')
                    member_count = group_details.get('memberCount', 0)
                    public_entry_allowed = group_details.get('publicEntryAllowed', False)
                    has_verified_badge = group_details.get('hasVerifiedBadge', False)
        
                    group_thumbnail = get_group_thumbnail(group_id)

                    groups.append({
                        'name': group_name,
                        'id': group_id,
                        'role': group['role']['name'],
                        'rank': group['role']['rank'],
                        'thumbnail': group_thumbnail,
                        'description': group_description,
                        'owner_username': owner_username,
                        'owner_display_name': owner_display_name,
                        'member_count': member_count,
                        'public_entry_allowed': public_entry_allowed,
                        'has_verified_badge': has_verified_badge,
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
                'avatarItems': avatar_items_list,
            }
        else:
            error_message = "User not found or no data returned."

    return render_template('index.html', user_data=user_data, error_message=error_message, current_year=current_year)

if __name__ == '__main__':
    app.run(debug=True)
