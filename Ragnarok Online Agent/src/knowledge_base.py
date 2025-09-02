"""
Knowledge Base System for Ragnarok Online Server Management
Provides help, documentation, and troubleshooting guides
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class KnowledgeBase:
    """Knowledge base for RO server management"""

    def __init__(self):
        # Load architecture analysis cache
        self.cache_dir = Path(__file__).parent.parent / "ANALYSIS_CACHE"
        self.architecture_data = self._load_architecture_cache()
        self.knowledge = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict:
        """Load the knowledge base data"""
        return {
            'emulators': {
                'rathena': {
                    'description': 'Most popular open-source RO emulator',
                    'website': 'https://rathena.org',
                    'features': ['Complete server emulation', 'Active community', 'Regular updates'],
                    'setup_guide': '1. Download from GitHub\n2. Compile with make\n3. Configure conf files\n4. Import SQL files\n5. Start server'
                },
                'hercules': {
                    'description': 'Alternative RO emulator with different features',
                    'website': 'https://herc.ws',
                    'features': ['Plugin system', 'Extended scripting', 'Modern codebase'],
                    'setup_guide': '1. Clone repository\n2. Run configure script\n3. Make and install\n4. Setup database\n5. Configure server'
                },
                'openkore': {
                    'description': 'Bot framework for RO',
                    'website': 'https://openkore.com',
                    'features': ['Automated gameplay', 'Plugin support', 'Cross-platform'],
                    'setup_guide': '1. Download release\n2. Extract files\n3. Configure servers.txt\n4. Setup control folder\n5. Run openkore.pl'
                }
            },
            'common_issues': {
                'connection_failed': {
                    'symptoms': ['Cannot connect to server', 'Login failed', 'Character selection error'],
                    'solutions': [
                        'Check if server is running (check ports 6900, 6121, 5121)',
                        'Verify clientinfo.xml has correct server settings',
                        'Check firewall settings',
                        'Verify database connection in conf files'
                    ]
                },
                'script_errors': {
                    'symptoms': ['NPC not working', 'Script parse errors', 'Map server crashes'],
                    'solutions': [
                        'Check script syntax in npc/scripts_custom.conf',
                        'Verify file encoding is UTF-8',
                        'Check for missing brackets or semicolons',
                        'Use script checker tools'
                    ]
                },
                'database_errors': {
                    'symptoms': ['SQL connection failed', 'Table not found', 'Import errors'],
                    'solutions': [
                        'Verify MySQL/MariaDB is running',
                        'Check database credentials in conf files',
                        'Run database import scripts',
                        'Check for missing tables or columns'
                    ]
                }
            },
            'commands': {
                'file_management': {
                    'organize': 'Organize server files by type (scripts, configs, maps)',
                    'backup': 'Create backups of server files',
                    'examples': [
                        'ro_agent files organize --type scripts',
                        'ro_agent files backup --configs --database'
                    ]
                },
                'script_generation': {
                    'npc': 'Generate NPC scripts (shop, quest, warp)',
                    'item': 'Generate item database entries',
                    'examples': [
                        'ro_agent script npc --type shop --name "Tool Dealer"',
                        'ro_agent script item --id 501 --name "Red Potion"'
                    ]
                },
                'database_updates': {
                    'items': 'Update item database from kRO',
                    'mobs': 'Update monster database from kRO',
                    'examples': [
                        'ro_agent update items --source kro --backup',
                        'ro_agent update mobs --source kro'
                    ]
                },
                'translation': {
                    'items': 'Translate item descriptions',
                    'client': 'Translate client files',
                    'examples': [
                        'ro_agent translate items --to thai --file itemnametable.txt',
                        'ro_agent translate client --files msgstringtable.txt --language spanish'
                    ]
                }
            },
            'best_practices': {
                'server_setup': [
                    'Always backup before making changes',
                    'Test on development server first',
                    'Use version control for custom scripts',
                    'Keep server software updated',
                    'Monitor server logs regularly'
                ],
                'scripting': [
                    'Use descriptive variable names',
                    'Add comments to complex scripts',
                    'Test scripts in small areas first',
                    'Use proper error handling',
                    'Follow existing code style'
                ],
                'database': [
                    'Regular database backups',
                    'Use transactions for data changes',
                    'Monitor database performance',
                    'Clean up old logs periodically',
                    'Verify data integrity after updates'
                ]
            },
            'tutorials': {
                'beginner': {
                    'title': 'Setting up your first RO server',
                    'description': 'Complete beginner\'s guide to launching your RO server',
                    'estimated_time': '2-3 hours',
                    'prerequisites': ['Basic computer knowledge', 'Understanding of databases'],
                    'learning_objectives': [
                        'Understand RO server architecture',
                        'Install and configure rAthena',
                        'Set up MySQL database',
                        'Configure basic server settings',
                        'Launch and connect to your server'
                    ],
                    'steps': [
                        {
                            'title': 'Choose Your Emulator',
                            'description': 'Learn about different RO emulators and choose the right one for your needs',
                            'command': 'ro_agent ask "emulators"',
                            'explanation': 'rAthena is recommended for beginners due to its active community and comprehensive documentation'
                        },
                        {
                            'title': 'Install Prerequisites',
                            'description': 'Install MySQL/MariaDB, Git, and compiler tools',
                            'command': 'ro_agent ask "server setup"',
                            'explanation': 'These tools are essential for compiling and running your RO server'
                        },
                        {
                            'title': 'Download and Compile',
                            'description': 'Clone rAthena repository and compile the server',
                            'command': 'ro_agent ask "compilation guide"',
                            'explanation': 'Compilation turns source code into executable programs your computer can run'
                        },
                        {
                            'title': 'Configure Database',
                            'description': 'Set up MySQL database and import server data',
                            'command': 'ro_agent ask "database setup"',
                            'explanation': 'The database stores all game data including items, monsters, and player accounts'
                        },
                        {
                            'title': 'Basic Configuration',
                            'description': 'Configure server settings, rates, and network options',
                            'command': 'ro_agent ask "configuration guide"',
                            'explanation': 'Server configuration controls gameplay mechanics, rates, and server behavior'
                        },
                        {
                            'title': 'Launch and Test',
                            'description': 'Start your server and test the connection',
                            'command': 'ro_agent ask "testing server"',
                            'explanation': 'Verify that all server components are working correctly before opening to players'
                        }
                    ]
                },
                'intermediate': {
                    'title': 'Adding custom content',
                    'description': 'Learn to create and add custom NPCs, items, and quests',
                    'estimated_time': '4-6 hours',
                    'prerequisites': ['Basic server setup completed', 'Understanding of RO scripting'],
                    'learning_objectives': [
                        'Master RO scripting syntax',
                        'Create custom NPCs and shops',
                        'Add new items to the database',
                        'Design engaging quests',
                        'Test and balance custom content'
                    ],
                    'steps': [
                        {
                            'title': 'Learn RO Scripting Basics',
                            'description': 'Understand the fundamentals of RO NPC scripting',
                            'command': 'ro_agent ask "scripting basics"',
                            'explanation': 'RO uses a custom scripting language for NPCs, items, and game logic'
                        },
                        {
                            'title': 'Create Your First NPC',
                            'description': 'Generate a basic NPC using the script generator',
                            'command': 'ro_agent script npc --type shop --name "My First NPC"',
                            'explanation': 'Start with simple NPCs and gradually add complexity'
                        },
                        {
                            'title': 'Add Custom Items',
                            'description': 'Create new items and add them to your database',
                            'command': 'ro_agent script item --id 30000 --name "Custom Sword"',
                            'explanation': 'Custom items allow you to create unique content for your server'
                        },
                        {
                            'title': 'Design a Quest',
                            'description': 'Create an engaging quest with multiple steps',
                            'command': 'ro_agent script npc --type quest --name "Hero Quest"',
                            'explanation': 'Quests provide structure and goals for players'
                        },
                        {
                            'title': 'Test Your Content',
                            'description': 'Thoroughly test all custom content before release',
                            'command': 'ro_agent ask "testing custom content"',
                            'explanation': 'Testing ensures your content works correctly and provides good player experience'
                        }
                    ]
                },
                'advanced': {
                    'title': 'Server optimization and management',
                    'description': 'Master advanced server administration and optimization techniques',
                    'estimated_time': '6-8 hours',
                    'prerequisites': ['Intermediate scripting knowledge', 'Basic server management experience'],
                    'learning_objectives': [
                        'Optimize server performance',
                        'Implement security measures',
                        'Set up automated backups',
                        'Monitor server health',
                        'Handle player support issues'
                    ],
                    'steps': [
                        {
                            'title': 'Performance Optimization',
                            'description': 'Learn to optimize server performance and resource usage',
                            'command': 'ro_agent ask "server optimization"',
                            'explanation': 'Proper optimization ensures smooth gameplay for all players'
                        },
                        {
                            'title': 'Security Implementation',
                            'description': 'Implement security measures to protect your server',
                            'command': 'ro_agent ask "server security"',
                            'explanation': 'Security is crucial for protecting player data and preventing exploits'
                        },
                        {
                            'title': 'Backup Systems',
                            'description': 'Set up automated backup systems for your server data',
                            'command': 'ro_agent files backup --configs --database',
                            'explanation': 'Regular backups protect against data loss from crashes or attacks'
                        },
                        {
                            'title': 'Monitoring Setup',
                            'description': 'Configure monitoring tools to track server health',
                            'command': 'ro_agent ask "server monitoring"',
                            'explanation': 'Monitoring helps you identify and resolve issues before they affect players'
                        },
                        {
                            'title': 'Player Support',
                            'description': 'Learn to handle common player issues and support requests',
                            'command': 'ro_agent ask "player support"',
                            'explanation': 'Good player support improves satisfaction and server reputation'
                        }
                    ]
                }
            },
            'learning_concepts': {
                'server_architecture': {
                    'title': 'RO Server Architecture',
                    'description': 'Understanding how RO servers work',
                    'content': '''
RO (Ragnarok Online) servers consist of three main components:

1. **Login Server**: Handles player authentication and account management
2. **Character Server**: Manages character creation, deletion, and selection
3. **Map Server**: Handles actual gameplay, NPC interactions, and world state

Each component runs as a separate process and communicates with the others.
The database (MySQL/MariaDB) stores all persistent game data.

Key Files:
- conf/login_athena.conf: Login server configuration
- conf/char_athena.conf: Character server configuration
- conf/map_athena.conf: Map server configuration
- conf/inter_athena.conf: Database connection settings
                    '''
                },
                'scripting_fundamentals': {
                    'title': 'RO Scripting Fundamentals',
                    'description': 'Basic concepts of RO NPC scripting',
                    'content': '''
RO uses a custom scripting language for NPCs, items, and game logic.

Basic Structure:
map,x,y,direction	script	NPC_Name	Sprite,{
 // NPC code here
}

Key Commands:
- mes "text": Display dialogue to player
- next: Wait for player to click Next
- close: End conversation
- set variable,value: Set a variable
- if(condition) { code }: Conditional execution

Variables:
- Permanent: Store in database, persist across server restarts
- Temporary: Exist only during conversation
- Account: Tied to player account
- Character: Tied to specific character
                    '''
                },
                'database_structure': {
                    'title': 'RO Database Structure',
                    'description': 'Understanding the RO database schema',
                    'content': '''
The RO database contains several key tables:

Core Tables:
- login: Player account information
- char: Character data and stats
- inventory: Player inventory items
- cart_inventory: Cart/shopping cart items
- storage: Player storage items

Game Data Tables:
- item_db: Item definitions and properties
- mob_db: Monster definitions and stats
- skill_db: Skill definitions and properties

Important Concepts:
- Item IDs: Unique identifiers for all items (0-65,535)
- Monster IDs: Unique identifiers for monsters
- Job IDs: Character class identifiers
- Map names: Unique identifiers for game maps
                    '''
                }
            },
            'learning_paths': {
                'server_admin': ['beginner', 'intermediate', 'advanced'],
                'content_creator': ['beginner', 'intermediate'],
                'scripter': ['scripting_fundamentals', 'intermediate'],
                'quick_start': ['beginner']
            }
        }

    def search(self, query: str) -> str:
        """Search the knowledge base for relevant information"""
        query = query.lower().strip()

        # Direct category matches
        if query in self.knowledge:
            return self._format_category_info(query, self.knowledge[query])

        # Search for keywords
        results = []

        # Search emulators
        for emulator, info in self.knowledge['emulators'].items():
            if query in emulator.lower() or query in info['description'].lower():
                results.append(f"**{emulator.upper()}**: {info['description']}")
                results.append(f"Website: {info['website']}")
                results.append("")

        # Search common issues
        for issue, info in self.knowledge['common_issues'].items():
            if query in issue.lower() or any(query in symptom.lower() for symptom in info['symptoms']):
                results.append(f"**Issue: {issue.replace('_', ' ').title()}**")
                results.append("Symptoms:")
                for symptom in info['symptoms']:
                    results.append(f"• {symptom}")
                results.append("Solutions:")
                for solution in info['solutions']:
                    results.append(f"• {solution}")
                results.append("")

        # Search commands
        for category, commands in self.knowledge['commands'].items():
            if query in category.lower():
                results.append(f"**{category.replace('_', ' ').title()} Commands:**")
                for cmd, desc in commands.items():
                    if cmd != 'examples':
                        results.append(f"• {cmd}: {desc}")
                if 'examples' in commands:
                    results.append("Examples:")
                    for example in commands['examples']:
                        results.append(f"  {example}")
                results.append("")

        # Search tutorials
        for level, tutorial in self.knowledge['tutorials'].items():
            if query in level.lower() or query in tutorial['title'].lower():
                results.append(f"**{tutorial['title']}** ({level.title()})")
                results.append("Steps:")
                for i, step in enumerate(tutorial['steps'], 1):
                    results.append(f"{i}. {step}")
                results.append("")

        if not results:
            return self._get_general_help()

        return "\n".join(results)

    def _format_category_info(self, category: str, info: Dict) -> str:
        """Format information for a specific category"""
        if category == 'emulators':
            result = "**Supported Emulators:**\n\n"
            for emulator, details in info.items():
                result += f"**{emulator.upper()}**\n"
                result += f"• Description: {details['description']}\n"
                result += f"• Website: {details['website']}\n"
                result += f"• Key Features: {', '.join(details['features'])}\n"
                result += f"• Setup: {details['setup_guide']}\n\n"
            return result

        elif category == 'best_practices':
            result = "**Best Practices:**\n\n"
            for practice_area, practices in info.items():
                result += f"**{practice_area.replace('_', ' ').title()}:**\n"
                for practice in practices:
                    result += f"• {practice}\n"
                result += "\n"
            return result

        return f"Information about {category}"

    def _get_general_help(self) -> str:
        """Get general help information"""
        return """Ragnarok Online Server Management Agent Help

