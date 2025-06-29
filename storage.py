<<<<<<< HEAD
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fpdf import FPDF
import pandas as pd
from aws_services import get_user_data, store_data_in_s3, store_report_in_s3, send_alert, test_aws_connection
import boto3

class DataManager:
    """Manages data storage and retrieval operations."""
    
    def __init__(self):
        self.cache = {}
        # Test AWS connection on initialization
        print("DEBUG: Initializing DataManager...")
        test_aws_connection()

    def save_daily_entry(self, user_id: str, date: str, transcript: str, 
                        emotion_analysis: str, cognitive_metrics: Dict[str, Any], 
                        score_data: Dict[str, Any], source: str = 'text') -> bool:
        """
        Saves a daily wellness entry to storage with improved error handling.
        
        Args:
            user_id: User identifier
            date: Date string (YYYY-MM-DD)
            transcript: User's transcript
            emotion_analysis: Emotion analysis results
            cognitive_metrics: Dictionary of metrics from nlp_metrics.py
            score_data: Calculated score data
            source: Source of the entry ('voice' or 'text')
        
        Returns:
            Success status
        """
        print(f"DEBUG: save_daily_entry called - User: {user_id}, Date: {date}, Source: {source}")
        print(f"DEBUG: Transcript length: {len(transcript)} characters")
        print(f"DEBUG: Score data: {score_data}")
        
        # Validate inputs
        if not user_id or not date or not transcript:
            print("ERROR: Missing required parameters (user_id, date, or transcript)")
            return False
        
        if not score_data or 'score' not in score_data:
            print("ERROR: Invalid score_data - missing score")
            return False
        
        # Debug print for primary emotion
        if isinstance(emotion_analysis, str):
            try:
                emotion_data = json.loads(emotion_analysis)
                primary_emotion = emotion_data.get('primary_emotion', 'unknown')
            except Exception as e:
                print(f"ERROR: Failed to parse emotion_analysis JSON: {e}")
                primary_emotion = 'unknown'
        else:
            primary_emotion = emotion_analysis.get('primary_emotion', 'unknown')
        
        print(f"DEBUG: Primary emotion: {primary_emotion}")
        
        try:
            # Step 1: Store transcript in S3
            print("DEBUG: Step 1 - Storing transcript in S3...")
            transcript_key = store_data_in_s3(user_id, date, transcript)
            
            if not transcript_key:
                print("ERROR: Failed to store transcript in S3")
                return False
            
            print(f"DEBUG: Transcript stored in S3: {transcript_key}")
            
            # Step 2: Prepare data for DynamoDB
            print("DEBUG: Step 2 - Preparing data for DynamoDB...")
            entry_data = {
                'user_id': user_id,
                'date': date,
                'transcript': transcript,
                'emotion_analysis': emotion_analysis,
                'cognitive_metrics': json.dumps(cognitive_metrics),
                'score': score_data['score'],
                'emotion_score': score_data.get('emotion_score', score_data['score']),
                'cognitive_score': score_data.get('cognitive_score', score_data['score']),
                'zone': score_data.get('zone', 'unknown'),
                'zone_name': score_data.get('zone_name', 'Unknown'),
                'transcript_s3_key': transcript_key,
                'source': source,  # Track the source (voice or text)
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"DEBUG: Entry data prepared: {entry_data}")
            
            # Step 3: Save to DynamoDB
            print("DEBUG: Step 3 - Saving to DynamoDB...")
            from aws_services import save_to_dynamodb
            
            # Prepare feedback message
            feedback = score_data.get('feedback', '')
            if not feedback:
                score = score_data['score']
                if score >= 75:
                    feedback = "Positive emotional and cognitive indicators"
                elif score >= 50:
                    feedback = "Moderate wellness indicators"
                else:
                    feedback = "Lower wellness indicators detected"
            
            success = save_to_dynamodb(
                user_id=user_id,
                date=date,
                transcript=transcript,
                emotion=primary_emotion,
                score=score_data['score'],
                feedback=feedback,
                cognitive_metrics=cognitive_metrics,
                source=source  # Pass the source parameter
            )
            
            if not success:
                print("ERROR: Failed to save to DynamoDB")
                return False
            
            print("DEBUG: Successfully saved to DynamoDB")
            
            # Step 4: Update cache
            print("DEBUG: Step 4 - Updating cache...")
            if user_id not in self.cache:
                self.cache[user_id] = []
            self.cache[user_id].append(entry_data)
            
            print(f"DEBUG: save_daily_entry - SUCCESS! Entry saved for user {user_id} on {date} from {source}")
            return True
            
        except Exception as e:
            print(f"ERROR: Exception in save_daily_entry: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieves user's wellness history with improved error handling.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of historical entries
        """
        print(f"DEBUG: get_user_history called - User: {user_id}, Days: {days}")
        
        try:
            # Try cache first
            if user_id in self.cache:
                cached_data = self.cache[user_id][-days:]
                print(f"DEBUG: Returning {len(cached_data)} items from cache")
                return cached_data
            
            # Fetch from DynamoDB
            print("DEBUG: Cache miss - fetching from DynamoDB...")
            data = get_user_data(user_id)
            
            if not data:
                print(f"DEBUG: No data found in DynamoDB for user {user_id}")
                return []
            
            # Sort by date and limit
            data.sort(key=lambda x: x.get('date', ''), reverse=True)
            result = data[:days]
            
            print(f"DEBUG: Retrieved {len(result)} items from DynamoDB")
            
            # Update cache
            self.cache[user_id] = data
            
            return result
            
        except Exception as e:
            print(f"ERROR: Exception in get_user_history: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_recent_scores(self, user_id: str, days: int = 7) -> list:
        """
        Gets recent Cognora scores for alert evaluation.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of recent scores
        """
        print(f"DEBUG: get_recent_scores called - User: {user_id}, Days: {days}")
        
        history = self.get_user_history(user_id, days)
        scores = [entry.get('score', 50.0) for entry in history]
        print(f"DEBUG: get_recent_scores for user {user_id}: {scores}")
        return scores
    
    def get_recent_emotions(self, user_id: str, days: int = 7) -> List[str]:
        """
        Gets recent primary emotions for alert evaluation.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of recent emotions
        """
        print(f"DEBUG: get_recent_emotions called - User: {user_id}, Days: {days}")
        
        history = self.get_user_history(user_id, days)
        emotions = [entry.get('emotion', 'unknown') for entry in history]
        print(f"DEBUG: get_recent_emotions for user {user_id}: {emotions}")
        return emotions

    def get_recent_cognitive_scores(self, user_id: str, days: int = 7) -> list:
        """
        Gets recent cognitive scores for alert evaluation.
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        Returns:
            List of recent cognitive scores
        """
        print(f"DEBUG: get_recent_cognitive_scores called - User: {user_id}, Days: {days}")
        
        history = self.get_user_history(user_id, days)
        cognitive_scores = [entry.get('cognitive_score', 50.0) for entry in history]
        print(f"DEBUG: get_recent_cognitive_scores for user {user_id}: {cognitive_scores}")
        return cognitive_scores

    def test_data_retrieval(self, user_id: str) -> Dict[str, Any]:
        """
        Test function to check data retrieval and storage.
        
        Args:
            user_id: User identifier
        
        Returns:
            Test results
        """
        print(f"DEBUG: test_data_retrieval called for user {user_id}")
        
        result = {
            'user_id': user_id,
            'cache_entries': len(self.cache.get(user_id, [])),
            'dynamodb_entries': 0,
            'aws_connection': False,
            'errors': []
        }
        
        try:
            # Test AWS connection
            test_aws_connection()
            result['aws_connection'] = True
            
            # Test DynamoDB retrieval
            data = get_user_data(user_id)
            result['dynamodb_entries'] = len(data)
            
            if data:
                result['sample_entry'] = data[0]
            
        except Exception as e:
            result['errors'].append(f"DynamoDB test failed: {e}")
        
        print(f"DEBUG: test_data_retrieval result: {result}")
        return result

class ReportGenerator:
    """Generates wellness reports and exports."""
    
    def __init__(self):
        self.pdf = None
    
    def generate_weekly_report(self, user_id: str, week_start: str) -> Optional[Dict[str, Any]]:
        """
        Generates a weekly PDF report and uploads it to S3.
        
        Args:
            user_id: User identifier
            week_start: Start date of the week (YYYY-MM-DD)
        
        Returns:
            A dictionary containing the PDF bytes and the S3 key, or None
        """
        try:
            # Get week's data
            week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
            data_manager = DataManager()
            week_data = data_manager.get_user_history(user_id, 7)
            
            if not week_data:
                return None
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Cognora+ Weekly Wellness Report', ln=True, align='C')
            pdf.ln(10)
            
            # Week info
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Week of {week_start} to {week_end}', ln=True)
            pdf.ln(5)
            
            # Summary statistics
            scores = [entry.get('score', 0) for entry in week_data]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Weekly Summary:', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, f'Average Cognora Score: {avg_score:.1f}', ln=True)
            pdf.cell(0, 8, f'Days tracked: {len(week_data)}', ln=True)
            pdf.ln(5)
            
            # Daily breakdown
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Daily Breakdown:', ln=True)
            
            for entry in week_data:
                date = entry.get('date', 'Unknown')
                score = entry.get('score', 0)
                emotion = entry.get('emotion', 'Unknown')
                zone = entry.get('zone_name', 'Unknown')
                
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 8, f'{date}: Score {score:.1f} ({zone}) - {emotion}', ln=True)
            
            # Get PDF bytes
            pdf_bytes = pdf.output(dest='S').encode('latin-1')

            # ✅ Verified: Report generation exists. Adding S3 upload functionality.
            # Upload to S3
            report_date = f"weekly_{week_start}"
            s3_key = store_report_in_s3(user_id, report_date, pdf_bytes)
            print(f"Weekly report for {user_id} uploaded to S3: {s3_key}")
            
            return {
                'pdf_bytes': pdf_bytes,
                's3_key': s3_key
            }
            
        except Exception as e:
            print(f"Error generating weekly report: {e}")
            return None
    
    def export_data_csv(self, user_id: str, days: int = 30) -> Optional[str]:
        """
        Exports user data to CSV format.
        
        Args:
            user_id: User identifier
            days: Number of days to export
        
        Returns:
            CSV data as string
        """
        try:
            data_manager = DataManager()
            history = data_manager.get_user_history(user_id, days)
            
            if not history:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(history)
            
            # Select relevant columns
            columns = ['date', 'score', 'emotion_score', 'cognitive_score', 'zone', 'zone_name', 'emotion']
            df_export = df[columns].copy()
            
            return df_export.to_csv(index=False)
            
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return None

class AlertManager:
    """Manages caregiver alerts and notifications."""
    
    def __init__(self):
        self.alert_history = []
    
    def check_and_send_alerts(self, user_id: str) -> Dict[str, Any]:
        """
        Checks alert conditions and sends notifications if needed.
        
        Args:
            user_id: User identifier
        
        Returns:
            Alert status and details
        """
        try:
            data_manager = DataManager()
            recent_scores = data_manager.get_recent_scores(user_id, 7)
            recent_emotions = data_manager.get_recent_emotions(user_id, 7)
            recent_cognitive_scores = data_manager.get_recent_cognitive_scores(user_id, 7)
            print("DEBUG: check_and_send_alerts - recent_scores:", recent_scores)
            from scoring import check_alert_conditions
            alert_status = check_alert_conditions(recent_scores, recent_emotions, recent_cognitive_scores)
            print("DEBUG: check_and_send_alerts - alert_status:", alert_status)
            if alert_status['alert_needed']:
                # Send SNS alert
                subject = "Cognora+ Wellness Alert"
                message = f"""
                Wellness Alert for User {user_id}
                \nReasons: {', '.join(alert_status['reasons'])}
                Urgency: {alert_status['urgency']}
                \nRecent scores: {recent_scores[-3:]}
                Recent emotions: {recent_emotions[-3:]}
                \nPlease check on the user's wellbeing.
                """
                alert_sent = send_alert(subject, message)
                print("DEBUG: check_and_send_alerts - alert_sent:", alert_sent)
                
                # Log alert
                alert_log = {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id,
                    'alert_sent': alert_sent,
                    'reasons': alert_status['reasons'],
                    'urgency': alert_status['urgency']
                }
                self.alert_history.append(alert_log)
                
                return {
                    'alert_sent': alert_sent,
                    'alert_status': alert_status,
                    'message': 'Alert sent to caregiver' if alert_sent else 'Failed to send alert'
                }
            
            return {
                'alert_sent': False,
                'alert_status': alert_status,
                'message': 'No alert conditions met'
            }
            
        except Exception as e:
            print(f"Error checking alerts: {e}")
            return {
                'alert_sent': False,
                'error': str(e),
                'message': 'Error checking alert conditions'
            }
    
    def get_alert_history(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Gets alert history.
        
        Args:
            user_id: Optional user filter
        
        Returns:
            List of alert logs
        """
        if user_id:
            return [alert for alert in self.alert_history if alert.get('user_id') == user_id]
        return self.alert_history

# Global instances
data_manager = DataManager()
report_generator = ReportGenerator()
alert_manager = AlertManager()
=======
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fpdf import FPDF
import pandas as pd
from aws_services import get_user_data, store_data_in_s3, store_report_in_s3, send_alert

class DataManager:
    """Manages data storage and retrieval operations."""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
    
    def save_daily_entry(self, user_id: str, date: str, transcript: str, 
                        emotion_analysis: str, cognitive_analysis: str, 
                        score_data: Dict[str, Any]) -> bool:
        """
        Saves a daily wellness entry to storage.
        
        Args:
            user_id: User identifier
            date: Date string (YYYY-MM-DD)
            transcript: User's transcript
            emotion_analysis: Emotion analysis results
            cognitive_analysis: Cognitive analysis results
            score_data: Calculated score data
        
        Returns:
            Success status
        """
        try:
            # Store transcript in S3
            transcript_key = store_data_in_s3(user_id, date, transcript)
            
            # Prepare data for DynamoDB
            entry_data = {
                'user_id': user_id,
                'date': date,
                'transcript': transcript,
                'emotion_analysis': emotion_analysis,
                'cognitive_analysis': cognitive_analysis,
                'score': score_data['score'],
                'emotion_score': score_data['emotion_score'],
                'cognitive_score': score_data['cognitive_score'],
                'zone': score_data['zone'],
                'zone_name': score_data['zone_name'],
                'transcript_s3_key': transcript_key,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to DynamoDB
            from aws_services import save_to_dynamodb
            success = save_to_dynamodb(
                user_id=user_id,
                date=date,
                transcript=transcript,
                emotion=json.loads(emotion_analysis).get('primary_emotion', 'unknown'),
                score=score_data['score'],
                feedback=score_data.get('feedback', '')
            )
            
            # Update cache
            if user_id not in self.cache:
                self.cache[user_id] = []
            self.cache[user_id].append(entry_data)
            
            return success
            
        except Exception as e:
            print(f"Error saving daily entry: {e}")
            return False
    
    def get_user_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieves user's wellness history.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of historical entries
        """
        try:
            # Try cache first
            if user_id in self.cache:
                return self.cache[user_id][-days:]
            
            # Fetch from DynamoDB
            data = get_user_data(user_id)
            
            # Sort by date and limit
            data.sort(key=lambda x: x.get('date', ''), reverse=True)
            return data[:days]
            
        except Exception as e:
            print(f"Error retrieving user history: {e}")
            return []
    
    def get_recent_scores(self, user_id: str, days: int = 7) -> List[float]:
        """
        Gets recent Cognora scores for alert evaluation.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of recent scores
        """
        history = self.get_user_history(user_id, days)
        return [entry.get('score', 50.0) for entry in history]
    
    def get_recent_emotions(self, user_id: str, days: int = 7) -> List[str]:
        """
        Gets recent primary emotions for alert evaluation.
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
        
        Returns:
            List of recent emotions
        """
        history = self.get_user_history(user_id, days)
        return [entry.get('emotion', 'unknown') for entry in history]

class ReportGenerator:
    """Generates wellness reports and exports."""
    
    def __init__(self):
        self.pdf = None
    
    def generate_weekly_report(self, user_id: str, week_start: str) -> Optional[bytes]:
        """
        Generates a weekly PDF report.
        
        Args:
            user_id: User identifier
            week_start: Start date of the week (YYYY-MM-DD)
        
        Returns:
            PDF report as bytes
        """
        try:
            # Get week's data
            week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
            data_manager = DataManager()
            week_data = data_manager.get_user_history(user_id, 7)
            
            if not week_data:
                return None
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Cognora+ Weekly Wellness Report', ln=True, align='C')
            pdf.ln(10)
            
            # Week info
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Week of {week_start} to {week_end}', ln=True)
            pdf.ln(5)
            
            # Summary statistics
            scores = [entry.get('score', 0) for entry in week_data]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Weekly Summary:', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, f'Average Cognora Score: {avg_score:.1f}', ln=True)
            pdf.cell(0, 8, f'Days tracked: {len(week_data)}', ln=True)
            pdf.ln(5)
            
            # Daily breakdown
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Daily Breakdown:', ln=True)
            
            for entry in week_data:
                date = entry.get('date', 'Unknown')
                score = entry.get('score', 0)
                emotion = entry.get('emotion', 'Unknown')
                zone = entry.get('zone_name', 'Unknown')
                
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 8, f'{date}: Score {score:.1f} ({zone}) - {emotion}', ln=True)
            
            # Get PDF bytes
            return pdf.output(dest='S').encode('latin-1')
            
        except Exception as e:
            print(f"Error generating weekly report: {e}")
            return None
    
    def export_data_csv(self, user_id: str, days: int = 30) -> Optional[str]:
        """
        Exports user data to CSV format.
        
        Args:
            user_id: User identifier
            days: Number of days to export
        
        Returns:
            CSV data as string
        """
        try:
            data_manager = DataManager()
            history = data_manager.get_user_history(user_id, days)
            
            if not history:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(history)
            
            # Select relevant columns
            columns = ['date', 'score', 'emotion_score', 'cognitive_score', 'zone', 'zone_name', 'emotion']
            df_export = df[columns].copy()
            
            return df_export.to_csv(index=False)
            
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return None

class AlertManager:
    """Manages caregiver alerts and notifications."""
    
    def __init__(self):
        self.alert_history = []
    
    def check_and_send_alerts(self, user_id: str) -> Dict[str, Any]:
        """
        Checks alert conditions and sends notifications if needed.
        
        Args:
            user_id: User identifier
        
        Returns:
            Alert status and details
        """
        try:
            data_manager = DataManager()
            recent_scores = data_manager.get_recent_scores(user_id, 7)
            recent_emotions = data_manager.get_recent_emotions(user_id, 7)
            
            # Check alert conditions
            from scoring import check_alert_conditions
            alert_status = check_alert_conditions(recent_scores, recent_emotions)
            
            if alert_status['alert_needed']:
                # Send SNS alert
                subject = "Cognora+ Wellness Alert"
                message = f"""
                Wellness Alert for User {user_id}
                
                Reasons: {', '.join(alert_status['reasons'])}
                Urgency: {alert_status['urgency']}
                
                Recent scores: {recent_scores[-3:]}
                Recent emotions: {recent_emotions[-3:]}
                
                Please check on the user's wellbeing.
                """
                
                alert_sent = send_alert(subject, message)
                
                # Log alert
                alert_log = {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id,
                    'alert_sent': alert_sent,
                    'reasons': alert_status['reasons'],
                    'urgency': alert_status['urgency']
                }
                self.alert_history.append(alert_log)
                
                return {
                    'alert_sent': alert_sent,
                    'alert_status': alert_status,
                    'message': 'Alert sent to caregiver' if alert_sent else 'Failed to send alert'
                }
            
            return {
                'alert_sent': False,
                'alert_status': alert_status,
                'message': 'No alert conditions met'
            }
            
        except Exception as e:
            print(f"Error checking alerts: {e}")
            return {
                'alert_sent': False,
                'error': str(e),
                'message': 'Error checking alert conditions'
            }
    
    def get_alert_history(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Gets alert history.
        
        Args:
            user_id: Optional user filter
        
        Returns:
            List of alert logs
        """
        if user_id:
            return [alert for alert in self.alert_history if alert.get('user_id') == user_id]
        return self.alert_history

# Global instances
data_manager = DataManager()
report_generator = ReportGenerator()
alert_manager = AlertManager()
>>>>>>> 23a3f924b5333426fb4b4fb6085453f9515378f8
