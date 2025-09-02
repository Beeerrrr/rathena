"""
Database Update System for Ragnarok Online Servers
Handles synchronization with kRO databases and item/mob updates
"""

import os
import requests
import json
import csv
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import shutil
import re

class DatabaseUpdater:
    """Updates RO databases from various sources"""

    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.cache_dir = server_path / "ANALYSIS_CACHE"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Known data sources
        self.sources = {
            'kro': {
                'base_url': 'https://raw.githubusercontent.com/zackdreaver/ROenglishRE/master',
                'item_db': '/DB/item_db.txt',
                'mob_db': '/DB/mob_db.txt',
                'item_db_re': '/DB/item_db_re.txt',
                'mob_db_re': '/DB/mob_db_re.txt'
            },
            'iro': {
                'base_url': 'https://raw.githubusercontent.com/zackdreaver/ROenglishRE/master',
                'item_db': '/DB/item_db_iro.txt',
                'mob_db': '/DB/mob_db_iro.txt'
            }
        }

    def update_items(self, source: str = 'kro', version: str = 'latest',
                    item_range: Optional[str] = None, backup: bool = False) -> str:
        """Update item database from specified source"""
        if source not in self.sources:
            return f"Unknown source: {source}"

        try:
            # Create backup if requested
            if backup:
                self._backup_database('items')

            # Download latest data
            item_data = self._download_item_data(source, version)

            if not item_data:
                return "Failed to download item data"

            # Parse item range if specified
            start_id, end_id = self._parse_item_range(item_range)

            # Update database files
            updated_count = self._update_item_files(item_data, start_id, end_id)

            # Cache the update
            self._cache_update('items', source, version, updated_count)

            return f"Updated {updated_count} items from {source}"

        except Exception as e:
            return f"Error updating items: {str(e)}"

    def update_mobs(self, source: str = 'kro', backup: bool = False) -> str:
        """Update monster database from specified source"""
        if source not in self.sources:
            return f"Unknown source: {source}"

        try:
            # Create backup if requested
            if backup:
                self._backup_database('mobs')

            # Download latest data
            mob_data = self._download_mob_data(source)

            if not mob_data:
                return "Failed to download mob data"

            # Update database files
            updated_count = self._update_mob_files(mob_data)

            # Cache the update
            self._cache_update('mobs', source, 'latest', updated_count)

            return f"Updated {updated_count} monsters from {source}"

        except Exception as e:
            return f"Error updating mobs: {str(e)}"

    def _download_item_data(self, source: str, version: str) -> Optional[List[Dict]]:
        """Download item data from source"""
        source_config = self.sources[source]

        # Try different item database files
        urls_to_try = []
        if version == 're' or version == 'renewal':
            urls_to_try.append(source_config['base_url'] + source_config.get('item_db_re', source_config['item_db']))
        else:
            urls_to_try.append(source_config['base_url'] + source_config['item_db'])

        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Parse the item database
                return self._parse_item_db(response.text)

            except requests.RequestException:
                continue

        return None

    def _download_mob_data(self, source: str) -> Optional[List[Dict]]:
        """Download mob data from source"""
        source_config = self.sources[source]

        url = source_config['base_url'] + source_config['mob_db']

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse the mob database
            return self._parse_mob_db(response.text)

        except requests.RequestException:
            return None

    def _parse_item_db(self, content: str) -> List[Dict]:
        """Parse item database content"""
        items = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Parse item entry (simplified parsing)
            parts = line.split(',')
            if len(parts) >= 10:
                try:
                    item = {
                        'id': int(parts[0]),
                        'name': parts[1].strip('"'),
                        'type': parts[2],
                        'price_buy': int(parts[3]) if parts[3].isdigit() else 0,
                        'price_sell': int(parts[4]) if parts[4].isdigit() else 0,
                        'weight': int(parts[5]) if parts[5].isdigit() else 0,
                        'attack': int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0,
                        'defense': int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0,
                        'range': int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0,
                        'slots': int(parts[9]) if len(parts) > 9 and parts[9].isdigit() else 0
                    }
                    items.append(item)
                except (ValueError, IndexError):
                    continue

        return items

    def _parse_mob_db(self, content: str) -> List[Dict]:
        """Parse monster database content"""
        mobs = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Parse mob entry (simplified parsing)
            parts = line.split(',')
            if len(parts) >= 15:
                try:
                    mob = {
                        'id': int(parts[0]),
                        'sprite': parts[1].strip('"'),
                        'name': parts[2].strip('"'),
                        'level': int(parts[3]) if parts[3].isdigit() else 1,
                        'hp': int(parts[4]) if parts[4].isdigit() else 100,
                        'sp': int(parts[5]) if parts[5].isdigit() else 10,
                        'base_exp': int(parts[6]) if parts[6].isdigit() else 10,
                        'job_exp': int(parts[7]) if parts[7].isdigit() else 5,
                        'attack': int(parts[8]) if parts[8].isdigit() else 10,
                        'attack2': int(parts[9]) if parts[9].isdigit() else 15,
                        'defense': int(parts[10]) if parts[10].isdigit() else 5,
                        'magic_defense': int(parts[11]) if parts[11].isdigit() else 5,
                        'str': int(parts[12]) if parts[12].isdigit() else 1,
                        'agi': int(parts[13]) if parts[13].isdigit() else 1,
                        'vit': int(parts[14]) if parts[14].isdigit() else 1,
                        'int': int(parts[15]) if len(parts) > 15 and parts[15].isdigit() else 1,
                        'dex': int(parts[16]) if len(parts) > 16 and parts[16].isdigit() else 1,
                        'luk': int(parts[17]) if len(parts) > 17 and parts[17].isdigit() else 1
                    }
                    mobs.append(mob)
                except (ValueError, IndexError):
                    continue

        return mobs

    def _parse_item_range(self, item_range: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """Parse item ID range string"""
        if not item_range:
            return None, None

        match = re.match(r'(\d+)-(\d+)', item_range)
        if match:
            return int(match.group(1)), int(match.group(2))

        return None, None

    def _update_item_files(self, items: List[Dict], start_id: Optional[int],
                          end_id: Optional[int]) -> int:
        """Update item database files"""
        updated_count = 0

        # Find item database files
        db_files = self._find_db_files('item_db')

        for db_file in db_files:
            try:
                # Read existing content
                with open(db_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

                # Update items
                updated_content = self._merge_item_data(existing_content, items, start_id, end_id)

                # Write back
                with open(db_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                updated_count += len(items)

            except Exception as e:
                print(f"Error updating {db_file}: {e}")
                continue

        return updated_count

    def _update_mob_files(self, mobs: List[Dict]) -> int:
        """Update monster database files"""
        updated_count = 0

        # Find mob database files
        db_files = self._find_db_files('mob_db')

        for db_file in db_files:
            try:
                # Read existing content
                with open(db_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

                # Update mobs
                updated_content = self._merge_mob_data(existing_content, mobs)

                # Write back
                with open(db_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                updated_count += len(mobs)

            except Exception as e:
                print(f"Error updating {db_file}: {e}")
                continue

        return updated_count

    def _find_db_files(self, db_type: str) -> List[Path]:
        """Find database files of specified type"""
        db_files = []

        # Common database directories
        db_dirs = ['db', 'database', 'sql-files']

        for db_dir in db_dirs:
            search_dir = self.server_path / db_dir
            if search_dir.exists():
                # Look for files matching the pattern
                if db_type == 'item_db':
                    patterns = ['item_db.txt', 'item_db_re.txt', 'item_db_*.txt']
                else:
                    patterns = ['mob_db.txt', 'mob_db_re.txt', 'mob_db_*.txt']

                for pattern in patterns:
                    for file_path in search_dir.glob(pattern):
                        if file_path.is_file():
                            db_files.append(file_path)

        return db_files

    def _merge_item_data(self, existing_content: str, new_items: List[Dict],
                        start_id: Optional[int], end_id: Optional[int]) -> str:
        """Merge new item data with existing content"""
        lines = existing_content.split('\n')
        updated_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                updated_lines.append(line)
                continue

            # Check if this item should be updated
            parts = line.split(',')
            if len(parts) >= 2:
                try:
                    item_id = int(parts[0])
                    if start_id and end_id:
                        if start_id <= item_id <= end_id:
                            # Find matching new item
                            new_item = next((item for item in new_items if item['id'] == item_id), None)
                            if new_item:
                                # Update the line
                                line = self._format_item_line(new_item)
                except (ValueError, IndexError):
                    pass

            updated_lines.append(line)

        return '\n'.join(updated_lines)

    def _merge_mob_data(self, existing_content: str, new_mobs: List[Dict]) -> str:
        """Merge new mob data with existing content"""
        lines = existing_content.split('\n')
        updated_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                updated_lines.append(line)
                continue

            # Check if this mob should be updated
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    mob_id = int(parts[0])
                    # Find matching new mob
                    new_mob = next((mob for mob in new_mobs if mob['id'] == mob_id), None)
                    if new_mob:
                        # Update the line
                        line = self._format_mob_line(new_mob)
                except (ValueError, IndexError):
                    pass

            updated_lines.append(line)

        return '\n'.join(updated_lines)

    def _format_item_line(self, item: Dict) -> str:
        """Format item data as database line"""
        return f"{item['id']},{item['name']},{item['type']},{item['price_buy']},{item['price_sell']},{item['weight']},{item['attack']},{item['defense']},{item['range']},{item['slots']}"

    def _format_mob_line(self, mob: Dict) -> str:
        """Format mob data as database line"""
        return f"{mob['id']},{mob['sprite']},{mob['name']},{mob['level']},{mob['hp']},{mob['sp']},{mob['base_exp']},{mob['job_exp']},{mob['attack']},{mob['attack2']},{mob['defense']},{mob['magic_defense']},{mob['str']},{mob['agi']},{mob['vit']},{mob['int']},{mob['dex']},{mob['luk']}"

    def _backup_database(self, db_type: str):
        """Create backup of database files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.server_path / f'backup_db_{db_type}_{timestamp}'
        backup_dir.mkdir(exist_ok=True)

        db_files = self._find_db_files(db_type)

        for db_file in db_files:
            rel_path = db_file.relative_to(self.server_path)
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(db_file, backup_path)

    def _cache_update(self, update_type: str, source: str, version: str, count: int):
        """Cache update information"""
        cache_file = self.cache_dir / 'updates.json'

        # Load existing cache
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        else:
            cache = {}

        # Add new update
        update_key = f"{update_type}_{source}_{version}"
        cache[update_key] = {
            'timestamp': datetime.now().isoformat(),
            'count': count,
            'source': source,
            'version': version
        }

        # Save cache
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)

    def get_update_history(self) -> Dict:
        """Get update history from cache"""
        cache_file = self.cache_dir / 'updates.json'

        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)

        return {}