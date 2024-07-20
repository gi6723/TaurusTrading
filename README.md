## Overview
TaurusTrading is a personal project developed as part of a portfolio for a my major. It's designed to automate a daily stock trading algorithm, leveraging various technologies to analyze and select stocks for day trading. This project is currently in the development phase and is not open for external contributions.

## Features:
Automated Stock Selection: Uses a set of predefined criteria on Finviz to filter stocks and selects the best candidates based on recent financial news analysis.

## Sentiment Analysis:
Incorporates FinBERT for analyzing financial news sentiment to make informed trading decisions.

##Progressive Web App: 
Ensures accessibility across different devices, offering a seamless user experience.

## Firebase Integration: 
Utilizes Firebase for real-time database management and other backend functionalities.

## Technologies Used:
Python: Primary programming language for backend development.

Selenium: Automates browser interactions for stock data extraction from Finviz.

FinBERT: Analyzes financial news articles for sentiment analysis.

Firebase: Manages database, authentication, and hosting.

PWA Technologies: Service workers and modern web capabilities for a native-like experience on mobile devices.

## Taurus Trading Refined Plan

1. Finviz Screener Execution:
    * Time: Start at 9:15 AM.
    * Task: Execute the Finviz screener to identify tickers that meet your filtering criteria.
    * Output: Save the tickers and their information into a temp.json file.
2. Initiate Pool Process for Spider Crawling:
    * Trigger: As soon as the temp.json file is updated.
    * Process: Use a process pool to handle 5 tickers at a time.
    * Task: Crawl Finviz, Yahoo Finance, and TradingView to gather relevant news articles for each ticker.
    * Output: Append a new section in the temp.json file for each ticker with the following details:
        * Time
        * Title
        * Publisher
        * URL of each recent news article (within the last 24 hours)
    * Note: If no relevant articles are found for a ticker, add “No relevant articles found”.
3. NLP Relevance Check and Sentiment Analysis:
    * Trigger: After updating the temp.json file with news articles.
    * Task:
        * Use spaCy to determine the relevance of each article based on its title.
        * Update the JSON file with “Relevancy Check” and “Relevancy Score” for each article.
            * If relevant, mark as “Relevant” and include the score.
            * If not relevant, mark as “Not Relevant” and leave the score blank.
        * For relevant articles, use a text scraping functionality to extract the full text.
        * Perform sentiment analysis using FinBERT on the extracted text.
    * Output: Update the JSON file with sentiment scores for relevant articles.
4. Machine Learning for Trade Decision:
    * Task: Use machine learning algorithms to rank the tickers based on their relevance and sentiment scores.
    * Output: Identify the ticker with the highest probability of success for trading that day.
5. Execute Trades:
    * Task: Once the most probable ticker is identified, use the machine learning algorithm to generate buy and sell signals.
    * Execution: Use the Alpaca Trading API to execute the trades.
6. End-of-Day Analysis:
    * Time: At the end of the trading day.
    * Task: Re-run the Finviz scraper to check which stocks performed the best.
    * Additional Data: Collect more data for training and improving the machine learning model.
    * Add all data to firebase for data storage