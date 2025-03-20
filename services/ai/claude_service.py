#!/usr/bin/env python3
"""
Enterprise-grade Claude API Service
Provides a secure, monitored, and compliant interface to Claude's AI capabilities.
"""

import os
import time
import logging
import asyncio
import re
import hashlib
from typing import Dict, Optional, List
from datetime import datetime

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram, Gauge
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from cryptography.fernet import Fernet

# Configure logging with sensitive data masking
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            record.msg = self._mask_sensitive_data(record.msg)
        return True

    def _mask_sensitive_data(self, msg):
        patterns = [
            (r'api[-_]key["\']?\s*[:=]\s*["\']?[\w\-]+["\']?', 'api_key=***'),
            (r'bearer\s+[\w\-]+', 'bearer ***'),
            (r'password["\']?\s*[:=]\s*["\']?[\w\-]+["\']?', 'password=***'),
            (r'secret["\']?\s*[:=]\s*["\']?[\w\-]+["\']?', 'secret=***'),
        ]
        result = str(msg)
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

# Initialize tracing
tracer = trace.get_tracer(__name__)

# Prometheus metrics
REQUESTS_TOTAL = Counter(
    'claude_api_requests_total',
    'Total number of requests to Claude API',
    ['method', 'status']
)
RESPONSE_TIME = Histogram(
    'claude_api_response_seconds',
    'Response latency in seconds',
    ['method']
)
RATE_LIMIT_REMAINING = Gauge(
    'claude_api_rate_limit_remaining',
    'Number of requests remaining in the current time window'
)
SECURITY_VIOLATIONS = Counter(
    'claude_api_security_violations_total',
    'Total number of security violations',
    ['type']
)

