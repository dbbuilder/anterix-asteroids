#!/usr/bin/env python3
"""
============================================================
ANTERIX SPECTRUM DEFENDER - DALL-E SPRITE GENERATOR
============================================================

This script generates retro-style pixel art sprites for the
Anterix Spectrum Defender game using OpenAI's DALL-E API.

Usage:
    python generate_sprites.py [--all] [--sprite <name>] [--list]

Environment Variables:
    OPENAI_API_KEY: Your OpenAI API key (required)

Output:
    Sprites are saved to ../sprites/ directory as PNG files
============================================================
"""

import os
import sys
import json
import logging
import argparse
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional

# Third-party imports with error handling
try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)

try:
    from PIL import Image
    import io
except ImportError:
    print("ERROR: Pillow package not installed. Run: pip install Pillow")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("WARNING: python-dotenv not installed. Using environment variables directly.")
    load_dotenv = None

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not available
    def tqdm(iterable, **kwargs):
        return iterable

try:
    import colorlog
    
    # Configure colored logging
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s]%(reset)s %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
except ImportError:
    # Fallback to standard logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

# Output directory for generated sprites
SPRITES_DIR = Path(__file__).parent.parent / "sprites"

# DALL-E configuration
DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1024x1024"
DALLE_QUALITY = "standard"

# Color palette for the game (neon retro)
COLOR_PALETTE = {
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "yellow": "#ffff00",
    "red": "#ff0000",
    "green": "#00ff00",
    "orange": "#ff6600",
    "background": "#0a0a12"
}

# ============================================================
# SPRITE DEFINITIONS
# ============================================================
# Each sprite has a name, description, and detailed DALL-E prompt

