import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from textblob import TextBlob

app = Flask(__name__)

# Function to perform sentiment analysis on a single review
def analyze_sentiment(review):
    sentiment_score = TextBlob(review).sentiment.polarity
    return 'Positive' if sentiment_score > 0 else 'Negative' if sentiment_score < 0 else 'Neutral'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the URL from the form submission
        url = request.form['url']

        # Define a list of user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            # Add more user agents as needed
        ]

        # Select a random user agent
        user_agent = random.choice(user_agents)

        try:
            # Send a GET request to the provided URL with the user-agent header
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <p> tags with the specified class
            p_tags = soup.find_all('p', class_='yelp-emotion-38n4c1')

            # Extract the text content of each matching <p> tag
            p_texts = [p_tag.get_text() for p_tag in p_tags]

            # Perform sentiment analysis on each review
            sentiments = [analyze_sentiment(review) for review in p_texts]

            # Calculate positive and negative percentages
            total_reviews = len(sentiments)

            if total_reviews > 0:
                positive_percentage = (sentiments.count('Positive') / total_reviews) * 100
                negative_percentage = (sentiments.count('Negative') / total_reviews) * 100
            else:
                positive_percentage = 0
                negative_percentage = 0

            return render_template('dashboard.html', url=url, p_texts=p_texts,
                                   positive_percentage=positive_percentage, negative_percentage=negative_percentage)

        except requests.RequestException as e:
            return f"Failed to retrieve the page. Error: {e}"

    return render_template('dashboard.html', url=None, p_texts=None,
                           positive_percentage=None, negative_percentage=None)

if __name__ == '__main__':
    app.run(debug=True)
