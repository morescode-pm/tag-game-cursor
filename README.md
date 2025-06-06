# Cartoon Tag Game

A fun, local tag game where you play as a rabbit against multiple AI hunters in a 2D arena! The game features obstacles, edge wrapping, cartoon-style sprites, and advanced tag rules for a dynamic experience.

## Features
- **Play as a rabbit** (arrow keys) against multiple AI hunters
- **Obstacles** and **corner barriers** for strategic movement
- **Edge wrapping** (Pac-Man style), but corners are blocked
- **No tag backs** within 3 seconds
- **Freeze** for 2 seconds after being tagged
- **Repel effect**: after a tag, all other players are pushed away from the new "it"
- **AI is imperfect** (makes mistakes for more fun)
- **Cartoon-style sprites** (rabbit and hunters)
- **Adjustable number of AI players**

## Setup
1. **Install Python 3.7+**
2. **Install Pygame**
   ```bash
   pip install pygame
   ```
3. **Download or clone this repository**

## How to Play
1. Run the game:
   ```bash
   python tag_game.py
   ```
2. Use the **arrow keys** to move your rabbit.
3. Avoid being tagged by the hunters! If you become "it", chase and tag another player.

## Controls
- **Arrow keys**: Move your rabbit
- **Close window**: Quit the game

## Adjusting the Number of AI Players
- Open `tag_game.py`
- Change the value of `NUM_AI` at the top of the file to your desired number of AI hunters (e.g., `NUM_AI = 3`)

## Game Rules
- Only one player is "it" at a time
- After a tag:
  - The new "it" is frozen for 2 seconds
  - No tag backs for 3 seconds
  - All other players are repelled away from the new "it"
- Edge wrapping is allowed, but corners are blocked by barriers
- AI hunters are imperfect and make mistakes for a more fun experience

## Credits
- Game logic and sprites: Generated by AI
- Inspired by classic cartoons and tag games

Enjoy the chase! 