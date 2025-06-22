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
