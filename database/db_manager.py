"""
Database manager for CRUD operations on residents, visits, and medical history.
Handles all database interactions with proper error handling and transaction management.
"""

import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
from supabase import create_client, Client
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Clinical thresholds and constants
MALNUTRITION_Z_SCORE_THRESHOLD = -2  # WHO standard for malnutrition
PREGNANCY_DURATION_DAYS = 280  # Approximate duration of pregnancy
HYPERTENSION_THRESHOLD_SYSTOLIC = 140  # Systolic BP threshold for hypertension (mmHg)


class DatabaseManager:
    """Manages all database operations for the health tracking system."""
    
    def __init__(self):
        """
        Initialize database manager with Supabase client.
        Credentials are loaded from Streamlit secrets or environment variables.
        """
        # Try to get credentials from Streamlit secrets first, then env vars
        try:
            supabase_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
            supabase_key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
        except (AttributeError, KeyError):
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY.")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def _convert_row_to_dict(self, data) -> Optional[Dict]:
        """Convert Supabase response to dictionary."""
        if data and len(data) > 0:
            return data[0]
        return None
    
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
            data = {
                'unique_id': resident_data['unique_id'],
                'name': resident_data['name'],
                'age': resident_data.get('age'),
                'gender': resident_data.get('gender'),
                'address': resident_data.get('address'),
                'phone': resident_data.get('phone'),
                'village_area': resident_data.get('village_area'),
                'photo_path': resident_data.get('photo_path'),
                'registration_date': resident_data['registration_date'],
                'registered_by': resident_data['registered_by']
            }
            
            self.supabase.table('residents').insert(data).execute()
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
            response = self.supabase.table('residents').select('*').eq('unique_id', unique_id).execute()
            return self._convert_row_to_dict(response.data)
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
            response = self.supabase.table('residents').select('*').order('registration_date', desc=True).execute()
            return response.data if response.data else []
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
            # Supabase's .ilike operator is parameterized and safe from SQL injection
            # Basic sanitization: limit length and remove null bytes
            search_term = search_term[:100].replace('\x00', '')
            
            # Supabase full-text search on name and unique_id
            response = self.supabase.table('residents').select('*').or_(
                f'name.ilike.%{search_term}%,unique_id.ilike.%{search_term}%'
            ).order('name').execute()
            return response.data if response.data else []
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
            query = self.supabase.table('residents').select('*')
            
            if filters.get('gender'):
                query = query.eq('gender', filters['gender'])
            
            if filters.get('age_min') is not None:
                query = query.gte('age', filters['age_min'])
            
            if filters.get('age_max') is not None:
                query = query.lte('age', filters['age_max'])
            
            if filters.get('village_area'):
                query = query.eq('village_area', filters['village_area'])
            
            response = query.order('name').execute()
            return response.data if response.data else []
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
            response = self.supabase.table('residents').select('*', count='exact').execute()
            return response.count if response.count else 0
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
            data = {
                'resident_id': visit_data['resident_id'],
                'visit_date': visit_data['visit_date'],
                'visit_time': visit_data['visit_time'],
                'health_worker': visit_data['health_worker'],
                'bp_systolic': visit_data.get('bp_systolic'),
                'bp_diastolic': visit_data.get('bp_diastolic'),
                'temperature': visit_data.get('temperature'),
                'pulse': visit_data.get('pulse'),
                'weight': visit_data.get('weight'),
                'height': visit_data.get('height'),
                'bmi': visit_data.get('bmi'),
                'spo2': visit_data.get('spo2'),
                'complaints': visit_data.get('complaints'),
                'observations': visit_data.get('observations'),
                'photo_paths': visit_data.get('photo_paths')
            }
            
            self.supabase.table('visits').insert(data).execute()
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
            response = self.supabase.table('visits').select('*').eq(
                'resident_id', resident_id
            ).order('visit_date', desc=True).order('visit_time', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting resident visits: {e}")
            return []
    
    def get_all_visits(self) -> List[Dict]:
        """Get all visits."""
        try:
            response = self.supabase.table('visits').select('*').order(
                'visit_date', desc=True
            ).order('visit_time', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting all visits: {e}")
            return []
    
    def get_visit_count(self) -> int:
        """Get total number of visits."""
        try:
            response = self.supabase.table('visits').select('*', count='exact').execute()
            return response.count if response.count else 0
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
            # Supabase doesn't have native GROUP BY in select, so we fetch all and process
            response = self.supabase.table('visits').select('health_worker').execute()
            if not response.data:
                return []
            
            # Count occurrences manually
            counts = {}
            for visit in response.data:
                worker = visit.get('health_worker', 'Unknown')
                counts[worker] = counts.get(worker, 0) + 1
            
            # Sort by count descending
            return sorted(counts.items(), key=lambda x: x[1], reverse=True)
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
            # Get visits with JOIN-like behavior (we'll fetch separately and merge)
            # Note: The foreign key reference 'visits_resident_id_fkey' follows Supabase's
            # default naming convention. If your FK has a custom name, update this.
            response = self.supabase.table('visits').select(
                '*, residents!visits_resident_id_fkey(name)'
            ).order('visit_date', desc=True).order('visit_time', desc=True).limit(limit).execute()
            
            if response.data:
                # Flatten the nested resident data
                for visit in response.data:
                    if 'residents' in visit and visit['residents']:
                        visit['resident_name'] = visit['residents']['name']
                        del visit['residents']
                return response.data
            return []
        except Exception as e:
            print(f"Error getting recent visits: {e}")
            # Fallback: fetch without join if FK reference fails
            try:
                response = self.supabase.table('visits').select('*').order(
                    'visit_date', desc=True
                ).order('visit_time', desc=True).limit(limit).execute()
                return response.data if response.data else []
            except:
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
            # Check if history already exists
            response = self.supabase.table('medical_history').select('history_id').eq(
                'resident_id', history_data['resident_id']
            ).execute()
            
            data = {
                'chronic_conditions': history_data.get('chronic_conditions'),
                'past_diagnoses': history_data.get('past_diagnoses'),
                'current_medications': history_data.get('current_medications'),
                'allergies': history_data.get('allergies'),
                'family_history': history_data.get('family_history'),
                'notes': history_data.get('notes'),
                'last_updated': history_data['last_updated'],
                'updated_by': history_data['updated_by']
            }
            
            if response.data and len(response.data) > 0:
                # Update existing record
                self.supabase.table('medical_history').update(data).eq(
                    'resident_id', history_data['resident_id']
                ).execute()
            else:
                # Insert new record
                data['resident_id'] = history_data['resident_id']
                self.supabase.table('medical_history').insert(data).execute()
            
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
            response = self.supabase.table('medical_history').select('*').eq(
                'resident_id', resident_id
            ).execute()
            return self._convert_row_to_dict(response.data)
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
            # Gender distribution
            response = self.supabase.table('residents').select('gender').neq('gender', None).execute()
            gender_dist = {}
            if response.data:
                for row in response.data:
                    gender = row.get('gender', 'Unknown')
                    if gender:  # Additional check for empty strings
                        gender_dist[gender] = gender_dist.get(gender, 0) + 1
            
            # Age groups - fetch all ages and categorize
            response = self.supabase.table('residents').select('age').neq('age', None).execute()
            age_groups = {
                'Child (0-17)': 0,
                'Adult (18-39)': 0,
                'Middle Age (40-59)': 0,
                'Senior (60+)': 0
            }
            
            if response.data:
                for row in response.data:
                    age = row.get('age')
                    if age is not None:
                        if age < 18:
                            age_groups['Child (0-17)'] += 1
                        elif 18 <= age < 40:
                            age_groups['Adult (18-39)'] += 1
                        elif 40 <= age < 60:
                            age_groups['Middle Age (40-59)'] += 1
                        else:
                            age_groups['Senior (60+)'] += 1
            
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
            # Monthly registrations - fetch all dates and process
            response = self.supabase.table('residents').select('registration_date').neq(
                'registration_date', None
            ).execute()
            
            registrations = {}
            if response.data:
                for row in response.data:
                    date_str = row.get('registration_date', '')
                    if date_str:
                        # Extract year-month (format: YYYY-MM)
                        month = date_str[:7]
                        registrations[month] = registrations.get(month, 0) + 1
            
            # Monthly visits - fetch all dates and process
            response = self.supabase.table('visits').select('visit_date').neq(
                'visit_date', None
            ).execute()
            
            visits = {}
            if response.data:
                for row in response.data:
                    date_str = row.get('visit_date', '')
                    if date_str:
                        month = date_str[:7]
                        visits[month] = visits.get(month, 0) + 1
            
            return {
                'monthly_registrations': dict(sorted(registrations.items())),
                'monthly_visits': dict(sorted(visits.items()))
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
            response = self.supabase.table('medical_history').select('*').execute()
            histories = response.data if response.data else []
            return pd.DataFrame(histories)
        except Exception as e:
            print(f"Error exporting medical history: {e}")
            return pd.DataFrame()
    
    def export_growth_data(self) -> pd.DataFrame:
        """
        Export all growth monitoring data to pandas DataFrame.
        
        Returns:
            DataFrame with growth monitoring data including resident_id
        """
        try:
            response = self.supabase.table('growth_monitoring').select('*').order(
                'record_date', desc=True
            ).execute()
            growth_data = response.data if response.data else []
            return pd.DataFrame(growth_data)
        except Exception as e:
            print(f"Error exporting growth data: {e}")
            return pd.DataFrame()
    
    def export_maternal_data(self) -> pd.DataFrame:
        """
        Export all maternal health data to pandas DataFrame.
        
        Returns:
            DataFrame with maternal health data including resident_id
        """
        try:
            response = self.supabase.table('maternal_health').select('*').order(
                'visit_date', desc=True
            ).execute()
            maternal_data = response.data if response.data else []
            return pd.DataFrame(maternal_data)
        except Exception as e:
            print(f"Error exporting maternal health data: {e}")
            return pd.DataFrame()
    
    def export_ncd_data(self) -> pd.DataFrame:
        """
        Export all NCD followup data to pandas DataFrame.
        
        Returns:
            DataFrame with NCD followup data including resident_id
        """
        try:
            response = self.supabase.table('ncd_followup').select('*').order(
                'checkup_date', desc=True
            ).execute()
            ncd_data = response.data if response.data else []
            return pd.DataFrame(ncd_data)
        except Exception as e:
            print(f"Error exporting NCD followup data: {e}")
            return pd.DataFrame()
    
    # ==================== NEW HEALTH MODULES OPERATIONS ====================
    
    def add_growth_monitoring(self, growth_data: Dict) -> bool:
        """Add growth monitoring record for a child."""
        try:
            self.supabase.table('growth_monitoring').insert(growth_data).execute()
            return True
        except Exception as e:
            print(f"Error adding growth monitoring: {e}")
            return False
    
    def get_child_growth_records(self, resident_id: str) -> List[Dict]:
        """Get all growth records for a child."""
        try:
            response = self.supabase.table('growth_monitoring').select('*').eq(
                'resident_id', resident_id
            ).order('record_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting growth records: {e}")
            return []
    
    def add_maternal_health_record(self, maternal_data: Dict) -> bool:
        """Add maternal health (ANC/PNC) record."""
        try:
            self.supabase.table('maternal_health').insert(maternal_data).execute()
            return True
        except Exception as e:
            print(f"Error adding maternal health record: {e}")
            return False
    
    def get_maternal_health_records(self, resident_id: str) -> List[Dict]:
        """Get all maternal health records for a resident."""
        try:
            response = self.supabase.table('maternal_health').select('*').eq(
                'resident_id', resident_id
            ).order('visit_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting maternal health records: {e}")
            return []
    
    def get_high_risk_mothers(self) -> List[Dict]:
        """Get list of high-risk mothers (high BP or low Hb)."""
        try:
            # Get recent ANC records with danger signs or abnormal vitals
            # Note: The foreign key reference 'maternal_health_resident_id_fkey' follows
            # Supabase's default naming convention. If your FK has a custom name, update this.
            response = self.supabase.table('maternal_health').select(
                '*, residents!maternal_health_resident_id_fkey(name, unique_id)'
            ).eq('visit_type', 'ANC').order('visit_date', desc=True).execute()
            
            high_risk = []
            seen_residents = set()
            
            if response.data:
                for record in response.data:
                    resident_id = record.get('resident_id')
                    if resident_id in seen_residents:
                        continue
                    
                    # Check for high risk factors
                    bp_systolic = record.get('bp_systolic', 0) or 0
                    hemoglobin = record.get('hemoglobin', 100) or 100
                    danger_signs = record.get('danger_signs', '')
                    
                    if bp_systolic >= 140 or hemoglobin < 11 or danger_signs:
                        seen_residents.add(resident_id)
                        # Flatten nested resident data
                        if 'residents' in record and record['residents']:
                            record['resident_name'] = record['residents']['name']
                            del record['residents']
                        high_risk.append(record)
            
            return high_risk
        except Exception as e:
            print(f"Error getting high risk mothers: {e}")
            # Fallback: fetch without join if FK reference fails
            try:
                response = self.supabase.table('maternal_health').select('*').eq(
                    'visit_type', 'ANC'
                ).order('visit_date', desc=True).execute()
                
                high_risk = []
                seen_residents = set()
                
                if response.data:
                    for record in response.data:
                        resident_id = record.get('resident_id')
                        if resident_id in seen_residents:
                            continue
                        
                        bp_systolic = record.get('bp_systolic', 0) or 0
                        hemoglobin = record.get('hemoglobin', 100) or 100
                        danger_signs = record.get('danger_signs', '')
                        
                        if bp_systolic >= 140 or hemoglobin < 11 or danger_signs:
                            seen_residents.add(resident_id)
                            # Get resident name separately
                            resident = self.get_resident(resident_id)
                            if resident:
                                record['resident_name'] = resident['name']
                            high_risk.append(record)
                
                return high_risk
            except:
                return []
    
    def add_ncd_followup(self, ncd_data: Dict) -> bool:
        """Add NCD followup record."""
        try:
            self.supabase.table('ncd_followup').insert(ncd_data).execute()
            return True
        except Exception as e:
            print(f"Error adding NCD followup: {e}")
            return False
    
    def get_ncd_followup_records(self, resident_id: str) -> List[Dict]:
        """Get all NCD followup records for a resident."""
        try:
            response = self.supabase.table('ncd_followup').select('*').eq(
                'resident_id', resident_id
            ).order('checkup_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting NCD followup records: {e}")
            return []
    
    def get_ncd_due_list(self, days_threshold: int = 30) -> List[Dict]:
        """Get patients who haven't visited in specified days."""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days_threshold)).strftime('%Y-%m-%d')
            
            # Get all NCD patients with their last visit
            response = self.supabase.table('ncd_followup').select(
                'resident_id, checkup_date, condition_type'
            ).order('checkup_date', desc=True).execute()
            
            if not response.data:
                return []
            
            # Group by resident and find last visit
            last_visits = {}
            for record in response.data:
                resident_id = record['resident_id']
                if resident_id not in last_visits:
                    last_visits[resident_id] = record
            
            # Filter those overdue
            due_list = []
            for resident_id, record in last_visits.items():
                if record['checkup_date'] < cutoff_date:
                    # Get resident details
                    resident = self.get_resident(resident_id)
                    if resident:
                        due_list.append({
                            **record,
                            'resident_name': resident['name'],
                            'days_overdue': (datetime.now() - datetime.strptime(
                                record['checkup_date'], '%Y-%m-%d'
                            )).days
                        })
            
            return sorted(due_list, key=lambda x: x['days_overdue'], reverse=True)
        except Exception as e:
            print(f"Error getting NCD due list: {e}")
            return []
    
    # ==================== NEW MODULE ANALYTICS ====================
    
    def get_child_health_analytics(self) -> Dict:
        """
        Get analytics data for child health.
        
        Returns:
            Dictionary with child health statistics
        """
        try:
            # Get children under 5 years
            children = self.filter_residents({'age_min': 0, 'age_max': 5})
            total_children = len(children)
            
            # Get all growth records with latest z-scores
            response = self.supabase.table('growth_monitoring').select('*').order(
                'record_date', desc=True
            ).execute()
            
            growth_records = response.data if response.data else []
            
            # Calculate nutritional status distribution
            nutritional_status = {'Normal': 0, 'Malnourished': 0}
            seen_residents = set()
            
            for record in growth_records:
                resident_id = record.get('resident_id')
                if resident_id not in seen_residents:
                    seen_residents.add(resident_id)
                    z_score = record.get('z_score_weight_age', 0)
                    if z_score is not None:
                        if z_score < MALNUTRITION_Z_SCORE_THRESHOLD:
                            nutritional_status['Malnourished'] += 1
                        else:
                            nutritional_status['Normal'] += 1
            
            return {
                'total_children': total_children,
                'nutritional_status': nutritional_status,
                'children_with_records': len(seen_residents)
            }
        except Exception as e:
            print(f"Error getting child health analytics: {e}")
            return {'total_children': 0, 'nutritional_status': {}, 'children_with_records': 0}
    
    def get_maternal_health_analytics(self) -> Dict:
        """
        Get analytics data for maternal health.
        
        Returns:
            Dictionary with maternal health statistics
        """
        try:
            # Get all maternal health records
            response = self.supabase.table('maternal_health').select('*').execute()
            maternal_records = response.data if response.data else []
            
            # Count active pregnancies (recent ANC visits)
            active_pregnancies = set()
            anc_visits = 0
            pnc_visits = 0
            
            for record in maternal_records:
                visit_type = record.get('visit_type', '')
                if visit_type == 'ANC':
                    anc_visits += 1
                    # Consider pregnancy active if EDD is in the future or within last 9 months
                    edd_date = record.get('edd_date')
                    if edd_date:
                        from datetime import datetime, timedelta
                        try:
                            edd = datetime.strptime(edd_date, '%Y-%m-%d')
                            if edd >= datetime.now() - timedelta(days=PREGNANCY_DURATION_DAYS):
                                active_pregnancies.add(record.get('resident_id'))
                        except:
                            pass
                elif visit_type == 'PNC':
                    pnc_visits += 1
            
            # Count high-risk mothers
            high_risk_mothers = self.get_high_risk_mothers()
            
            return {
                'active_pregnancies': len(active_pregnancies),
                'high_risk_count': len(high_risk_mothers),
                'anc_visits': anc_visits,
                'pnc_visits': pnc_visits
            }
        except Exception as e:
            print(f"Error getting maternal health analytics: {e}")
            return {'active_pregnancies': 0, 'high_risk_count': 0, 'anc_visits': 0, 'pnc_visits': 0}
    
    def get_ncd_analytics(self) -> Dict:
        """
        Get analytics data for NCD control.
        
        Returns:
            Dictionary with NCD statistics and trend data
        """
        try:
            # Get all NCD records
            response = self.supabase.table('ncd_followup').select('*').order(
                'checkup_date', desc=True
            ).execute()
            ncd_records = response.data if response.data else []
            
            # Count unique NCD patients
            unique_patients = set()
            for record in ncd_records:
                unique_patients.add(record.get('resident_id'))
            
            # Calculate uncontrolled BP trend over last 6 months
            from datetime import datetime, timedelta
            six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            monthly_uncontrolled_bp = {}
            for record in ncd_records:
                checkup_date = record.get('checkup_date', '')
                if checkup_date >= six_months_ago:
                    bp_systolic = record.get('bp_systolic', 0) or 0
                    
                    # Extract year-month
                    month = checkup_date[:7]  # YYYY-MM
                    
                    if month not in monthly_uncontrolled_bp:
                        monthly_uncontrolled_bp[month] = 0
                    
                    # Count if BP is uncontrolled (>140 systolic)
                    if bp_systolic > HYPERTENSION_THRESHOLD_SYSTOLIC:
                        monthly_uncontrolled_bp[month] += 1
            
            return {
                'total_ncd_patients': len(unique_patients),
                'uncontrolled_bp_trend': dict(sorted(monthly_uncontrolled_bp.items()))
            }
        except Exception as e:
            print(f"Error getting NCD analytics: {e}")
            return {'total_ncd_patients': 0, 'uncontrolled_bp_trend': {}}

    def add_child_assessment(self, assessment_data: Dict) -> bool:
        """Add a comprehensive Under-5 child assessment record."""
        try:
            self.supabase.table('child_assessment').insert(assessment_data).execute()
            return True
        except Exception as e:
            print(f"Error adding child assessment: {e}")
            return False

    def get_child_assessment_records(self, resident_id: str) -> List[Dict]:
        """Get all child assessment records for a child."""
        try:
            response = self.supabase.table('child_assessment').select('*').eq(
                'resident_id', resident_id
            ).order('assessment_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting child assessment records: {e}")
            return []

    def add_household_proforma(self, proforma_data: Dict) -> Optional[int]:
        """Add a household proforma record. Returns the new record's ID."""
        try:
            response = self.supabase.table('household_proforma').insert(proforma_data).execute()
            if response.data:
                return response.data[0].get('id')
            return None
        except Exception as e:
            print(f"Error adding household proforma: {e}")
            return None

    def get_household_proforma_records(self) -> List[Dict]:
        """Get all household proforma records."""
        try:
            response = self.supabase.table('household_proforma').select('*').order(
                'visit_date', desc=True
            ).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting household proforma records: {e}")
            return []

    def add_household_members(self, members: List[Dict]) -> bool:
        """Add household member records."""
        try:
            if members:
                self.supabase.table('household_members').insert(members).execute()
            return True
        except Exception as e:
            print(f"Error adding household members: {e}")
            return False

    def get_household_members(self, household_id: int) -> List[Dict]:
        """Get all members for a household."""
        try:
            response = self.supabase.table('household_members').select('*').eq(
                'household_id', household_id
            ).order('sl_no').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting household members: {e}")
            return []

    def add_mch_screening(self, screening_records: List[Dict]) -> bool:
        """Add MCH screening records for a household."""
        try:
            if screening_records:
                self.supabase.table('mch_screening').insert(screening_records).execute()
            return True
        except Exception as e:
            print(f"Error adding MCH screening: {e}")
            return False

    def get_mch_screening(self, household_id: int) -> List[Dict]:
        """Get MCH screening records for a household."""
        try:
            response = self.supabase.table('mch_screening').select('*').eq(
                'household_id', household_id
            ).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting MCH screening: {e}")
            return []