SPRITE_DEFINITIONS = {
    # Player ship - "A" made of vertical lines
    "player_ship": {
        "filename": "player_ship.png",
        "description": "Player spaceship shaped like letter A",
        "prompt": """Create a pixel art sprite of a spaceship shaped like the capital letter "A" made entirely of vertical glowing cyan lines. 

Style requirements:
- 32-bit retro pixel art style
- The ship is the letter "A" rotated so the point faces upward
- Made of multiple parallel vertical cyan (#00FFFF) glowing lines
- Neon glow effect around the lines
- Transparent background (use solid black #000000 for transparency keying)
- Size should fill most of the 1024x1024 canvas
- Clean, crisp pixel edges
- Slight blue-white glow emanating from the lines
- The crossbar of the "A" should also be visible as horizontal lines

The aesthetic should match classic arcade games like Asteroids and Tempest with vector-style graphics."""
    },
    
    # Player ship with thrust
    "player_ship_thrust": {
        "filename": "player_ship_thrust.png",
        "description": "Player spaceship with engine thrust",
        "prompt": """Create a pixel art sprite of a spaceship shaped like the capital letter "A" made of vertical glowing cyan lines, with an orange/yellow thrust flame coming from the bottom.

Style requirements:
- 32-bit retro pixel art style
- The ship is the letter "A" rotated so the point faces upward
- Made of multiple parallel vertical cyan (#00FFFF) glowing lines
- Orange (#FF6600) and yellow thrust flame at the bottom
- Neon glow effect around the lines and flame
- Transparent background (use solid black #000000 for transparency keying)
- Size should fill most of the 1024x1024 canvas
- Clean, crisp pixel edges
- The thrust flame should look like classic arcade thruster fire

The aesthetic should match classic arcade games like Asteroids with vector-style graphics."""
    },
    
    # Signal Disruptor enemy
    "signal_disruptor": {
        "filename": "signal_disruptor.png",
        "description": "Signal interference enemy",
        "prompt": """Create a pixel art sprite of an alien enemy representing signal interference/disruption.

Style requirements:
- 32-bit retro pixel art style
- Circular shape with a zigzag/sine wave pattern inside
- Magenta (#FF00FF) color with neon glow
- Looks like a radio wave or signal being disrupted
- Should appear slightly menacing but abstract
- Transparent background (use solid black #000000 for transparency keying)
- Size: circular, about 64x64 pixels scaled up to fill canvas
- Clean, crisp pixel edges
- Pulsing glow effect appearance

The aesthetic should match Space Invaders but with a telecommunications theme."""
    },
    
    # Data Packet enemy (bonus target)
    "data_packet": {
        "filename": "data_packet.png",
        "description": "Fast moving data packet bonus enemy",
        "prompt": """Create a pixel art sprite of a small, fast data packet enemy.

Style requirements:
- 32-bit retro pixel art style
- Small square/rectangular shape representing a data packet
- Lime green (#66FF33) color with neon glow
- Binary-style dots or "10" pattern inside
- Appears to be moving fast (motion lines optional)
- Transparent background (use solid black #000000 for transparency keying)
- Size: small, about 32x32 pixels scaled up to fill canvas
- Clean, crisp pixel edges
- Should look like digital data in transit

The aesthetic should be retro-futuristic like Tron."""
    },
    
    # Network Node enemy (splits when destroyed)
    "network_node_large": {
        "filename": "network_node_large.png",
        "description": "Large network node that splits",
        "prompt": """Create a pixel art sprite of a large network node/hub enemy.

Style requirements:
- 32-bit retro pixel art style
- Hexagonal shape representing a network node
- Pink-red (#FF3366) color with neon glow
- Internal connecting lines like a network diagram
- Center dot representing the node core
- Transparent background (use solid black #000000 for transparency keying)
- Size: large hexagon, about 100x100 pixels scaled up
- Clean, crisp pixel edges
- Should look like network infrastructure

The aesthetic should be cyberpunk/tech style."""
    },
    
    "network_node_medium": {
        "filename": "network_node_medium.png",
        "description": "Medium network node",
        "prompt": """Create a pixel art sprite of a medium-sized network node enemy.

Style requirements:
- 32-bit retro pixel art style
- Hexagonal shape, smaller than parent
- Pink-red (#FF3366) color with neon glow
- Simpler internal pattern than the large version
- Center dot representing the node core
- Transparent background (use solid black #000000 for transparency keying)
- Size: medium hexagon, about 72x72 pixels scaled up
- Clean, crisp pixel edges

Same style as the large network node but smaller and simpler."""
    },
    
    "network_node_small": {
        "filename": "network_node_small.png",
        "description": "Small network node",
        "prompt": """Create a pixel art sprite of a small network node enemy.

Style requirements:
- 32-bit retro pixel art style
- Hexagonal shape, smallest version
- Pink-red (#FF3366) color with neon glow
- Minimal internal detail, mostly solid with glow
- Transparent background (use solid black #000000 for transparency keying)
- Size: small hexagon, about 40x40 pixels scaled up
- Clean, crisp pixel edges

Same style as the larger network nodes but smallest and simplest."""
    },
    
    # Legacy Tower (asteroid-like)
    "legacy_tower": {
        "filename": "legacy_tower.png",
        "description": "Old infrastructure asteroid",
        "prompt": """Create a pixel art sprite of an old, decommissioned communication tower floating in space like an asteroid.

Style requirements:
- 32-bit retro pixel art style
- Irregular rocky asteroid shape with an old antenna/tower on top
- Gray (#888888) color - appears old and outdated
- Subtle darker shadows and lighter highlights
- Small antenna or transmission tower element visible
- Transparent background (use solid black #000000 for transparency keying)
- Size: large irregular shape, about 140x140 pixels scaled up
- Clean, crisp pixel edges
- Should look like abandoned space debris

The aesthetic should be like Asteroids but with tech infrastructure elements."""
    },
    
    # Spectrum Jammer (Boss)
    "spectrum_jammer": {
        "filename": "spectrum_jammer.png",
        "description": "Boss enemy - spectrum jamming device",
        "prompt": """Create a pixel art sprite of a large, menacing spectrum jamming device boss enemy.

Style requirements:
- 32-bit retro pixel art style
- Large circular shape with multiple concentric rings
- Bright red (#FF0000) primary color with neon glow
- Internal radial lines emanating from center (jamming waves)
- Multiple rings: outer ring, middle ring, inner core
- Appears powerful and dangerous
- Transparent background (use solid black #000000 for transparency keying)
- Size: large, about 200x200 pixels scaled up to fill canvas
- Clean, crisp pixel edges
- Pulsing/energy effect appearance

The aesthetic should be intimidating boss enemy style from classic arcade shooters."""
    },
    
    # Power-ups
    "powerup_bandwidth": {
        "filename": "powerup_bandwidth.png",
        "description": "Bandwidth boost power-up (rapid fire)",
        "prompt": """Create a pixel art sprite of a "Bandwidth Boost" power-up icon.

Style requirements:
- 32-bit retro pixel art style
- Circular outer ring with inner square
- Light blue (#00AAFF) color with neon glow
- Letter "B" in the center
- Spinning/rotating appearance
- Transparent background (use solid black #000000 for transparency keying)
- Size: about 60x60 pixels scaled up
- Clean, crisp pixel edges
- Collectible power-up appearance

Should look like a beneficial pickup item from arcade games."""
    },
    
    "powerup_shield": {
        "filename": "powerup_shield.png",
        "description": "Signal shield power-up (invincibility)",
        "prompt": """Create a pixel art sprite of a "Signal Shield" power-up icon.

Style requirements:
- 32-bit retro pixel art style
- Circular outer ring with inner square
- Bright green (#00FF00) color with neon glow
- Letter "S" in the center
- Protective/defensive appearance
- Transparent background (use solid black #000000 for transparency keying)
- Size: about 60x60 pixels scaled up
- Clean, crisp pixel edges
- Collectible power-up appearance

Should look like a shield/defense pickup from arcade games."""
    },
    
    "powerup_spread": {
        "filename": "powerup_spread.png",
        "description": "Spectrum spread power-up (triple shot)",
        "prompt": """Create a pixel art sprite of a "Spectrum Spread" power-up icon.

Style requirements:
- 32-bit retro pixel art style
- Circular outer ring with inner square
- Bright yellow (#FFFF00) color with neon glow
- Number "3" in the center (representing triple shot)
- Spreading/expanding appearance
- Transparent background (use solid black #000000 for transparency keying)
- Size: about 60x60 pixels scaled up
- Clean, crisp pixel edges
- Collectible power-up appearance

Should look like a weapon upgrade pickup from arcade games."""
    },
    
    "powerup_surge": {
        "filename": "powerup_surge.png",
        "description": "Network surge power-up (bomb)",
        "prompt": """Create a pixel art sprite of a "Network Surge" power-up icon (screen-clearing bomb).

Style requirements:
- 32-bit retro pixel art style
- Circular outer ring with inner square
- Hot pink/red (#FF0066) color with neon glow
- Exclamation mark "!" in the center
- Explosive/powerful appearance
- Transparent background (use solid black #000000 for transparency keying)
- Size: about 60x60 pixels scaled up
- Clean, crisp pixel edges
- Rare/powerful collectible appearance

Should look like a special weapon pickup from arcade games."""
    },
    
    # Projectile
    "projectile_player": {
        "filename": "projectile_player.png",
        "description": "Player spectrum beam projectile",
        "prompt": """Create a pixel art sprite of a player's "Spectrum Beam" projectile.

Style requirements:
- 32-bit retro pixel art style
- Elongated ellipse/beam shape
- Bright yellow (#FFFF00) color with neon glow
- Energy beam appearance
- Transparent background (use solid black #000000 for transparency keying)
- Size: elongated, about 24x8 pixels scaled up
- Clean, crisp pixel edges
- Fast-moving energy appearance

Should look like a laser/beam from classic space shooters."""
    },
    
    # Explosion frames
    "explosion_1": {
        "filename": "explosion_1.png",
        "description": "Explosion animation frame 1",
        "prompt": """Create a pixel art sprite of an explosion, frame 1 of 4 (smallest/beginning).

Style requirements:
- 32-bit retro pixel art style
- Small starburst/explosion shape
- Orange, yellow, and white colors
- Beginning of explosion - compact
- Transparent background (use solid black #000000 for transparency keying)
- Size: small, about 32x32 pixels scaled up
- Clean, crisp pixel edges

Classic arcade explosion beginning frame."""
    },
    
    "explosion_2": {
        "filename": "explosion_2.png",
        "description": "Explosion animation frame 2",
        "prompt": """Create a pixel art sprite of an explosion, frame 2 of 4 (expanding).

Style requirements:
- 32-bit retro pixel art style
- Medium expanding explosion shape
- Orange, yellow, and white colors
- Explosion expanding outward
- Transparent background (use solid black #000000 for transparency keying)
- Size: medium, about 64x64 pixels scaled up
- Clean, crisp pixel edges

Classic arcade explosion mid frame."""
    },
    
    "explosion_3": {
        "filename": "explosion_3.png",
        "description": "Explosion animation frame 3",
        "prompt": """Create a pixel art sprite of an explosion, frame 3 of 4 (large).

Style requirements:
- 32-bit retro pixel art style
- Large explosion shape
- Orange, yellow, red, and white colors
- Explosion at maximum size
- Transparent background (use solid black #000000 for transparency keying)
- Size: large, about 96x96 pixels scaled up
- Clean, crisp pixel edges

Classic arcade explosion peak frame."""
    },
    
    "explosion_4": {
        "filename": "explosion_4.png",
        "description": "Explosion animation frame 4",
        "prompt": """Create a pixel art sprite of an explosion, frame 4 of 4 (dissipating).

Style requirements:
- 32-bit retro pixel art style
- Dissipating explosion particles
- Fading orange, yellow, and gray colors
- Explosion breaking apart and fading
- Transparent background (use solid black #000000 for transparency keying)
- Size: large but sparse, about 96x96 pixels scaled up
- Clean, crisp pixel edges

Classic arcade explosion ending frame."""
    },
    
    # Title logo
    "title_logo": {
        "filename": "title_logo.png",
        "description": "Anterix game title logo",
        "prompt": """Create a pixel art logo for "ANTERIX SPECTRUM DEFENDER" arcade game.

Style requirements:
- 32-bit retro pixel art style
- Text "ANTERIX" in large bold letters at top
- Text "SPECTRUM DEFENDER" below in slightly smaller letters
- Cyan (#00FFFF) and Magenta (#FF00FF) neon colors
- Retro arcade game title style
- Glowing neon effect
- Transparent background (use solid black #000000 for transparency keying)
- Size: wide banner, fills the canvas
- Clean, crisp pixel edges
- 80s arcade aesthetic

Should look like a classic arcade game title screen."""
    }
}


