"""
Test script for audio recording functionality
"""

import streamlit as st
from audio_recorder import get_audio_input_method

def test_audio_recording():
    """Test the audio recording functionality."""
    
    st.title("🎤 Audio Recording Test")
    st.markdown("This page tests the audio recording functionality for Cognora+")
    
    # Test the audio input method
    audio_data, input_method = get_audio_input_method()
    
    if audio_data:
        st.success(f"✅ Audio captured successfully via {input_method}!")
        
        # Display info about the audio
        if hasattr(audio_data, 'name'):
            st.info(f"File: {audio_data.name}")
            st.info(f"Size: {audio_data.size} bytes")
        else:
            st.info("Audio data captured from microphone")
        
        # Test transcription (if AWS is configured)
        if st.button("🎵 Test Transcription"):
            try:
                from aws_services import transcribe_audio
                import io
                
                if hasattr(audio_data, 'name'):
                    transcript = transcribe_audio(audio_data)
                else:
                    audio_file = io.BytesIO(audio_data)
                    audio_file.name = "test_recording.wav"
                    transcript = transcribe_audio(audio_file)
                
                if transcript:
                    st.success("✅ Transcription successful!")
                    st.text_area("Transcript", transcript, height=200)
                else:
                    st.error("❌ Transcription failed")
                    
            except Exception as e:
                st.error(f"Error during transcription: {e}")
                st.info("Make sure AWS credentials are configured properly")
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📋 Test Instructions")
    st.markdown("""
    1. **Choose your input method** above
    2. **For microphone recording:**
       - Click "Start Recording" and speak clearly
       - Click "Stop Recording" when done
       - Click "Use This Recording" to process
    3. **For file upload:**
       - Upload an audio file
       - The file will be processed automatically
    4. **Test transcription** to verify AWS integration
    """)

if __name__ == "__main__":
    test_audio_recording() 