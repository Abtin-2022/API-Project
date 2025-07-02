import requests
import os
from google import genai
from google.genai import types
import nlpcloud
import types
import pandas as pd
import sqlalchemy as db

genai.api_key = os.environ["key1"]
nlp_key = os.environ["key2"]
news_key = os.environ["key3"]
# TODO: create env variable
database_dict = {}


print(genai.api_key)
#print(nlp_key)

categories = ["general", "world", "nation", "business", "technology", "entertainment", "esports", "science", "health"]

engine = db.create_engine('sqlite:///out.db') # initialize database at beginning

# We ask the user what news they want
user = str(input("Do you want to read an article or retrieve your history?\n"))

# We use gemini first to tell us if the user is asking for:
# - a category of news
# - previous news they asked for in the past (their history) 
# - for news that are not in a category

user_categories = ["category", "history", "general"]

client = genai.Client(
    api_key=genai.api_key,
)

response1 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"From now on you are a professional suggester. Can you categorize the user's prompt, which is: {user}. According to this list of categories: {user_categories}? To be in the category `category` means that the user is asking for one of the following categories: {categories}. Give just one word.",
)
out = response1.text.lower()
print(out)

if out == 'category':
    response2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"From now on you are a professional suggester. Can you categorize the user's prompt, which is: {user}. According to this list of categories: {categories}? Give just one word.",
    )
    
    #print(response2.text)
    news_api_link = f'https://gnews.io/api/v4/top-headlines?category={response2.text}&apikey={news_key}'
    out = requests.get(news_api_link)
    articles = out.json()['articles']

    first_article_link = articles[0]['url']

    response3 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"From now on you are a professional article reader. Can you read this article {first_article_link} and give back the whole content?",
    )

    
    if response2.text in database_dict.keys():
        database_dict[response2.text].append(response3.text)
    else:
        database_dict[response2.text] = [response3.text]
    print(response3.text)
    out = pd.DataFrame.from_dict(database_dict)
    print(out)
    out.to_sql('articles', con=engine, if_exists='append', index=True) # update for database
    print(out)





#database stuff
elif out == 'history':
    with engine.connect() as connection: # just access the stuff from the database, but we need to change the query for accessing
        query_result = connection.execute(db.text("SELECT * FROM articles;")).fetchall()
        print(pd.DataFrame(query_result))

# the query for searching general info not categorized
else:
    pass





# TODO: if user asks for a category we use the category endpoint

# TODO: else user asks for "show me the all new previous news I asked about" then we retrieve from the db

# TODO: else we use gemini to create the api url (for correct formatting for the url)

# We get news from news api
# news_api_link = f'https://gnews.io/api/v4/top-headlines?category={category}&apikey={news_key}'
# out = requests.get(news_api_link)
# articles = out.json()['articles']
# first_article_link = articles[0]['url']

# We parse the news and extract all links

# TODO: send news and their links to db to create a history



# We call Gemini and tell it to read and do stuff with our links


# We call nlpcloud for summarization of the news
# second_client = nlpcloud.Client("bart-large-cnn", nlp_key)

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=f"From now on you are a professional article reader. Read this article for me: {first_article_link}",
# )

# print(response.text)


#print(json['articles'][0]['content'])
# print(second_client.summarization(response.text))