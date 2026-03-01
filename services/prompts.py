BEDROCK_EXPLANATION_PROMPT = """You are an AI assistant helping Amazon FBA sellers understand profit risks.

SKU: {sku_name}
Current Margin: {margin}%
Risk Score: {risk_score}/100

Top Risk Factors:
{factors_text}

Generate a clear, concise explanation (2-3 sentences) of why this SKU is at risk. 
Focus on actionable insights. Use specific numbers from the data points."""
