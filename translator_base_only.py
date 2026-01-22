"""
Translator using ONLY base model (no fine-tuned) for testing
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoConfig
import torch


class NLLBTranslator:
    def __init__(self, source_lang, target_lang):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🔧 Initializing NLLB translator: {source_lang} -> {target_lang}")
        print(f"🖥️  Using device: {self.device}")
        
        # Language codes for NLLB
        self.lang_codes = {
            'en': 'eng_Latn',
            'pl': 'pol_Latn'
        }
        
        self.src_lang_code = self.lang_codes.get(source_lang, 'eng_Latn')
        self.tgt_lang_code = self.lang_codes.get(target_lang, 'pol_Latn')
        
        print(f"🌍 Language codes: {self.src_lang_code} -> {self.tgt_lang_code}")
        
        # ONLY USE BASE MODEL
        model_name = "facebook/nllb-200-distilled-600M"
        
        print(f"📥 Loading base model: {model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.model.to(self.device)
            print("✅ Base model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading base model: {e}")
            raise
    
    def translate_text(self, text):
        """Translate a single text string."""
        if not text or not text.strip():
            return ""
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=1024
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[self.tgt_lang_code],
                    max_length=1024,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode
            translated_text = self.tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )[0]
            
            return translated_text
        
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return text  # Return original text on error
    
    def translate_document(self, parsed_document):
        """Translate a parsed document structure."""
        def translate_element(element):
            if isinstance(element, dict):
                translated = {}
                for key, value in element.items():
                    if key == 'text' and isinstance(value, str):
                        translated[key] = self.translate_text(value)
                    elif isinstance(value, (dict, list)):
                        translated[key] = translate_element(value)
                    else:
                        translated[key] = value
                return translated
            elif isinstance(element, list):
                return [translate_element(item) for item in element]
            else:
                return element
        
        return translate_element(parsed_document)


def create_translator(source_lang, target_lang):
    """Create and return a translator instance."""
    return NLLBTranslator(source_lang, target_lang)