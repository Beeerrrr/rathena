"""
Translation Tools for Ragnarok Online Servers
Handles translation of game text, client files, and server content
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re
import shutil

class TranslationTools:
    """Translation utilities for RO game content"""

    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.cache_dir = server_path / "ANALYSIS_CACHE"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Supported languages
        self.languages = {
            'english': 'en',
            'thai': 'th',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'portuguese': 'pt',
            'russian': 'ru',
            'japanese': 'ja',
            'korean': 'ko',
            'chinese_simplified': 'zh-cn',
            'chinese_traditional': 'zh-tw'
        }

        # Common RO text files
        self.text_files = [
            'msgstringtable.txt',
            'itemnametable.txt',
            'itemslotnametable.txt',
            'skillinfolist.txt',
            'skillnametable.txt',
            'npctalktable.txt'
        ]

    def translate_file(self, file_path: str, from_lang: str, to_lang: str) -> str:
        """Translate a single file"""
        source_file = self.server_path / file_path

        if not source_file.exists():
            return f"File not found: {file_path}"

        try:
            # Read file content
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Detect file type and translate
            if file_path.endswith('.txt'):
                translated_content = self._translate_text_file(content, from_lang, to_lang)
            else:
                return f"Unsupported file type: {file_path}"

            # Create backup
            self._backup_file(source_file)

            # Write translated content
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)

            return f"Translated {file_path} from {from_lang} to {to_lang}"

        except Exception as e:
            return f"Error translating file: {str(e)}"

    def translate_client_files(self, file_list: List[str], target_lang: str) -> str:
        """Translate multiple client files"""
        results = []

        for file_path in file_list:
            result = self.translate_file(file_path, 'english', target_lang)
            results.append(result)

        return f"Translation completed:\n" + "\n".join(results)

    def _translate_text_file(self, content: str, from_lang: str, to_lang: str) -> str:
        """Translate text file content"""
        lines = content.split('\n')
        translated_lines = []

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('//') or line.startswith('#'):
                translated_lines.append(line)
                continue

            # Handle different file formats
            if '\t' in line:
                # Tab-separated format (msgstringtable.txt, etc.)
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    key, text = parts
                    translated_text = self._translate_text(text, from_lang, to_lang)
                    translated_lines.append(f"{key}\t{translated_text}")
                else:
                    translated_lines.append(line)
            else:
                # Regular text line
                translated_text = self._translate_text(line, from_lang, to_lang)
                translated_lines.append(translated_text)

        return '\n'.join(translated_lines)

    def _translate_text(self, text: str, from_lang: str, to_lang: str) -> str:
        """Translate individual text using translation service"""
        # For now, this is a placeholder that would integrate with a translation API
        # In a real implementation, this would use Google Translate, DeepL, or similar

        # Check cache first
        cache_key = f"{from_lang}_{to_lang}_{hash(text)}"
        cached_translation = self._get_cached_translation(cache_key)

        if cached_translation:
            return cached_translation

        # Placeholder translation logic
        # This would be replaced with actual translation API calls
        translated = self._mock_translate(text, from_lang, to_lang)

        # Cache the translation
        self._cache_translation(cache_key, translated)

        return translated

    def _mock_translate(self, text: str, from_lang: str, to_lang: str) -> str:
        """Mock translation for demonstration purposes"""
        # This is just for demonstration - real implementation would use translation APIs

        # Simple replacements for common RO terms
        translations = {
            'th': {
                'Hello': 'สวัสดี',
                'Welcome': 'ยินดีต้อนรับ',
                'Item': 'ไอเทม',
                'Skill': 'สกิล',
                'Monster': 'มอนสเตอร์',
                'Quest': 'เควส',
                'Shop': 'ร้านค้า',
                'Warp': 'วอร์ป',
                'Attack': 'โจมตี',
                'Defense': 'ป้องกัน'
            },
            'es': {
                'Hello': 'Hola',
                'Welcome': 'Bienvenido',
                'Item': 'Objeto',
                'Skill': 'Habilidad',
                'Monster': 'Monstruo',
                'Quest': 'Misión',
                'Shop': 'Tienda',
                'Warp': 'Transportar',
                'Attack': 'Ataque',
                'Defense': 'Defensa'
            }
        }

        if to_lang in translations:
            lang_translations = translations[to_lang]
            for english, translated in lang_translations.items():
                text = re.sub(r'\b' + re.escape(english) + r'\b', translated, text, flags=re.IGNORECASE)

        return text

    def _get_cached_translation(self, cache_key: str) -> Optional[str]:
        """Get translation from cache"""
        cache_file = self.cache_dir / 'translations.json'

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    return cache.get(cache_key)
            except:
                pass

        return None

    def _cache_translation(self, cache_key: str, translation: str):
        """Cache translation"""
        cache_file = self.cache_dir / 'translations.json'

        # Load existing cache
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except:
                cache = {}
        else:
            cache = {}

        # Add new translation
        cache[cache_key] = translation

        # Save cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except:
            pass

    def _backup_file(self, file_path: Path):
        """Create backup of file before translation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.server_path / 'backup_translations'
        backup_dir.mkdir(exist_ok=True)

        rel_path = file_path.relative_to(self.server_path)
        backup_path = backup_dir / f"{rel_path.stem}_{timestamp}{rel_path.suffix}"

        shutil.copy2(file_path, backup_path)

    def create_translation_template(self, source_lang: str = 'english') -> str:
        """Create translation template for custom translations"""
        template = {
            'metadata': {
                'source_language': source_lang,
                'created': datetime.now().isoformat(),
                'version': '1.0'
            },
            'translations': {
                # Common RO terms that need translation
                'ui_terms': {
                    'Status': '',
                    'Inventory': '',
                    'Equipment': '',
                    'Skills': '',
                    'Party': '',
                    'Guild': '',
                    'Friends': '',
                    'Settings': ''
                },
                'game_terms': {
                    'Attack': '',
                    'Defense': '',
                    'Magic': '',
                    'Heal': '',
                    'Buff': '',
                    'Debuff': '',
                    'Critical': '',
                    'Miss': ''
                },
                'item_types': {
                    'Weapon': '',
                    'Armor': '',
                    'Accessory': '',
                    'Consumable': '',
                    'Card': '',
                    'Etc': ''
                }
            }
        }

        template_path = self.server_path / 'translation_template.json'
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        return f"Created translation template at {template_path}"

    def apply_translation_template(self, template_path: str, target_files: List[str]) -> str:
        """Apply custom translation template to files"""
        template_file = self.server_path / template_path

        if not template_file.exists():
            return f"Template file not found: {template_path}"

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)

            translations = template.get('translations', {})

            # Flatten translations
            flat_translations = {}
            for category, terms in translations.items():
                flat_translations.update(terms)

            results = []
            for file_path in target_files:
                result = self._apply_translations_to_file(file_path, flat_translations)
                results.append(result)

            return f"Applied translations:\n" + "\n".join(results)

        except Exception as e:
            return f"Error applying template: {str(e)}"

    def _apply_translations_to_file(self, file_path: str, translations: Dict[str, str]) -> str:
        """Apply translations to a specific file"""
        source_file = self.server_path / file_path

        if not source_file.exists():
            return f"File not found: {file_path}"

        try:
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Apply translations
            for english, translated in translations.items():
                if translated:  # Only apply non-empty translations
                    content = re.sub(r'\b' + re.escape(english) + r'\b', translated, content, flags=re.IGNORECASE)

            # Create backup
            self._backup_file(source_file)

            # Write translated content
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Applied {len(translations)} translations to {file_path}"

        except Exception as e:
            return f"Error translating {file_path}: {str(e)}"

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.languages.keys())

    def validate_translation_file(self, file_path: str) -> Dict[str, int]:
        """Validate translation file and count entries"""
        source_file = self.server_path / file_path

        if not source_file.exists():
            return {'error': f"File not found: {file_path}"}

        try:
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.split('\n')
            total_lines = len(lines)
            translated_lines = 0
            empty_lines = 0
            comment_lines = 0

            for line in lines:
                line = line.strip()
                if not line:
                    empty_lines += 1
                elif line.startswith('//') or line.startswith('#'):
                    comment_lines += 1
                elif '\t' in line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2 and parts[1].strip():
                        translated_lines += 1

            return {
                'total_lines': total_lines,
                'translated_lines': translated_lines,
                'empty_lines': empty_lines,
                'comment_lines': comment_lines,
                'completion_percentage': (translated_lines / max(1, total_lines - empty_lines - comment_lines)) * 100
            }

        except Exception as e:
            return {'error': str(e)}