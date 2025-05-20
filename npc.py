from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random


class NPC:
    def __init__(self, id: int, name: str, personality: int, gang_related: bool = False):
        self.id = id
        self.name = name
        self.personality = personality
        self.gang_related = gang_related
        self.mood = 50  # 0-100
        self.conversation_history = []
        self.relationships = {}  # {npc_id: (description, strength)}
        self.mood_history = []
        self.creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.long_term_memory = []  # For important facts
        self.conversation_topics = {}  # {topic: (sentiment, times_discussed)}
   
    def get_personality_traits(self) -> List[str]:
        personalities = {
            1: ["flamboyant", "ruthless", "obsessed with appearances", "charismatic", "never modest", "always dramatic"],
            2: ["detached", "meticulous", "amoral", "perfectionist", "never emotional", "always analytical"],
            3: ["paranoid", "conspiracy-minded", "highly intelligent", "volatile", "never trusting", "always suspicious"],
            4: ["stoic", "adaptable", "fiercely independent", "loyal to the gang", "never talkative", "always guarded"],
            5: ["wry", "world-weary", "calculating", "intuitive", "never naive", "always cynical"],
            6: ["bitter", "manipulative", "morally compromised", "exhausted", "never kind", "always sharp-tongued"],
            7: ["enigmatic", "unsettling", "visionary", "poetic", "never direct", "always cryptic"]
        }
        return personalities.get(self.personality, ["mysterious"])
   
    def get_personality_description(self) -> str:
        primary_trait = self.get_personality_traits()[0]
        return f"{primary_trait} ({', '.join(self.get_personality_traits()[1:3])})"
   
    def get_gang_affiliation(self) -> str:
        return "Exodyne" if self.gang_related else "Stray"
   
    def update_mood(self, sentiment_score: float):
        old_mood = self.mood
        if sentiment_score < -0.5:
            self.mood -= 15
        elif sentiment_score < -0.2:
            self.mood -= 8
        elif sentiment_score > 0.5:
            self.mood += 15
        elif sentiment_score > 0.2:
            self.mood += 8
        
        # Personality-specific mood modifiers
        if self.personality in [1, 3, 6]:  # More volatile personalities
            self.mood += random.randint(-5, 5)
        elif self.personality in [2, 4, 7]:  # More stable personalities
            self.mood += random.randint(-2, 2)
            
        # Gang members have more controlled mood swings
        if self.gang_related:
            self.mood = max(20, min(80, self.mood))
        else:
            self.mood = max(0, min(100, self.mood))
            
        if old_mood != self.mood:
            self.mood_history.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "old_mood": old_mood,
                "new_mood": self.mood,
                "change": self.mood - old_mood
            })
   
    def add_relationship(self, npc_id: int, description: str, strength: int = 50):
        self.relationships[npc_id] = (description, strength)
   
    def get_relationship_to(self, npc_id: int) -> Optional[Tuple[str, int]]:
        return self.relationships.get(npc_id, ("no relationship", 50))
   
    def get_mood_description(self) -> str:
        if self.mood > 75:
            descriptors = {
                1: "exuberant",
                2: "pleased",
                3: "unusually calm",
                4: "content",
                5: "amused",
                6: "satisfied",
                7: "transcendent"
            }
            return descriptors.get(self.personality, "very positive")
        elif self.mood > 60:
            return "positive"
        elif self.mood > 40:
            return "neutral"
        elif self.mood > 25:
            descriptors = {
                1: "irritated",
                2: "displeased",
                3: "agitated",
                4: "tense",
                5: "sarcastic",
                6: "hostile",
                7: "withdrawn"
            }
            return descriptors.get(self.personality, "negative")
        else:
            descriptors = {
                1: "furious",
                2: "cold",
                3: "paranoid",
                4: "dangerous",
                5: "bitter",
                6: "vicious",
                7: "catatonic"
            }
            return descriptors.get(self.personality, "very negative")
   
    def remember_fact(self, fact: str, importance: int = 1):
        """Store important conversation facts"""
        if importance > 0.5:  # Threshold
            self.long_term_memory.append({
                "fact": fact,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "importance": importance
            })

    def track_conversation_topic(self, topic: str, sentiment: float):
        """Track and weight conversation topics"""
        current = self.conversation_topics.get(topic, (0, 0))
        self.conversation_topics[topic] = (
            (current[0] * current[1] + sentiment) / (current[1] + 1),  # Weighted average
            current[1] + 1  # Count
        )

    def get_status_report(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "personality": {
                "type": self.personality,
                "description": self.get_personality_description(),
                "traits": self.get_personality_traits()
            },
            "gang_affiliation": self.get_gang_affiliation(),
            "current_mood": {
                "value": self.mood,
                "description": self.get_mood_description()
            },
            "mood_history": self.mood_history[-5:],
            "relationships": {nid: self.get_relationship_to(nid) for nid in self.relationships},
            "conversation_history": self.conversation_history[-3:],
            "long_term_memory": [m['fact'] for m in self.long_term_memory[-3:]],
            "topics": self.conversation_topics,
            "created_at": self.creation_time,
            "known_locations": {
                "window": [7, 1, 5],
                "bar": [6, 4, 2],
                "bartender": [3]
            }
        }