"""
Audio Recording Component for Cognora+
Provides real-time microphone recording functionality using HTML5 Audio API
"""

import streamlit as st
import tempfile
import os
import wave
import numpy as np
from datetime import datetime
import base64
from io import BytesIO

def create_audio_recorder():
    """Creates an audio recorder using HTML5 Audio API."""
    
    st.markdown("### 🎤 Real-time Voice Recording")
    st.markdown("Click the button below to start recording your voice directly through your microphone.")
    
    # HTML/JavaScript for audio recording
    audio_recorder_html = """
    <div style="text-align: center; padding: 20px; border: 2px solid #e0e0e0; border-radius: 10px; background-color: #f8f9fa;">
        <div style="margin-bottom: 20px;">
            <button id="recordButton" style="background-color: #ff4b4b; color: white; border: none; padding: 15px 30px; border-radius: 25px; font-size: 16px; cursor: pointer; margin: 10px; transition: all 0.3s;">
                🎙️ Start Recording
            </button>
            <button id="stopButton" style="background-color: #4b4b4b; color: white; border: none; padding: 15px 30px; border-radius: 25px; font-size: 16px; cursor: pointer; margin: 10px; display: none; transition: all 0.3s;">
                ⏹️ Stop Recording
            </button>
        </div>
        
        <div id="recordingStatus" style="margin: 20px; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 5px;"></div>
        
        <div id="audioSection" style="margin: 20px; display: none;">
            <audio id="audioPlayback" controls style="margin: 20px; width: 100%; max-width: 400px;"></audio>
            <div style="margin: 20px;">
                <button id="downloadButton" style="background-color: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 15px; cursor: pointer; margin: 5px;">
                    💾 Download Recording
                </button>
            </div>
        </div>
        
        <div id="recordingTimer" style="font-size: 24px; font-weight: bold; color: #ff4b4b; margin: 10px; display: none;">
            00:00
        </div>
    </div>
    
    <script>
    let mediaRecorder;
    let audioChunks = [];
    let audioBlob;
    let recordingStartTime;
    let timerInterval;
    
    function updateTimer() {
        if (recordingStartTime) {
            const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('recordingTimer').textContent = 
                (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        }
    }
    
    document.getElementById('recordButton').addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                } 
            });
            
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioUrl = URL.createObjectURL(audioBlob);
                document.getElementById('audioPlayback').src = audioUrl;
                document.getElementById('audioSection').style.display = 'block';
                document.getElementById('recordingStatus').textContent = '✅ Recording completed! Download your file below.';
                document.getElementById('recordingStatus').style.color = 'green';
                document.getElementById('recordingStatus').style.backgroundColor = '#d4edda';
                document.getElementById('recordingTimer').style.display = 'none';
                clearInterval(timerInterval);
            };
            
            mediaRecorder.start();
            recordingStartTime = Date.now();
            timerInterval = setInterval(updateTimer, 1000);
            
            document.getElementById('recordButton').style.display = 'none';
            document.getElementById('stopButton').style.display = 'inline-block';
            document.getElementById('recordingStatus').textContent = '🔴 Recording... Speak now!';
            document.getElementById('recordingStatus').style.color = 'red';
            document.getElementById('recordingStatus').style.backgroundColor = '#f8d7da';
            document.getElementById('recordingTimer').style.display = 'block';
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            document.getElementById('recordingStatus').textContent = '❌ Error: Could not access microphone. Please check permissions.';
            document.getElementById('recordingStatus').style.color = 'red';
            document.getElementById('recordingStatus').style.backgroundColor = '#f8d7da';
        }
    });
    
    document.getElementById('stopButton').addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            document.getElementById('recordButton').style.display = 'inline-block';
            document.getElementById('stopButton').style.display = 'none';
        }
    });
    
    document.getElementById('downloadButton').addEventListener('click', () => {
        if (audioBlob) {
            const url = URL.createObjectURL(audioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cognora_recording_' + new Date().toISOString().slice(0,19).replace(/:/g,'-') + '.webm';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            // Show success message
            document.getElementById('recordingStatus').textContent = '✅ File downloaded! Now upload it below to continue.';
            document.getElementById('recordingStatus').style.color = 'green';
            document.getElementById('recordingStatus').style.backgroundColor = '#d4edda';
        }
    });
    </script>
    """
    
    st.components.v1.html(audio_recorder_html, height=450)
    
    return None

def get_audio_input_method():
    """Returns the preferred audio input method."""
    
    st.markdown("### 🎤 Choose Your Voice Input Method")
    
    method = st.radio(
        "Select how you want to provide voice input:",
        [
            "🎙️ Real-time Microphone Recording (Recommended)",
            "📁 Upload Audio File"
        ],
        key="audio_input_method"
    )
    
    if "Real-time Microphone Recording" in method:
        # Show the audio recorder
        create_audio_recorder()
        
        # Instructions for microphone recording
        st.markdown("---")
        st.markdown("### 📋 How to Use Microphone Recording")
        st.markdown("""
        1. **Click "Start Recording"** in the interface above
        2. **Speak clearly** into your microphone
        3. **Click "Stop Recording"** when done
        4. **Review your recording** using the audio player
        5. **Click "Download Recording"** to save the file
        6. **Upload the downloaded file** below to continue
        """)
        
        # File upload for downloaded recordings
        st.markdown("---")
        st.markdown("### 📁 Upload Your Downloaded Recording")
        st.markdown("After downloading your recording above, upload it here to continue:")
        
        uploaded_file = st.file_uploader(
            "Upload your downloaded audio file (WEBM, WAV, MP3, M4A, FLAC)",
            type=['webm', 'wav', 'mp3', 'm4a', 'flac'],
            key="audio_upload_fallback"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            return uploaded_file, "upload"
    else:
        # File upload method
        uploaded_file = st.file_uploader(
            "Upload audio file (WAV, MP3, M4A, FLAC, WEBM)",
            type=['wav', 'mp3', 'm4a', 'flac', 'webm'],
            key="audio_file_upload"
        )
        if uploaded_file:
            return uploaded_file, "upload"
    
    return None, None 