---
title: Jarvis AI
updated: 2024-07-10 19:14:27Z
created: 2024-07-10 17:43:00Z
latitude: 32.96595660
longitude: -97.68363840
altitude: 0.0000
tags:
  - todo
---

# Jarvis AI
## AI Personal Assistant

- Build a local hosted AI (LLM) 
- use RAG and other memory mechanisms
- route to specialized LLMs as needed
- integrate all user data into context - the LLM is hosted on the user's local PC (interactable through Jan.ai open-source API) - this will allow for a personal assistant like we've never seen before

We want to use the most intelligent, uncensored, unbiased open-source LLM (Large-Language Model) currently available. Currently, it would be too expensive for us to train new models and we can't trust others with our data. So this is the route we take. It is the ONLY option.

### TODO:
* * *
- [ ] allow for main.py to populate_weaviate_document when Jarvis starts to make sure it always has the latest user data
- [ ] better yet, make it check while its running for any changes to data sources
- [ ] integrate Jarvis with Joplin
* * *

## How to start Jarvis AI:
1. open Jan.ai and start server
2. open Docker Desktop
	1. start Jarvis container
4. open PyCharm project `jarvis`
	1. run main.py
	2. interact with app through console


#### using Python
1. download and install latest Python
2. navigate to directory you want to put the files into
3. open cmd and create a virtual envrionment to manage dependencies and avoid conflicts:
`python -m venv venv`
3. activate the venv
`.\jarvis-venv\Scripts\activate`
4. start the app
`python main.py`


### Requirements:
`pip install logging`
`pip install weaviate-client`
`pip install aiohttp`
