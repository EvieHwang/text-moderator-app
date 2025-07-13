"""
Alternative Text Moderation using HuggingFace Inference API
This provides a backup solution if Duc Haba's API is unavailable
"""

import requests
import json
import os
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class AlternativeTextModerator:
    def __init__(self, hf_token=None):
        self.hf_token = hf_token
        self.api_url = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
        self.headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        
    def analyze_text_hf_api(self, text):
        """Use HuggingFace Inference API for toxicity detection"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text},
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Convert to our expected format
                analysis = {
                    "text_analyzed": len(text),
                    "max_value": 0,
                    "max_key": "clean",
                    "is_flagged": False,
                    "categories": {},
                    "safer_value": 0.02,
                    "method": "huggingface_toxic_bert"
                }
                
                # Process results
                if isinstance(results, list) and len(results) > 0:
                    for result in results[0]:
                        label = result.get('label', '').lower()
                        score = result.get('score', 0)
                        
                        # Map labels to our categories
                        if 'toxic' in label:
                            analysis['categories']['toxic'] = score
                            if score > analysis['max_value']:
                                analysis['max_value'] = score
                                analysis['max_key'] = 'toxic'
                        elif 'non-toxic' in label or 'clean' in label:
                            analysis['categories']['clean'] = score
                
                # Determine if flagged
                analysis['is_flagged'] = analysis['max_value'] > 0.5
                
                return True, {
                    "chart_data": None,  # No chart from this API
                    "analysis": analysis
                }
                
            else:
                return False, f"API returned status {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"HuggingFace API error: {str(e)}"
    
    def analyze_text_local(self, text):
        """Use local transformers pipeline as final fallback"""
        try:
            # This will download the model on first use
            classifier = pipeline(
                "text-classification", 
                model="unitary/toxic-bert",
                device=-1  # Use CPU
            )
            
            results = classifier(text)
            
            # Convert to our format
            analysis = {
                "text_analyzed": len(text),
                "max_value": 0,
                "max_key": "clean",
                "is_flagged": False,
                "categories": {},
                "safer_value": 0.02,
                "method": "local_toxic_bert"
            }
            
            for result in results:
                label = result['label'].lower()
                score = result['score']
                
                analysis['categories'][label] = score
                if 'toxic' in label and score > analysis['max_value']:
                    analysis['max_value'] = score
                    analysis['max_key'] = label
            
            analysis['is_flagged'] = analysis['max_value'] > 0.5
            
            return True, {
                "chart_data": None,
                "analysis": analysis
            }
            
        except Exception as e:
            return False, f"Local model error: {str(e)}"
    
    def analyze_text(self, text, safer=0.02):
        """Try multiple methods to analyze text"""
        
        # Method 1: Try HuggingFace API first
        if self.hf_token:
            logger.info("🔍 Trying HuggingFace Inference API...")
            success, result = self.analyze_text_hf_api(text)
            if success:
                logger.info("✅ HuggingFace API successful")
                return success, result
            else:
                logger.warning(f"⚠️ HuggingFace API failed: {result}")
        
        # Method 2: Try local model as fallback
        logger.info("🔍 Trying local model fallback...")
        try:
            success, result = self.analyze_text_local(text)
            if success:
                logger.info("✅ Local model successful")
                return success, result
            else:
                logger.warning(f"⚠️ Local model failed: {result}")
        except ImportError:
            logger.warning("⚠️ Transformers library not available for local fallback")
        
        # Method 3: Simple rule-based fallback
        logger.info("🔍 Using simple rule-based fallback...")
        return self.analyze_text_simple(text)
    
    def analyze_text_simple(self, text):
        """Simple rule-based toxicity detection as final fallback"""
        
        # Simple toxic word list (you can expand this)
        toxic_words = [
            'hate', 'kill', 'die', 'stupid', 'idiot', 'dumb', 'moron',
            'shut up', 'go away', 'loser', 'pathetic', 'worthless'
        ]
        
        text_lower = text.lower()
        toxic_count = sum(1 for word in toxic_words if word in text_lower)
        
        # Simple scoring based on toxic word count
        max_value = min(toxic_count * 0.3, 0.9)  # Cap at 0.9
        
        analysis = {
            "text_analyzed": len(text),
            "max_value": max_value,
            "max_key": "toxic" if max_value > 0.3 else "clean",
            "is_flagged": max_value > 0.5,
            "categories": {
                "toxic": max_value,
                "clean": 1 - max_value
            },
            "safer_value": 0.02,
            "method": "simple_rule_based",
            "toxic_words_found": toxic_count
        }
        
        return True, {
            "chart_data": None,
            "analysis": analysis
        }

def test_alternative_moderator():
    """Test the alternative moderator"""
    
    # Load HF token
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    
    moderator = AlternativeTextModerator(hf_token)
    
    test_texts = [
        "Hello world, this is a nice message!",
        "This is stupid and I hate it",
        "You are an amazing person",
        "Go away, you moron!"
    ]
    
    print("🧪 Testing Alternative Text Moderator")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: '{text}'")
        success, result = moderator.analyze_text(text)
        
        if success:
            analysis = result['analysis']
            print(f"✅ Success! Method: {analysis['method']}")
            print(f"   Risk Level: {analysis['max_value']:.2f}")
            print(f"   Flagged: {analysis['is_flagged']}")
            print(f"   Categories: {analysis['categories']}")
        else:
            print(f"❌ Failed: {result}")

if __name__ == "__main__":
    test_alternative_moderator()
