# WRaThioN: WRTN Client For Python

> [!WARNING]
> This is an **unofficial** client.

## Installation

```bash
$ pip install WRaThioN
```

## Usage

## Requirements
- Python3 or newer
- [WRTN Account](https://wrtn.ai)

## Get Cookies

To use WRaThioN, you need a refresh token and an id called '__w_id' in the cookie.

You can retrieve cookies from [WRTN](https://wrtn.ai) as follows:
1. Go to [WRTN](https://wrtn.ai).
1. Log in with your WRTN account.
1. Open developer tools in your browser (usually by pressing 'F12').
1. You can view all cookies associated with 'https://wrtn.ai' by selecting the 'Application' tab and clicking on the 'Cookies' option.
1. Find the '__w_id' and 'refresh_token' cookies and click on them to expand their details.
1. Copy the value of each cookie.

## Use Prompt

```bash
$ python3 -m WRaThioN --help
usage: WRaThioN.py [-h] [--token TOKEN] [--id ID]

WRTN AI Prompt

options:
  -h, --help     show this help message and exit
  --token TOKEN  refresh token
  --id ID        wrtn id(__w_id)
```

## Example

```python
from WRaThioN import WRaThioN
import argparse
import asyncio

async def main() -> None:
    client = await WRaThioN.WRaThioN.WRTN(args.token, args.id)

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
```

