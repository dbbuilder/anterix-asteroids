# REQUIREMENTS.md - Anterix Launch: Spectrum Defender

## Project Overview
A corporate launch arcade game combining Asteroids and Space Invaders mechanics, themed around Anterix's critical telecommunications business.

## Functional Requirements

### FR-001: Core Game Mechanics
- **FR-001.1**: Player controls a ship shaped like an "A" made of vertical lines
- **FR-001.2**: Ship can rotate 360 degrees (Asteroids-style)
- **FR-001.3**: Ship can thrust forward in facing direction
- **FR-001.4**: Ship can fire projectiles ("spectrum beams")
- **FR-001.5**: Screen wrapping for player ship
- **FR-001.6**: Collision detection between all game objects

### FR-002: Enemy Types (Telecom Themed)
- **FR-002.1**: "Signal Disruptors" - Small, fast enemies (basic invaders)
- **FR-002.2**: "Legacy Towers" - Large, slow asteroid-like obstacles
- **FR-002.3**: "Data Packets" - Tiny, very fast bonus enemies
- **FR-002.4**: "Spectrum Jammers" - Boss enemies appearing every 5 waves
- **FR-002.5**: "Network Nodes" - Medium enemies that split when destroyed

### FR-003: Power-Up System
- **FR-003.1**: "Bandwidth Boost" - Rapid fire capability
- **FR-003.2**: "Signal Shield" - Temporary invincibility
- **FR-003.3**: "Spectrum Spread" - Triple shot
- **FR-003.4**: "Network Surge" - Screen-clearing bomb (limited uses)

### FR-004: Scoring System
- **FR-004.1**: Points awarded per enemy type destroyed
- **FR-004.2**: Combo multiplier for rapid kills
- **FR-004.3**: High score persistence (localStorage)
- **FR-004.4**: Wave completion bonuses

### FR-005: Visual Requirements
- **FR-005.1**: Retro CRT scanline effect
- **FR-005.2**: Neon color palette (cyan, magenta, yellow on dark)
- **FR-005.3**: Particle effects for explosions
- **FR-005.4**: Star field parallax background
- **FR-005.5**: Screen shake on damage/explosions
- **FR-005.6**: All sprites drawn with Canvas primitives (no external images)
- **FR-005.7**: Optional: DALL-E generated sprite assets for enhanced visuals

### FR-006: Audio Requirements
- **FR-006.1**: 8-bit style sound effects using Web Audio API
- **FR-006.2**: Background music loop
- **FR-006.3**: Volume control
- **FR-006.4**: Mute toggle

### FR-007: Game Flow
- **FR-007.1**: Title screen with company branding
- **FR-007.2**: Wave-based progression
- **FR-007.3**: Lives system (3 lives default)
- **FR-007.4**: Game over screen with replay option
- **FR-007.5**: Pause functionality

## Non-Functional Requirements

### NFR-001: Performance
- Target 60 FPS on modern browsers
- Efficient collision detection using spatial partitioning
- Object pooling for projectiles and particles

### NFR-002: Compatibility
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Responsive canvas scaling
- Keyboard and touch controls

### NFR-003: Deployment
- Single HTML file with embedded CSS/JS
- No external dependencies for core game
- < 100KB total size (excluding optional sprites)

## Technical Specifications
- **Language**: Vanilla JavaScript (ES6+)
- **Rendering**: HTML5 Canvas 2D
- **Audio**: Web Audio API
- **Storage**: localStorage for high scores
- **Input**: Keyboard (WASD/Arrows, Space, P for pause)
- **Sprite Generation**: Python + OpenAI DALL-E API (optional)