Available Topics:
- emulators - Information about supported RO emulators
- common_issues - Troubleshooting common server problems
- commands - Available CLI commands and usage
- best_practices - Server management best practices
- tutorials - Step-by-step guides for different skill levels

Quick Commands:
- ro_agent status - Show server status
- ro_agent files organize --type scripts - Organize script files
- ro_agent script npc --type shop --name "My Shop" - Generate NPC
- ro_agent update items --source kro - Update from kRO
- ro_agent translate items --to thai --file itemnametable.txt - Translate files

Getting Started:
1. Copy the agent to your RO server directory
2. Run the auto-setup script
3. Use ro_agent status to check your setup
4. Start with basic file organization

Need more help? Try searching for specific topics like "rathena setup" or "script errors"."""

    def get_emulator_info(self, emulator: str) -> Optional[Dict]:
        """Get information about a specific emulator"""
        return self.knowledge['emulators'].get(emulator.lower())

    def get_troubleshooting_guide(self, issue: str) -> Optional[Dict]:
        """Get troubleshooting guide for a specific issue"""
        return self.knowledge['common_issues'].get(issue.lower())

    def get_tutorial_dict(self, level: str) -> Optional[Dict]:
        """Get tutorial dictionary for a specific skill level"""
        return self.knowledge['tutorials'].get(level.lower())

    def list_topics(self) -> List[str]:
        """List all available knowledge base topics"""
        topics = []
        for category in self.knowledge.keys():
            topics.append(category)
        return topics

    def get_command_help(self, command: str) -> Optional[str]:
        """Get help for a specific command"""
        for category, commands in self.knowledge['commands'].items():
            if command in commands:
                return commands[command]
        return None

    def get_learning_path(self, path_name: str) -> str:
        """Get information about a learning path"""
        if path_name not in self.knowledge['learning_paths']:
            available_paths = list(self.knowledge['learning_paths'].keys())
            return f"Available learning paths: {', '.join(available_paths)}"

        path_steps = self.knowledge['learning_paths'][path_name]

        result = f"Learning Path: {path_name.replace('_', ' ').title()}\n\n"
        result += f"This path includes {len(path_steps)} modules:\n\n"

        for i, step in enumerate(path_steps, 1):
            if step in self.knowledge['tutorials']:
                tutorial = self.knowledge['tutorials'][step]
                result += f"{i}. {tutorial['title']}\n"
                result += f"   Time: {tutorial.get('estimated_time', 'Varies')}\n"
                result += f"   Description: {tutorial.get('description', '')}\n\n"
            elif step in self.knowledge['learning_concepts']:
                concept = self.knowledge['learning_concepts'][step]
                result += f"{i}. {concept['title']}\n"
                result += f"   Description: {concept.get('description', '')}\n\n"

        result += f"Start this path with: ro_agent learn tutorial {path_steps[0]}"
        return result

    def get_tutorial(self, level: str) -> str:
        """Get detailed tutorial information"""
        if level not in self.knowledge['tutorials']:
            available_levels = list(self.knowledge['tutorials'].keys())
            return f"Available tutorials: {', '.join(available_levels)}"

        tutorial = self.knowledge['tutorials'][level]

        result = f"Tutorial: {tutorial['title']}\n"
        result += f"Description: {tutorial.get('description', '')}\n"
        result += f"Estimated Time: {tutorial.get('estimated_time', 'Varies')}\n\n"

        if 'prerequisites' in tutorial:
            result += "Prerequisites:\n"
            for prereq in tutorial['prerequisites']:
                result += f"- {prereq}\n"
            result += "\n"

        if 'learning_objectives' in tutorial:
            result += "What You'll Learn:\n"
            for objective in tutorial['learning_objectives']:
                result += f"- {objective}\n"
            result += "\n"

        result += "Steps:\n"
        for i, step in enumerate(tutorial['steps'], 1):
            if isinstance(step, dict):
                result += f"{i}. {step['title']}\n"
                result += f"   {step.get('description', '')}\n"
                if 'command' in step:
                    result += f"   Command: {step['command']}\n"
                if 'explanation' in step:
                    result += f"   Why: {step['explanation']}\n"
                result += "\n"
            else:
                result += f"{i}. {step}\n"

        return result

    def explain_concept(self, concept_name: str) -> str:
        """Explain a specific RO server concept"""
        if concept_name not in self.knowledge['learning_concepts']:
            available_concepts = list(self.knowledge['learning_concepts'].keys())
            return f"Available concepts: {', '.join(available_concepts)}"

        concept = self.knowledge['learning_concepts'][concept_name]

        result = f"Concept: {concept['title']}\n"
        result += f"Description: {concept.get('description', '')}\n\n"
        result += concept.get('content', '')

        return result

    def get_next_step(self) -> str:
        """Get the next step in current tutorial (placeholder for progress tracking)"""
        return "Progress tracking feature coming soon! For now, use 'ro_agent learn tutorial <level>' to access specific tutorials."

    def get_progress(self) -> str:
        """Get learning progress (placeholder for progress tracking)"""
        return """Learning Progress Tracking

