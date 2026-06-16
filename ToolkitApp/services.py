import json
import cohere
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from decouple import config

# Initialize Cohere client using your .env file
co = cohere.Client(config('COHERE_API_KEY'))

def extract_video_id(url):
    """Safely extracts the YouTube video ID from various URL formats."""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
    return None

def get_youtube_transcript(url):
    """Fetches the transcript using a bulletproof, version-agnostic approach."""
    video_id = extract_video_id(url)
    if not video_id:
        return None, "Invalid YouTube URL format."
    
    try:
        # Step 1: Attempt the standard fetch method (covers 99% of versions)
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        except AttributeError:
            # Fallback for weird or object-oriented library versions
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
        
        # Step 2: The Failsafe Extractor (Duck Typing)
        text_chunks = []
        for item in transcript_list:
            if isinstance(item, dict) and 'text' in item:
                # Handles traditional dictionary outputs
                text_chunks.append(item['text'])
            elif hasattr(item, 'text'):
                # Handles custom object outputs
                text_chunks.append(item.text)
            else:
                # Absolute fallback so the server never crashes
                text_chunks.append(str(item))
                
        transcript_text = " ".join(text_chunks)
        
        # Step 3: Final validation
        if not transcript_text.strip():
            return None, "Transcript was found but is completely empty."
            
        return transcript_text, None
        
    except Exception as e:
        # This safely catches videos with disabled captions
        return None, f"Could not retrieve transcript. (Error: {str(e)})"
    
    
import json
import re

def analyze_with_cohere(transcript):
    """Sends the transcript to Cohere and safely parses the JSON response for v4.57 SDK."""
    
    # We truncate the transcript slightly to ensure we don't hit token limits
    safe_transcript = transcript[:20000] 
    
    prompt = f"""
    You are an expert YouTube strategist. Analyze the following video transcript and extract the optimal metadata.
    You MUST respond with a valid JSON object containing exactly these keys:
    - "summary": A concise, 3-sentence summary of the video content.
    - "tone_analysis": A short string describing the tone (e.g., "Educational and Fast-Paced").
    - "target_audience": A short string describing the ideal viewer demographic.
    - "suggested_titles": A list of exactly 5 highly engaging, click-worthy YouTube titles.
    - "seo_tags": A list of exactly 15 optimal SEO tags/hashtags for this content.

    CRITICAL INSTRUCTION: Return ONLY raw JSON. Do not include markdown blocks like ```json. Do not include any conversational text before or after the JSON object.

    Transcript:
    {safe_transcript}
    """
    
    try:
        # Standard chat call compatible with Cohere SDK v4.57
        response = co.chat(
            model="command-a-03-2025",
            message=prompt
        )
        
        # Clean the text to ensure it's pure JSON (stripping accidental markdown)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
            
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        raw_text = raw_text.strip()
        
        # Parse the string into a Python dictionary
        result_dict = json.loads(raw_text)
        return result_dict, None
        
    except json.JSONDecodeError as e:
        return None, f"AI Output Parsing Error: The AI did not return perfect JSON. ({str(e)})"
    except Exception as e:
        return None, f"AI Analysis failed. (Error: {str(e)})"   
    
import requests

def get_video_metadata(url):
    """Fetches the video title and thumbnail using YouTube's free oEmbed API."""
    try:
        # The oEmbed endpoint returns basic public info about a video as JSON
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('title', 'Unknown Title'), data.get('thumbnail_url', '')
    except Exception:
        pass
    
    return "Processed YouTube Video", ""    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    