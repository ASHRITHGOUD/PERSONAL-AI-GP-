# services/llm_service.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_response(prompt: str) -> str:
    """Sends a text prompt to the Gemini API and returns the AI's response."""
    try:
        # Create a GenerativeModel instance
        model = genai.GenerativeModel('gemini-pro')
        
        # Call the generate_content method to get a response
        response = model.generate_content(prompt)
        
        # Check if the response contains text and return it
        if response.text:
            return response.text
        else:
            return "No text response generated."
            
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I am unable to generate a response right now."