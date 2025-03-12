import re
import unicodedata
from transformers import AutoTokenizer

class TextProcessor:
    @staticmethod
    def clean_text(text):
        text = unicodedata.normalize("NFKD", text)  # Unicode Normalisation
        text = re.sub(r'\s+', ' ', text)  # Delete multiple spaces
        text = re.sub(r'[^a-zA-Z0-9.,;!?()\s]', '', text)  # Remove special characters
        return text.strip()

    @staticmethod
    def tokenize_text(text):
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        # Tokenisation du texte
        tokens = tokenizer.tokenize(text)
        return tokens