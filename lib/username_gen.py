"""Username generation utilities (2026)"""
import random
import os
from typing import Optional
from pathlib import Path


class UsernameGenerator:
    """
    Pronounceable username generator
    SOURCE: https://github.com/mrsobakin/pungen
    Credits to @mrsobakin for the original algorithm
    """
    
    CONSONANTS = "bcdfghjklmnpqrstvwxyz"
    VOWELS = "aeiou"
    
    CONS_WEIGHTED = ("tn", "rshd", "lfcm", "gypwb", "vbjxq", "z")
    VOW_WEIGHTED = ("eao", "iu")
    DOUBLE_CONS = ("he", "re", "ti", "ti", "hi", "to", "ll", "tt", "nn", "pp", "th", "nd", "st", "qu")
    DOUBLE_VOW = ("ee", "oo", "ei", "ou", "ai", "ea", "an", "er", "in", "on", "at", "es", "en", "of", "ed", "or", "as")
    
    def __init__(self, min_length: int = 10, max_length: int = 15):
        self.min_length = min_length
        self.max_length = max_length
    
    def generate(self) -> str:
        """Generate a random pronounceable username"""
        username, is_double, num_length = "", False, 0
        
        is_consonant = random.randrange(10) > 0
        length = random.randrange(self.min_length, self.max_length + 1)
        
        if random.randrange(5) == 0:
            num_length = random.randrange(3) + 1
            if length - num_length < 2:
                num_length = 0
        
        letter_length = max(1, length - num_length)
        
        for _ in range(letter_length):
            if len(username) > 0:
                if username[-1] in self.CONSONANTS:
                    is_consonant = False
                elif username[-1] in self.VOWELS:
                    is_consonant = True
            
            if not is_double:
                if random.randrange(8) == 0 and len(username) < int(letter_length) - 1:
                    is_double = True
                
                if is_consonant:
                    username += self._get_consonant(is_double)
                else:
                    username += self._get_vowel(is_double)
                
                is_consonant = not is_consonant
            else:
                is_double = False
        
        # Capitalize first letter sometimes
        if random.randrange(2) == 0:
            username = username[:1].upper() + username[1:]
        
        # Add numbers
        if num_length > 0:
            for _ in range(num_length):
                username += str(random.randrange(10))
        
        return username
    
    def _get_consonant(self, is_double: bool) -> str:
        """Get consonant with weighted probability"""
        if is_double:
            return random.choice(self.DOUBLE_CONS)
        
        i = random.randrange(100)
        if i < 40:
            weight = 0
        elif 40 <= i < 65:
            weight = 1
        elif 65 <= i < 80:
            weight = 2
        elif 80 <= i < 90:
            weight = 3
        elif 90 <= i < 97:
            weight = 4
        else:
            return self.CONS_WEIGHTED[5]
        
        return self.CONS_WEIGHTED[weight][random.randrange(len(self.CONS_WEIGHTED[weight]))]
    
    def _get_vowel(self, is_double: bool) -> str:
        """Get vowel with weighted probability"""
        if is_double:
            return random.choice(self.DOUBLE_VOW)
        
        i = random.randrange(100)
        weight = 0 if i < 70 else 1
        return self.VOW_WEIGHTED[weight][random.randrange(len(self.VOW_WEIGHTED[weight]))]


class StructuredUsernameGenerator:
    """Generate structured usernames from word lists"""
    
    def __init__(self, lib_path: Optional[str] = None):
        self.lib_path = lib_path or str(Path(__file__).parent)
        self.verbs = self._load_words("verbs.txt")
        self.nouns = self._load_words("nouns.txt")
        self.adjectives = self._load_words("adjectives.txt")
    
    def _load_words(self, filename: str) -> list:
        """Load words from file"""
        try:
            filepath = os.path.join(self.lib_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
            return words
        except FileNotFoundError:
            return []
    
    def generate(self) -> str:
        """Generate structured username (verb + noun + adjective + number)"""
        if not all([self.verbs, self.nouns, self.adjectives]):
            # Fallback to scrambled if word lists not found
            return UsernameGenerator().generate()
        
        verb = random.choice(self.verbs)
        noun = random.choice(self.nouns)
        adjective = random.choice(self.adjectives)
        number = random.randint(10, 99)
        
        return f"{verb}{noun}{adjective}{number}"


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for PyInstaller bundles"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        import sys
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    # Test generators
    print("Scrambled usernames:")
    gen = UsernameGenerator()
    for _ in range(5):
        print(f"  {gen.generate()}")
    
    print("\nStructured usernames:")
    structured_gen = StructuredUsernameGenerator()
    for _ in range(5):
        print(f"  {structured_gen.generate()}")
