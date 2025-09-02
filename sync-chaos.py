#!/usr/bin/env python3
"""
Chaos Branch Synchronization Script
Automates the process of syncing upstream rAthena changes with the Chaos branch
while preserving custom modifications and optimizations.
"""

import os
import sys
import subprocess
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ChaosSync:
    """Main synchronization manager"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config = self._load_config()
        self.upstream_repo = "https://github.com/rathena/rathena.git"
        self.upstream_branch = "master"
        self.main_branch = "main"
        self.chaos_branch = "chaos"
        
        # Ensure we're in a git repository
        if not (self.repo_path / ".git").exists():
            raise RuntimeError("Not a git repository")
        
        os.chdir(self.repo_path)
    
    def _load_config(self) -> Dict:
        """Load synchronization configuration"""
        config_file = self.repo_path / "Ragnarok Online Agent" / "ANALYSIS_CACHE" / "branch_strategy.yml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        # Default configuration
        return {
            'sync_strategy': {
                'conflict_resolution': {
                    'priority_order': [
                        'Security fixes (always take upstream)',
                        'Performance optimizations (merge carefully)',
                        'Chaos custom features (maintain custom logic)',
                        'Code organization (prefer Chaos structure)'
                    ]
                }
            }
        }
    
    def run_git_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command and return the result"""
        try:
            result = subprocess.run(['git'] + command, 
                                  capture_output=True, 
                                  text=True, 
                                  check=check)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: git {' '.join(command)}")
            print(f"Error: {e.stderr}")
            if check:
                raise
            return e
    
    def get_current_branch(self) -> str:
        """Get the current branch name"""
        result = self.run_git_command(['branch', '--show-current'])
        return result.stdout.strip()
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists"""
        result = self.run_git_command(['branch', '--list', branch_name], check=False)
        return bool(result.stdout.strip())
    
    def setup_upstream(self) -> bool:
        """Setup upstream remote if not already configured"""
        # Check if upstream remote exists
        result = self.run_git_command(['remote'], check=False)
        remotes = result.stdout.strip().split('\n')
        
        if 'upstream' not in remotes:
            print("Adding upstream remote...")
            result = self.run_git_command(['remote', 'add', 'upstream', self.upstream_repo])
            if result.returncode != 0:
                print(f"Failed to add upstream remote: {result.stderr}")
                return False
        
        # Fetch upstream
        print("Fetching upstream changes...")
        result = self.run_git_command(['fetch', 'upstream'])
        if result.returncode != 0:
            print(f"Failed to fetch upstream: {result.stderr}")
            return False
        
        return True
    
    def get_upstream_commits(self, since_commit: Optional[str] = None) -> List[Dict]:
        """Get list of new upstream commits"""
        if since_commit:
            range_spec = f"{since_commit}..upstream/{self.upstream_branch}"
        else:
            # Get last 50 commits if no reference point
            range_spec = f"upstream/{self.upstream_branch}"
        
        result = self.run_git_command([
            'log', '--oneline', '--no-merges', '--max-count=50', range_spec
        ], check=False)
        
        if result.returncode != 0:
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    commits.append({
                        'hash': parts[0],
                        'message': parts[1],
                        'important': self._is_important_commit(parts[1])
                    })
        
        return commits
    
    def _is_important_commit(self, message: str) -> bool:
        """Check if a commit message indicates an important change"""
        important_keywords = [
            'breaking', 'security', 'critical', 'fix', 'database', 
            'config', 'api', 'compatibility', 'performance'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in important_keywords)
    
    def sync_main_branch(self, force: bool = False) -> bool:
        """Synchronize main branch with upstream"""
        print("=== Synchronizing main branch ===")
        
        # Ensure we have upstream configured
        if not self.setup_upstream():
            return False
        
        # Switch to main branch or create it
        if not self.branch_exists(self.main_branch):
            print(f"Creating {self.main_branch} branch from upstream...")
            result = self.run_git_command([
                'checkout', '-b', self.main_branch, f'upstream/{self.upstream_branch}'
            ])
            if result.returncode != 0:
                print(f"Failed to create {self.main_branch} branch")
                return False
        else:
            # Switch to main branch
            result = self.run_git_command(['checkout', self.main_branch])
            if result.returncode != 0:
                print(f"Failed to switch to {self.main_branch} branch")
                return False
        
        # Check if main is behind upstream
        result = self.run_git_command([
            'rev-list', '--count', f'HEAD..upstream/{self.upstream_branch}'
        ], check=False)
        
        if result.returncode == 0 and result.stdout.strip() != '0':
            commits_behind = int(result.stdout.strip())
            print(f"Main branch is {commits_behind} commits behind upstream")
            
            if not force and commits_behind > 100:
                print("Too many commits behind. Use --force to proceed.")
                return False
            
            # Fast-forward merge
            print("Fast-forwarding main branch...")
            result = self.run_git_command(['merge', '--ff-only', f'upstream/{self.upstream_branch}'])
            
            if result.returncode != 0:
                print("Cannot fast-forward main branch. Manual intervention required.")
                print("This suggests main branch has diverged from upstream.")
                return False
            
            print(f"Successfully updated main branch with {commits_behind} new commits")
        else:
            print("Main branch is up to date with upstream")
        
        return True
    
    def analyze_chaos_conflicts(self) -> Dict:
        """Analyze potential conflicts between Chaos and upstream changes"""
        print("=== Analyzing potential conflicts ===")
        
        # Get merge base
        result = self.run_git_command([
            'merge-base', self.chaos_branch, f'upstream/{self.upstream_branch}'
        ], check=False)
        
        if result.returncode != 0:
            return {'error': 'Could not find merge base'}
        
        merge_base = result.stdout.strip()
        
        # Simulate merge to detect conflicts
        result = self.run_git_command([
            'merge-tree', merge_base, self.chaos_branch, f'upstream/{self.upstream_branch}'
        ], check=False)
        
        analysis = {
            'merge_base': merge_base,
            'has_conflicts': False,
            'conflicted_files': [],
            'chaos_modified_files': [],
            'upstream_modified_files': [],
            'common_modified_files': []
        }
        
        if result.returncode == 0 and result.stdout:
            # Check for conflict markers
            if '<<<<<<< ' in result.stdout:
                analysis['has_conflicts'] = True
                
                # Extract conflicted files
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('+++') or line.startswith('---'):
                        file_path = line[4:].replace('a/', '').replace('b/', '')
                        if file_path not in analysis['conflicted_files']:
                            analysis['conflicted_files'].append(file_path)
        
        # Get files modified in each branch
        chaos_files = self.run_git_command([
            'diff', '--name-only', f'{merge_base}..{self.chaos_branch}'
        ], check=False)
        
        if chaos_files.returncode == 0:
            analysis['chaos_modified_files'] = chaos_files.stdout.strip().split('\n')
        
        upstream_files = self.run_git_command([
            'diff', '--name-only', f'{merge_base}..upstream/{self.upstream_branch}'
        ], check=False)
        
        if upstream_files.returncode == 0:
            analysis['upstream_modified_files'] = upstream_files.stdout.strip().split('\n')
        
        # Find commonly modified files
        chaos_set = set(analysis['chaos_modified_files'])
        upstream_set = set(analysis['upstream_modified_files'])
        analysis['common_modified_files'] = list(chaos_set & upstream_set)
        
        return analysis
    
    def sync_chaos_branch(self, strategy: str = 'merge') -> bool:
        """Synchronize Chaos branch with latest upstream changes"""
        print("=== Synchronizing Chaos branch ===")
        
        # Ensure main branch is up to date first
        if not self.sync_main_branch():
            print("Failed to update main branch. Aborting Chaos sync.")
            return False
        
        # Switch to Chaos branch
        if not self.branch_exists(self.chaos_branch):
            print(f"Chaos branch does not exist. Creating from main branch...")
            result = self.run_git_command(['checkout', '-b', self.chaos_branch, self.main_branch])
            if result.returncode != 0:
                print(f"Failed to create Chaos branch")
                return False
        else:
            result = self.run_git_command(['checkout', self.chaos_branch])
            if result.returncode != 0:
                print(f"Failed to switch to Chaos branch")
                return False
        
        # Analyze conflicts before attempting merge
        conflict_analysis = self.analyze_chaos_conflicts()
        
        if conflict_analysis.get('has_conflicts', False):
            print(f"⚠️  Conflicts detected in {len(conflict_analysis['conflicted_files'])} files")
            print("Conflicted files:")
            for file in conflict_analysis['conflicted_files']:
                print(f"  - {file}")
            
            print("\nThis requires manual resolution. Consider:")
            print("1. Creating a backup branch: git checkout -b chaos-backup")
            print("2. Manually resolving conflicts")
            print("3. Testing all Chaos features after merge")
            
            return False
        
        # Perform the sync based on strategy
        if strategy == 'merge':
            print(f"Merging main branch into Chaos...")
            result = self.run_git_command(['merge', self.main_branch, '-m', 
                f'Sync with upstream rAthena ({datetime.now().strftime("%Y-%m-%d")})'])
        elif strategy == 'rebase':
            print(f"Rebasing Chaos branch onto main...")
            result = self.run_git_command(['rebase', self.main_branch])
        else:
            print(f"Unknown strategy: {strategy}")
            return False
        
        if result.returncode != 0:
            print(f"Sync failed. You may need to resolve conflicts manually.")
            print("Check 'git status' for details.")
            return False
        
        print("✅ Chaos branch synchronized successfully!")
        
        # Validate Chaos-specific features
        return self.validate_chaos_features()
    
    def validate_chaos_features(self) -> bool:
        """Validate that Chaos-specific features are still working"""
        print("=== Validating Chaos features ===")
        
        try:
            # Test RO Agent functionality
            agent_path = self.repo_path / "Ragnarok Online Agent" / "src" / "cli.py"
            if agent_path.exists():
                result = subprocess.run([
                    sys.executable, str(agent_path), '--help'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    print("❌ RO Agent validation failed")
                    return False
            
            # Test cache manager
            cache_path = self.repo_path / "Ragnarok Online Agent" / "src" / "cache_manager.py"
            if cache_path.exists():
                test_script = '''
import sys
sys.path.insert(0, ".")
from cache_manager import CacheManager
from pathlib import Path

cache = CacheManager(Path("test_cache"))
cache.set("test", "validation", "success", 60)
result = cache.get("test", "validation")
assert result == "success", "Cache validation failed"
print("Cache validation passed")
'''
                
                result = subprocess.run([
                    sys.executable, '-c', test_script
                ], cwd=agent_path.parent, capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    print("❌ Cache manager validation failed")
                    print(result.stderr)
                    return False
            
            print("✅ Chaos features validated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def create_sync_report(self, commits: List[Dict], analysis: Dict) -> str:
        """Create a synchronization report"""
        report = f"""# Chaos Branch Sync Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Upstream Changes
