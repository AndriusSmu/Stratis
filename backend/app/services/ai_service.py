"""
AI service for integration with LLM providers.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..config import config
from ..exceptions import AIError

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered features."""
    
    def __init__(self):
        self.url = config.ai.url
        self.model = config.ai.model
        self.timeout = config.ai.timeout
        self.enabled = config.ai.enabled
    
    def _call_ollama(self, prompt: str) -> str:
        if not self.enabled:
            raise AIError("AI features are disabled")
        
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }).encode("utf-8")
        
        try:
            req = Request(
                self.url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("response", "").strip()
                
        except URLError as e:
            logger.error(f"Ollama connection error: {e}")
            raise AIError(f"Cannot connect to Ollama: {e.reason}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ollama: {e}")
            raise AIError("Invalid response from AI service")
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            raise AIError(f"AI service error: {str(e)}")
    
    def _parse_json_response(self, raw: str, default: Dict[str, Any]) -> Dict[str, Any]:
        try:
            clean = raw.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean = "\n".join(lines)
            return json.loads(clean.strip())
        except json.JSONDecodeError:
            return default
    
    def generate_brief(
        self,
        name: str,
        target_audience: Optional[str] = None,
        budget: Optional[float] = None,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        budget_info = f" with a budget of {budget} {currency}" if budget else ""
        audience_info = f" targeting {target_audience}" if target_audience else ""
        
        prompt = f"""You are a marketing strategist. Generate a brief for a campaign called "{name}"{audience_info}{budget_info}.

Respond ONLY with a JSON object in this exact format, no extra text:
{{
  "description": "2-3 sentence campaign description",
  "tags": ["tag1", "tag2", "tag3"],
  "notes": "1-2 sentences on key goals or success metrics"
}}"""
        
        raw_response = self._call_ollama(prompt)
        result = self._parse_json_response(raw_response, {
            "description": raw_response,
            "tags": [],
            "notes": ""
        })
        
        return result
    
    def generate_insights(self, campaigns: List[Dict[str, Any]]) -> str:
        if not campaigns:
            return "No campaigns to analyze."

        summary_lines = []
        for c in campaigns[:20]:
            line = (
                f"- \"{c.get('name', 'Unnamed')}\" | Status: {c.get('status', 'Unknown')} | "
                f"Budget: {c.get('budget', 0)} {c.get('currency', 'USD')} | "
                f"Spent: {c.get('spent', 0)} | "
                f"Progress: {c.get('progress_pct', 0)}% | "
                f"Expired: {c.get('is_expired', False)}"
            )
            summary_lines.append(line)

        campaigns_text = "\n".join(summary_lines)

        prompt = f"""You are a marketing analyst. Here is a summary of marketing campaigns:

{campaigns_text}

Write a short, direct health report (3-5 sentences). Mention:
- Any campaigns that are over budget or nearly spent
- Any expired campaigns still marked active
- Overall portfolio health
- One concrete recommendation

Be direct and specific. No bullet points, just plain sentences."""

        raw_response = self._call_ollama(prompt)
        return raw_response