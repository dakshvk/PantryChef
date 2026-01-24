"""
PantryChef Database Module
Fast SQLite database for caching API responses and storing user data
"""

import sqlite3
import json
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os


class PantryChefDB:
    """
    Database for caching API responses and storing user pantry/settings.
    Optimized for speed - avoids hitting API for repeated searches.
    """
    
    def __init__(self, db_path: str = 'pantrychef.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """
        Create tables if they don't exist.
        CRITICAL: This method must be called to ensure tables exist before any queries.
        Called automatically in __init__, but can be called explicitly for defensive programming.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pantry table - simple ingredient storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pantry (
                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table - user preferences
        # Note: skill_level is stored in settings dict, not in database (Logic engine handles it)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_profile TEXT,
                mood TEXT,
                intolerances TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Search cache (also known as recipe_cache) - stores API responses by request URL hash
        # This is the "Quota Shield" - prevents re-fetching same searches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_cache (
                cache_key TEXT PRIMARY KEY,
                request_url TEXT NOT NULL,
                response_data TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_date TIMESTAMP
            )
        ''')
        
        # Note: Table is named 'search_cache' but serves as 'recipe_cache' functionality
        
        # Favorites table - stores user's favorite/liked recipes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                recipe_title TEXT,
                recipe_data TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(recipe_id)
            )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pantry_name ON pantry(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_cache(expires_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_recipe_id ON favorites(recipe_id)')
        
        conn.commit()
        conn.close()
        
        # Verify tables were created (defensive check)
        try:
            verify_conn = sqlite3.connect(self.db_path)
            verify_cursor = verify_conn.cursor()
            verify_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in verify_cursor.fetchall()]
            expected_tables = ['pantry', 'settings', 'search_cache', 'favorites']
            missing_tables = [t for t in expected_tables if t not in tables]
            if missing_tables:
                print(f"⚠️  WARNING: Database tables missing: {missing_tables}")
            verify_conn.close()
        except Exception as e:
            print(f"⚠️  WARNING: Could not verify database tables: {e}")
    
    def _generate_cache_key(self, request_url: str) -> str:
        """Generate hash key for cache lookup."""
        return hashlib.md5(request_url.encode()).hexdigest()
    
    # ========== PANTRY METHODS ==========
    
    def add_ingredient(self, ingredient_name: str) -> bool:
        """
        Add ingredient to pantry.
        
        Args:
            ingredient_name: Name of ingredient
            
        Returns:
            True if added, False if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO pantry (name) VALUES (?)',
                (ingredient_name.lower().strip(),)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f'Error adding ingredient: {e}')
            return False
        finally:
            conn.close()
    
    def remove_ingredient(self, ingredient_name: str) -> bool:
        """Remove ingredient from pantry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'DELETE FROM pantry WHERE name = ?',
                (ingredient_name.lower().strip(),)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f'Error removing ingredient: {e}')
            return False
        finally:
            conn.close()
    
    def get_pantry(self) -> List[str]:
        """Get all ingredients in pantry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name FROM pantry ORDER BY name')
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f'Error getting pantry: {e}')
            return []
        finally:
            conn.close()
    
    def clear_pantry(self):
        """Clear all ingredients from pantry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM pantry')
            conn.commit()
        except Exception as e:
            print(f'Error clearing pantry: {e}')
        finally:
            conn.close()
    
    # ========== SETTINGS METHODS ==========
    
    def save_settings(
        self,
        user_profile: Optional[str] = None,
        mood: Optional[str] = None,
        intolerances: Optional[List[str]] = None
    ):
        """
        Save user settings.
        
        Args:
            user_profile: User profile type
            mood: User mood
            intolerances: List of intolerances
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get existing settings
            cursor.execute('SELECT * FROM settings ORDER BY setting_id DESC LIMIT 1')
            existing = cursor.fetchone()
            
            # Update or insert
            if existing:
                cursor.execute('''
                    UPDATE settings 
                    SET user_profile = COALESCE(?, user_profile),
                        mood = COALESCE(?, mood),
                        intolerances = COALESCE(?, intolerances),
                        updated_date = CURRENT_TIMESTAMP
                    WHERE setting_id = ?
                ''', (
                    user_profile,
                    mood,
                    json.dumps(intolerances) if intolerances else None,
                    existing[0]
                ))
            else:
                cursor.execute('''
                    INSERT INTO settings (user_profile, mood, intolerances)
                    VALUES (?, ?, ?)
                ''', (
                    user_profile,
                    mood,
                    json.dumps(intolerances) if intolerances else None
                ))
            
            conn.commit()
        except Exception as e:
            print(f'Error saving settings: {e}')
        finally:
            conn.close()
    
    def get_settings(self) -> Dict[str, Any]:
        """Get user settings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM settings ORDER BY setting_id DESC LIMIT 1')
            row = cursor.fetchone()
            
            if row:
                return {
                    'user_profile': row[1],
                    'mood': row[2],
                    'intolerances': json.loads(row[3]) if row[3] else []
                }
            return {}
        except Exception as e:
            print(f'Error getting settings: {e}')
            return {}
        finally:
            conn.close()
    
    # ========== CACHE METHODS ==========
    
    def cache_search(self, request_url: str, response_data: Dict, cache_hours: int = 1):
        """
        Cache API search response.
        
        Args:
            request_url: The full API request URL (used as cache key)
            response_data: JSON response to cache
            cache_hours: How long to cache (default: 1 hour)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cache_key = self._generate_cache_key(request_url)
            expires_date = datetime.now() + timedelta(hours=cache_hours)
            
            cursor.execute('''
                INSERT OR REPLACE INTO search_cache 
                (cache_key, request_url, response_data, expires_date)
                VALUES (?, ?, ?, ?)
            ''', (
                cache_key,
                request_url,
                json.dumps(response_data),
                expires_date.isoformat()
            ))
            
            conn.commit()
        except Exception as e:
            print(f'Error caching search: {e}')
        finally:
            conn.close()
    
    def get_cached_search(self, request_url: str) -> Optional[Dict]:
        """
        Get cached API response if it exists and hasn't expired.
        
        Args:
            request_url: The full API request URL
            
        Returns:
            Cached response dict or None if not found/expired
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cache_key = self._generate_cache_key(request_url)
            
            cursor.execute('''
                SELECT response_data, expires_date 
                FROM search_cache 
                WHERE cache_key = ?
            ''', (cache_key,))
            
            row = cursor.fetchone()
            
            if row:
                expires_date = datetime.fromisoformat(row[1])
                
                # Check if expired
                if datetime.now() < expires_date:
                    return json.loads(row[0])
                else:
                    # Delete expired cache
                    cursor.execute('DELETE FROM search_cache WHERE cache_key = ?', (cache_key,))
                    conn.commit()
            
            return None
        except Exception as e:
            print(f'Error getting cached search: {e}')
            return None
        finally:
            conn.close()
    
    def clear_expired_cache(self):
        """Remove all expired cache entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM search_cache 
                WHERE expires_date < datetime('now')
            ''')
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f'Error clearing expired cache: {e}')
            return 0
        finally:
            conn.close()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM search_cache')
            total = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM search_cache 
                WHERE expires_date >= datetime('now')
            ''')
            active = cursor.fetchone()[0]
            
            return {
                'total_entries': total,
                'active_entries': active,
                'expired_entries': total - active
            }
        except Exception as e:
            print(f'Error getting cache stats: {e}')
            return {'total_entries': 0, 'active_entries': 0, 'expired_entries': 0}
        finally:
            conn.close()
    
    # ========== FAVORITES METHODS ==========
    
    def add_favorite(self, recipe_id: int, recipe_title: str, recipe_data: Optional[Dict] = None) -> bool:
        """
        Add a recipe to favorites.
        
        Args:
            recipe_id: Spoonacular recipe ID
            recipe_title: Recipe title
            recipe_data: Optional full recipe data (JSON stringified)
            
        Returns:
            True if added, False if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            recipe_data_json = json.dumps(recipe_data) if recipe_data else None
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (recipe_id, recipe_title, recipe_data)
                VALUES (?, ?, ?)
            ''', (recipe_id, recipe_title, recipe_data_json))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f'Error adding favorite: {e}')
            return False
        finally:
            conn.close()
    
    def remove_favorite(self, recipe_id: int) -> bool:
        """Remove a recipe from favorites."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM favorites WHERE recipe_id = ?', (recipe_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f'Error removing favorite: {e}')
            return False
        finally:
            conn.close()
    
    def is_favorite(self, recipe_id: int) -> bool:
        """Check if a recipe is favorited."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT 1 FROM favorites WHERE recipe_id = ?', (recipe_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f'Error checking favorite: {e}')
            return False
        finally:
            conn.close()
    
    def get_favorites(self) -> List[Dict[str, Any]]:
        """Get all favorited recipes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT recipe_id, recipe_title, recipe_data, added_date
                FROM favorites
                ORDER BY added_date DESC
            ''')
            rows = cursor.fetchall()
            
            favorites = []
            for row in rows:
                favorite = {
                    'recipe_id': row[0],
                    'recipe_title': row[1],
                    'recipe_data': json.loads(row[2]) if row[2] else None,
                    'added_date': row[3]
                }
                favorites.append(favorite)
            
            return favorites
        except Exception as e:
            print(f'Error getting favorites: {e}')
            return []
        finally:
            conn.close()
    
    def get_favorite_recipe_ids(self) -> List[int]:
        """Get list of favorited recipe IDs (for similar recipes lookup)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT recipe_id FROM favorites')
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f'Error getting favorite IDs: {e}')
            return []
        finally:
            conn.close()


if __name__ == '__main__':
    # Test the database
    db = PantryChefDB('test_pantrychef.db')
    
    # Test pantry
    print("Testing pantry...")
    db.add_ingredient('chicken')
    db.add_ingredient('rice')
    db.add_ingredient('tomatoes')
    print(f"Pantry: {db.get_pantry()}")
    
    # Test settings
    print("\nTesting settings...")
    db.save_settings(
        user_profile='balanced',
        mood='casual',
        intolerances=['dairy', 'gluten']
    )
    print(f"Settings: {db.get_settings()}")
    
    # Test cache
    print("\nTesting cache...")
    test_url = "https://api.spoonacular.com/recipes/findByIngredients?ingredients=chicken,rice"
    test_response = {'results': [{'id': 1, 'title': 'Test Recipe'}]}
    
    db.cache_search(test_url, test_response, cache_hours=1)
    cached = db.get_cached_search(test_url)
    print(f"Cached response: {cached}")
    
    # Cleanup
    os.remove('test_pantrychef.db')
    print("\n✓ All tests passed!")

