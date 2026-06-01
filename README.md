# What-s-the-number-
This is a fairly simple game. You have  minutes to guess a number that the program has picked between 1-50. You will be told whether you are close (HOT) or far away from the actual number (COLD)

A single-player number guessing game built with Python & Tkinter. The computer secretly picks a number between 1 and 50 — you have **4 minutes** to crack it using hot/cold feedback after every guess.

🚀 How to Run

```bash
pip install pillow   # optional – only needed for meme images
python guess_till_you_can.py
```

> **Requirements:** Python 3.8+ · Tkinter (built-in on Windows & macOS · Linux: `sudo apt install python3-tk`)

---

## 🎯 How to Play

1. Enter your name and hit **LET'S GO**
2. Type a number between 1–50 and press **GUESS** (or hit Enter)
3. Read the hot/cold feedback and keep guessing
4. Win by guessing correctly — or lose when the 4-minute timer hits zero!

---

🌡️ Hot / Cold Scale

| Feedback | Difference from the secret number |
|---|---|
| 🔥 **HOT AS F\*\*K!** | Within 1–3 |
| 🥵 **HOT!** | Within 4–6 |
| ☀️ **WARM** | Within 7–10 |
| 🧊 **EW, COLD** | Within 11–25 |
| ❄️ **UM NOO, VERY COLD!** | Within 26–35 |
| 🥶 **COLD AS F\*\*K!** | Within 36–45 |
| 🌨️ **COLDEST YOU COULD BE!** | Within 46–50 |

---

## 🛠️ Customisation

All settings live at the top of `guess_till_you_can.py` — search for these tags:

| Tag | What it controls |
|---|---|
| `#CFG-COLOURS` | Every colour in the UI |
| `#CFG-FEEDBACK` | Hot/cold thresholds, messages & emojis |
| `#CFG-WINMSGS` | Random win messages |
| `#CFG-TIMER` | Game duration (default: 240 seconds) |
| `#CFG-MEMES` | Meme image paths per feedback tier |
| `#CFG-FONTS` | Font family & sizes |

### Adding Meme Images

1. Install Pillow: `pip install Pillow`
2. Add your image paths to `MEME_PATHS` in the script
3. Uncomment the image block inside `_load_meme()`

---

📁 Files


guess_till_you_can.py   ← the entire game (single file)
README.md


📜 License

Do whatever you want with it. Have fun. Go touch grass after. 🌿
