#!/usr/bin/env python3
"""
Ragnarok Online Server Management Agent - CLI Interface
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add src directory to path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    # Try relative imports first (when run as module)
    from .file_manager import FileManager
    from .script_generator import ScriptGenerator
    from .database_updater import DatabaseUpdater
    from .translation_tools import TranslationTools
    from .knowledge_base import KnowledgeBase
except ImportError:
    # Fall back to absolute imports (when run directly)
    from file_manager import FileManager
    from script_generator import ScriptGenerator
    from database_updater import DatabaseUpdater
    from translation_tools import TranslationTools
    from knowledge_base import KnowledgeBase
    from shared_context import SharedContext
else:
    from .shared_context import SharedContext

class ROAgent:
    """Main Ragnarok Online Agent class"""

    def __init__(self, server_path: Optional[str] = None):
        self.server_path = Path(server_path) if server_path else Path.cwd()
        self.ctx = SharedContext(self.server_path)
        self.file_manager = FileManager(self.server_path)
        self.script_generator = ScriptGenerator(self.server_path)
        self.database_updater = DatabaseUpdater(self.server_path)
        self.translation_tools = TranslationTools(self.server_path)
        self.knowledge_base = KnowledgeBase(shared_context=self.ctx)

        # Initialize workspace metadata
        self._init_workspace_meta()

    def _init_workspace_meta(self):
        try:
            name = self.server_path.name
            self.ctx.set("workspace.name", name)
            # Minimal tech stack guess
            stack = "rAthena/Hercules/OpenKore"
            self.ctx.set("workspace.tech_stack", stack)
            # Record emulator detection
            emulator = self.detect_emulator()
            last = self.ctx.get("last.ro_agent", {}) or {}
            prev = last.get("emulator")
            self.ctx.set("last.ro_agent", {**last, "emulator": emulator})
            if prev and prev != emulator and emulator != "unknown":
                # Log a notice about emulator change
                self.ctx.log_event("ro_agent", "emulator_changed", {"from": prev, "to": emulator})
        except Exception:
            pass

    def detect_emulator(self) -> str:
        """Detect which RO emulator is being used"""
        # Common layouts:
        # - rAthena checked either by a nested 'rathena' folder or typical dirs at project root
        # - Hercules often uses similar dirs; only disambiguate when explicit folder present
        root = self.server_path
        try:
            if (root / "rathena").exists():
                return "rathena"
            # Typical rAthena tree when repo root is the emulator itself
            if (root / "npc").exists() and (root / "db").exists() and (root / "conf").exists():
                return "rathena"
            if (root / "hercules").exists():
                return "hercules"
            if (root / "openkore").exists():
                return "openkore"
        except Exception:
            pass
        return "unknown"

@click.group()
@click.option('--server-path', '-p', default=None,
              help='Path to RO server directory (defaults to current directory)')
@click.pass_context
def cli(ctx, server_path):
    """Ragnarok Online Server Management Agent

    AI-powered tools for managing RO private servers including rAthena, Hercules, and more.
    """
    ctx.ensure_object(dict)
    ctx.obj['agent'] = ROAgent(server_path)

@cli.command()
@click.pass_context
def status(ctx):
    """Show server status and detected emulator"""
    agent = ctx.obj['agent']
    emulator = agent.detect_emulator()

    click.echo("Ragnarok Online Server Management Agent")
    click.echo(f"Server Path: {agent.server_path}")
    click.echo(f"Detected Emulator: {emulator}")
    click.echo("Status: Active and ready")
    try:
        agent.ctx.log_event("ro_agent", "status_checked", {"emulator": emulator})
    except Exception:
        pass

@cli.command()
@click.argument('query')
@click.pass_context
def ask(ctx, query):
    """Ask the knowledge base for help"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.search(query)
    click.echo(result)

# Learning and Education Commands
@cli.group()
def learn():
    """Learning and educational tools"""
    pass

@learn.command('path')
@click.argument('path_name')
@click.pass_context
def learn_path(ctx, path_name):
    """Start a learning path (server_admin, content_creator, scripter, quick_start)"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.get_learning_path(path_name)
    click.echo(result)
    try:
        agent.ctx.set("progress.ro_agent.last_learning_path", path_name)
    except Exception:
        pass

@learn.command('tutorial')
@click.argument('level')
@click.pass_context
def learn_tutorial(ctx, level):
    """Start an interactive tutorial (beginner, intermediate, advanced)"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.get_tutorial(level)
    click.echo(result)
    try:
        # Initialize or move pointer to this tutorial
        agent.ctx.set("progress.ro_agent.current_tutorial", level)
        agent.ctx.set("progress.ro_agent.current_step", 0)
        agent.ctx.log_event("ro_agent", "tutorial_opened", {"level": level})
    except Exception:
        pass

@learn.command('concept')
@click.argument('concept_name')
@click.pass_context
def learn_concept(ctx, concept_name):
    """Learn about RO server concepts (server_architecture, scripting_fundamentals, database_structure)"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.explain_concept(concept_name)
    click.echo(result)

@learn.command('next')
@click.pass_context
def learn_next(ctx):
    """Continue to the next step in your current tutorial"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.get_next_step()
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "tutorial_next", {})
    except Exception:
        pass

