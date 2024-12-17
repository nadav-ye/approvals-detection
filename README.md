# approvals-detection

Hi,

In order to run the first assignment, please do the following:
1. make sure you have python 3.13.0 installed
2. make sure you're running from the base dir of the project
3. create a venv ("python3 -m venv venv")
4. activate the venv ("source venv/bin/activate")
5. install the requirements ("pip install -r 'requirements.txt'")
6. run "python my_approvals.py --address <address>"

In order to run the second assignment:
1. repeat 1-5 (if you havn't)
2. run "fastapi dev main.py"
3. please use the provided the request template ("query_example.sh") for the API (extracted from Postman)

notes:
1. there are some cases that I didn't fully understand what they meant - "0x" in data, that's different from 0, seems like a malformed log, I avoided those logs.
2. I didn't know if you meant to delete after a "0" amount of approval, I kept it (simply removable) as the latest approval.
3. the free tier of infura is 2000 creds per second: each "get logs" call costs 255 creds, and there might be more calls for contract names and chain verification (please see the next note), so the I limit with semaphore to 6 concurrent. Inside it, while calling for "eth_call" (80 creds) for each name, and eth_chainID (called multi times, 5 creds each) - i didn't passed the limit. I'm sure that it's possible to implement a caching mechanism for the chainID (verifying the chain AFAIK), but had to deliever.
4. having said that, the first run to get a lot of token names (specifically), will be slower, but as long as the app is up and running, it should be save in memory as a DB alternative. 
5. in a whole system, I'd use a DB for storing the name for each contract (if exists). For now, I kept it as in-memory map while the app is running.
6. the api for coin price is very limited (30 pre minute, 10k for month), i beleive that for a production we'd use a combination of a DB (even that it won't be the most updated), and / or a paid account. However, concatinating the token addresses saved a lot of API calls.
7. of course, API keys shouldn't be exposed like that (secrets and etc.)

Thanks,
Nadav
