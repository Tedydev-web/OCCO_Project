import requests
import json


def send_post_request(personal_access_token, bot_id, user_id, additional_messages):
    url = 'https://api.coze.com/v3/chat'
    headers = {
        'Authorization': f'Bearer {personal_access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'bot_id': bot_id,
        'user_id': user_id,
        'stream': True,  # Ensure streaming is supported
        'auto_save_history': True,
        'additional_messages': additional_messages
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

        if response.status_code == 200:
            full_content = ""
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        line = chunk.decode('utf-8').strip()

                        if line.startswith('event:'):
                            # Get event type
                            event_type = line[len('event:'):].strip()

                            if event_type =='conversation.chat.completed':
                                print('')


                        elif line.startswith('data:'):
                            # Process JSON data
                            data_str = line[len('data:'):].strip()
                            try:
                                data_json = json.loads(data_str)

                                if event_type == 'conversation.message.delta':
                                    content_part = data_json.get('content', '')
                                    full_content += content_part
                                    print(content_part, end='', flush=True)

                            except json.JSONDecodeError:
                                print(f"Invalid JSON data: {data_str}")

                    except Exception as e:
                        print(f"Error processing chunk: {e}")

        else:
            print(f'Error: {response.status_code}')
            print(response.text)

    except requests.RequestException as e:
        print(f"Request failed: {e}")


def chat_loop(personal_access_token, bot_id, user_id):
    additional_messages = []

    while True:
        user_message = input("Bạn: ")
        if user_message.lower() in ['exit', 'quit']:
            print("Kết thúc trò chuyện.")
            break

        # Thêm tin nhắn của người dùng vào danh sách
        additional_messages.append({
            'role': 'user',
            'content': user_message,
            'content_type': 'text'
        })

        # Gửi tin nhắn và nhận phản hồi
        send_post_request(personal_access_token, bot_id, user_id, additional_messages)

        # Ghi lại tin nhắn đã gửi
        additional_messages.append({
            'role': 'user',
            'content': user_message,
            'content_type': 'text'
        })


# Ví dụ về cách sử dụng hàm
personal_access_token = 'pat_tpBlkbGh9AHhdH4jCfigKizknR2CGaxNOJrCRsGtUiCPGm3wdh6q33HUEA0KR4ML'
bot_id = '7390246610821447698'
user_id = 'your_user_id'

chat_loop(personal_access_token, bot_id, user_id)
