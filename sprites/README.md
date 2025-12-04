# Sprites Directory

This directory contains generated sprite assets for Anterix Spectrum Defender.

## Sprite Generation

Sprites are generated using OpenAI's DALL-E API via the Python script in `/scripts/generate_sprites.py`.

### Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API Key** with DALL-E access

### Setup

```bash
# Navigate to scripts directory
cd scripts

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
# Windows:
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac:
export OPENAI_API_KEY=your-api-key-here
```

### Generate Sprites

```bash
# List all available sprites
python generate_sprites.py --list

# Generate a single sprite
python generate_sprites.py --sprite player_ship

# Generate ALL sprites (may take several minutes and API credits)
python generate_sprites.py --all
```

## Available Sprites

| Sprite Name | Filename | Description |
|-------------|----------|-------------|
| player_ship | player_ship.png | Player spaceship shaped like letter A |
| player_ship_thrust | player_ship_thrust.png | Player ship with engine thrust |
| signal_disruptor | signal_disruptor.png | Signal interference enemy |
| data_packet | data_packet.png | Fast moving bonus enemy |
| network_node_large | network_node_large.png | Large splitting enemy |
| network_node_medium | network_node_medium.png | Medium splitting enemy |
| network_node_small | network_node_small.png | Small splitting enemy |
| legacy_tower | legacy_tower.png | Old infrastructure asteroid |
| spectrum_jammer | spectrum_jammer.png | Boss enemy |
| powerup_bandwidth | powerup_bandwidth.png | Rapid fire power-up |
| powerup_shield | powerup_shield.png | Invincibility power-up |
| powerup_spread | powerup_spread.png | Triple shot power-up |
| powerup_surge | powerup_surge.png | Screen-clear bomb power-up |
| projectile_player | projectile_player.png | Player laser beam |
| explosion_1-4 | explosion_*.png | Explosion animation frames |
| title_logo | title_logo.png | Game title logo |

## Integration with Game

The game (`index.html`) currently uses Canvas-drawn vector graphics. To use generated sprites instead:

1. Generate sprites using the script above
2. Modify the game's draw methods to load and render sprite images
3. Example sprite loading code:

```javascript
// In the game initialization
const sprites = {};

async function loadSprites() {
    const spriteNames = ['player_ship', 'signal_disruptor', /* ... */];
    
    for (const name of spriteNames) {
        const img = new Image();
        img.src = `sprites/${name}.png`;
        await new Promise(resolve => img.onload = resolve);
        sprites[name] = img;
    }
}

// In the draw method
ctx.drawImage(sprites['player_ship'], x - width/2, y - height/2, width, height);
```

## Notes

- DALL-E generates 1024x1024 images which should be scaled down for the game
- Generated sprites have black backgrounds (use as transparency key or manually edit)
- Each sprite generation costs OpenAI API credits
- Generation may take 10-30 seconds per sprite

## Style Guidelines

All sprites should follow these visual guidelines:

- **Color Palette**: Neon cyan (#00FFFF), magenta (#FF00FF), yellow (#FFFF00), with black background
- **Style**: 32-bit retro pixel art with glow effects
- **Aesthetic**: Classic arcade games (Asteroids, Space Invaders, Tempest)
- **Theme**: Telecommunications / spectrum / network infrastructure
