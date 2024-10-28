import gradio as gr
from groq import Groq
from PIL import Image, ImageGrab
import google.generativeai as genai
import cv2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiModalAssistant:
    def __init__(self, groq_api_key: str, google_api_key: str):
        """Initialize the assistant with API keys."""
        self.groq_client = Groq(api_key=groq_api_key)
        genai.configure(api_key=google_api_key)
        self.web_cam = cv2.VideoCapture(0)
        self.conversation = [{'role': 'system', 'content': self._get_system_message()}]
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            generation_config=self._get_generation_config(),
            safety_settings=self._get_safety_settings()
        )
        logger.info("Assistant initialized successfully")

    def _get_system_message(self) -> str:
        return "You are a multi-modal AI assistant. Generate concise responses using conversation context."

    def _get_generation_config(self):
        return {'temperature': 0.7, 'top_p': 1, 'top_k': 1, 'max_output_tokens': 2048}

    def _get_safety_settings(self):
        return [
            {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'}
        ]

    def generate_response(self, prompt: str) -> str:
        """Generate a response to the user prompt."""
        self.conversation.append({'role': 'user', 'content': prompt})
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=self.conversation, model='llama3-70b-8192'
            )
            response = chat_completion.choices[0].message
            self.conversation.append(response)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error generating a response."

def respond_to_user(prompt):
    """Wrapper function for Gradio interface"""
    return assistant.generate_response(prompt)

# Initialize your assistant with API keys (replace these with your actual keys)
groq_api_key = "ENTER YOUR GROQ API KEY"
google_api_key = "ENTER YOUR GOOGLE(GEMINI) API KEY"
assistant = MultiModalAssistant(groq_api_key, google_api_key)

# Gradio Interface
iface = gr.Interface(fn=respond_to_user, inputs="text", outputs="text", title="MultiModal Assistant")

# Launch the interface
iface.launch()
