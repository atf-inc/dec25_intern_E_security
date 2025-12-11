# Worker Service

The Worker service is the core detection engine of ShadowGuard AI. It consumes events from Redis, applies multi-layer analysis (rule-based, semantic, behavioral), and generates risk scores using a fusion algorithm.

**Files:**
- `worker.py` - Main worker loop consuming from Redis queue
- `rules.py` - Rule-based detection using blacklist/whitelist matching
- `semantic.py` - Semantic analysis using LLM for context understanding
- `behavior.py` - Behavioral analysis for anomaly detection
- `fusion.py` - Risk score fusion combining all detection layers
