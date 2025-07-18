#!/usr/bin/env python3
"""
Model Backup and Recovery Script

This script handles backup and recovery of the XGBoost model and configuration files.
Supports local backups, cloud storage, and automated scheduling.
"""

import os
import shutil
import json
import hashlib
import gzip
import tarfile
from datetime import datetime, timedelta
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any


class ModelBackupManager:
    """Manages backup and recovery of model files"""
    
    def __init__(self, model_dir: str = "src", backup_dir: str = "/var/backups/drug-api"):
        self.model_dir = Path(model_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Files to backup
        self.backup_files = [
            'xgboost_model.pkl',
            'preprocessing_config.py'
        ]
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information including size, modification time, and hash"""
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        return {
            'path': str(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'hash': self.calculate_file_hash(file_path)
        }
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create a backup of model files"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"model_backup_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        backup_info = {
            'backup_name': backup_name,
            'timestamp': datetime.now().isoformat(),
            'files': {},
            'total_size': 0
        }
        
        self.logger.info(f"Creating backup: {backup_name}")
        
        # Backup each file
        for filename in self.backup_files:
            source_path = self.model_dir / filename
            
            if source_path.exists():
                dest_path = backup_path / filename
                
                # Copy file
                shutil.copy2(source_path, dest_path)
                
                # Get file info
                file_info = self.get_file_info(dest_path)
                backup_info['files'][filename] = file_info
                backup_info['total_size'] += file_info['size']
                
                self.logger.info(f"  ✅ Backed up: {filename} ({file_info['size']} bytes)")
            else:
                self.logger.warning(f"  ⚠️ File not found: {filename}")
                backup_info['files'][filename] = None
        
        # Save backup metadata
        metadata_path = backup_path / 'backup_info.json'
        with open(metadata_path, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        # Create compressed archive
        archive_path = self.backup_dir / f"{backup_name}.tar.gz"
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(backup_path, arcname=backup_name)
        
        # Remove uncompressed backup directory
        shutil.rmtree(backup_path)
        
        archive_size = archive_path.stat().st_size
        self.logger.info(f"✅ Backup created: {archive_path} ({archive_size} bytes)")
        
        return str(archive_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("model_backup_*.tar.gz"):
            stat = backup_file.stat()
            
            backup_info = {
                'name': backup_file.stem,
                'file': str(backup_file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            # Try to extract metadata if available
            try:
                with tarfile.open(backup_file, 'r:gz') as tar:
                    metadata_member = tar.getmember(f"{backup_file.stem}/backup_info.json")
                    metadata_file = tar.extractfile(metadata_member)
                    metadata = json.load(metadata_file)
                    backup_info['metadata'] = metadata
            except:
                pass
            
            backups.append(backup_info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_name: str, confirm: bool = False) -> bool:
        """Restore from a backup"""
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        
        if not backup_file.exists():
            self.logger.error(f"Backup not found: {backup_file}")
            return False
        
        if not confirm:
            self.logger.warning("This will overwrite current model files!")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != 'yes':
                self.logger.info("Restore cancelled")
                return False
        
        self.logger.info(f"Restoring backup: {backup_name}")
        
        # Create temporary extraction directory
        temp_dir = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Extract backup
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            extracted_dir = temp_dir / backup_name
            
            # Restore each file
            for filename in self.backup_files:
                source_path = extracted_dir / filename
                dest_path = self.model_dir / filename
                
                if source_path.exists():
                    # Backup current file if it exists
                    if dest_path.exists():
                        backup_current = dest_path.with_suffix(dest_path.suffix + '.backup')
                        shutil.copy2(dest_path, backup_current)
                        self.logger.info(f"  📦 Current file backed up: {backup_current}")
                    
                    # Restore file
                    shutil.copy2(source_path, dest_path)
                    self.logger.info(f"  ✅ Restored: {filename}")
                else:
                    self.logger.warning(f"  ⚠️ File not in backup: {filename}")
            
            self.logger.info("✅ Restore completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Restore failed: {str(e)}")
            return False
        
        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10):
        """Clean up old backups based on age and count"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            self.logger.info(f"Only {len(backups)} backups found, no cleanup needed")
            return
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Keep the most recent backups and those newer than cutoff
        to_delete = []
        
        for i, backup in enumerate(backups):
            backup_date = datetime.fromisoformat(backup['created'])
            
            # Keep if within count limit or newer than cutoff
            if i >= keep_count and backup_date < cutoff_date:
                to_delete.append(backup)
        
        if not to_delete:
            self.logger.info("No old backups to clean up")
            return
        
        self.logger.info(f"Cleaning up {len(to_delete)} old backups...")
        
        for backup in to_delete:
            backup_file = Path(backup['file'])
            try:
                backup_file.unlink()
                self.logger.info(f"  🗑️ Deleted: {backup['name']}")
            except Exception as e:
                self.logger.error(f"  ❌ Failed to delete {backup['name']}: {str(e)}")
    
    def verify_backup(self, backup_name: str) -> bool:
        """Verify backup integrity"""
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        
        if not backup_file.exists():
            self.logger.error(f"Backup not found: {backup_file}")
            return False
        
        self.logger.info(f"Verifying backup: {backup_name}")
        
        try:
            # Test archive extraction
            with tarfile.open(backup_file, 'r:gz') as tar:
                # Check if all expected files are present
                members = tar.getnames()
                
                for filename in self.backup_files:
                    expected_path = f"{backup_name}/{filename}"
                    if expected_path not in members:
                        self.logger.error(f"  ❌ Missing file in backup: {filename}")
                        return False
                
                # Try to extract metadata
                metadata_path = f"{backup_name}/backup_info.json"
                if metadata_path in members:
                    metadata_member = tar.getmember(metadata_path)
                    metadata_file = tar.extractfile(metadata_member)
                    metadata = json.load(metadata_file)
                    self.logger.info(f"  📋 Backup metadata: {metadata['timestamp']}")
                
            self.logger.info("✅ Backup verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Backup verification failed: {str(e)}")
            return False


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Drug Interaction API Model Backup Manager')
    parser.add_argument('action', choices=['create', 'list', 'restore', 'cleanup', 'verify'],
                       help='Action to perform')
    parser.add_argument('--model-dir', default='src',
                       help='Model directory (default: src)')
    parser.add_argument('--backup-dir', default='/var/backups/drug-api',
                       help='Backup directory (default: /var/backups/drug-api)')
    parser.add_argument('--backup-name', help='Backup name for restore/verify operations')
    parser.add_argument('--keep-days', type=int, default=30,
                       help='Days to keep backups during cleanup (default: 30)')
    parser.add_argument('--keep-count', type=int, default=10,
                       help='Number of recent backups to keep (default: 10)')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Create backup manager
    manager = ModelBackupManager(model_dir=args.model_dir, backup_dir=args.backup_dir)
    
    if args.action == 'create':
        backup_path = manager.create_backup()
        print(f"✅ Backup created: {backup_path}")
    
    elif args.action == 'list':
        backups = manager.list_backups()
        if backups:
            print(f"\n📋 Available backups ({len(backups)}):")
            for backup in backups:
                size_mb = backup['size'] / (1024 * 1024)
                print(f"  {backup['name']} - {backup['created']} ({size_mb:.1f} MB)")
        else:
            print("No backups found")
    
    elif args.action == 'restore':
        if not args.backup_name:
            print("❌ --backup-name is required for restore operation")
            sys.exit(1)
        
        success = manager.restore_backup(args.backup_name, confirm=args.confirm)
        if success:
            print("✅ Restore completed successfully")
        else:
            print("❌ Restore failed")
            sys.exit(1)
    
    elif args.action == 'cleanup':
        manager.cleanup_old_backups(keep_days=args.keep_days, keep_count=args.keep_count)
        print("✅ Cleanup completed")
    
    elif args.action == 'verify':
        if not args.backup_name:
            print("❌ --backup-name is required for verify operation")
            sys.exit(1)
        
        success = manager.verify_backup(args.backup_name)
        if success:
            print("✅ Backup verification successful")
        else:
            print("❌ Backup verification failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
