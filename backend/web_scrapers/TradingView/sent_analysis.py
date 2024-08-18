from pydantic import BaseModel
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os
from dotenv import load_dotenv
import json

load_dotenv()

class Explanation(BaseModel):
    decision: str
    reasoning: str

class TradingViewSentimentAnalysis:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.openAI_model = "gpt-4o-2024-08-06"

        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.classifier = pipeline("text-classification", model=self.finbert_model, tokenizer=self.tokenizer)

    def gpt_title_relevance(self, title, ticker):   
        completion = self.client.beta.chat.completions.parse(
            model = self.openAI_model,
            messages = [
                {"role": "system",
                 "content": 'You are a financial analyst. Given an article title and a stock ticker, decide if the title of the article is relevant to the given stock. Your response should be either "Relevant" or "Discard" based on how much impact this article could have on the ticker/stock. Additionally, explain the reasoning behind your response in a concise manner.'
                },
                {"role": "user",
                 "content": f"Article Title: '{title}', Stock Ticker: '{ticker}'"
                }
            ],
            temperature= 0.5,
            max_tokens = 150,
            response_format = Explanation,
        )
        
        title_relevance = completion.choices[0].message.parsed        
        # Manually extract 'decision' and 'reasoning' from the output
        decision = title_relevance.decision
        reasoning = title_relevance.reasoning
    
        # Return a dictionary
        return {
            "decision": decision,
            "reasoning": reasoning
        }

    def gpt_article_sentiment(self, text, ticker):
        completion = self.client.beta.chat.completions.parse(
            model = self.openAI_model,
            messages = [
                {"role": "system",
                 "content": 'You are a financial analyst. You will be given the text of an article and a stock ticker. Analyze the sentiment of the articles text with respect to the given ticker. Your descion needs to be one of the following: "Positve", "Negative", or "Neutral" based off the overall sentiment of the article. Additionally, provide a concise explanation of your reasoning.'
                },
                {"role": "user",
                 "content": f"Article Text: '{text}', Stock Ticker: '{ticker}'"
                }
            ],
            temperature= 0.5,
            max_tokens = 200,
            response_format = Explanation
        )
        
        article_sentiment = completion.choices[0].message.parsed  # Already an Explanation object
        decision = article_sentiment.decision
        reasoning = article_sentiment.reasoning

        return {
            "decision": decision,
            "reasoning": reasoning
        }

    
    def finbert_article_sentiment(self, text):
        text = text[:512]
        results = self.classifier(text)
        sentiment_label = results[0]['label'].capitalize()  # Ensuring it matches "Positive", "Neutral", "Negative"
        return {"Sentiment": sentiment_label}



    '''
    def test(self):
        text = "To gain an edge, this is what you need to know today. Strong Data. Please click here for an enlarged chart of Walmart Inc WMT. Note the following: This article is about the big picture, not an individual stock. The chart of WMT stock is being used to illustrate the point. Three news pieces of data have triggered aggressive buying in NVIDIA Corp NVDA and AI stocks. The three new pieces of data are: Walmart earnings, Jobless claims, and Retail sales. Investors are building position in NVDA stock ahead of earnings on August 28. As NVDA stock goes higher, it brings along other AI stocks. The chart shows a gap up on the release of WMT earnings this morning. The chart shows there was also a gap up after WMT earnings were reported last quarter. RSI on the chart shows that WMT is now overbought. Overbought stocks tend to pullback. Walmart earnings are important due to its sheer size and because it gives a good picture of consumer sentiment. Here are the key points from Walmart's earnings: Walmart is not seeing consumer weakness. This data is contrary to other recent pieces of data. Smart money is always analyzing both sides. In contrast, the momo crowd pays attention only to the data that supports its position and ignores the rest. Weight loss drugs are contributing to healthy sales. High income earners have shifted to shopping at Walmart. Walmart reported EPS of $0.67 vs. $0.65 consensus for Q2. Walmart is projecting EPS of $0.51 – $0.52 vs. $0.54 consensus for Q3. Walmart is raising FY25 EPS to $2.35 – $2.43 vs. $2.23 – $2.37 prior. As full disclosure, WMT is in the ZYX Buy Model Portfolio from The Arora Report. WMT is long from $19.25 post split. The U.S. economy is 70% consumer based. For this reason, prudent investors pay attention to retail sales. The just released data shows that after a brief hiatus, the consumer is back on a spending spree. Here are the details: Retail sales came at 1.0% vs. 0.3% consensus and whisper numbers of 0.2%. Retail sales ex-auto came at 0.4% vs. 0.2% consensus. The foregoing data flies in the face of other recent data. The other recent data has been showing weakness. Weekly initial jobless claims came at 227K vs. 232K consensus. Initial jobless claims is a leading indicator and carries heavy weight in our adaptive ZYX Asset Allocation Model with inputs in ten categories. In plain English, adaptiveness means that the model changes itself with market conditions. Please click here to see how this is achieved. One of the reasons behind The Arora Report's unrivaled performance in both bull and bear markets is the adaptiveness of the model. Most models on Wall Street are static. They work for a while and then stop working when market conditions change. On August 12, we shared with you The Arora Report call. In The Arora Report analysis, the market reaction to the news has changed. In November 2022, Powell triggered the stock market reaction function of bad news is good news and good news is bad news. This reaction function persisted until mid-July 2024. Starting in mid-July 2024, the market reaction function has changed – good news is good news and bad news is bad news. As a member of The Arora Report, you knew in advance that this change was coming. We have repeatedly written that the prior market reaction function was highly flawed as it counted on bad news leading to rate cuts but did not consider that bad news also negatively impacts earnings. Now, the stock market is understanding the reality and has stopped ignoring the fact that bad news leads to bad earnings. The early market reaction to the good news from Walmart, retail sales, and jobless claims is very positive. This shows that so far The Arora Report call on market reaction function is spot on. What is the connection between aggressive buying in NVDA stock and the three new pieces of data above? The connection is the stronger economy combined with upcoming Fed cuts will drive PEs of AI stocks higher. The stock market always has crosscurrents. The data today is producing a fly in the ointment. The fly is that bonds are falling. This goes against the prevailing wisdom that bonds should be rising. Falling bonds is a negative for the stock market as it negatively impacts PE ratios. Magnificent Seven Money Flows. In the early trade, money flows are positive in Apple Inc AAPL, Amazon.com, Inc. AMZN, Alphabet Inc Class C GOOG, Meta Platforms Inc META, Microsoft Corp MSFT, NVDA, and Tesla Inc TSLA. In the early trade, money flows are positive in SPDR S&P 500 ETF Trust SPY and Invesco QQQ Trust Series 1 QQQ. Momo Crowd And Smart Money In Stocks. Investors can gain an edge by knowing money flows in SPY and QQQ. Investors can get a bigger edge by knowing when smart money is buying stocks, gold, and oil. The most popular ETF for gold is SPDR Gold Trust GLD. The most popular ETF for silver is iShares Silver Trust SLV. The most popular ETF for oil is United States Oil ETF USO. Bitcoin. Bitcoin is range bound. Protection Band And What To Do Now. It is important for investors to look ahead and not in the rearview mirror. Consider continuing to hold good, very long term, existing positions. Based on individual risk preference, consider a protection band consisting of cash or Treasury bills or short-term tactical trades as well as short to medium term hedges and short term hedges. This is a good way to protect yourself and participate in the upside at the same time. You can determine your protection bands by adding cash to hedges. The high band of the protection is appropriate for those who are older or conservative. The low band of the protection is appropriate for those who are younger or aggressive. If you do not hedge, the total cash level should be more than stated above but significantly less than cash plus hedges. A protection band of 0% would be very bullish and would indicate full investment with 0% in cash. A protection band of 100% would be very bearish and would indicate a need for aggressive protection with cash and hedges or aggressive short selling. It is worth reminding that you cannot take advantage of new upcoming opportunities if you are not holding enough cash. When adjusting hedge levels, consider adjusting partial stop quantities for stock positions (non-ETF); consider using wider stops on remaining quantities and also allowing more room for high beta stocks. High beta stocks are the ones that move more than the market. Traditional 60/40 Portfolio. Probability-based risk-reward adjusted for inflation does not favor long duration strategic bond allocation at this time. Those who want to stick to traditional 60% allocation to stocks and 40% to bonds may consider focusing on only high quality bonds and bonds of five-year duration or less. Those willing to bring sophistication to their investing may consider using bond ETFs as tactical positions and not strategic positions at this time. The Arora Report is known for its accurate calls. The Arora Report correctly called the big artificial intelligence rally before anyone else, the new bull market of 2023, the bear market of 2022, new stock market highs right after the virus low in 2020, the virus drop in 2020, the DJIA rally to 30,000 when it was trading at 16,000, the start of a mega bull market in 2009, and the financial crash of 2008. Please click here to sign up for a free forever Generate Wealth Newsletter. © 2024 Benzinga.com. Benzinga does not provide investment advice. All rights reserved."
        title = "Three New Pieces Of Data Trigger Aggressive Buying In Nvidia And AI Stocks"
        ticker = "NVDA"

        gpt_title_sent = self.gpt_title_relevance(title, ticker)
        gpt_text_sent = self.gpt_article_sentiment(text, ticker)
        finbert_text_sent = self.finbert_article_sentiment(text)

        print(gpt_title_sent)
        #type(f"\n{gpt_title_sent}")
        print(gpt_text_sent)
        #type(f"\n{gpt_text_sent}")
        print(finbert_text_sent)
        #type(f"\n{finbert_text_sent}")

if __name__ == "__main__":
    analyzer = TradingViewSentimentAnalysis()
    analyzer.test() 
'''






