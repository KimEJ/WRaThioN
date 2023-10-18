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
    def __init__(self, token, __w_id, level=logging.DEBUG):
        self.loop = asyncio.get_event_loop()
        logging.basicConfig(level=level)
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)

        self.session = aiohttp.ClientSession(headers={"X-Wrtn-Id": __w_id}, trace_configs=[trace_config])
        self.loop.run_until_complete(self._refresh_token(token))
        self.room = None

    async def _refresh_token(self, token):
        async with self.session.post('https://api.wow.wrtn.ai/auth/refresh', headers={"Refresh": token}) as request:
            response = await request.json()
            if response['result'] != "SUCCESS":
                raise Exception("Failed to refresh token")
            decoded = jwt.decode(response['data']['accessToken'], options={"verify_signature": False})
            print (decoded["email"])

            self.user=decoded["email"]
            self.session.headers.update({"Authorization": "Bearer "+response['data']['accessToken']})
            return response['data']['accessToken']
        
    async def create_chat(self):
        if(self.room):
            await self.delete_chat(self.room)
            self.room = None

        async with self.session.post(f'https://api.wow.wrtn.ai/chat') as request:
            response = await request.json()
            print(response)
            result = response['result']
            if result != "SUCCESS":
                raise Exception("Failed to create chat session")

            self.room = response['data']['_id']

            return self.room
    
    async def delete_chat(self, room):
        room = room or self.room
        async with self.session.delete(f'https://api.wow.wrtn.ai/chat/{room}') as request:
            response = await request.json()
            print(response)
            return response
        
    async def chat(self, text):
        if(not self.room):
            await self.create_chat()

        async with self.session.post(f'https://api.wow.wrtn.ai/chat/{self.room}/message', json={"content": text}) as request:
            response = await request.json()
            print(response)
            return response
        
    async def tool(self, id, inputs, model='gpt-4'):
        text = text[:1500]
        async with self.session.post(url=f'https://studio-api.wow.wrtn.ai/store/tool/{id}/generate', 
                                     params={'model':model, 'platform': 'web', 'user':self.user}, 
                                     json={"inputs": inputs,"model": model}, 
                                     headers={'Host': 'studio-api.wow.wrtn.ai', }) as request:
            response = await request.read()
            # data: {"chunk":null}\n\ndata: {"chunk":""}\n\ndata: {"chunk":"I"}\n\ndata: {"chunk":"\'m"}\n\ndata: {"chunk":" sorry"}\n\ndata: {"chunk":","}\n\ndata: {"chunk":" but"}\n\ndata: {"chunk":" I"}\n\ndata: {"chunk":" cannot"}\n\ndata: {"chunk":" generate"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" response"}\n\ndata: {"chunk":" without"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" specific"}\n\ndata: {"chunk":" context"}\n\ndata: {"chunk":" or"}\n\ndata: {"chunk":" user"}\n\ndata: {"chunk":" input"}\n\ndata: {"chunk":"."}\n\ndata: {"chunk":" Please"}\n\ndata: {"chunk":" provide"}\n\ndata: {"chunk":" more"}\n\ndata: {"chunk":" information"}\n\ndata: {"chunk":" or"}\n\ndata: {"chunk":" a"}\n\ndata: {"chunk":" specific"}\n\ndata: {"chunk":" question"}\n\ndata: {"chunk":" for"}\n\ndata: {"chunk":" me"}\n\ndata: {"chunk":" to"}\n\ndata: {"chunk":" answer"}\n\ndata: {"chunk":"."}\n\ndata: {"chunk":""}\n\ndata: {"chunk":null}\n\ndata: {"content":"I\'m sorry, but I cannot generate a response without a specific context or user input. Please provide more information or a specific question for me to answer."}\n\ndata: {"end":"[DONE]"}\n\n
            response = response.decode('utf-8').split('\n')
            matching = [s for s in response if '"content"' in s]
            response = json.loads(matching[0].replace('data: ', ''))

            return response
        

    async def close(self):
        await self.session.close()
        self.loop.close()

async def main(client: WRaThioN) -> None:
    await client.create_chat()
    while True:
        prompt = input("You: ")

        if prompt == "!reset":
            await client.create_chat()
            continue
        elif prompt == "!exit":
            await client.delete_chat()
            break

        print("Bot: ", end="", flush=True)
        async for response in client.chat(prompt):
            print(response, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WRTN AI Prompt')
    parser.add_argument('--token', type=str, help='refresh token')
    parser.add_argument('--id', type=str, help='wrtn id(__w_id))')

    args = parser.parse_args()
    print(args.token)
    print(args.id)
    client = WRaThioN(args.token, args.id) 

    asyncio.run(main(client))
