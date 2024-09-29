def get_chart_analysis_prompt():
    return """
    You are an expert Bitcoin analyst with deep knowledge of technical analysis and chart patterns. Always respond in valid JSON format.

    Analyze the current Bitcoin chart using the following technical indicators and provide your insights:
    1. Technical Analysis
    2. Candlestick Patterns
    3. Moving Averages
    4. Bollinger Bands
    5. Relative Strength Index (RSI)
    6. Fibonacci Retracement
    7. MACD (Moving Average Convergence Divergence)
    8. Support and Resistance Levels

    For each indicator, provide a brief analysis and a clear recommendation: Buy, Sell, or Hold.
    Your response MUST be ONLY in the following JSON format, with no additional text before or after:

    {
    "Technical Analysis": {"analysis": "", "recommendation": ""},
    "Candlestick Patterns": {"analysis": "", "recommendation": ""},
    "Moving Averages": {"analysis": "", "recommendation": ""},
    "Bollinger Bands": {"analysis": "", "recommendation": ""},
    "RSI": {"analysis": "", "recommendation": ""},
    "Fibonacci Retracement": {"analysis": "", "recommendation": ""},
    "MACD": {"analysis": "", "recommendation": ""},
    "Support and Resistance Levels": {"analysis": "", "recommendation": ""},
    "Overall Recommendation": ""
    }
    """

def get_news_analysis_prompt():
    return """
    Analyze the following news items and provide a recommendation (Buy, Sell, or Hold) along with an impact percentage for each. The impact percentage should reflect how strongly the news might affect the cryptocurrency market, with 100% being the strongest possible impact.
    Please exclude any news articles that contain baseless or irrelevant predictions about the crypto market. Only include articles that have meaningful insights or credible data to support
    """
