"""
File Management System for Ragnarok Online Servers
Handles organization, backup, and management of server/client files
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

class FileManager:
    """Manages RO server and client files"""

    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.cache_dir = server_path / "ANALYSIS_CACHE"
        self.cache_dir.mkdir(exist_ok=True)

    def detect_emulator_structure(self) -> Dict[str, List[str]]:
        """Detect the file structure of the RO emulator"""
        structure = {
            'rathena': ['npc', 'db', 'conf', 'src', 'rathena'],
            'hercules': ['npc', 'db', 'conf', 'src', 'hercules'],
            'openkore': ['control', 'logs', 'plugins', 'tables'],
            'eathena': ['npc', 'db', 'conf', 'src']
        }

        detected = {}
        for emulator, dirs in structure.items():
            if any((self.server_path / d).exists() for d in dirs):
                detected[emulator] = dirs

        return detected

    def organize_files(self, file_type: str, destination: Optional[str] = None) -> str:
        """Organize files by type"""
        if file_type == 'scripts':
            return self._organize_scripts(destination)
        elif file_type == 'configs':
            return self._organize_configs(destination)
        elif file_type == 'maps':
            return self._organize_maps(destination)
        elif file_type == 'all':
            results = []
            results.append(self._organize_scripts())
            results.append(self._organize_configs())
            results.append(self._organize_maps())
            return "\n".join(results)
        else:
            return f"Unknown file type: {file_type}"

    def _organize_scripts(self, destination: Optional[str] = None) -> str:
        """Organize script files"""
        script_dirs = ['npc', 'scripts']
        dest_dir = Path(destination) if destination else self.server_path / 'organized' / 'scripts'
        dest_dir.mkdir(parents=True, exist_ok=True)

        moved_files = 0
        for script_dir in script_dirs:
            src_dir = self.server_path / script_dir
            if src_dir.exists():
                for file_path in src_dir.rglob('*.txt'):
                    if file_path.is_file():
                        # Create subdirectory based on file content hints
                        sub_dir = self._categorize_script(file_path)
                        final_dest = dest_dir / sub_dir
                        final_dest.mkdir(exist_ok=True)

                        shutil.copy2(file_path, final_dest / file_path.name)
                        moved_files += 1

        return f"Organized {moved_files} script files to {dest_dir}"

    def _organize_configs(self, destination: Optional[str] = None) -> str:
        """Organize configuration files"""
        dest_dir = Path(destination) if destination else self.server_path / 'organized' / 'configs'
        dest_dir.mkdir(parents=True, exist_ok=True)

        config_patterns = ['*.conf', '*.cfg', '*.ini', 'inter*.txt', 'login*.txt', 'char*.txt', 'map*.txt']
        moved_files = 0

        for pattern in config_patterns:
            for file_path in self.server_path.rglob(pattern):
                if file_path.is_file():
                    shutil.copy2(file_path, dest_dir / file_path.name)
                    moved_files += 1

        return f"Organized {moved_files} configuration files to {dest_dir}"

    def _organize_maps(self, destination: Optional[str] = None) -> str:
        """Organize map files"""
        dest_dir = Path(destination) if destination else self.server_path / 'organized' / 'maps'
        dest_dir.mkdir(parents=True, exist_ok=True)

        map_files = ['maps.conf', 'map_index.txt']
        moved_files = 0

        for map_file in map_files:
            src_file = self.server_path / map_file
            if src_file.exists():
                shutil.copy2(src_file, dest_dir / map_file)
                moved_files += 1

        # Also look for .gat, .rsw files in maps directory
        maps_dir = self.server_path / 'maps'
        if maps_dir.exists():
            for file_path in maps_dir.rglob('*'):
                if file_path.suffix in ['.gat', '.rsw', '.gnd', '.act', '.spr']:
                    shutil.copy2(file_path, dest_dir / file_path.name)
                    moved_files += 1

        return f"Organized {moved_files} map files to {dest_dir}"

    def _categorize_script(self, file_path: Path) -> str:
        """Categorize script file based on content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000).lower()

            if 'shop' in content or 'buy' in content or 'sell' in content:
                return 'shops'
            elif 'quest' in content or 'mission' in content:
                return 'quests'
            elif 'warp' in content or 'goto' in content:
                return 'warps'
            elif 'monster' in content or 'mob' in content:
                return 'monsters'
            elif 'function' in content or 'callfunc' in content:
                return 'functions'
            else:
                return 'misc'
        except:
            return 'misc'

    def create_backup(self, configs: bool = False, database: bool = False, scripts: bool = False) -> str:
        """Create backup of specified file types"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.server_path / f'backup_{timestamp}'
        backup_dir.mkdir(exist_ok=True)

        backed_up = 0

        if configs:
            backed_up += self._backup_configs(backup_dir)
        if database:
            backed_up += self._backup_database(backup_dir)
        if scripts:
            backed_up += self._backup_scripts(backup_dir)

        # Save backup metadata
        metadata = {
            'timestamp': timestamp,
            'configs': configs,
            'database': database,
            'scripts': scripts,
            'files_backed_up': backed_up
        }

        with open(backup_dir / 'backup_info.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        return f"Created backup with {backed_up} files in {backup_dir}"

    def _backup_configs(self, backup_dir: Path) -> int:
        """Backup configuration files"""
        config_dir = backup_dir / 'configs'
        config_dir.mkdir(exist_ok=True)

        config_patterns = ['*.conf', '*.cfg', '*.ini', 'inter*.txt', 'login*.txt', 'char*.txt', 'map*.txt']
        backed_up = 0

        for pattern in config_patterns:
            for file_path in self.server_path.rglob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.server_path)
                    dest_path = config_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    backed_up += 1

        return backed_up

    def _backup_database(self, backup_dir: Path) -> int:
        """Backup database files"""
        db_dir = backup_dir / 'database'
        db_dir.mkdir(exist_ok=True)

        db_patterns = ['*.txt', '*.sql', '*.db']
        backed_up = 0

        # Common database directories
        db_locations = ['db', 'sql-files', 'database']

        for location in db_locations:
            src_dir = self.server_path / location
            if src_dir.exists():
                for pattern in db_patterns:
                    for file_path in src_dir.rglob(pattern):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(self.server_path)
                            dest_path = db_dir / rel_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dest_path)
                            backed_up += 1

        return backed_up

    def _backup_scripts(self, backup_dir: Path) -> int:
        """Backup script files"""
        script_dir = backup_dir / 'scripts'
        script_dir.mkdir(exist_ok=True)

        backed_up = 0

        # Common script directories
        script_locations = ['npc', 'scripts']

        for location in script_locations:
            src_dir = self.server_path / location
            if src_dir.exists():
                for file_path in src_dir.rglob('*.txt'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.server_path)
                        dest_path = script_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                        backed_up += 1

        return backed_up