"""
Database manager for CRUD operations on residents, visits, and medical history.
Handles all database interactions with proper error handling and transaction management.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd


class DatabaseManager:
    """Manages all database operations for the health tracking system."""
    
    def __init__(self, db_path: str = "health_tracking.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    # ==================== RESIDENTS OPERATIONS ====================
    
    def add_resident(self, resident_data: Dict) -> bool:
        """
        Add a new resident to the database.
        
        Args:
            resident_data: Dictionary with resident information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO residents (unique_id, name, age, gender, address, phone, 
                                     village_area, photo_path, registration_date, registered_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resident_data['unique_id'],
                resident_data['name'],
                resident_data.get('age'),
                resident_data.get('gender'),
                resident_data.get('address'),
                resident_data.get('phone'),
                resident_data.get('village_area'),
                resident_data.get('photo_path'),
                resident_data['registration_date'],
                resident_data['registered_by']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding resident: {e}")
            return False
    
    def get_resident(self, unique_id: str) -> Optional[Dict]:
        """
        Get resident by unique ID.
        
        Args:
            unique_id: Resident's unique ID
            
        Returns:
            Dictionary with resident data or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM residents WHERE unique_id = ?", (unique_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error getting resident: {e}")
            return None
    
    def get_all_residents(self) -> List[Dict]:
        """
        Get all residents.
        
        Returns:
            List of dictionaries with resident data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM residents ORDER BY registration_date DESC")
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting all residents: {e}")
            return []
    
    def search_residents(self, search_term: str) -> List[Dict]:
        """
        Search residents by name or unique ID.
        
        Args:
            search_term: Search string
            
        Returns:
            List of matching residents
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT * FROM residents 
                WHERE name LIKE ? OR unique_id LIKE ?
                ORDER BY name
            """, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching residents: {e}")
            return []
    
    def filter_residents(self, filters: Dict) -> List[Dict]:
        """
        Filter residents by multiple criteria.
        
        Args:
            filters: Dictionary with filter criteria (gender, age_min, age_max, village_area)
            
        Returns:
            List of matching residents
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM residents WHERE 1=1"
            params = []
            
            if filters.get('gender'):
                query += " AND gender = ?"
                params.append(filters['gender'])
            
            if filters.get('age_min') is not None:
                query += " AND age >= ?"
                params.append(filters['age_min'])
            
            if filters.get('age_max') is not None:
                query += " AND age <= ?"
                params.append(filters['age_max'])
            
            if filters.get('village_area'):
                query += " AND village_area = ?"
                params.append(filters['village_area'])
            
            query += " ORDER BY name"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error filtering residents: {e}")
            return []
    
    def resident_exists(self, unique_id: str) -> bool:
        """
        Check if resident with given ID exists.
        
        Args:
            unique_id: Resident's unique ID
            
        Returns:
            True if exists, False otherwise
        """
        resident = self.get_resident(unique_id)
        return resident is not None
    
    def get_resident_count(self) -> int:
        """Get total number of residents."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM residents")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting resident count: {e}")
            return 0
    
    # ==================== VISITS OPERATIONS ====================
    
    def add_visit(self, visit_data: Dict) -> bool:
        """
        Add a new visit record.
        
        Args:
            visit_data: Dictionary with visit information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO visits (resident_id, visit_date, visit_time, health_worker,
                                  bp_systolic, bp_diastolic, temperature, pulse,
                                  weight, height, bmi, spo2, complaints, observations, photo_paths)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                visit_data['resident_id'],
                visit_data['visit_date'],
                visit_data['visit_time'],
                visit_data['health_worker'],
                visit_data.get('bp_systolic'),
                visit_data.get('bp_diastolic'),
                visit_data.get('temperature'),
                visit_data.get('pulse'),
                visit_data.get('weight'),
                visit_data.get('height'),
                visit_data.get('bmi'),
                visit_data.get('spo2'),
                visit_data.get('complaints'),
                visit_data.get('observations'),
                visit_data.get('photo_paths')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding visit: {e}")
            return False
    
    def get_resident_visits(self, resident_id: str) -> List[Dict]:
        """
        Get all visits for a resident.
        
        Args:
            resident_id: Resident's unique ID
            
        Returns:
            List of visit records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM visits 
                WHERE resident_id = ?
                ORDER BY visit_date DESC, visit_time DESC
            """, (resident_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting resident visits: {e}")
            return []
    
    def get_all_visits(self) -> List[Dict]:
        """Get all visits."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM visits ORDER BY visit_date DESC, visit_time DESC")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting all visits: {e}")
            return []
    
    def get_visit_count(self) -> int:
        """Get total number of visits."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM visits")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting visit count: {e}")
            return 0
    
    def get_visits_by_health_worker(self) -> List[Tuple[str, int]]:
        """
        Get visit counts grouped by health worker.
        
        Returns:
            List of tuples (health_worker, count)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT health_worker, COUNT(*) as count
                FROM visits
                GROUP BY health_worker
                ORDER BY count DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            return [(row[0], row[1]) for row in rows]
        except Exception as e:
            print(f"Error getting visits by health worker: {e}")
            return []
    
    def get_recent_visits(self, limit: int = 10) -> List[Dict]:
        """
        Get recent visits.
        
        Args:
            limit: Maximum number of visits to return
            
        Returns:
            List of recent visit records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.*, r.name as resident_name
                FROM visits v
                JOIN residents r ON v.resident_id = r.unique_id
                ORDER BY v.visit_date DESC, v.visit_time DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting recent visits: {e}")
            return []
    
    # ==================== MEDICAL HISTORY OPERATIONS ====================
    
    def add_or_update_medical_history(self, history_data: Dict) -> bool:
        """
        Add or update medical history for a resident.
        
        Args:
            history_data: Dictionary with medical history information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if history already exists
            cursor.execute("SELECT history_id FROM medical_history WHERE resident_id = ?",
                         (history_data['resident_id'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE medical_history
                    SET chronic_conditions = ?, past_diagnoses = ?, current_medications = ?,
                        allergies = ?, family_history = ?, notes = ?, 
                        last_updated = ?, updated_by = ?
                    WHERE resident_id = ?
                """, (
                    history_data.get('chronic_conditions'),
                    history_data.get('past_diagnoses'),
                    history_data.get('current_medications'),
                    history_data.get('allergies'),
                    history_data.get('family_history'),
                    history_data.get('notes'),
                    history_data['last_updated'],
                    history_data['updated_by'],
                    history_data['resident_id']
                ))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO medical_history (resident_id, chronic_conditions, past_diagnoses,
                                               current_medications, allergies, family_history,
                                               notes, last_updated, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    history_data['resident_id'],
                    history_data.get('chronic_conditions'),
                    history_data.get('past_diagnoses'),
                    history_data.get('current_medications'),
                    history_data.get('allergies'),
                    history_data.get('family_history'),
                    history_data.get('notes'),
                    history_data['last_updated'],
                    history_data['updated_by']
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding/updating medical history: {e}")
            return False
    
    def get_medical_history(self, resident_id: str) -> Optional[Dict]:
        """
        Get medical history for a resident.
        
        Args:
            resident_id: Resident's unique ID
            
        Returns:
            Dictionary with medical history or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM medical_history WHERE resident_id = ?", (resident_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error getting medical history: {e}")
            return None
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_demographics_summary(self) -> Dict:
        """
        Get demographics summary.
        
        Returns:
            Dictionary with demographic statistics
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Gender distribution
            cursor.execute("""
                SELECT gender, COUNT(*) as count
                FROM residents
                WHERE gender IS NOT NULL
                GROUP BY gender
            """)
            gender_dist = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Age groups
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN age < 18 THEN 'Child (0-17)'
                        WHEN age >= 18 AND age < 40 THEN 'Adult (18-39)'
                        WHEN age >= 40 AND age < 60 THEN 'Middle Age (40-59)'
                        ELSE 'Senior (60+)'
                    END as age_group,
                    COUNT(*) as count
                FROM residents
                WHERE age IS NOT NULL
                GROUP BY age_group
            """)
            age_groups = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'gender_distribution': gender_dist,
                'age_groups': age_groups
            }
        except Exception as e:
            print(f"Error getting demographics summary: {e}")
            return {'gender_distribution': {}, 'age_groups': {}}
    
    def get_monthly_trends(self) -> Dict:
        """
        Get monthly registration and visit trends.
        
        Returns:
            Dictionary with monthly trends
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Monthly registrations
            cursor.execute("""
                SELECT strftime('%Y-%m', registration_date) as month, COUNT(*) as count
                FROM residents
                WHERE registration_date IS NOT NULL
                GROUP BY month
                ORDER BY month
            """)
            registrations = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Monthly visits
            cursor.execute("""
                SELECT strftime('%Y-%m', visit_date) as month, COUNT(*) as count
                FROM visits
                WHERE visit_date IS NOT NULL
                GROUP BY month
                ORDER BY month
            """)
            visits = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'monthly_registrations': registrations,
                'monthly_visits': visits
            }
        except Exception as e:
            print(f"Error getting monthly trends: {e}")
            return {'monthly_registrations': {}, 'monthly_visits': {}}
    
    # ==================== EXPORT OPERATIONS ====================
    
    def export_residents_to_df(self) -> pd.DataFrame:
        """Export all residents to pandas DataFrame."""
        residents = self.get_all_residents()
        return pd.DataFrame(residents)
    
    def export_visits_to_df(self, resident_id: Optional[str] = None) -> pd.DataFrame:
        """
        Export visits to pandas DataFrame.
        
        Args:
            resident_id: Optional resident ID to filter visits
            
        Returns:
            DataFrame with visit data
        """
        if resident_id:
            visits = self.get_resident_visits(resident_id)
        else:
            visits = self.get_all_visits()
        return pd.DataFrame(visits)
    
    def export_medical_history_to_df(self) -> pd.DataFrame:
        """Export all medical histories to pandas DataFrame."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medical_history")
            rows = cursor.fetchall()
            conn.close()
            histories = [dict(row) for row in rows]
            return pd.DataFrame(histories)
        except Exception as e:
            print(f"Error exporting medical history: {e}")
            return pd.DataFrame()
