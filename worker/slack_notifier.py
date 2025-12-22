import json
import os
import requests
from typing import Dict, Any

class SlackNotifier:
    def __init__(self, webhook_url: str = None):
        """
        Initialize Slack notifier with a webhook URL.
        
        Args:
            webhook_url: Slack Incoming Webhook URL. If None, looks for SLACK_WEBHOOK_URL env var.
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)
        
        if self.enabled:
            # We don't print the whole URL for security
            url_part = self.webhook_url.split('/')[-1][:10]
            print(f"✅ Slack notifications enabled (Webhook: ...{url_part})")
        else:
            print("ℹ️  Slack notifications disabled (SLACK_WEBHOOK_URL not set)")
    
    def send_alert(self, fused_result: Dict[str, Any]) -> bool:
        """
        Send a rich-formatted alert to Slack.
        
        Args:
            fused_result: Fused analysis result from FusionEngine
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            payload = self._format_message(fused_result)
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[SLACK] Alert sent for {fused_result.get('domain')}")
                return True
            else:
                print(f"[SLACK] Failed to send alert: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[SLACK] Error sending notification: {e}")
            return False
            
    def _format_message(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the alert as a Slack Block Kit message."""
        risk = result.get("risk_level", "UNKNOWN")
        score = result.get("final_risk_score", 0.0)
        domain = result.get("domain", "unknown")
        user = result.get("user_id", "unknown")
        method = result.get("method", "UNKNOWN")
        upload_mb = result.get("upload_size_mb", 0)
        category = result.get("semantic_analysis", {}).get("category_type", "unknown")
        
        # Color and Emoji mapping
        config = {
            "CRITICAL": ("#dc2626", "🚨"),
            "HIGH": ("#ea580c", "⚠️"),
            "MEDIUM": ("#eab308", "⚡"),
            "LOW": ("#3b82f6", "ℹ️"),
            "SAFE": ("#22c55e", "✅")
        }
        color, emoji = config.get(risk, ("#64748b", "📊"))
        
        # Build blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {risk} Risk: Shadow AI/IT Activation"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*User:*\n{user}"},
                    {"type": "mrkdwn", "text": f"*Domain:*\n{domain}"},
                    {"type": "mrkdwn", "text": f"*Category:*\n{category}"},
                    {"type": "mrkdwn", "text": f"*Risk Score:*\n{score:.2f}"}
                ]
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Action:*\n{method}"},
                    {"type": "mrkdwn", "text": f"*Data Exposure:*\n{upload_mb:.2f} MB"}
                ]
            }
        ]
        
        # Add explanation / factors
        explanation = result.get("semantic_analysis", {}).get("explanation", "")
        factors = []
        
        if result.get("behavior_analysis", {}).get("is_first_visit"):
            factors.append("• First-time visit to this domain")
        if method in ["POST", "PUT"] and upload_mb > 5:
            factors.append(f"• Significant data upload ({upload_mb:.2f} MB)")
            
        if explanation:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Context:* {explanation}"
                }
            })
            
        if factors:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Risk Factors:*\n" + "\n".join(factors)
                }
            })
            
        # Add recommendation
        recommendation = "Review for unintentional data exposure."
        if risk == "CRITICAL":
            recommendation = "High risk of data exfiltration. Immediate review required."
        elif risk == "HIGH":
            recommendation = "Unapproved AI/IT service detected with significant interaction."
            
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"*Recommendation:* {recommendation}"}
            ]
        })
        
        return {
            "attachments": [
                {
                    "color": color,
                    "blocks": blocks
                }
            ]
        }
