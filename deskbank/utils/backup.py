"""
Backup utilities for DeskBank application.
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class BackupManager:
    """Backup and restore utilities."""
    
    def __init__(self, backup_directory: str):
        """
        Initialize backup manager.
        
        Args:
            backup_directory: Directory to store backups
        """
        self.backup_directory = Path(backup_directory)
        self.backup_directory.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, data_directory: str, 
                     backup_name: Optional[str] = None) -> str:
        """
        Create a backup of the data directory.
        
        Args:
            data_directory: Directory containing data files
            backup_name: Optional backup name (will generate if not provided)
            
        Returns:
            Path to created backup file
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"deskbank_backup_{timestamp}"
        
        backup_file = self.backup_directory / f"{backup_name}.zip"
        
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                data_path = Path(data_directory)
                
                # Add all files from data directory
                for file_path in data_path.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path for the archive
                        arc_name = file_path.relative_to(data_path)
                        zipf.write(file_path, arc_name)
                
                # Add metadata
                metadata = {
                    "backup_date": datetime.now().isoformat(),
                    "backup_name": backup_name,
                    "source_directory": str(data_path),
                    "deskbank_version": "1.0.0",
                    "backup_type": "full"
                }
                
                zipf.writestr("backup_metadata.json", 
                            json.dumps(metadata, indent=2))
            
            return str(backup_file)
        
        except Exception as e:
            # Clean up failed backup file
            if backup_file.exists():
                backup_file.unlink()
            raise Exception(f"Backup creation failed: {str(e)}")
    
    def restore_backup(self, backup_file: str, 
                      restore_directory: str) -> bool:
        """
        Restore data from backup file.
        
        Args:
            backup_file: Path to backup file
            restore_directory: Directory to restore data to
            
        Returns:
            True if restore was successful
        """
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            restore_path = Path(restore_directory)
            
            # Create backup of existing data before restore
            if restore_path.exists():
                existing_backup = self._create_existing_data_backup(restore_path)
                print(f"Created backup of existing data: {existing_backup}")
            
            # Clear restore directory
            if restore_path.exists():
                shutil.rmtree(restore_path)
            restore_path.mkdir(parents=True)
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)
            
            # Verify metadata
            metadata_file = restore_path / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"Restored backup from: {metadata.get('backup_date', 'Unknown')}")
                # Remove metadata file from restored data
                metadata_file.unlink()
            
            return True
        
        except Exception as e:
            print(f"Restore failed: {str(e)}")
            return False
    
    def _create_existing_data_backup(self, data_directory: Path) -> str:
        """Create backup of existing data before restore."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_restore_backup_{timestamp}"
        return self.create_backup(str(data_directory), backup_name)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_file in self.backup_directory.glob("*.zip"):
            try:
                backup_info = {
                    "filename": backup_file.name,
                    "filepath": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "created": datetime.fromtimestamp(backup_file.stat().st_mtime),
                    "metadata": None
                }
                
                # Try to read metadata from backup
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        if "backup_metadata.json" in zipf.namelist():
                            metadata_content = zipf.read("backup_metadata.json")
                            backup_info["metadata"] = json.loads(metadata_content)
                except:
                    pass  # Ignore metadata read errors
                
                backups.append(backup_info)
            
            except Exception:
                continue  # Skip corrupted backup files
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def delete_backup(self, backup_filename: str) -> bool:
        """
        Delete a backup file.
        
        Args:
            backup_filename: Name of backup file to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            backup_file = self.backup_directory / backup_filename
            if backup_file.exists():
                backup_file.unlink()
                return True
            return False
        except Exception:
            return False
    
    def cleanup_old_backups(self, max_backups: int = 10) -> List[str]:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            max_backups: Maximum number of backups to keep
            
        Returns:
            List of deleted backup filenames
        """
        backups = self.list_backups()
        deleted_files = []
        
        if len(backups) > max_backups:
            # Delete oldest backups
            for backup in backups[max_backups:]:
                if self.delete_backup(backup["filename"]):
                    deleted_files.append(backup["filename"])
        
        return deleted_files
    
    def verify_backup(self, backup_file: str) -> Dict[str, Any]:
        """
        Verify backup file integrity.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            Dictionary with verification results
        """
        result = {
            "is_valid": False,
            "error": None,
            "metadata": None,
            "file_count": 0,
            "total_size": 0
        }
        
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                result["error"] = "Backup file not found"
                return result
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Test archive integrity
                zipf.testzip()
                
                # Get file count and total size
                result["file_count"] = len(zipf.namelist())
                result["total_size"] = sum(info.file_size for info in zipf.infolist())
                
                # Read metadata if available
                if "backup_metadata.json" in zipf.namelist():
                    metadata_content = zipf.read("backup_metadata.json")
                    result["metadata"] = json.loads(metadata_content)
                
                result["is_valid"] = True
        
        except zipfile.BadZipFile:
            result["error"] = "Corrupted backup file"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_backup_size(self, backup_file: str) -> int:
        """
        Get backup file size in bytes.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            File size in bytes
        """
        try:
            return Path(backup_file).stat().st_size
        except Exception:
            return 0
    
    def format_backup_size(self, size_bytes: int) -> str:
        """
        Format backup size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def export_backup_report(self, output_file: str) -> bool:
        """
        Export backup report to file.
        
        Args:
            output_file: Path to output report file
            
        Returns:
            True if export was successful
        """
        try:
            backups = self.list_backups()
            
            report = {
                "report_date": datetime.now().isoformat(),
                "backup_directory": str(self.backup_directory),
                "total_backups": len(backups),
                "total_size": sum(backup["size"] for backup in backups),
                "backups": []
            }
            
            for backup in backups:
                backup_info = {
                    "filename": backup["filename"],
                    "size": backup["size"],
                    "size_formatted": self.format_backup_size(backup["size"]),
                    "created": backup["created"].isoformat(),
                    "metadata": backup["metadata"]
                }
                report["backups"].append(backup_info)
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
        
        except Exception:
            return False
    
    def schedule_automatic_backup(self, data_directory: str, 
                                interval_hours: int = 24) -> None:
        """
        Schedule automatic backup (placeholder for future implementation).
        
        Args:
            data_directory: Directory to backup
            interval_hours: Backup interval in hours
        """
        # This would integrate with system scheduler (cron, Task Scheduler, etc.)
        print(f"Automatic backup scheduled every {interval_hours} hours")
        print(f"Data directory: {data_directory}")
        print(f"Backup directory: {self.backup_directory}")
        print("Note: Automatic scheduling requires system-level integration")