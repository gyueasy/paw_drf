def get_chart_analysis_prompt():
    return """
    You are an expert Bitcoin analyst with deep knowledge of technical analysis and chart patterns. Always respond in valid JSON format.
    If there are any numbers that should be referenced in the chart, please make sure to include them in the report.
    
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

def get_report_weights_prompt():
    return """
    나는 너에게 너가 판단한 가중치, 최근 너의 분석값에 대한 적중률을 제공할 것이다.
    참고할 수 있도록 나는 너에게 이전 판단 근거를 추가로 제공할 것이다.
    이를 근거로 너는 가중치를 조정해야 한다.
    """

def get_main_report_prompt():
    return """
    I will provide you with three components: market_analysis, chart_analysis, and their respective weights.
    1. market_analysis: This includes an analysis of news and the Fear and Greed Index.
    2. chart_analysis: This provides an analysis of the price chart.
    3. weights: These are the weightings you've determined, reflecting the results of your previous judgments.
    
    Your task is to analyze these three components and provide a result based on the weights.
    Additionally, create a catchy and informative title for this report that reflects the current market situation and your analysis.
    
    Please provide your analysis, recommendation, and title in the following format:
    
    {
        "title": "A catchy and informative title for the report",
        "overall_analysis": "analysis",
        "market_analysis": "analysis",
        "chart_analysis": "analysis",
        "recommendation": "Buy, Hold, or Sell, A number between 0 and 100 indicating your confidence in the recommendation",
        "confidence_level": "A brief explanation of your recommendation and confidence level",
        "reasoning": "Your reasoning for the recommendation"
    }
    Please respond with the content in Korean only.
    If there are any numbers that should be referenced in the chart, please make sure to include them in the report.
    """