# ============================================================
# SPRITE GENERATOR CLASS
# ============================================================

class SpriteGenerator:
    """
    Handles sprite generation using OpenAI's DALL-E API.
    
    This class manages:
    - API connection and authentication
    - Sprite generation from prompts
    - Image saving and post-processing
    - Error handling and retries
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the sprite generator.
        
        Args:
            api_key: OpenAI API key (if not provided, uses environment variable)
        """
        # Load environment variables from .env file if available
        if load_dotenv:
            load_dotenv()
        
        # Get API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
        
        # Ensure sprites directory exists
        SPRITES_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Sprites directory: {SPRITES_DIR}")
    
    def generate_sprite(self, sprite_name: str) -> Optional[Path]:
        """
        Generate a single sprite using DALL-E.
        
        Args:
            sprite_name: Name of the sprite from SPRITE_DEFINITIONS
            
        Returns:
            Path to saved sprite file, or None if generation failed
        """
        if sprite_name not in SPRITE_DEFINITIONS:
            logger.error(f"Unknown sprite: {sprite_name}")
            logger.info(f"Available sprites: {', '.join(SPRITE_DEFINITIONS.keys())}")
            return None
        
        sprite_def = SPRITE_DEFINITIONS[sprite_name]
        filename = sprite_def["filename"]
        prompt = sprite_def["prompt"]
        description = sprite_def["description"]
        
        logger.info(f"Generating sprite: {sprite_name} ({description})")
        
        try:
            # Call DALL-E API
            response = self.client.images.generate(
                model=DALLE_MODEL,
                prompt=prompt,
                size=DALLE_SIZE,
                quality=DALLE_QUALITY,
                n=1,
                response_format="b64_json"  # Get base64 data directly
            )
            
            # Extract image data
            image_data = response.data[0].b64_json
            
            # Decode and save image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Save to sprites directory
            output_path = SPRITES_DIR / filename
            image.save(output_path, "PNG")
            
            logger.info(f"Saved sprite: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate sprite '{sprite_name}': {e}")
            return None
    
    def generate_all_sprites(self) -> dict:
        """
        Generate all defined sprites.
        
        Returns:
            Dictionary mapping sprite names to their output paths (or None if failed)
        """
        results = {}
        sprite_names = list(SPRITE_DEFINITIONS.keys())
        
        logger.info(f"Generating {len(sprite_names)} sprites...")
        
        for sprite_name in tqdm(sprite_names, desc="Generating sprites"):
            results[sprite_name] = self.generate_sprite(sprite_name)
        
        # Summary
        successful = sum(1 for path in results.values() if path is not None)
        failed = len(results) - successful
        
        logger.info(f"Generation complete: {successful} successful, {failed} failed")
        
        return results
    
    def list_sprites(self):
        """Print list of all available sprites."""
        print("\n" + "=" * 60)
        print("AVAILABLE SPRITES")
        print("=" * 60)
        
        for name, definition in SPRITE_DEFINITIONS.items():
            print(f"\n  {name}")
            print(f"    File: {definition['filename']}")
            print(f"    Description: {definition['description']}")
        
        print("\n" + "=" * 60)
        print(f"Total: {len(SPRITE_DEFINITIONS)} sprites")
        print("=" * 60 + "\n")


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    """Main entry point for the sprite generator."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate retro pixel art sprites using DALL-E for Anterix Spectrum Defender",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_sprites.py --list           # List all available sprites
  python generate_sprites.py --sprite player_ship  # Generate single sprite
  python generate_sprites.py --all            # Generate all sprites

Environment:
  Set OPENAI_API_KEY environment variable before running.
  Or create a .env file in the scripts directory with:
  OPENAI_API_KEY=your-api-key-here
        """
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate all sprites"
    )
    
    parser.add_argument(
        "--sprite", "-s",
        type=str,
        help="Generate a specific sprite by name"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available sprites"
    )
    
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        help="OpenAI API key (overrides environment variable)"
    )
    
    args = parser.parse_args()
    
    # List sprites if requested
    if args.list:
        # Create a temporary generator just to list (doesn't need valid API key)
        try:
            gen = SpriteGenerator(api_key=args.api_key or "dummy")
        except ValueError:
            # If no API key, still allow listing
            pass
        
        # Print sprite list manually since we might not have a valid generator
        print("\n" + "=" * 60)
        print("AVAILABLE SPRITES")
        print("=" * 60)
        
        for name, definition in SPRITE_DEFINITIONS.items():
            print(f"\n  {name}")
            print(f"    File: {definition['filename']}")
            print(f"    Description: {definition['description']}")
        
        print("\n" + "=" * 60)
        print(f"Total: {len(SPRITE_DEFINITIONS)} sprites")
        print("=" * 60 + "\n")
        return
    
    # Generate sprites
    if not args.all and not args.sprite:
        parser.print_help()
        print("\nERROR: Specify --all to generate all sprites or --sprite <name> for a specific one.")
        return
    
    try:
        generator = SpriteGenerator(api_key=args.api_key)
        
        if args.all:
            # Generate all sprites
            results = generator.generate_all_sprites()
            
            # Print summary
            print("\n" + "=" * 60)
            print("GENERATION SUMMARY")
            print("=" * 60)
            
            for name, path in results.items():
                status = "✓" if path else "✗"
                print(f"  {status} {name}")
            
            print("=" * 60 + "\n")
            
        elif args.sprite:
            # Generate single sprite
            path = generator.generate_sprite(args.sprite)
            
            if path:
                print(f"\n✓ Successfully generated: {path}\n")
            else:
                print(f"\n✗ Failed to generate: {args.sprite}\n")
                sys.exit(1)
                
    except ValueError as e:
        logger.error(str(e))
        print("\nTo set your API key:")
        print("  Windows:  set OPENAI_API_KEY=your-key-here")
        print("  Linux/Mac: export OPENAI_API_KEY=your-key-here")
        print("  Or create a .env file with: OPENAI_API_KEY=your-key-here")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
