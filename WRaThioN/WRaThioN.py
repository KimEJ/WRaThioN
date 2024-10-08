# from bardapi import BardCookies
import jwt
import requests
import logging
import json
import argparse
import sseclient

API_SERVER_URL = "https://api.wrtn.ai/be"
GENERATE_API_SERVER_URL = 'https://william.wow.wrtn.ai'
SSO_URL = 'https://sso.wrtn.ai/',

async def on_request_start(session, context, params):
    logging.getLogger('requests.packages.urllib3').debug(f'Starting request <{params}>')

class WRaThioN:
    def __init__(self, token, __w_id, level=None):
        logging.basicConfig(level=level)
        self.session = requests.Session()
        self.session.headers.update({"X-Wrtn-Id": __w_id})
        self.__refresh_token(token)
        self.room = None

    def __refresh_token(self, token):
        with self.session.post('https://api.wow.wrtn.ai/auth/refresh', headers={"Refresh": token}) as response:
            response = response.json()
            if response['result'] != "SUCCESS":
                raise Exception("Failed to refresh token")
            decoded = jwt.decode(response['data']['accessToken'], options={"verify_signature": False})

            self.user=decoded["email"]
            self.session.headers.update({"Authorization": "Bearer "+response['data']['accessToken']})
            return response['data']['accessToken']
        
    def __get_response(self, response):
        sse = sseclient.SSEClient(response)
        for event in sse.events():
            if event.event == 'message' and event.data.startswith('{"message":'):
                response = json.loads(event.data)
                return response
            
    def login(self, email, password):
        with self.session.post('https://sso.wrtn.ai/server/auth/local', json={"email": email, "password": password}) as response:
            response = response.json()
            print(response)
            if response['result'] != "SUCCESS":
                raise Exception("Failed to login")
            decoded = jwt.decode(response['data']['accessToken'], options={"verify_signature": False})

            self.user=decoded["email"]
            self.session.headers.update({"Authorization": "Bearer "+response['data']['accessToken']})
            return response['data']['accessToken']
        
    def create_chat(self):
        if(self.room):
            self.delete_chat(self.room)
            self.room = None

        with self.session.post(f'https://api.wrtn.ai/be/chat') as response:
            response = response.json()
            result = response['result']
            if result != "SUCCESS":
                raise Exception("Failed to create chat session")

            self.room = response['data']['unitId']
            self.session.headers.update({"X-Wrtn-Unit-Id": self.room})

            return self.room
    
    def delete_chat(self, room=None):
        room = room or self.room
        with self.session.put(f'https://api.wrtn.ai/be/api/v2/chat/delete', data={"chatIds": room}) as response:
            response = response.json()
            return response
        
    def chat(self, text, model='gpt-4'):
        if(not self.room):
            self.create_chat()

        with self.session.post(f'https://api.wrtn.ai/be/chat/{self.room}/stream', stream=True,
                                     params={'model':model, 'platform': 'web', 'user':self.user}, 
                                     json={'message': text, 'reroll': False}) as response:
            return self.__get_response(response)
            
    def tool(self, id, inputs, model='gpt-4'):
        text = text[:1500]
        with self.session.post(url=f'https://studio-api.wow.wrtn.ai/store/tool/{id}/generate', stream=True,
                                     params={'model':model, 'platform': 'web', 'type': 'mini', 'user':self.user}, 
                                     json={"inputs": inputs,"model": model}, 
                                     headers={'Host': 'studio-api.wow.wrtn.ai', }) as response:
            return self.__get_response(response)

def main() -> None:
    client = WRaThioN(args.token, args.id)

    client.create_chat()
    while True:
        prompt = input("You: ")

        if prompt == "!reset":
            client.create_chat()
            continue
        elif prompt == "!exit":
            client.delete_chat()
            break

        print("Bot: ", end="", flush=True)
        response = client.chat(prompt)
        print(response['message']['content'], end="", flush=True)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WRTN AI Prompt')
    parser.add_argument('--token', type=str, help='refresh token', required=True)
    parser.add_argument('--id', type=str, help='wrtn id(__w_id)', required=True)


    args = parser.parse_args()
    main()
