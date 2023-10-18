# from bardapi import BardCookies
import asyncio
import jwt
import logging
import aiohttp
import json
import argparse
    
async def on_request_start(session, context, params):
    logging.getLogger('aiohttp.client').debug(f'Starting request <{params}>')

class WRaThioN:
    def __init__(self, __w_id, level=None):
        logging.basicConfig(level=level)
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)

        self.session = aiohttp.ClientSession(headers={"X-Wrtn-Id": __w_id}, trace_configs=[trace_config])
        self.room = None

    @classmethod
    async def WRTN(cls, token, __w_id, level=None):
        self = cls(__w_id, level)
        await self._refresh_token(token)
        return self

    async def _refresh_token(self, token):
        async with self.session.post('https://api.wow.wrtn.ai/auth/refresh', headers={"Refresh": token}) as request:
            response = await request.json()
            if response['result'] != "SUCCESS":
                raise Exception("Failed to refresh token")
            decoded = jwt.decode(response['data']['accessToken'], options={"verify_signature": False})
            # print (decoded["email"])

            self.user=decoded["email"]
            self.session.headers.update({"Authorization": "Bearer "+response['data']['accessToken']})
            return response['data']['accessToken']
        
    async def create_chat(self):
        if(self.room):
            await self.delete_chat(self.room)
            self.room = None

        async with self.session.post(f'https://api.wow.wrtn.ai/chat') as request:
            response = await request.json()
            # print(response)
            result = response['result']
            if result != "SUCCESS":
                raise Exception("Failed to create chat session")

            self.room = response['data']['_id']

            return self.room
    
    async def delete_chat(self, room=None):
        room = room or self.room
        async with self.session.delete(f'https://api.wow.wrtn.ai/chat/{room}') as request:
            response = await request.json()
            # print(response)
            return response
        
    async def chat(self, text, model='gpt-4'):
        if(not self.room):
            await self.create_chat()

        async with self.session.post(f'https://william.wow.wrtn.ai/chat/{self.room}/stream',
                                     params={'model':model, 'platform': 'web', 'user':self.user}, 
                                     json={'message': text, 'reroll': False}) as request:
            response = await request.read()
            response = response.decode('utf-8').split('\n')
            matching = [s for s in response if '"content"' in s]
            response = json.loads(matching[0].replace('data: ', ''))
            return response
        
    async def tool(self, id, inputs, model='gpt-4'):
        text = text[:1500]
        async with self.session.post(url=f'https://studio-api.wow.wrtn.ai/store/tool/{id}/generate', 
                                     params={'model':model, 'platform': 'web', 'type': 'mini', 'user':self.user}, 
                                     json={"inputs": inputs,"model": model}, 
                                     headers={'Host': 'studio-api.wow.wrtn.ai', }) as request:
            response = await request.read()
            response = response.decode('utf-8').split('\n')
            matching = [s for s in response if '"content"' in s]
            response = json.loads(matching[0].replace('data: ', ''))

            return response
        

    async def close(self):
        await self.session.close()

async def main() -> None:
    client = await WRaThioN.WRTN(args.token, args.id)

    await client.create_chat()
    while True:
        prompt = input("You: ")

        if prompt == "!reset":
            await client.create_chat()
            continue
        elif prompt == "!exit":
            await client.delete_chat()
            await client.close()
            break

        print("Bot: ", end="", flush=True)
        response = await client.chat(prompt)
        print(response['message']['content'], end="", flush=True)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WRTN AI Prompt')
    parser.add_argument('--token', type=str, help='refresh token')
    parser.add_argument('--id', type=str, help='wrtn id(__w_id))')

    args = parser.parse_args()
    # print(args.token)
    # print(args.id)
    
    asyncio.run(main())
