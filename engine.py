import json
import re
import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Region:
    def __init__(self, name: str, abbr: str, stability: int, personality: str, status_with_player: str, wealth: int = 50, troops: int = 100):
        self.name = name
        self.abbr = abbr
        self.stability = stability
        self.personality = personality
        self.status_with_player = status_with_player
        self.wealth = wealth
        self.troops = troops

class GameState:
    def __init__(self):
        self.year = 2077
        self.month = "January"
        self.regions: Dict[str, Region] = {}
        self.history: List[str] = []
        self.player_wealth = 100
        self.player_troops = 500
        self.llm_client = OpenAI(
            base_url=os.getenv("LLM_API_BASE"),
            api_key=os.getenv("LLM_API_KEY", "sk-1234")
        )
        self.model = os.getenv("LLM_MODEL", "llama3")

    def reset(self, start_date: str = "January 2077"):
        parts = start_date.split()
        if len(parts) == 2:
            self.month, year_str = parts
            self.year = int(year_str)

        import random
        personalities = ["Paranoid", "Expansionist", "Technophile", "Isolationist", "Aggressive", "Diplomatic"]
        random.shuffle(personalities)

        self.regions = {
            "WA": Region("The Emu Empire", "WA", 80, personalities[0], "Neutral"),
            "NT": Region("The Great Sandy Republic", "NT", 70, personalities[1], "Neutral"),
            "QLD": Region("The Iron Range Syndicate", "QLD", 60, personalities[2], "Neutral"),
            "NSW": Region("The Sydney Commune", "NSW", 50, personalities[3], "Neutral"),
            "VIC": Region("The Bass Strait Union", "VIC", 75, personalities[4], "Neutral"),
            "SA": Region("The Nullarbor Nomads", "SA", 65, personalities[5], "Neutral"),
        }
        self.player_wealth = 100
        self.player_troops = 500
        self.history = [f"Game started in {self.month} {self.year}."]
        self.save_to_earth()
        self.log_event("Game reset.")

    def load_from_earth(self):
        if not os.path.exists("EARTH.md"):
            self.reset()
            return

        with open("EARTH.md", "r") as f:
            content = f.read()

        date_match = re.search(r"## Date: (\w+) (\d+)", content)
        if date_match:
            self.month = date_match.group(1)
            self.year = int(date_match.group(2))

        player_match = re.search(r"## Player: Wealth (\d+), Troops (\d+)", content)
        if player_match:
            self.player_wealth = int(player_match.group(1))
            self.player_troops = int(player_match.group(2))

        self.regions = {}
        in_table = False
        for line in content.split('\n'):
            if line.startswith("| Region"):
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 7:
                    name, abbr, stability, personality, status, wealth, troops = parts[:7]
                    self.regions[abbr] = Region(name, abbr, int(stability), personality, status, int(wealth), int(troops))
                elif len(parts) >= 5:
                    name, abbr, stability, personality, status = parts[:5]
                    self.regions[abbr] = Region(name, abbr, int(stability), personality, status)
            elif in_table and not line.strip():
                in_table = False

        self.history = []
        in_history = False
        for line in content.split('\n'):
            if line.startswith("## History"):
                in_history = True
                continue
            if in_history and line.startswith("- "):
                self.history.append(line[2:].strip())
            elif in_history and line.startswith("##"):
                in_history = False

    def save_to_earth(self):
        with open("EARTH.md", "w") as f:
            f.write("# AUSTRA-NULL World State\n\n")
            f.write(f"## Date: {self.month} {self.year}\n")
            f.write(f"## Player: Wealth {self.player_wealth}, Troops {self.player_troops}\n\n")
            f.write("## Regions\n\n")
            f.write("| Region | Abbr | Stability | Personality | Status with Player | Wealth | Troops |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for abbr, r in self.regions.items():
                f.write(f"| {r.name} | {r.abbr} | {r.stability} | {r.personality} | {r.status_with_player} | {r.wealth} | {r.troops} |\n")
            f.write("\n## History\n\n")
            for h in self.history[-10:]:
                f.write(f"- {h}\n")

    def log_event(self, message: str):
        log_entry = {"date": f"{self.month} {self.year}", "message": message}
        mode = "a" if os.path.exists("log.json") else "w"
        with open("log.json", mode) as f:
            f.write(json.dumps(log_entry) + "\n")

        with open("history.txt", "a") as f:
            f.write(f"[{self.month} {self.year}] {message}\n")

    def parse_action(self, action: str) -> str:
        """Parses player action, applying local math for resources and returning a summary."""
        action_lower = action.lower().strip()
        
        if "build factory in" in action_lower:
            abbr = action_lower.split("in")[-1].strip().upper()
            if abbr in self.regions:
                if self.player_wealth >= 50:
                    self.player_wealth -= 50
                    self.regions[abbr].wealth += 20
                    self.regions[abbr].stability = min(100, self.regions[abbr].stability + 10)
                    return f"Built a factory in {abbr}. (-50 Player Wealth, +20 {abbr} Wealth, +10 Stability)"
                else:
                    return f"Failed to build factory in {abbr}: insufficient wealth."
            else:
                return f"Failed to build factory: {abbr} not found."
                
        match = re.search(r"deploy (\d+) troops to ([a-z]+)", action_lower)
        if match:
            amount = int(match.group(1))
            abbr = match.group(2).upper()
            if abbr in self.regions:
                if self.player_troops >= amount:
                    self.player_troops -= amount
                    self.regions[abbr].troops += amount
                    self.regions[abbr].status_with_player = "Hostile" if amount > 200 else self.regions[abbr].status_with_player
                    return f"Deployed {amount} troops to {abbr}. (-{amount} Player Troops, +{amount} {abbr} Troops)"
                else:
                    return f"Failed to deploy troops to {abbr}: insufficient troops."
            else:
                return f"Failed to deploy troops: {abbr} not found."

        if "send envoy to" in action_lower:
            abbr = action_lower.split("to")[-1].strip().upper()
            if abbr in self.regions:
                if self.player_wealth >= 10:
                    self.player_wealth -= 10
                    self.regions[abbr].stability = min(100, self.regions[abbr].stability + 5)
                    if self.regions[abbr].status_with_player == "Hostile":
                        self.regions[abbr].status_with_player = "Neutral"
                    elif self.regions[abbr].status_with_player == "Neutral":
                        self.regions[abbr].status_with_player = "Friendly"
                    return f"Sent an envoy to {abbr}. (-10 Player Wealth, Relations Improved)"
                else:
                    return f"Failed to send envoy to {abbr}: insufficient wealth."
            else:
                return f"Failed to send envoy: {abbr} not found."

        return f"Issued order: {action}"

    def process_turn(self, actions: List[str]) -> str:
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        idx = months.index(self.month)
        if idx == 11:
            self.month = months[0]
            self.year += 1
        else:
            self.month = months[idx + 1]

        parsed_results = []
        affected_regions = set()
        
        for action in actions:
            res = self.parse_action(action)
            parsed_results.append(res)
            for abbr in self.regions:
                if abbr.lower() in action.lower():
                    affected_regions.add(abbr)

        prompt = f"You are the game engine for AUSTRA-NULL. Current Date: {self.month} {self.year}.\n"
        prompt += "Player actions and local math results:\n" + "\n".join(f"- {r}" for r in parsed_results) + "\n"
        prompt += "Generate a brief narrative summary of the turn's events, including any consequences of the player's actions and one random world event. Keep it under 4 sentences."

        compressed_state = "Relevant Regional States:\n"
        if not affected_regions:
            import random
            affected_regions.add(random.choice(list(self.regions.keys())))
            
        for abbr in affected_regions:
            r = self.regions[abbr]
            compressed_state += f"- {r.name} ({r.abbr}): Stability {r.stability}, Status {r.status_with_player}, Wealth {r.wealth}, Troops {r.troops}\n"
            
        prompt += "\n" + compressed_state

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a concise, atmospheric strategy game narrator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            narrative = response.choices[0].message.content.strip()
        except Exception as e:
            narrative = f"The turn passed, but the archives are silent. (Error: {e})"

        self.history.append(narrative)
        self.log_event(f"Actions: {actions} -> {narrative}")

        import random
        for r in self.regions.values():
            r.stability += random.randint(-5, 5)
            r.stability = max(0, min(100, r.stability))
            if r.stability == 0:
                self.history.append(f"FRACTURE EVENT in {r.name}!")

        self.save_to_earth()
        return narrative

    def chat_with_nation(self, abbr: str, message: str) -> str:
        if abbr not in self.regions:
            return "Nation not found."
        region = self.regions[abbr]

        system_prompt = f"You are the leader of {region.name}. Your personality is {region.personality}. The player's status with you is {region.status_with_player}. Respond to the player's message in character. Keep it brief, 1-2 sentences."

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Communication failed. (Error: {e})"

    def consult_oracle(self, question: str) -> str:
        state_summary = f"Date: {self.month} {self.year}\n"
        for r in self.regions.values():
            state_summary += f"{r.name} ({r.abbr}): Stability {r.stability}, Status {r.status_with_player}\n"

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are the Oracle of AUSTRA-NULL, an AI archivist. Answer the player's question based on the current world state. Be cryptic but helpful. Keep it brief."},
                    {"role": "user", "content": f"World State:\n{state_summary}\n\nQuestion: {question}"}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"The Oracle is offline. (Error: {e})"
