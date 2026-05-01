# Act as a Senior Python Developer and Game Designer.
Build a terminal-based grand strategy game titled "AUSTRA-NULL". 
The game uses a local LLM (via OpenAI-compatible API) for narrative and diplomacy.

## Technical Specifications
1. **Language:** Python 3.10+
2. **Environment:** Use `.env` to store `LLM_API_BASE`, `LLM_API_KEY`, and `LLM_MODEL`.
3. **State Management:** - All world data MUST persist in `EARTH.md`. 
   - The LLM should read this file at the start of a turn and update it at the end.
   - Format: Markdown tables for stats, bullet points for history.
4. **UI:** Use the `rich` library for a beautiful terminal interface and ASCII maps.

## Game Features
1. **Setting:** A fictionally fractured Australia. Regions: 
   - The Emu Empire (WA)
   - The Great Sandy Republic (NT)
   - The Iron Range Syndicate (QLD)
   - The Sydney Commune (NSW)
   - The Bass Strait Union (VIC/TAS)
   - The Nullarbor Nomads (SA)
2. **World Map:** A static ASCII map of Australia displayed in the terminal. Color-code regions based on the player's status with them.
3. **Gameplay Loop:**
   - **Start/Reset:** Ability to wipe `EARTH.md` and start fresh.
   - **Custom Start:** Allow the user to input a starting Year/Month (e.g., "January 2077").
   - **Batch Actions:** Player types multiple commands (e.g., "Build factory in Perth; Send envoy to Sydney") before hitting "End Turn".
4. **Diplomacy:** A "Chat with Nation" mode where the LLM assumes the persona of a specific regional leader based on their "Personality" trait in `EARTH.md`.
5. **Oracle Mode:** A specific command to "Consult the Archives" where the LLM answers questions about the world state without progressing time.

## Local LLM Optimization (Token Economy)
- **State Compression:** Only send the *current* region's stats and the *immediate* neighbors' status to the LLM during turn processing, not the entire `EARTH.md` if it gets too long.
- **Narrative Logic:** Use the LLM to generate "World Events" (e.g., "Dust storm hits the Nullarbor") and "Diplomatic Responses." Use local Python logic for math (Resource management, troop movements).

## Additional Strategic Depth
- **Stability Score:** Each region has a 0-100 stability. If it hits 0, a "Fracture Event" occurs (LLM-generated).
- **Secret Personalities:** On reset, assign hidden traits to AI nations (e.g., "Paranoid," "Expansionist," "Technophile") that dictate their diplomatic tone.
- **The 'Black Box' Log:** Maintain a `log.json` for technical debugging and a `history.txt` for the player's "chronicle."

## Development Steps
1. Create the `.env` template and `main.py` entry point.
2. Implement the `EARTH.md` parser and writer.
3. Build the ASCII map renderer.
4. Implement the "Action Parser" that batches player inputs.
5. Connect the LLM wrapper with a configurable system prompt that emphasizes brevity.