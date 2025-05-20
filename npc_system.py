import torch
import re
import random
from typing import Optional
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM


from sentiment import SentimentAnalyzer
from text_processing import enforce_character_consistency
from npc import NPC


class NPCSystem:
    def __init__(self):
        self.npcs = {}
        self.system_log = []
        self.tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-2.7B")
        self.model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-2.7B").to(
            torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model.eval()
        self.sentiment_analyzer = SentimentAnalyzer()
        self._initialize_npcs()
        self._setup_relationships()
        self._setup_locations()
        self._log_system_event("System initialized")
   
    def _log_system_event(self, message: str):
        self.system_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": message
        })
   
    def _initialize_npcs(self):
        names = ["Axel", "Vesper", "Jinx", "Rook", "Sloane", "Mirage", "Oracle"]
        for i in range(1, 8):
            gang_related = i >= 4
            self.npcs[i] = NPC(
                id=i,
                name=names[i-1],
                personality=i,
                gang_related=gang_related
            )
            self._log_system_event(f"Created NPC {i}: {names[i-1]} (Personality {i}, {self.npcs[i].get_gang_affiliation()})")
   
    def _setup_relationships(self):
        self.npcs[1].add_relationship(2, "professional acquaintance but finds them irritating", 40)
        self.npcs[2].add_relationship(1, "necessary business contact but dislikes their flamboyance", 35)
        self.npcs[2].add_relationship(3, "distrusts their paranoid nature", 30)
        self.npcs[2].add_relationship(4, "respects their professionalism but wary of gang ties", 60)
        self.npcs[3].add_relationship(2, "suspects they have hidden agendas", 25)
        self.npcs[4].add_relationship(2, "useful business contact outside the gang", 65)
        self.npcs[4].add_relationship(5, "trusted lieutenant", 80)
        self.npcs[4].add_relationship(6, "reliable enforcer", 75)
        self.npcs[5].add_relationship(4, "gang leader respected for their leadership", 85)
        self.npcs[6].add_relationship(4, "gang leader but has some disagreements", 70)
        self.npcs[6].add_relationship(7, "only person they somewhat trust", 65)
        self.npcs[7].add_relationship(6, "only connection to the physical world", 60)
        self._log_system_event("All relationships established")

    def _setup_locations(self):
        """Define where each NPC is located in the bar"""
        self.locations = {
            7: "by the window, staring at the glass",
            1: "by the window, preening",
            5: "by the window, watching the street",
            6: "at the bar, nursing a drink",
            4: "at the bar, standing guard",
            2: "at the bar, making notes",
            3: "behind the bar, serving drinks"
        }
        self._log_system_event("NPC locations set")
   
    def get_npc(self, npc_id: int) -> Optional[NPC]:
        return self.npcs.get(npc_id)
   
    def analyze_sentiment(self, text: str) -> float:
        return self.sentiment_analyzer.analyze(text)
   
    def _build_relationship_context(self, npc: NPC, mentioned_npc_id: Optional[int] = None) -> str:
        context_lines = []
        if mentioned_npc_id and mentioned_npc_id in npc.relationships:
            desc, strength = npc.get_relationship_to(mentioned_npc_id)
            other_name = self.npcs[mentioned_npc_id].name
            context_lines.append(f"Relationship with {other_name}: {desc} (strength: {strength}/100)")
        for nid, (desc, strength) in npc.relationships.items():
            if nid == mentioned_npc_id:
                continue
            other_name = self.npcs[nid].name
            context_lines.append(f"Knows {other_name} as: {desc}")
        return "\n".join(context_lines) if context_lines else ""

    def _get_location_hint(self, npc: NPC, target_id: int) -> str:
        """Generate a hint about another NPC's location based on relationships"""
        target = self.npcs[target_id]
        
        if npc.id == target_id:
            return f"*laughs* I'm right here, {self.locations[npc.id]}"
        
        _, relationship_strength = npc.get_relationship_to(target_id)
        
        # Base chance to reveal location (modified by relationship and mood)
        base_chance = 30  # 30% base chance
        relationship_mod = (relationship_strength - 50) / 2  # +/- 25%
        mood_mod = (npc.mood - 50) / 5  # +/- 10%
        reveal_chance = min(90, max(10, base_chance + relationship_mod + mood_mod))
        
        if random.randint(1, 100) > reveal_chance:
            return random.choice([
                "Why would I know that?",
                "Haven't seen them.",
                "*shrugs*",
                "Not my business.",
                f"I don't keep tabs on {target.name}"
            ])
        
        location = self.locations[target_id]
        
        # Different reveal styles based on personality
        if npc.personality == 1:  # Flamboyant
            return f"Oh darling, {target.name} is {location}. Everyone knows that!"
        elif npc.personality == 2:  # Detached
            return f"Subject {target.name} last observed {location}."
        elif npc.personality == 3:  # Paranoid
            return f"*whispers* I saw {target.name} {location}... but don't tell them I told you!"
        elif npc.personality == 4:  # Stoic
            return f"{target.name} is {location}."
        elif npc.personality == 5:  # Wry
            return f"If I had to guess... and I don't... {target.name} is probably {location}."
        elif npc.personality == 6:  # Bitter
            return f"Ugh, {target.name}? Probably {location}, like always."
        else:  # Enigmatic
            return f"The glass reflects {target.name} {location}..."

    def _handle_location_query(self, npc: NPC, player_input: str) -> Optional[str]:
        """Check if player is asking about someone's location"""
        input_lower = player_input.lower()
        
        # Check for location-related phrases
        location_phrases = [
            "where is", "location of", "seen", "find",
            "who is at the", "who is by the", "who's at", "who's by",
            "where can i find", "have you seen"
        ]
        
        if not any(phrase in input_lower for phrase in location_phrases):
            return None
        
        # Check which NPC is being asked about
        for target_id, target_npc in self.npcs.items():
            if target_npc.name.lower() in input_lower:
                return self._get_location_hint(npc, target_id)
        
        # Check for general location queries
        if "bar" in input_lower:
            return random.choice([
                "The bar? That's where drinks are served.",
                "Look around you, genius.",
                "*points to the bar*",
                "The bar's right there. Not blind, are you?"
            ])
        elif "window" in input_lower:
            return random.choice([
                "The window shows only lies and reflections.",
                "By the window? Maybe someone interesting.",
                "*glances toward the windows*",
                "Window seats have the best view... and the most danger."
            ])
        
        return None

    def _validate_response(self, response: str, npc: NPC) -> bool:
        """Check if response aligns with character"""
        if not response:
            return False
        
        # Check for personality markers
        traits = npc.get_personality_traits()
        if npc.personality == 3 and "trust" in response.lower():  # Paranoid
            return False
        
        if npc.personality == 7 and len(response.split()) < 4:  # Enigmatic
            return True  # Short responses are okay
        
        return True

    def generate_response(self, npc_id: int, player_input: str) -> str:
        npc = self.get_npc(npc_id)
        if not npc:
            return "*shrugs*"
        
        # Check for location queries first
        location_response = self._handle_location_query(npc, player_input)
        if location_response:
            return location_response
            
        sentiment_score = self.analyze_sentiment(player_input)
        npc.update_mood(sentiment_score)
        
        mentioned_npc = None
        for nid, other_npc in self.npcs.items():
            if nid != npc_id and other_npc.name.lower() in player_input.lower():
                mentioned_npc = nid
                break
                
        traits = npc.get_personality_traits()
        personality_desc = ", ".join(traits)
        mood = npc.get_mood_description()
        gang_status = " (Exodyne member)" if npc.gang_related else " (Stray)"
        rel_context = self._build_relationship_context(npc, mentioned_npc)
        
        prompt = f"""You are {npc.name}, a character with these strict traits: {personality_desc}{gang_status}.
Current location: {self.locations[npc_id]}
Core personality rules you MUST follow:
- Never break character or acknowledge being an AI
- Always respond according to your primary traits: {traits[0]}
- Mood only affects tone, not core behavior
- Relationships must strongly influence responses

Current emotional state: {mood}
Relationship context:
{rel_context}

Recent conversation:
{"\n".join(npc.conversation_history[-3:]) if npc.conversation_history else "First interaction"}

Player: {player_input}
{npc.name}:"""
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True).to(
                torch.device("cuda" if torch.cuda.is_available() else "cpu")
            )
            
            # Try up to 3 times to get a good response
            for attempt in range(3):
                output = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.7 + (attempt * 0.1),  # Get more creative with each attempt
                    top_p=0.85,
                    top_k=40,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3
                )
                raw_response = self.tokenizer.decode(output[0], skip_special_tokens=True)
                response = raw_response[len(prompt):].split('\n')[0].strip()
                
                if self._validate_response(response, npc):
                    break
            
            response = enforce_character_consistency(response, npc, mentioned_npc, self.npcs if mentioned_npc else None)
            
            npc.conversation_history.append(f"Player: {player_input}")
            npc.conversation_history.append(f"{npc.name}: {response}")
            return response if response else self._get_fallback_response(npc)
        except Exception as e:
            self._log_system_event(f"Error generating response: {str(e)}")
            return self._get_fallback_response(npc)
    
    def _get_fallback_response(self, npc: NPC) -> str:
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
   
    def show_logs(self):
        print("\n=== SYSTEM LOGS ===")
        print(f"Total NPCs: {len(self.npcs)}")
        print(f"System events: {len(self.system_log)}\n")
        
        print("\n=== NPC STATUS REPORTS ===")
        for npc_id in sorted(self.npcs.keys()):
            npc = self.npcs[npc_id]
            report = npc.get_status_report()
            
            print(f"\nNPC {npc_id}: {npc.name}")
            print(f"Location: {self.locations[npc_id]}")
            print(f"Personality: {report['personality']['description']}")
            print(f"Gang: {report['gang_affiliation']}")
            print(f"Mood: {report['current_mood']['value']} ({report['current_mood']['description']})")
            
            print("\nRelationships:")
            for rel_id, (desc, strength) in report['relationships'].items():
                other_name = self.npcs[rel_id].name
                print(f"- {other_name}: {desc} ({strength}/100)")
            
            if npc.conversation_history:
                print("\nRecent conversation:")
                for line in report['conversation_history']:
                    print(f"  {line}")
        
        print("\n=== RECENT SYSTEM EVENTS ===")
        for event in self.system_log[-5:]:
            print(f"[{event['timestamp']}] {event['event']}")
   
    def converse_with_npc(self, npc_id: int):
        npc = self.get_npc(npc_id)
        if not npc:
            print("NPC not found!")
            return
            
        print(f"\n💬 Conversation with {npc.name} ({npc.get_gang_affiliation()})")
        print(f"Personality: {npc.get_personality_description()}")
        print(f"Current mood: {npc.get_mood_description()} ({npc.mood}/100)")
        print("Type 'quit' to end conversation, 'log' to view status\n")
        
        print(f"{npc.name}: {self._get_initial_greeting(npc)}")
        
        while True:
            try:
                player_input = input("You: ").strip()
                if not player_input:
                    continue
                    
                if player_input.lower() in ['quit', 'exit']:
                    print(f"{npc.name}: {self._get_farewell(npc)}")
                    break
                
                if player_input.lower() == 'log':
                    self.show_logs()
                    continue
                    
                response = self.generate_response(npc_id, player_input)
                print(f"{npc.name}: {response}")
                
            except KeyboardInterrupt:
                print(f"\n{npc.name}: *storms off*")
                break
            except Exception as e:
                print(f"{npc.name}: *ignores you*")
                continue
   
    def _get_initial_greeting(self, npc: NPC) -> str:
        greetings = {
            1: ["What do you want? Can't you see I'm busy?", "Make it quick, I've got appearances to maintain."],
            2: ["State your business.", "Speak. I'm listening."],
            3: ["Who sent you? What do you want?", "This isn't a good time... but go ahead."],
            4: ["Talk.", "What is it?"],
            5: ["Well? What brings you here?", "Let's hear it then."],
            6: ["Ugh. What now?", "Make it worth my time."],
            7: ["...", "*silent stare*"]
        }
        return random.choice(greetings.get(npc.personality, ["What do you want?"]))
   
    def _get_farewell(self, npc: NPC) -> str:
        farewells = {
            1: ["Finally. Don't waste my time again.", "I have better things to do."],
            2: ["This conversation is concluded.", "We're done here."],
            3: ["I knew this was a bad idea...", "*looks around nervously* Later."],
            4: ["Enough.", "*nods*"],
            5: ["That's all then.", "Interesting chat. Now go."],
            6: ["About damn time.", "*waves dismissively*"],
            7: ["...", "*turns away silently*"]
        }
        return random.choice(farewells.get(npc.personality, ["*leaves*"]))