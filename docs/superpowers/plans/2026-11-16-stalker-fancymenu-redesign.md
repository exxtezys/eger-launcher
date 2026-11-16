# S.T.A.L.K.E.R. FancyMenu Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign all 10 FancyMenu layout files with authentic S.T.A.L.K.E.R. "Zone" aesthetic — gritty, atmospheric, immersive UI inspired by the game's PDA and terminal interfaces.

**Architecture:** Each layout file will be completely rewritten from scratch with improved visual hierarchy, authentic color palette, atmospheric effects (scanlines, vignettes, borders), and proper Russian typography matching the game's UI style.

**Tech Stack:** FancyMenu custom layout format (.txt), S.T.A.L.K.E.R. aesthetic design patterns

**Spec:** Conversation context — user rejected previous design as "уродство" (ugly), needs authentic Zone atmosphere

## Global Constraints

- All 10 files must share consistent visual language
- Color palette: dark greens (#1A1F1A), rusty browns (#3D3428), muted grays (#4A4D4A), amber highlights (#FFB833), radiation green (#32CD32)
- Typography: bold headlines, smaller subtitles, proper Russian text
- Atmospheric elements: scanlines, vignettes, worn borders, subtle gradients
- Maintain vanilla button compatibility where screens have them
- Keep layout_index = 0, is_enabled = true, render_custom_elements_behind_vanilla = true

## Review Focus

1. Color contrast — text must be readable on dark backgrounds
2. Russian text encoding — must display correctly in-game
3. Element positioning — anchor points must work across resolutions
4. Vanilla button styling — hover states must be visible
5. Atmospheric consistency — all screens feel like same PDA/terminal system

---

### Task 1: Redesign ege-title.txt (Main Menu)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-title.txt`

**Interfaces:**
- Produces: Main title screen layout with S.T.A.L.K.E.R. PDA-style branding

- [ ] **Step 1: Implement redesigned layout**

Replace entire file with:
- Dark vignette background (#0D0F0D center to #1A1F1A edges)
- Scanline overlay effect (repeating 2px pattern)
- Bold "S.T.A.L.K.E.R." logo top-left with amber glow
- "ЗОНА ЧЕРНОБЫЛЯ" subtitle with tracking
- Decorative corner brackets (L-shaped borders)
- Radiation symbol or Zone marker element
- Vanilla buttons styled with green/amber hover

- [ ] **Step 2: Verify syntax**

Run: Check file opens without FancyMenu errors
Expected: Valid layout structure

- [ ] **Step 3: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-title.txt"
git commit -m "style: redesign title screen with authentic S.T.A.L.K.E.R. PDA aesthetic"
```

---

### Task 2: Redesign ege-loading.txt (Loading Screen)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-loading.txt`

**Interfaces:**
- Consumes: Visual language from Task 1
- Produces: Loading screen with Zone atmosphere

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- Dark background with subtle noise texture
- Central loading indicator area
- "ЗАГРУВКА ПАРТИИ" headline (amber)
- Rotating status messages: "ПОДГОТОВКА СТАНЦИИ", "СИНХРОНИЗАЦИЯ", etc.
- Progress bar frame (rusty metal style)
- Bottom copyright with fade

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-loading.txt"
git commit -m "style: redesign loading screen with Zone terminal aesthetic"
```

---

### Task 3: Redesign ege-connect.txt (Connecting)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-connect.txt`

**Interfaces:**
- Produces: Multiplayer connecting screen

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- Dark green terminal background
- "МНОГОИГРОВАЯ" headline
- "ПОДКЛЮЧЕНИЕ К СТАНЦИИ..." animated text
- Signal strength indicator bars
- Connection status flicker effect
- Decorative data stream elements

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-connect.txt"
git commit -m "style: redesign connect screen with terminal signal aesthetic"
```

---

### Task 4: Redesign ege-receiving.txt (Receiving Level)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-receiving.txt`

**Interfaces:**
- Produces: Level receiving screen

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- PDA data transfer visual
- "ПРИЁМ ПАРТИИ" headline
- "ПОЛУЧЕНИЕ ДАННЫХ..." status
- Packet transfer animation frames
- Checksum/validation display
- Green data flow indicators

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-receiving.txt"
git commit -m "style: redesign receiving screen with PDA data transfer aesthetic"
```

---

### Task 5: Redesign ege-pause.txt (Pause Menu)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-pause.txt`

**Interfaces:**
- Produces: Pause menu with vanilla button support

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- Semi-transparent dark overlay
- "ПЕРЕРЫВ" headline (large, amber)
- "ПАУЗА" subtitle
- Styled vanilla buttons (Return, Options, Stats, Disconnect)
- Border frame with worn metal texture
- Subtle radiation glow effect

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-pause.txt"
git commit -m "style: redesign pause screen with PDA menu aesthetic"
```

---

### Task 6: Redesign ege-stations.txt (Server List)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-stations.txt`

**Interfaces:**
- Produces: Server/stations list screen

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- "СТАНЦИИ" headline
- "СПИСОК ДОСТУПНЫХ" subtitle
- Server list frame with scanlines
- Signal strength indicators per server
- Frequency/channel labels
- Static noise background element

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-stations.txt"
git commit -m "style: redesign stations screen with radio scanner aesthetic"
```

---

### Task 7: Redesign ege-options.txt (Options Screen)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-options.txt`

**Interfaces:**
- Produces: Options/settings screen

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- "НАСТРОЙКИ" headline
- "ИГРОВЫЕ ПАРАМЕТРЫ" subtitle
- Settings panel frame
- Toggle/switch visual styling hints
- Slider track indicators
- PDA configuration aesthetic

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-options.txt"
git commit -m "style: redesign options screen with PDA config aesthetic"
```

---

### Task 8: Redesign ege-newworld.txt (Create World)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-newworld.txt`

**Interfaces:**
- Produces: New world creation screen

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- "НОВАЯ ПАРТИЯ" headline
- "ОФОРМЛЕНИЕ УЧАСТКА" subtitle
- Map/sector selection frame
- Difficulty indicator badges
- Zone sector labels
- Warning/caution elements

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-newworld.txt"
git commit -m "style: redesign new world screen with sector selection aesthetic"
```

---

### Task 9: Redesign ege-death.txt (Death Screen)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-death.txt`

**Interfaces:**
- Produces: Death screen with respawning

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- Red-tinted dark background (danger)
- "ПАРТИЯ ЗАКРЫТА" headline (red/amber)
- "СМЕРТЬ В ЗОНЕ" subtitle
- Skull/radiation hazard symbol
- Vanilla buttons (Respawn, Title)
- Critical alert styling

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-death.txt"
git commit -m "style: redesign death screen with critical alert aesthetic"
```

---

### Task 10: Redesign ege-disconnected.txt (Disconnected)

**Files:**
- Modify: `C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\customization\ege-disconnected.txt`

**Interfaces:**
- Produces: Disconnection screen

- [ ] **Step 1: Implement redesigned layout**

Replace with:
- "СВЯЗЬ ПРЕРВАНА" headline (amber warning)
- "СТАНЦИЯ НЕ ОТВЕЧАЕТ" subtitle
- Signal lost animation elements
- Static/noise visual
- Reconnect hint
- Emergency broadcast aesthetic

- [ ] **Step 2: Commit**

```bash
git add "src/main/resources/config/fancymenu/customization/ege-disconnected.txt"
git commit -m "style: redesign disconnected screen with signal loss aesthetic"
```

---

## Verification

- [ ] **Step 1: Run launcher verification**

Run: `C:\Users\User\AppData\Local\Temp\opencode\fm-run.ps1`
Expected: All 10 screens render without errors, consistent S.T.A.L.K.E.R. aesthetic

- [ ] **Step 2: Final commit**

```bash
git commit --amend -m "style: complete S.T.A.L.K.E.R. FancyMenu redesign - authentic Zone PDA aesthetic"
```
