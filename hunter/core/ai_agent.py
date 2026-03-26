"""
LLM Integration for Hunter AI Agent
Standalone LLM client with reasoning capabilities
"""
import os
import json
from typing import Dict, List, Optional, Generator
from dataclasses import dataclass
import requests


@dataclass
class LLMMessage:
    role: str  # system, user, assistant
    content: str


class LLMClient:
    """Standalone LLM client for Hunter AI Agent"""
    
    def __init__(
        self,
        api_key: str = None,
        provider: str = "openrouter",  # openrouter, kimi, openai
        model: str = None
    ):
        self.api_key = api_key or os.getenv("HUNTER_LLM_API_KEY")
        self.provider = provider.lower()
        
        # Default models per provider
        default_models = {
            "openrouter": "anthropic/claude-3.5-sonnet",
            "kimi": "kimi-k2.5",
            "openai": "gpt-4o"
        }
        self.model = model or default_models.get(self.provider, "gpt-4o")
        
        # API endpoints
        self.endpoints = {
            "openrouter": "https://openrouter.ai/api/v1/chat/completions",
            "kimi": "https://api.moonshot.cn/v1/chat/completions",
            "openai": "https://api.openai.com/v1/chat/completions"
        }
    
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """Send chat completion request"""
        
        if not self.api_key:
            raise ValueError("API key not configured. Set HUNTER_LLM_API_KEY env var.")
        
        endpoint = self.endpoints.get(self.provider)
        if not endpoint:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Provider-specific headers
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/nathabot/hunter"
            headers["X-Title"] = "Hunter AI Agent"
        
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract content based on provider response format
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected response format: {data}")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LLM API error: {e}")
    
    def analyze_strategy(
        self,
        strategy_data: Dict,
        market_context: Dict = None
    ) -> Dict:
        """Analyze a strategy using LLM reasoning"""
        
        system_prompt = """You are Hunter, an elite Web3 strategy analyst with a proven track record of identifying profitable opportunities.

Your personality:
- Sharp, analytical, and data-driven
- Skeptical of hype, focused on fundamentals
- Always consider risks before rewards
- Speak with confidence backed by logic
- Use trading slang naturally ("diamond hands", "ape in", "rug pull", etc.)

When analyzing strategies:
1. Evaluate the opportunity objectively
2. Identify hidden risks others might miss
3. Consider market context and timing
4. Provide clear recommendation with reasoning
5. Suggest position sizing based on risk

Respond in JSON format with these fields:
{
    "analysis": "detailed analysis of the opportunity",
    "confidence_score": 0.0-1.0,
    "risk_assessment": "low/medium/high/critical",
    "hidden_risks": ["risk 1", "risk 2"],
    "market_timing": "good/neutral/bad",
    "recommendation": "strong_buy/buy/hold/avoid",
    "position_size": "conservative/moderate/aggressive",
    "reasoning": "chain of thought explanation"
}"""

        user_prompt = f"""Analyze this Web3 strategy opportunity:

Strategy: {strategy_data.get('name', 'Unknown')}
Type: {strategy_data.get('type', 'Unknown')}
Confidence: {strategy_data.get('confidence', 0):.0%}
Risk Level: {strategy_data.get('risk_level', 'Unknown')}
Expected APR: {strategy_data.get('profit_potential', {}).get('apr', 'Unknown')}

Market Context: {json.dumps(market_context or {}, indent=2)}

Provide your analysis in the specified JSON format."""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]
        
        response = self.chat(messages, temperature=0.3)
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "No JSON found", "raw_response": response}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw_response": response}
    
    def chat_with_personality(
        self,
        user_message: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """Chat with Hunter's personality"""
        
        # Load personality from SOUL.md content
        personality = """You are Hunter - an elite Web3 strategy hunter. You speak like a seasoned crypto trader who's seen multiple cycles.

Your traits:
- Direct and no-nonsense
- Uses crypto slang naturally (wen lambo, ngmi, diamond hands, etc.)
- Always backs claims with data
- Skeptical of new projects until proven
- Celebrates wins but learns from losses
- Risk management is your religion

When discussing strategies:
- Start with "Listen up..." or "Here's the play..."
- End bullish opportunities with "This could print 🚀"
- Warn about risks with "But watch out for..." or "Rug risk:"
- Use emojis sparingly but effectively

Never give financial advice. Always say "DYOR" and "Not financial advice" when discussing specific plays."""

        messages = [LLMMessage(role="system", content=personality)]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                messages.append(LLMMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
        
        messages.append(LLMMessage(role="user", content=user_message))
        
        return self.chat(messages, temperature=0.8)


class HunterAI:
    """Main Hunter AI Agent class"""
    
    def __init__(self, config: Dict = None):
        config = config or {}
        
        self.llm = LLMClient(
            api_key=config.get("llm_api_key"),
            provider=config.get("llm_provider", "openrouter"),
            model=config.get("llm_model")
        )
        
        self.memory = []  # Conversation memory
        self.max_memory = 20
    
    def analyze(self, strategy_data: Dict, market_context: Dict = None) -> Dict:
        """Analyze a strategy with AI reasoning"""
        return self.llm.analyze_strategy(strategy_data, market_context)
    
    def chat(self, message: str) -> str:
        """Chat with Hunter AI"""
        response = self.llm.chat_with_personality(message, self.memory)
        
        # Update memory
        self.memory.append({"role": "user", "content": message})
        self.memory.append({"role": "assistant", "content": response})
        
        # Trim memory
        if len(self.memory) > self.max_memory * 2:
            self.memory = self.memory[-self.max_memory * 2:]
        
        return response
    
    def explain_strategy(self, strategy_name: str, details: Dict) -> str:
        """Explain a strategy in Hunter's voice"""
        prompt = f"""Explain this {strategy_name} strategy to a crypto newbie:

{json.dumps(details, indent=2)}

Make it:
- Easy to understand
- Include the risks
- Use some crypto slang
- End with a balanced take (not too bullish, not too bearish)"""

        return self.chat(prompt)
    
    def get_market_opinion(self, market_data: Dict) -> str:
        """Get Hunter's market opinion"""
        prompt = f"""Give me your market take on this data:

{json.dumps(market_data, indent=2)}

Respond with:
1. Overall sentiment (bearish/neutral/bullish)
2. Key opportunities you see
3. Risks to watch
4. Any alpha/leaks

Keep it brief but insightful."""

        return self.chat(prompt)
