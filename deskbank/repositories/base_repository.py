"""
Base repository class providing common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic
import json
import os
from pathlib import Path

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository class."""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            data_file: Optional file path for data persistence
        """
        self._data: Dict[str, T] = {}
        self.data_file = data_file
        self._setup_data_directory()
        
        if data_file and os.path.exists(data_file):
            self.load_data()
    
    def _setup_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        if self.data_file:
            data_dir = Path(self.data_file).parent
            data_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def _serialize_item(self, item: T) -> dict:
        """Serialize an item to dictionary for storage."""
        pass
    
    @abstractmethod
    def _deserialize_item(self, data: dict) -> T:
        """Deserialize dictionary data to item."""
        pass
    
    @abstractmethod
    def _get_item_id(self, item: T) -> str:
        """Get unique identifier for an item."""
        pass
    
    def add(self, item: T) -> None:
        """
        Add an item to the repository.
        
        Args:
            item: Item to add
        """
        item_id = self._get_item_id(item)
        self._data[item_id] = item
        self.save_data()
    
    def get_by_id(self, item_id: str) -> Optional[T]:
        """
        Get an item by its ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Item if found, None otherwise
        """
        return self._data.get(item_id)
    
    def get_all(self) -> List[T]:
        """
        Get all items in the repository.
        
        Returns:
            List of all items
        """
        return list(self._data.values())
    
    def update(self, item: T) -> bool:
        """
        Update an existing item.
        
        Args:
            item: Item to update
            
        Returns:
            True if item was updated, False if not found
        """
        item_id = self._get_item_id(item)
        if item_id in self._data:
            self._data[item_id] = item
            self.save_data()
            return True
        return False
    
    def delete(self, item_id: str) -> bool:
        """
        Delete an item by ID.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if item was deleted, False if not found
        """
        if item_id in self._data:
            del self._data[item_id]
            self.save_data()
            return True
        return False
    
    def delete_item(self, item: T) -> bool:
        """
        Delete an item.
        
        Args:
            item: Item to delete
            
        Returns:
            True if item was deleted, False if not found
        """
        item_id = self._get_item_id(item)
        return self.delete(item_id)
    
    def exists(self, item_id: str) -> bool:
        """
        Check if an item exists.
        
        Args:
            item_id: ID to check
            
        Returns:
            True if item exists
        """
        return item_id in self._data
    
    def count(self) -> int:
        """
        Get the count of items in the repository.
        
        Returns:
            Number of items
        """
        return len(self._data)
    
    def clear(self) -> None:
        """Clear all items from the repository."""
        self._data.clear()
        self.save_data()
    
    def save_data(self) -> None:
        """Save data to file if data_file is specified."""
        if not self.data_file:
            return
        
        try:
            serialized_data = {
                item_id: self._serialize_item(item)
                for item_id, item in self._data.items()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(serialized_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save data to {self.data_file}: {e}")
    
    def load_data(self) -> None:
        """Load data from file if data_file is specified."""
        if not self.data_file or not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r') as f:
                serialized_data = json.load(f)
            
            self._data = {
                item_id: self._deserialize_item(data)
                for item_id, data in serialized_data.items()
            }
        except Exception as e:
            print(f"Warning: Failed to load data from {self.data_file}: {e}")
            self._data = {}
    
    def backup_data(self, backup_file: str) -> bool:
        """
        Create a backup of the current data.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            True if backup was successful
        """
        try:
            serialized_data = {
                item_id: self._serialize_item(item)
                for item_id, item in self._data.items()
            }
            
            with open(backup_file, 'w') as f:
                json.dump(serialized_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False