- **New commits**: {len(commits)}
- **Important commits**: {sum(1 for c in commits if c['important'])}

## Conflict Analysis
- **Merge conflicts**: {'Yes' if analysis.get('has_conflicts') else 'No'}
- **Files modified in Chaos**: {len(analysis.get('chaos_modified_files', []))}
- **Files modified upstream**: {len(analysis.get('upstream_modified_files', []))}
- **Commonly modified files**: {len(analysis.get('common_modified_files', []))}

## Recent Upstream Commits
"""
        
        for commit in commits[:10]:  # Show latest 10 commits
            importance = " ⚠️" if commit['important'] else ""
            report += f"- `{commit['hash']}` {commit['message']}{importance}\n"
        
        if len(commits) > 10:
            report += f"... and {len(commits) - 10} more commits\n"
        
        if analysis.get('conflicted_files'):
            report += "\n## Conflicted Files\n"
            for file in analysis['conflicted_files']:
                report += f"- {file}\n"
        
        if analysis.get('common_modified_files'):
            report += "\n## Files Modified in Both Branches\n"
            for file in analysis['common_modified_files']:
                report += f"- {file}\n"
        
        return report
    
    def run_sync(self, strategy: str = 'merge', force: bool = False, 
                 dry_run: bool = False) -> bool:
        """Run the complete synchronization process"""
        print(f"🚀 Starting Chaos branch synchronization...")
        print(f"Strategy: {strategy}, Force: {force}, Dry run: {dry_run}")
        
        # Ensure clean working directory
        result = self.run_git_command(['status', '--porcelain'])
        if result.stdout.strip():
            print("❌ Working directory is not clean. Please commit or stash changes.")
            return False
        
        # Setup upstream
        if not self.setup_upstream():
            return False
        
        # Get upstream commits for reporting
        current_main_commit = None
        if self.branch_exists(self.main_branch):
            result = self.run_git_command(['rev-parse', self.main_branch], check=False)
            if result.returncode == 0:
                current_main_commit = result.stdout.strip()
        
        commits = self.get_upstream_commits(current_main_commit)
        
        if not commits:
            print("✅ No new upstream commits. Chaos branch is up to date.")
            return True
        
        print(f"📊 Found {len(commits)} new upstream commits")
        important_commits = [c for c in commits if c['important']]
        if important_commits:
            print(f"⚠️  {len(important_commits)} commits contain important changes")
        
        # Analyze conflicts
        analysis = self.analyze_chaos_conflicts()
        
        # Create and display report
        report = self.create_sync_report(commits, analysis)
        print("\n" + "="*50)
        print(report)
        print("="*50 + "\n")
        
        if dry_run:
            print("🔍 Dry run complete. No changes made.")
            return True
        
        # Check for conflicts
        if analysis.get('has_conflicts', False) and not force:
            print("❌ Conflicts detected. Use --force to proceed anyway (not recommended).")
            print("Consider resolving conflicts manually first.")
            return False
        
        # Perform synchronization
        success = self.sync_chaos_branch(strategy)
        
        if success:
            # Save sync report
            report_file = self.repo_path / "chaos-sync-report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"📝 Sync report saved to {report_file}")
            print("✅ Chaos branch synchronization completed successfully!")
        else:
            print("❌ Synchronization failed. Check the output above for details.")
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Synchronize Chaos branch with upstream rAthena')
    parser.add_argument('--strategy', choices=['merge', 'rebase'], default='merge',
                       help='Synchronization strategy')
    parser.add_argument('--force', action='store_true',
                       help='Force sync even with conflicts (use carefully)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--repo-path', default='.',
                       help='Path to the repository (default: current directory)')
    
    args = parser.parse_args()
    
    try:
        syncer = ChaosSync(args.repo_path)
        success = syncer.run_sync(args.strategy, args.force, args.dry_run)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Synchronization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Synchronization failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()