@learn.command('progress')
@click.pass_context
def learn_progress(ctx):
    """Check your learning progress"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.get_progress()
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "tutorial_progress_viewed", {})
    except Exception:
        pass

# File Management Commands
@cli.group()
def files():
    """File management tools"""
    pass

@files.command('organize')
@click.option('--type', '-t', required=True,
              type=click.Choice(['scripts', 'configs', 'maps', 'all']),
              help='Type of files to organize')
@click.option('--destination', '-d', default=None,
              help='Destination directory for organized files')
@click.pass_context
def files_organize(ctx, type, destination):
    """Organize server files by type"""
    agent = ctx.obj['agent']
    result = agent.file_manager.organize_files(type, destination)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "files_organized", {"type": type, "destination": destination or "default"})
    except Exception:
        pass

@files.command('backup')
@click.option('--configs', is_flag=True, help='Backup configuration files')
@click.option('--database', is_flag=True, help='Backup database files')
@click.option('--scripts', is_flag=True, help='Backup script files')
@click.pass_context
def files_backup(ctx, configs, database, scripts):
    """Create backups of server files"""
    agent = ctx.obj['agent']
    result = agent.file_manager.create_backup(configs, database, scripts)
    click.echo(result)
    try:
        agent.ctx.set("last.ro_agent.last_backup", datetime.utcnow().isoformat() + "Z")
        agent.ctx.log_event("ro_agent", "backup_created", {"configs": configs, "database": database, "scripts": scripts})
    except Exception:
        pass

# Script Generation Commands
@cli.group()
def script():
    """Script generation tools"""
    pass

@script.command('npc')
@click.option('--type', '-t', required=True,
              type=click.Choice(['shop', 'quest', 'warp', 'monster']),
              help='Type of NPC script to generate')
@click.option('--name', '-n', required=True, help='NPC name')
@click.option('--items', '-i', default=None, help='Comma-separated item IDs for shops')
@click.option('--dialog', '-d', default=None, help='NPC dialogue text')
@click.pass_context
def script_npc(ctx, type, name, items, dialog):
    """Generate NPC scripts"""
    agent = ctx.obj['agent']
    result = agent.script_generator.generate_npc(type, name, items, dialog)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "script_generated", {"kind": "npc", "type": type, "name": name})
    except Exception:
        pass

@script.command('item')
@click.option('--id', '-i', required=True, type=int, help='Item ID')
@click.option('--name', '-n', required=True, help='Item name')
@click.option('--type', '-t', default='etc', help='Item type')
@click.option('--price', '-p', default=0, type=int, help='Item price')
@click.pass_context
def script_item(ctx, id, name, type, price):
    """Generate item scripts"""
    agent = ctx.obj['agent']
    result = agent.script_generator.generate_item(id, name, type, price)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "script_generated", {"kind": "item", "id": id, "name": name})
    except Exception:
        pass

# Database Update Commands
@cli.group()
def update():
    """Database update tools"""
    pass

@update.command('items')
@click.option('--source', '-s', default='kro',
              type=click.Choice(['kro', 'iro', 'manual']),
              help='Data source for updates')
@click.option('--version', '-v', default='latest', help='Version to update to')
@click.option('--range', '-r', default=None, help='Item ID range (e.g., 500-1000)')
@click.option('--backup', is_flag=True, help='Create backup before updating')
@click.pass_context
def update_items(ctx, source, version, range, backup):
    """Update item database from various sources"""
    agent = ctx.obj['agent']
    result = agent.database_updater.update_items(source, version, range, backup)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "db_updated", {"what": "items", "source": source, "version": version, "range": range or "all"})
    except Exception:
        pass

@update.command('mobs')
@click.option('--source', '-s', default='kro', help='Data source')
@click.option('--backup', is_flag=True, help='Create backup')
@click.pass_context
def update_mobs(ctx, source, backup):
    """Update monster database"""
    agent = ctx.obj['agent']
    result = agent.database_updater.update_mobs(source, backup)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "db_updated", {"what": "mobs", "source": source})
    except Exception:
        pass

# Translation Commands
@cli.group()
def translate():
    """Translation tools"""
    pass

@translate.command('items')
@click.option('--from-lang', '-f', default='english', help='Source language')
@click.option('--to-lang', '-t', required=True, help='Target language')
@click.option('--file', required=True, help='File to translate')
@click.pass_context
def translate_items(ctx, from_lang, to_lang, file):
    """Translate item descriptions"""
    agent = ctx.obj['agent']
    result = agent.translation_tools.translate_file(file, from_lang, to_lang)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "translated", {"what": "items", "file": file, "from": from_lang, "to": to_lang})
    except Exception:
        pass

@translate.command('client')
@click.option('--files', required=True, help='Client files to translate (comma-separated)')
@click.option('--language', '-l', required=True, help='Target language')
@click.pass_context
def translate_client(ctx, files, language):
    """Translate client files"""
    agent = ctx.obj['agent']
    file_list = [f.strip() for f in files.split(',')]
    result = agent.translation_tools.translate_client_files(file_list, language)
    click.echo(result)
    try:
        agent.ctx.log_event("ro_agent", "translated", {"what": "client_files", "count": len(file_list), "to": language})
    except Exception:
        pass

if __name__ == '__main__':
    cli()
