"""
AI-powered parser for extracting structured data from calendar event descriptions.
Uses OpenAI GPT models to intelligently parse trailer repair job descriptions.
"""

import logging
import json
from decimal import Decimal, InvalidOperation
from django.conf import settings

logger = logging.getLogger(__name__)


def parse_description_with_ai(description_text):
    """
    Parse a job description using AI to extract structured fields.
    
    Args:
        description_text (str): The raw description text from calendar event
        
    Returns:
        dict: Extracted fields with keys:
            - trailer_color (str): Color of the trailer
            - trailer_serial (str): Serial number or model identifier
            - trailer_details (str): Specifications like dimensions, features
            - repair_notes (str): Specific repair work to be done
            - quote (str or None): Quote amount (can be number or text like "TBD")
            - unparsed_notes (str): Any text that doesn't fit other categories
    """
    
    # Default fallback structure
    fallback_result = {
        'trailer_color': '',
        'trailer_serial': '',
        'trailer_details': '',
        'repair_notes': '',
        'quote': None,
        'unparsed_notes': description_text
    }
    
    # Check if description is empty
    if not description_text or not description_text.strip():
        return fallback_result
    
    # Check if AI parsing is enabled and API key is configured
    if not getattr(settings, 'AI_PARSING_ENABLED', False):
        logger.info("AI parsing is disabled in settings")
        return fallback_result
        
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        logger.warning("OpenAI API key not configured - falling back to raw description")
        return fallback_result
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        
        # Build the prompt
        prompt = f"""You are an expert at parsing trailer repair job descriptions. Extract structured information from the following description.

Description:
{description_text}

Extract and return ONLY a valid JSON object with these exact fields:
- trailer_color: The color of the trailer (e.g., "PEWTER", "BLACK"). Empty string if not found.
- trailer_serial: Serial number, model, or identifier (e.g., "UXT 10-12'"). Empty string if not found.
- trailer_details: Specifications like dimensions, features, equipment (e.g., "W/LADDER RACKS ON ROOF"). Empty string if not found.
- repair_notes: Specific repair work to be done (e.g., "COMPLETE TRL. INSPECTION", "CHECK WATER LEAKS AT ROOF"). Combine multiple repair items with newlines. Empty string if not found.
- quote: Any dollar amounts mentioned (as a number without $ sign, e.g., 1500.00). Use null if not found.
- unparsed_notes: Any text that doesn't clearly fit the above categories (billing addresses, notices, misc notes). Empty string if everything was categorized.

Rules:
- Return ONLY valid JSON, no markdown formatting or explanation
- Use empty strings for missing text fields, null for missing quote
- Be conservative - only extract what you're confident about
- Put ambiguous text in unparsed_notes
"""
        
        logger.debug(f"Sending description to OpenAI for parsing: {description_text[:100]}...")
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a data extraction assistant that returns only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=500,
            timeout=10.0  # 10 second timeout
        )
        
        # Extract the response
        response_text = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response: {response_text}")
        
        # Try to parse JSON (handle potential markdown code blocks)
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        parsed_data = json.loads(response_text)
        
        # Validate and clean the response
        result = {
            'trailer_color': str(parsed_data.get('trailer_color', '')).strip(),
            'trailer_serial': str(parsed_data.get('trailer_serial', '')).strip(),
            'trailer_details': str(parsed_data.get('trailer_details', '')).strip(),
            'repair_notes': str(parsed_data.get('repair_notes', '')).strip(),
            'quote': None,
            'unparsed_notes': str(parsed_data.get('unparsed_notes', '')).strip()
        }
        
        # Quote can be text or number, store as string
        quote_value = parsed_data.get('quote')
        if quote_value is not None:
            result['quote'] = str(quote_value)
        
        logger.info(f"Successfully parsed description with AI - extracted {sum(1 for v in result.values() if v)} fields")
        return result
        
    except ImportError:
        logger.error("OpenAI package not installed - run: pip install openai")
        return fallback_result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI JSON response: {e}")
        logger.error(f"Response was: {response_text[:500]}")
        return fallback_result
        
    except Exception as e:
        logger.error(f"Error during AI parsing: {type(e).__name__}: {str(e)}")
        return fallback_result


def parse_description_batch(descriptions):
    """
    Parse multiple descriptions in batch (for future optimization).
    Currently just calls parse_description_with_ai for each item.
    
    Args:
        descriptions (list): List of description texts
        
    Returns:
        list: List of parsed result dicts
    """
    return [parse_description_with_ai(desc) for desc in descriptions]