Current Status: Not yet implemented
Planned Features:
- Track completed tutorials
- Mark learning objectives as complete
- Provide personalized recommendations
- Generate progress certificates

For now, you can manually track your progress by completing tutorials in order:
1. beginner -> intermediate -> advanced
2. Or focus on specific areas like scripting or content creation

Use 'ro_agent learn tutorial <level>' to start learning!"""

    def get_available_learning_resources(self) -> str:
        """Get overview of all available learning resources"""
        result = "Available Learning Resources:\n\n"

        result += "Learning Paths:\n"
        for path_name, steps in self.knowledge['learning_paths'].items():
            result += f"- {path_name.replace('_', ' ').title()}: {len(steps)} modules\n"
        result += "\n"

        result += "Tutorials:\n"
        for level, tutorial in self.knowledge['tutorials'].items():
            result += f"- {level.title()}: {tutorial['title']}\n"
        result += "\n"

        result += "Concepts:\n"
        for concept_name, concept in self.knowledge['learning_concepts'].items():
            result += f"- {concept_name.replace('_', ' ').title()}: {concept['title']}\n"
        result += "\n"

        result += "Quick Start Commands:\n"
        result += "- ro_agent learn path server_admin    # Complete server administration\n"
        result += "- ro_agent learn tutorial beginner     # Start with basics\n"
        result += "- ro_agent learn concept scripting_fundamentals  # Learn RO scripting\n"

        return result
    
    def _load_architecture_cache(self) -> Dict:
        """Load architecture analysis cache for enhanced responses"""
        try:
            cache_file = self.cache_dir / "rathena_architecture.yml"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load architecture cache: {e}")
        return {}
    
    def get_architecture_info(self, component: str = None) -> str:
        """Get rAthena architecture information"""
        if not self.architecture_data:
            return "Architecture data not loaded. Run analysis first."
        
        if component:
            # Get specific component info
            servers = self.architecture_data.get('architecture', {}).get('servers', {})
            if component in servers:
                info = servers[component]
                result = f"**{component.replace('_', ' ').title()}**\n"
                result += f"Purpose: {info.get('purpose', 'Not specified')}\n"
                result += f"Port: {info.get('port', 'Not specified')}\n"
                result += f"Source: {info.get('source', 'Not specified')}\n"
                result += f"Config: {info.get('config', 'Not specified')}\n"
                if 'key_files' in info:
                    result += "Key Files:\n"
                    for file in info['key_files']:
                        result += f"• {file}\n"
                return result
            else:
                available = list(servers.keys())
                return f"Available components: {', '.join(available)}"
        
        # Return general architecture overview
        result = "**rAthena Server Architecture**\n\n"
        
        servers = self.architecture_data.get('architecture', {}).get('servers', {})
        result += "**Server Components:**\n"
        for name, info in servers.items():
            result += f"• {name.replace('_', ' ').title()}: {info.get('purpose', 'No description')}\n"
        
        flow = self.architecture_data.get('architecture', {}).get('communication_flow', '')
        if flow:
            result += f"\n**Communication Flow:**\n{flow}\n"
        
        opt_targets = self.architecture_data.get('optimization_targets', {})
        if opt_targets:
            result += "\n**Optimization Opportunities:**\n"
            for target, info in opt_targets.items():
                result += f"• {target.replace('_', ' ').title()}: {info.get('current', 'Unknown')} → {', '.join(info.get('potential', []))}\n"
        
        return result
    
    def get_performance_guide(self) -> str:
        """Get performance optimization guide based on analysis"""
        if not self.architecture_data:
            return "Performance data not loaded. Run analysis first."
        
        result = "**rAthena Performance Optimization Guide**\n\n"
        
        cache_system = self.architecture_data.get('cache_system', {})
        if cache_system:
            result += "**Caching Strategy:**\n"
            levels = cache_system.get('levels', {})
            for level, desc in levels.items():
                result += f"• {level.replace('_', ' ').title()}: {desc}\n"
            
            result += "\n**Cache Candidates:**\n"
            candidates = cache_system.get('candidates', [])
            for candidate in candidates:
                result += f"• {candidate}\n"
        
        monitoring = self.architecture_data.get('performance_monitoring', {})
        if monitoring:
            result += "\n**Performance Monitoring:**\n"
            metrics = monitoring.get('metrics', [])
            for metric in metrics:
                result += f"• {metric}\n"
        
        return result
    
    def get_branch_strategy(self) -> str:
        """Get branch management strategy information"""
        if not self.architecture_data:
            return "Branch strategy data not loaded."
        
        strategy = self.architecture_data.get('branch_strategy', {})
        if not strategy:
            return "No branch strategy defined."
        
        result = "**Branch Management Strategy**\n\n"
        
        main = strategy.get('main_branch', {})
        chaos = strategy.get('chaos_branch', {})
        
        result += f"**Main Branch:**\n"
        result += f"• Purpose: {main.get('purpose', 'Not specified')}\n"
        result += f"• Updates: {main.get('updates', 'Not specified')}\n"
        result += f"• Protection: {main.get('protection', 'Not specified')}\n\n"
        
        result += f"**Chaos Branch:**\n"
        result += f"• Purpose: {chaos.get('purpose', 'Not specified')}\n"
        result += f"• Base: {chaos.get('base', 'Not specified')}\n"
        features = chaos.get('features', [])
        if features:
            result += "• Features:\n"
            for feature in features:
                result += f"  - {feature}\n"
        
        sync = strategy.get('sync_workflow', {})
        if sync:
            result += "\n**Sync Workflow:**\n"
            for step, desc in sync.items():
                result += f"• {step.replace('_', ' ').title()}: {desc}\n"
        
        return result