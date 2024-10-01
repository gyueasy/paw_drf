
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

def get_retrospective_analysis_prompt_template():
    return """Current Price: {current_price}
Previous Price: {previous_price}
Price Change: {price_change}
Latest Recommendation: {recommendation} ({recommendation_value})
Prediction Correct: {is_correct}
Current Accuracy: {current_accuracy}
Average Accuracy (7d): {avg_accuracy}

Previous Analysis:
Recommendation: {main_report.recommendation}
Confidence Level: {main_report.confidence_level}
Reasoning: {main_report.reasoning}
Overall Analysis: {main_report.overall_analysis}
Market Analysis: {main_report.market_analysis}
Chart Analysis: {main_report.chart_analysis}

Compare your previous analysis and recommendation with the actual price change. Based on this comparison, please adjust the following 12 weights:

{{
    "analysis": "Your analysis of the comparison between prediction and actual result",
    "weight_adjustments": {{
        "overall_weight": 0.0,
        "fear_greed_index_weight": 0.0,
        "news_weight": 0.0,
        "chart_overall_weight": 0.0,
        "chart_technical_weight": 0.0,
        "chart_candlestick_weight": 0.0,
        "chart_moving_average_weight": 0.0,
        "chart_bollinger_bands_weight": 0.0,
        "chart_rsi_weight": 0.0,
        "chart_fibonacci_weight": 0.0,
        "chart_macd_weight": 0.0,
        "chart_support_resistance_weight": 0.0
    }},
    "reasoning": "Provide a single reason for all weight adjustments",
    "overall_retrospective": "Overall thoughts on the performance and suggestions for improvement"
}}

The sum of all weights must always equal 100%. Please provide your adjustments directly in the format above.
"""

def basic_retrospective_analysis_prompt():
    return """{
        "summary_line": "Current Price: {current_price}",
        "analysis": "Your analysis of the comparison between prediction and actual result",
        "weight_adjustments": {
            "overall_weight": 0.0,
            "fear_greed_index_weight": 0.0,
            "news_weight": 0.0,
            "chart_overall_weight": 0.0,
            "chart_technical_weight": 0.0,
            "chart_candlestick_weight": 0.0,
            "chart_moving_average_weight": 0.0,
            "chart_bollinger_bands_weight": 0.0,
            "chart_rsi_weight": 0.0,
            "chart_fibonacci_weight": 0.0,
            "chart_macd_weight": 0.0,
            "chart_support_resistance_weight": 0.0
        },
        "reasoning": "Provide a single reason for all weight adjustments",
        "overall_retrospective": "Overall thoughts on the performance and suggestions for improvement"
    }
    The sum of all weights must always equal 100%. Please provide your adjustments directly in the format above.
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
        "title": "A catchy and informative title for the report, short and to the point",
        "overall_analysis": "analysis",
        "market_analysis": "analysis",
        "chart_analysis": "analysis",
        "recommendation": "Buy, Hold, or Sell, A number between 0 and 100 indicating your confidence in the recommendation",
        "confidence_level": "A brief explanation of your recommendation and confidence level",
        "reasoning": "Your reasoning for the recommendation"
    }
    If there are any numbers that should be referenced in the chart, please make sure to include them in the report.
    """