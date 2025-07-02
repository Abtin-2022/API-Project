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

def gemini_query(prompt):
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

def article_access(out):
    return out.json()['articles']

def link_extractor(articles): 
    return articles[0]['url']

def content_extractor(content):
    return content[0]['content']

def insert_to_db(category, content, engine):
    article_data = {
        'category': category,
        'content': content,
        'timestamp': pd.Timestamp.now()
    }
    
    # Create a DataFrame and append it to the database
    df_to_append = pd.DataFrame([article_data])
    df_to_append.to_sql('articles', con=engine, if_exists='append', index=False)
#print(nlp_key)

categories = ["general", "world", "nation", "business", "technology", "entertainment", "esports", "science", "health"]

database_dict = {category: [] for category in categories} # create a dictionary with all categories as keys and empty lists as values

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

response1 = gemini_query(
    f"From now on you are a professional suggester. Can you categorize the user's prompt, which is: {user}. According to this list of categories: {user_categories}? Only output `category` if the user uses one of the following words {categories}, catch misspelled words. Give just one word. If the user asks for their history like `i want my news health history`, then output `history`. If the user asks for something else, then output `general`.",
)

out = response1.text.lower()
print("Searching for:", out)

if out == 'category':
    response2 = gemini_query(
        f"From now on you are a professional suggester. Can you categorize the user's prompt, which is: {user}. According to this list of categories: {categories}? Give just one word.",
    )
    
    #print(response2.text)
    news_api_link = f'https://gnews.io/api/v4/top-headlines?category={response2.text}&apikey={news_key}'
    out = requests.get(news_api_link)
    articles = article_access(out)

    first_article_link = link_extractor(articles) # here maybe we need to check if the output is not empty (just to be safe)

    response3 = gemini_query(
        f"From now on you are a professional article reader. Can you read this article {first_article_link} and give back the whole content? If it's not in english, translate it to english. If you can't read it, just output the word `error` and absolutely nothing else, just the single word `error`.",
    )

    if response3.text.lower() == 'error':

        very_new_first_content = content_extractor(articles)

        response3 = gemini_query(
            f"From now on you are a professional article summarizer. Summarize the following as an article: {very_new_first_content}. Give a summary even if you have like 5 words of content. Do not output anything else, just the summary. Do not refuse!",
        )
    
    insert_to_db(response2.text, response3.text, engine)

    print(response3.text)

# If the user wants their history, we retrieve it from the database
# We use gemini to create the query for us
elif out == 'history':
    with engine.connect() as connection:
        
        response3 = gemini_query(
            f"From now on you are a professional sql programmer. According to the history user wants: {user}. If the user wants for example their business history you should output only business category. You can accept abbreviations like tech for technology. Createa an sql query to retrieve what they user is asking for. The table is called `articles` and has columns `category`, `content`, and `timestamp`. Timestamp looks like a string such as `2025-07-02 15:09:10.442605`. The query should return all articles in the table. Retrieve all articles the user wants. If the user wants a specific category, then filter by that category. If the user wants all articles, then return all articles. If the user wants a specific article, then filter by that article. If the user wants a specific date, then filter by that date. If the user wants a specific time range, then filter by that time range. If the user wants a specific keyword, then filter by that keyword. Only output valid SQL code, nothing else. Do not output any explanation or anything else, just the SQL code. NO MARKDOWN OR CODE BLOCKS, JUST THE SQL CODE.",
        )

        query_result = connection.execute(db.text(response3.text)).fetchall()
        print(pd.DataFrame(query_result))

# If the user wants news that is not in a category, we get it from the search endpoint
else:
    response2 = gemini_query(
        f"From now on you are a professional keyword querier. Can you give a set of keywords for use in an api query for the user's prompt, which is: {user}?  Give just keywords, nothing else. Do not output any explanation or markdown. you can see the corret query syntax in: https://gnews.io/docs/v4#search-endpoint-query-parameters. The query must be URL-encoded. It is not possible to use special characters without putting quotes around them.",
    )

    news_api_link = f'https://gnews.io/api/v4/search?q={response2.text}&apikey={news_key}'

    out = requests.get(news_api_link)
    articles = article_access(out)

    first_article_link = link_extractor(articles) # here maybe we need to check if the output is not empty (just to be safe)

    response3 = gemini_query(
        f"From now on you are a professional article reader. Can you read this article {first_article_link} and give back the whole content? If it's not in english, translate it to english. If you can't read it, just output the word `error` and absolutely nothing else, just the single word `error`.",
    )

    if response3.text.lower() == 'error':

        very_new_first_content = content_extractor(articles)

        response3 = gemini_query(
            f"From now on you are a professional article summarizer. Summarize the following as an article: {very_new_first_content}. Give a summary even if you have like 5 words of content. Do not output anything else, just the summary. Do not refuse!",
        )

    insert_to_db(response2.text, response3.text, engine)

    print(response3.text)





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