import re
import random
from typing import Optional
from npc import NPC


def enforce_character_consistency(
    response: str,
    npc: NPC,
    mentioned_npc: Optional[int] = None,
    all_npcs: Optional[dict] = None
) -> str:
    """Post-process response to enforce character consistency"""
    
    # Remove any meta-commentary or out-of-character phrases
    forbidden_phrases = [
        "as an AI", "language model", "I don't have personal",
        "I don't actually", "I'm just an AI", "my programming"
    ]
    
    for phrase in forbidden_phrases:
        if phrase in response.lower():
            return get_fallback_response(npc)
    
    # Remove any parentheses or brackets
    response = re.sub(r'\(.*?\)|\[.*?\]', '', response)
    response = re.sub(r'\s+', ' ', response).strip()
    
    # Ensure response ends properly
    if response and not response[-1] in '.!?':
        response += random.choice(['.', '...', '!'])
    
    # Personality-specific adjustments
    if npc.personality == 1:  # Flamboyant
        if len(response.split()) < 5 and not any(c in response for c in ['!', '~']):
            response = f"{response} Darling~"
        elif random.random() < 0.3:
            response = response.replace("I", "I, darling")
    
    elif npc.personality == 2:  # Detached
        if len(response.split()) > 15:
            response = ". ".join(response.split(". ")[:1]) + "."
        response = response.replace("I ", "This unit ").replace(" me ", " this unit ")
    
    elif npc.personality == 3:  # Paranoid
        if "?" in response and random.random() < 0.6:
            response = response.replace("?", "??")
        if len(response) > 0 and response[-1] not in ['!', '?']:
            response += "..."
    
    elif npc.personality == 4:  # Stoic
        if len(response.split()) > 8:
            response = " ".join(response.split()[:5]) + "."
    
    elif npc.personality == 7:  # Enigmatic
        if len(response.split()) > 8:
            response = " ".join(response.split()[:8]) + "..."
    
    # Location-related adjustments
    if "window" in response.lower() and npc.personality in [1, 5, 7]:
        response = response.replace("window", "glass")  # More thematic
    
    if "bar" in response.lower():
        if npc.personality == 3:  # Bartender
            response = response.replace("bar", "my bar")
        elif npc.personality == 6:  # Bitter
            response = response.replace("bar", "this dump")
    
    # Mood-based adjustments
    if npc.mood < 30:
        if npc.personality in [1, 6] and not any(c in response for c in ['!', '...', '?']):
            response = response[:-1] + '!' if response.endswith('.') else response + '!'
        elif npc.personality in [4, 5]:
            response = response.lower()
    
    # Relationship-based adjustments
    if mentioned_npc and all_npcs:
        _, strength = npc.get_relationship_to(mentioned_npc)
        other_name = all_npcs[mentioned_npc].name
        
        # Positive relationship
        if strength > 60:
            if not any(w in response.lower() for w in ['friend', 'trust', 'good', 'like']):
                response = f"{other_name}'s alright. " + response
        # Negative relationship
        elif strength < 40:
            if not any(w in response.lower() for w in ['hate', 'dislike', 'annoy', 'problem']):
                response = f"Don't talk to me about {other_name}. " + response
    
    return response


def get_fallback_response(npc: NPC) -> str:
    """Get a personality-appropriate fallback response"""
    fallbacks = {
        1: ["*adjusts tie* How crude.", "I don't have time for this."],
        2: ["Irrelevant.", "Data not found."],
        3: ["*looks around nervously* Not here...", "I can't talk about that."],
        4: ["*silent stare*", "No."],
        5: ["*sighs* Really?", "That's not important."],
        6: ["Ugh. No.", "*rolls eyes*"],
        7: ["...", "*turns away*"]
    }
    return random.choice(fallbacks.get(npc.personality, ["*shrugs*"]))