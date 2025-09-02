#!/usr/bin/env python3
"""
Ragnarok Online Server Management Agent - CLI Interface
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional

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

class ROAgent:
    """Main Ragnarok Online Agent class"""

    def __init__(self, server_path: Optional[str] = None):
        self.server_path = Path(server_path) if server_path else Path.cwd()
        self.file_manager = FileManager(self.server_path)
        self.script_generator = ScriptGenerator(self.server_path)
        self.database_updater = DatabaseUpdater(self.server_path)
        self.translation_tools = TranslationTools(self.server_path)
        self.knowledge_base = KnowledgeBase()

    def detect_emulator(self) -> str:
        """Detect which RO emulator is being used"""
        if (self.server_path / "rathena").exists():
            return "rathena"
        elif (self.server_path / "hercules").exists():
            return "hercules"
        elif (self.server_path / "openkore").exists():
            return "openkore"
        else:
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

@learn.command('tutorial')
@click.argument('level')
@click.pass_context
def learn_tutorial(ctx, level):
    """Start an interactive tutorial (beginner, intermediate, advanced)"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.get_tutorial(level)
    click.echo(result)

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

@learn.command('progress')
@click.pass_context
def learn_progress(ctx):
    """Check your learning progress"""
    agent = ctx.obj['agent']
    result = agent.knowledge_base.get_progress()
    click.echo(result)

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

@update.command('mobs')
@click.option('--source', '-s', default='kro', help='Data source')
@click.option('--backup', is_flag=True, help='Create backup')
@click.pass_context
def update_mobs(ctx, source, backup):
    """Update monster database"""
    agent = ctx.obj['agent']
    result = agent.database_updater.update_mobs(source, backup)
    click.echo(result)

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

if __name__ == '__main__':
    cli()