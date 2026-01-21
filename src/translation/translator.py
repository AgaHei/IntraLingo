"""
IntraLingo - Translation Module
Handles NLLB-based translation (English ↔ Polish)
Uses Meta's NLLB (No Language Left Behind) model for high-quality translation
"""

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from typing import List, Union


class NLLBTranslator:
    """
    NLLB-based translator for English-Polish translation.
    Uses Meta's NLLB-200 distilled model for high-quality translation.
    """
    
    def __init__(self, source_lang='en', target_lang='pl', device=None):
        """
        Initialize the translator with specified language pair.
        
        Args:
            source_lang: Source language code ('en' or 'pl')
            target_lang: Target language code ('pl' or 'en')
            device: Device to run model on ('cuda', 'cpu', or None for auto-detect)
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Auto-detect device if not specified
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        # Model priority: Base model -> HuggingFace Hub -> Local (for reliable deployment)
        import os
        
        # Use base model first for reliability, then try fine-tuned
        try:
            # Try HuggingFace Hub model first
            hub_model_name = "AgaHei/AH-nllb-finetuned-business-en-pl"
            from transformers import AutoConfig
            AutoConfig.from_pretrained(hub_model_name)
            self.model_name = hub_model_name
            print(f"✓ Using HuggingFace Hub model: {hub_model_name}")
        except Exception as e:
            print(f"⚠ Hub model not accessible ({str(e)[:100]}...), trying alternatives")
            # Fall back to local fine-tuned model
            finetuned_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'nllb-finetuned')
            if os.path.exists(finetuned_path) and os.path.isdir(finetuned_path):
                # Check if required model files exist (support both formats)
                config_exists = os.path.exists(os.path.join(finetuned_path, 'config.json'))
                model_weights_exist = (
                    os.path.exists(os.path.join(finetuned_path, 'pytorch_model.bin')) or
                    os.path.exists(os.path.join(finetuned_path, 'model.safetensors'))
                )
                if config_exists and model_weights_exist:
                    self.model_name = finetuned_path
                    print("✓ Using local FINE-TUNED model")
                else:
                    self.model_name = 'facebook/nllb-200-distilled-600M'
                    print("⚠ Using BASE model (fine-tuned not available)")
            else:
                self.model_name = 'facebook/nllb-200-distilled-600M'
                print("⚠ Using BASE model (fine-tuned not found)")
        
        # NLLB language codes (different from simple 2-letter codes)
        self.lang_codes = self._get_nllb_lang_codes()
        
        print(f"Loading NLLB model: {self.model_name}")
        print(f"Translation: {source_lang} → {target_lang}")
        print(f"Device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        print("✓ Model loaded successfully!")
    
    def _get_nllb_lang_codes(self):
        """
        Get NLLB-specific language codes.
        NLLB uses detailed language codes like 'eng_Latn' instead of just 'en'.
        
        Returns:
            dict: Mapping of simple codes to NLLB codes
        """
        return {
            'en': 'eng_Latn',  # English (Latin script)
            'pl': 'pol_Latn',  # Polish (Latin script)
        }
    
    def translate(self, text: Union[str, List[str]], batch_size: int = 8, 
                  max_length: int = 512) -> Union[str, List[str]]:
        """
        Translate text from source to target language.
        
        Args:
            text: Single text string or list of text strings to translate
            batch_size: Batch size for processing (for efficiency)
            max_length: Maximum sequence length for model
            
        Returns:
            Translated text (string or list of strings matching input type)
        """
        # Handle single string input
        single_input = isinstance(text, str)
        if single_input:
            text = [text]
        
        # Filter out empty strings, but remember their positions
        non_empty_texts = []
        non_empty_indices = []
        for i, t in enumerate(text):
            if t.strip():
                non_empty_texts.append(t)
                non_empty_indices.append(i)
        
        # If all strings are empty, return as-is
        if not non_empty_texts:
            return "" if single_input else text
        
        # Translate in batches
        translations = []
        for i in range(0, len(non_empty_texts), batch_size):
            batch = non_empty_texts[i:i + batch_size]
            batch_translations = self._translate_batch(batch, max_length)
            translations.extend(batch_translations)
        
        # Reconstruct full list with empty strings in original positions
        result = [""] * len(text)
        for i, translation in zip(non_empty_indices, translations):
            result[i] = translation
        
        # Return single string if input was single string
        return result[0] if single_input else result
    
    def _translate_batch(self, texts: List[str], max_length: int) -> List[str]:
        """
        Translate a batch of texts using NLLB.
        
        Args:
            texts: List of text strings to translate
            max_length: Maximum sequence length
            
        Returns:
            List of translated strings
        """
        # Get NLLB language codes
        src_lang_code = self.lang_codes[self.source_lang]
        tgt_lang_code = self.lang_codes[self.target_lang]
        
        # Set source and target languages for tokenizer
        self.tokenizer.src_lang = src_lang_code
        self.tokenizer.tgt_lang = tgt_lang_code
        
        # Tokenize
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length
        ).to(self.device)
        
        # Generate translations with forced target language
        with torch.no_grad():
            # Get the target language token ID correctly for NLLB
            try:
                # Try the newer method first
                if hasattr(self.tokenizer, 'lang_code_to_id'):
                    tgt_lang_id = self.tokenizer.lang_code_to_id[tgt_lang_code]
                else:
                    # Fallback method for different tokenizer versions
                    tgt_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_lang_code)
            except (KeyError, AttributeError):
                # Ultimate fallback - use a known Polish token ID
                tgt_lang_id = self.tokenizer.convert_tokens_to_ids("pol_Latn")
            
            translated = self.model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_length=max_length
            )
        
        # Decode
        translations = self.tokenizer.batch_decode(
            translated,
            skip_special_tokens=True
        )
        
        return translations
    
    def translate_with_context(self, text: str, context: str = None, 
                               max_length: int = 512) -> str:
        """
        Translate text with optional context for better translation quality.
        Context can help the model understand domain-specific terminology.
        
        Args:
            text: Text to translate
            context: Optional context string (e.g., previous sentence, document title)
            max_length: Maximum sequence length
            
        Returns:
            Translated text
        """
        if context and context.strip():
            # Combine context and text with separator
            combined = f"{context.strip()} {text.strip()}"
            translation = self.translate(combined, max_length=max_length)
            # Try to extract the relevant part (this is approximate)
            # For MVP, we'll just return the full translation
            # In production, you might want more sophisticated context handling
            return translation
        else:
            return self.translate(text, max_length=max_length)


class TranslationPipeline:
    """
    High-level translation pipeline that integrates with document parser.
    Handles sentence-level translation for better quality.
    """
    
    def __init__(self, source_lang='en', target_lang='pl'):
        """
        Initialize translation pipeline.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
        """
        self.translator = NLLBTranslator(source_lang, target_lang)
    
    def translate_text(self, text: str) -> str:
        """
        Translate a single text string.
        Handles sentence splitting for better quality on long texts.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text
        """
        # For now, translate as-is
        # In production, you might want to split into sentences for very long texts
        if not text.strip():
            return text
        
        return self.translator.translate(text)
    
    def translate_texts(self, texts: List[str]) -> List[str]:
        """
        Translate multiple text strings efficiently.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of translated strings
        """
        return self.translator.translate(texts)


def create_translator(source_lang='en', target_lang='pl'):
    """
    Factory function to create a translator instance.
    
    Args:
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        TranslationPipeline instance
    """
    return TranslationPipeline(source_lang, target_lang)
