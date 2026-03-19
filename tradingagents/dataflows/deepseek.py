import os
from dotenv import load_dotenv
from openai import OpenAI
from .config import get_config

load_dotenv()


def get_stock_news_deepseek(query, start_date, end_date):
    config = get_config()
    client = OpenAI(
        base_url=config["deepseek_backend_url"],
        api_key=os.getenv("DEEPSEEK_API_KEY")
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": f"Can you search Social Media for {query} from {start_date} to {end_date}? Make sure you only get the data posted during that period.",
            }
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
    )

    return response.choices[0].message.content


def get_global_news_deepseek(curr_date, look_back_days=7, limit=5):
    config = get_config()
    client = OpenAI(
        base_url=config["deepseek_backend_url"],
        api_key=os.getenv("DEEPSEEK_API_KEY")
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": f"Can you search global or macroeconomics news from {look_back_days} days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period. Limit the results to {limit} articles.",
            }
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
    )

    return response.choices[0].message.content


def get_fundamentals_deepseek(ticker, curr_date):
    config = get_config()
    client = OpenAI(
        base_url=config["deepseek_backend_url"],
        api_key=os.getenv("DEEPSEEK_API_KEY")
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
            }
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
    )

    return response.choices[0].message.content