class ClaudeService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude service with enterprise features."""
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("Claude API key must be provided")
        
        # Initialize encryption for sensitive data
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            encryption_key = Fernet.generate_key()
            logger.warning("No encryption key provided, generated new one")
        self.cipher_suite = Fernet(encryption_key)
        
        self.client = anthropic.Client(api_key=self.api_key)
        self.request_history: List[Dict] = []
        self.max_retries = 3
        self.rate_limit_per_minute = 50
        
        # Security settings
        self.max_prompt_length = 4000
        self.blocked_patterns = [
            r'(?i)(password|secret|key|token)[\s]*[=:][\s]*\w+',  # Credentials
            r'\b\d{16}\b',  # Credit card numbers
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'(?i)(select|insert|update|delete|drop|union).*from',  # SQL injection
            r'<script.*?>.*?</script>',  # XSS
        ]
        self.content_policy = {
            'allowed_topics': ['business', 'technology', 'science'],
            'blocked_topics': ['adult', 'violence', 'hate_speech'],
        }

    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage."""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def _decrypt_sensitive_data(self, data: str) -> str:
        """Decrypt sensitive data for processing."""
        return self.cipher_suite.decrypt(data.encode()).decode()

    def _validate_prompt(self, prompt: str) -> bool:
        """Validate prompt against security rules."""
        if len(prompt) > self.max_prompt_length:
            SECURITY_VIOLATIONS.labels(type='length_exceeded').inc()
            raise ValueError(f"Prompt exceeds maximum length of {self.max_prompt_length}")

        for pattern in self.blocked_patterns:
            if re.search(pattern, prompt):
                SECURITY_VIOLATIONS.labels(type='blocked_pattern').inc()
                raise ValueError("Prompt contains prohibited patterns")

        return True

    def _check_content_policy(self, text: str) -> bool:
        """Check if content complies with policy."""
        # Add your content policy checking logic here
        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict] = None
    ) -> Dict:
        """Generate a response from Claude with enterprise monitoring and safety features."""
        with tracer.start_as_current_span("claude_generate_response") as span:
            start_time = time.time()
            request_id = context.get('request_id') if context else None
            span.set_attribute("request_id", request_id)
            
            try:
                # Security validations
                self._validate_prompt(prompt)
                if not self._check_content_policy(prompt):
                    raise ValueError("Content policy violation")

                # Check rate limiting
                if not self._check_rate_limit():
                    raise Exception("Rate limit exceeded")

                # Log request for audit (with sensitive data encryption)
                self._log_request(self._encrypt_sensitive_data(prompt), context)

                # Make API call with safety measures
                response = await self._make_safe_api_call(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Validate response content
                if not self._check_content_policy(response):
                    raise ValueError("Response content policy violation")

                # Record metrics
                duration = time.time() - start_time
                RESPONSE_TIME.labels(method='generate').observe(duration)
                REQUESTS_TOTAL.labels(method='generate', status='success').inc()

                # Update rate limit tracking
                self._update_rate_limit_metrics()

                # Calculate request hash for integrity checking
                request_hash = hashlib.sha256(
                    f"{prompt}{request_id}{start_time}".encode()
                ).hexdigest()

                return {
                    'status': 'success',
                    'request_id': request_id,
                    'response': response,
                    'metadata': {
                        'duration': duration,
                        'timestamp': datetime.utcnow().isoformat(),
                        'model': 'claude-3-opus-20240229',
                        'request_hash': request_hash,
                        'security_level': 'high',
                        'content_filtered': True
                    }
                }

            except Exception as e:
                REQUESTS_TOTAL.labels(method='generate', status='error').inc()
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                logger.error(f"Error generating response: {str(e)}", exc_info=True)
                raise

    async def _make_safe_api_call(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Make API call with safety checks and content filtering."""
        # Add safety prefixes and constraints
        safe_prompt = self._sanitize_prompt(prompt)
        
        # Add security context to the prompt
        safe_prompt = f"""Please ensure your response:
1. Contains no sensitive information
2. Follows security best practices
3. Is appropriate for business context
4. Does not include harmful content

{safe_prompt}"""

        response = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": safe_prompt}]
        )
        
        # Validate and sanitize response
        safe_response = self._sanitize_response(response.content[0].text)
        
        return safe_response

    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize and validate input prompt."""
        # Remove potential command injection patterns
        prompt = re.sub(r'[;&|`$]', '', prompt)
        
        # Remove potential HTML/JavaScript
        prompt = re.sub(r'<[^>]*>', '', prompt)
        
        # Remove excessive whitespace
        prompt = ' '.join(prompt.split())
        
        return prompt.strip()

    def _sanitize_response(self, response: str) -> str:
        """Sanitize and validate Claude's response."""
        # Remove potential sensitive patterns
        for pattern in self.blocked_patterns:
            response = re.sub(pattern, '[REDACTED]', response)
            
        # Validate response length
        if len(response) > self.max_prompt_length:
            response = response[:self.max_prompt_length] + '...'
            
        return response.strip()

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_minute = int(time.time() / 60)
        recent_requests = [
            req for req in self.request_history 
            if req['timestamp'] >= current_minute * 60
        ]
        
        remaining = self.rate_limit_per_minute - len(recent_requests)
        RATE_LIMIT_REMAINING.set(remaining)
        
        return len(recent_requests) < self.rate_limit_per_minute

    def _log_request(self, prompt: str, context: Optional[Dict]) -> None:
        """Log request for audit and rate limiting."""
        self.request_history.append({
            'timestamp': time.time(),
            'prompt': prompt,
            'context': context
        })
        
        # Cleanup old history
        current_minute = int(time.time() / 60)
        self.request_history = [
            req for req in self.request_history 
            if req['timestamp'] >= (current_minute - 5) * 60
        ]

    def _update_rate_limit_metrics(self) -> None:
        """Update Prometheus metrics for rate limiting."""
        current_minute = int(time.time() / 60)
        recent_requests = len([
            req for req in self.request_history 
            if req['timestamp'] >= current_minute * 60
        ])
        remaining = self.rate_limit_per_minute - recent_requests
        RATE_LIMIT_REMAINING.set(remaining)

# Example usage
async def main():
    service = ClaudeService()
    response = await service.generate_response(
        prompt="What is the capital of France?",
        context={"request_id": "test-123"}
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main()) 