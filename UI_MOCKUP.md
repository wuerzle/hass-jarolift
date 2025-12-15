# Home Assistant UI - Jarolift Device View
# ========================================
# This shows what users will see in the Home Assistant UI

┌────────────────────────────────────────────────────────────────┐
│  Home Assistant                                                 │
├────────────────────────────────────────────────────────────────┤
│  Settings > Devices & Services > Jarolift                      │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  📦 Jarolift                                                    │
│  KeeLoq RF Controller                                           │
│  by Jarolift                                                    │
│  Software version: 2.0.5                                        │
│                                                                 │
│  ──────────────────────────────────────────────────────────    │
│                                                                 │
│  Entities (6)                                                   │
│                                                                 │
│  🪟 cover.living_room_cover                                     │
│     Living Room Cover                                           │
│     [Open] [Stop] [Close]                                       │
│                                                                 │
│  🔘 button.living_room_cover_learn                              │
│     Living Room Cover Learn                                     │
│     [Press to start learning mode]                              │
│                                                                 │
│  ──────────────────────────────────────────────────────────    │
│                                                                 │
│  🪟 cover.bedroom_cover                                         │
│     Bedroom Cover                                               │
│     [Open] [Stop] [Close]                                       │
│                                                                 │
│  🔘 button.bedroom_cover_learn                                  │
│     Bedroom Cover Learn                                         │
│     [Press to start learning mode]                              │
│                                                                 │
│  ──────────────────────────────────────────────────────────    │
│                                                                 │
│  🪟 cover.kitchen_blind                                         │
│     Kitchen Blind                                               │
│     [Open] [Stop] [Close]                                       │
│                                                                 │
│  🔘 button.kitchen_blind_learn                                  │
│     Kitchen Blind Learn                                         │
│     [Press to start learning mode]                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

HOW TO USE:
===========

1. Put your physical Jarolift cover into learning mode
   (consult your cover's manual for the specific procedure)

2. In Home Assistant, find the learning button for that cover

3. Click the button - it will turn blue/highlighted briefly

4. The cover will beep or flash to confirm it learned the remote

5. Done! The cover is now paired and ready to use

BENEFITS:
=========

✓ No need to remember hex codes
✓ No need to use Developer Tools
✓ Clear visual organization
✓ Each cover has its own button
✓ All entities grouped together
✓ Can't accidentally trigger wrong cover
