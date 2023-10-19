# from bardapi import BardCookies
import jwt
import requests
import logging
import json
import argparse
import sseclient
    
async def on_request_start(session, context, params):
    logging.getLogger('aiohttp.client').debug(f'Starting request <{params}>')

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
            # print (decoded["email"])

            self.user=decoded["email"]
            self.session.headers.update({"Authorization": "Bearer "+response['data']['accessToken']})
            return response['data']['accessToken']
        
    def __get_response(self, response):
        sse = sseclient.SSEClient(response)
        for event in sse.events():
            if event.event == 'message' and event.data.startswith('{"message":'):
                response = json.loads(event.data)
                return response
        
    def create_chat(self):
        if(self.room):
            self.delete_chat(self.room)
            self.room = None

        with self.session.post(f'https://api.wow.wrtn.ai/chat') as response:
            response = response.json()
            # print(response)
            result = response['result']
            if result != "SUCCESS":
                raise Exception("Failed to create chat session")

            self.room = response['data']['_id']

            return self.room
    
    def delete_chat(self, room=None):
        room = room or self.room
        with self.session.delete(f'https://api.wow.wrtn.ai/chat/{room}') as response:
            response = response.json()
            # print(response)
            return response
        
    def chat(self, text, model='gpt-4'):
        if(not self.room):
            self.create_chat()

        with self.session.post(f'https://william.wow.wrtn.ai/chat/{self.room}/stream', stream=True,
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
    parser.add_argument('--token', type=str, help='refresh token')
    parser.add_argument('--id', type=str, help='wrtn id(__w_id))')

    args = parser.parse_args()
    # print(args.token)
    # print(args.id)
    
    main()
