import requests
import os
from google import genai
from google.genai import types
import nlpcloud
import types

genai.api_key = os.environ["key1"]
nlp_key = os.environ["key2"]
news_key = os.environ["key3"]

print(genai.api_key)
print(nlp_key)

# We get news from news api
news_api_link = f'https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={news_key}'
out = requests.get(news_api_link)
articles = out.json()['articles']
first_article_link = articles[0]['url']

# We parse the news and extract links

# TODO: send news and their links to db

# TODO: ask the user what news they want and get that news from the db

# We call Gemini and tell it to read and do stuff with our links
client = genai.Client(
    api_key=genai.api_key,
)

# We call nlpcloud for summarization of the news
second_client = nlpcloud.Client("bart-large-cnn", nlp_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"From now on you are a professional article reader. Read this article for me: {first_article_link}",
)

print(response.text)


#print(json['articles'][0]['content'])
print(second_client.summarization(response.text))