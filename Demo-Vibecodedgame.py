"""
╔══════════════════════════════════════════════╗
║         GUESS TILL YOU CAN                   ║
║         Python / Tkinter  –  Fully Editable  ║
╚══════════════════════════════════════════════╝

HOW TO RUN:
  python guess_till_you_can.py

REQUIREMENTS:
  • Python 3.8+   (tkinter ships with Python on Windows & macOS)
  • Linux:  sudo apt install python3-tk
  • Pillow (optional – only needed if you add meme images):
      pip install Pillow

CUSTOMISATION GUIDE (search the tag to jump):
  #CFG-COLOURS   – all hex colours in one place
  #CFG-FEEDBACK  – hot/cold thresholds + messages + emojis
  #CFG-WINMSGS   – random win messages
  #CFG-TIMER     – total game time in seconds
  #CFG-MEMES     – drop-in meme image paths per feedback tier
  #CFG-FONTS     – font families & sizes
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import time

# ─────────────────────────────────────────────────────────────
# #CFG-TIMER  ── game duration
# ─────────────────────────────────────────────────────────────
TOTAL_SECONDS = 240          # 4 minutes

# ─────────────────────────────────────────────────────────────
# #CFG-COLOURS  ── every colour used in the UI
# ─────────────────────────────────────────────────────────────
C = {
    "bg":            "#0d0d0d",   # main background
    "bg2":           "#1a1a1a",   # card / input background
    "border":        "#2a2a2a",   # subtle borders
    "accent":        "#ff6b35",   # orange accent (buttons, highlights)
    "accent_hover":  "#e55a26",
    "text":          "#ffffff",   # primary text
    "text_muted":    "#888888",   # secondary / muted text
    "text_hint":     "#555555",   # placeholder / hints

    # timer bar colours
    "bar_green":     "#4caf50",
    "bar_yellow":    "#ffb700",
    "bar_red":       "#ff3333",

    # feedback tier colours  (text colour for each tier)
    "hot_af":        "#ff2b2b",
    "hot":           "#ff6b35",
    "warm":          "#ffb700",
    "cold":          "#64b5f6",
    "very_cold":     "#42a5f5",
    "cold_af":       "#1e88e5",
    "coldest":       "#0d47a1",   # note: also set bg for this tier if you like
}

# ─────────────────────────────────────────────────────────────
# #CFG-FONTS
# ─────────────────────────────────────────────────────────────
FONT_FAMILY = "Helvetica"   # change to any installed font

# ─────────────────────────────────────────────────────────────
# #CFG-FEEDBACK  ── (min_diff, max_diff, emoji, message, colour_key)
#   diff = abs(secret - guess)
# ─────────────────────────────────────────────────────────────
FEEDBACK = [
    (1,  3,  "🔥", "HOT AS F**K!",          "hot_af",   "SO close it burns!"),
    (4,  6,  "🥵", "HOT!",                   "hot",      "Getting warmer..."),
    (7,  10, "☀️", "WARM",                   "warm",     "Not bad, keep going!"),
    (11, 25, "🧊", "EW, COLD",               "cold",     "That's pretty far off..."),
    (26, 35, "❄️", "UM NOO, VERY COLD!",     "very_cold","Brr... way off!"),
    (36, 45, "🥶", "COLD AS F**K!",          "cold_af",  "Are you even trying?!"),
    (46, 50, "🌨️","COLDEST YOU COULD BE!",  "coldest",  "Literally the worst guess possible."),
]

# ─────────────────────────────────────────────────────────────
# #CFG-WINMSGS  ── randomly chosen on correct guess
# ─────────────────────────────────────────────────────────────
WIN_MESSAGES = [
    "WELL DONE!\nYou managed to successfully waste your time.",
    "YOU WILL RECEIVE no rewards of course,\ngo do better things.",
    "Hope you had fun, come again!",
    "HAD FUN?  SEE YAA 👋",
]

# ─────────────────────────────────────────────────────────────
# #CFG-MEMES  ── optional meme images per feedback tier
#
#   1. pip install Pillow
#   2. Put image paths below (PNG / JPG / GIF)
#   3. Uncomment the Pillow block in _load_meme()
#
#   Keys match the 5th element of each FEEDBACK tuple above.
# ─────────────────────────────────────────────────────────────
MEME_PATHS = {
    "hot_af":    "",   # e.g. "memes/hot_af.png"
    "hot":       "",
    "warm":      "",
    "cold":      "",
    "very_cold": "",
    "cold_af":   "",
    "coldest":   "",
}


# ══════════════════════════════════════════════════════════════
#  HELPER – get feedback for a diff value
# ══════════════════════════════════════════════════════════════
def get_feedback(diff):
    for lo, hi, emoji, msg, color_key, sub in FEEDBACK:
        if lo <= diff <= hi:
            return emoji, msg, color_key, sub
    return "🤔", "GUESS AGAIN", "text_muted", ""


# ══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════
class GuessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GUESS TILL YOU CAN")
        self.geometry("620x540")
        self.resizable(False, False)
        self.configure(bg=C["bg"])

        # game state
        self.secret      = None
        self.player_name = tk.StringVar()
        self.guess_count = 0
        self.secs_left   = TOTAL_SECONDS
        self._timer_job  = None
        self._running    = False

        # font helpers
        self._f  = lambda s, w="normal": tkfont.Font(family=FONT_FAMILY, size=s, weight=w)

        self._build_name_screen()

    # ──────────────────────────────────────────────────────────
    #  SCREEN MANAGEMENT
    # ──────────────────────────────────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ──────────────────────────────────────────────────────────
    #  SCREEN 1 – NAME ENTRY
    # ──────────────────────────────────────────────────────────
    def _build_name_screen(self):
        self._clear()
        f = self.frame = tk.Frame(self, bg=C["bg"])
        f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f, text="GUESS TILL YOU CAN",
                 font=self._f(26, "bold"),
                 fg=C["text"], bg=C["bg"]).pack(pady=(0, 6))

        tk.Label(f, text="Ready to beat the machine and guess what it's thinking?",
                 font=self._f(11), fg=C["text_muted"], bg=C["bg"],
                 wraplength=440, justify="center").pack(pady=(0, 4))

        tk.Label(f, text="Guess what number the computer thought of between 1–50.",
                 font=self._f(11), fg=C["text_hint"], bg=C["bg"],
                 wraplength=440, justify="center").pack(pady=(0, 26))

        tk.Label(f, text="Your name:", font=self._f(12),
                 fg=C["text_muted"], bg=C["bg"]).pack()

        entry = tk.Entry(f, textvariable=self.player_name,
                         font=self._f(14), width=20,
                         bg=C["bg2"], fg=C["text"],
                         insertbackground=C["text"],
                         relief="flat", highlightthickness=1,
                         highlightcolor=C["accent"],
                         highlightbackground=C["border"],
                         justify="center")
        entry.pack(pady=8, ipady=6)
        entry.focus_set()
        entry.bind("<Return>", lambda e: self._start_game())

        btn = tk.Button(f, text="LET'S GO  →",
                        font=self._f(13, "bold"),
                        bg=C["accent"], fg=C["text"],
                        activebackground=C["accent_hover"],
                        activeforeground=C["text"],
                        relief="flat", padx=28, pady=8,
                        cursor="hand2",
                        command=self._start_game)
        btn.pack(pady=12)

    # ──────────────────────────────────────────────────────────
    #  SCREEN 2 – GAME
    # ──────────────────────────────────────────────────────────
    def _build_game_screen(self):
        self._clear()

        # ── top bar ──────────────────────────────────────────
        top = tk.Frame(self, bg=C["bg2"], height=52)
        top.pack(fill="x")
        top.pack_propagate(False)

        # timer (left)
        timer_frame = tk.Frame(top, bg=C["bg2"])
        timer_frame.pack(side="left", padx=16, pady=6)
        tk.Label(timer_frame, text="TIME LEFT", font=self._f(9),
                 fg=C["text_hint"], bg=C["bg2"]).pack(anchor="w")
        self.timer_lbl = tk.Label(timer_frame, text="4:00",
                                  font=self._f(20, "bold"),
                                  fg=C["text"], bg=C["bg2"])
        self.timer_lbl.pack(anchor="w")

        # player name (right)
        name_disp = f"Playing:  {self.player_name.get()}"
        tk.Label(top, text=name_disp, font=self._f(11),
                 fg=C["accent"], bg=C["bg2"]).pack(side="right", padx=16)

        # ── timer progress bar ────────────────────────────────
        bar_bg = tk.Frame(self, bg=C["border"], height=5)
        bar_bg.pack(fill="x")
        bar_bg.pack_propagate(False)
        self.timer_bar = tk.Frame(bar_bg, bg=C["bar_green"], height=5)
        self.timer_bar.place(x=0, y=0, relwidth=1.0, height=5)

        # ── body ──────────────────────────────────────────────
        body = tk.Frame(self, bg=C["bg"])
        body.pack(expand=True, fill="both", padx=40, pady=20)

        tk.Label(body,
                 text="What number is the computer thinking of?  (1–50)",
                 font=self._f(11), fg=C["text_hint"], bg=C["bg"]).pack(pady=(0, 16))

        # feedback area
        self.fb_emoji = tk.Label(body, text="🤔", font=self._f(48),
                                 fg=C["text"], bg=C["bg"])
        self.fb_emoji.pack()

        self.fb_main = tk.Label(body, text="Waiting for your first guess...",
                                font=self._f(20, "bold"),
                                fg=C["text_hint"], bg=C["bg"])
        self.fb_main.pack(pady=4)

        self.fb_sub = tk.Label(body, text="",
                               font=self._f(11),
                               fg=C["text_muted"], bg=C["bg"])
        self.fb_sub.pack(pady=(0, 16))

        # meme image label (hidden until a meme path is set)
        self.meme_lbl = tk.Label(body, bg=C["bg"])
        self.meme_lbl.pack(pady=(0, 8))

        # input row
        row = tk.Frame(body, bg=C["bg"])
        row.pack()

        self.guess_var = tk.StringVar()
        self.guess_entry = tk.Entry(row, textvariable=self.guess_var,
                                    font=self._f(18), width=6,
                                    bg=C["bg2"], fg=C["text"],
                                    insertbackground=C["text"],
                                    relief="flat", highlightthickness=1,
                                    highlightcolor=C["accent"],
                                    highlightbackground=C["border"],
                                    justify="center")
        self.guess_entry.grid(row=0, column=0, ipady=8, padx=(0, 8))
        self.guess_entry.bind("<Return>", lambda e: self._submit_guess())
        self.guess_entry.focus_set()

        btn = tk.Button(row, text="GUESS",
                        font=self._f(13, "bold"),
                        bg=C["accent"], fg=C["text"],
                        activebackground=C["accent_hover"],
                        activeforeground=C["text"],
                        relief="flat", padx=20, pady=6,
                        cursor="hand2",
                        command=self._submit_guess)
        btn.grid(row=0, column=1)

        self.count_lbl = tk.Label(body, text="Guesses made:  0",
                                  font=self._f(10), fg=C["text_hint"], bg=C["bg"])
        self.count_lbl.pack(pady=12)

    # ──────────────────────────────────────────────────────────
    #  SCREEN 3 – END
    # ──────────────────────────────────────────────────────────
    def _build_end_screen(self, won: bool, time_used: int):
        self._clear()
        f = tk.Frame(self, bg=C["bg"])
        f.place(relx=0.5, rely=0.5, anchor="center")

        if won:
            emoji = "🎉"
            title = f"NAILED IT, {self.player_name.get().upper()}!"
            msg   = random.choice(WIN_MESSAGES)
            title_col = C["accent"]
        else:
            emoji = "⏰"
            title = "TIME'S UP!"
            msg   = (f"The machine was thinking of  {self.secret}.\n"
                     f"You had {self.guess_count} guess{'es' if self.guess_count != 1 else ''} "
                     f"and still couldn't crack it.\nThe machine wins this round, "
                     f"{self.player_name.get()}!")
            title_col = "#ff3333"

        tk.Label(f, text=emoji, font=self._f(64), bg=C["bg"]).pack(pady=(0, 8))
        tk.Label(f, text=title, font=self._f(22, "bold"),
                 fg=title_col, bg=C["bg"]).pack()
        tk.Label(f, text=msg, font=self._f(12),
                 fg=C["text_muted"], bg=C["bg"],
                 wraplength=460, justify="center").pack(pady=16)

        # stats row
        stats_frame = tk.Frame(f, bg=C["bg"])
        stats_frame.pack(pady=8)

        mins = time_used // 60
        secs = time_used % 60
        stats = [
            ("THE NUMBER",  str(self.secret)),
            ("GUESSES",     str(self.guess_count)),
            ("TIME USED",   f"{mins}:{secs:02d}"),
        ]
        for label, val in stats:
            box = tk.Frame(stats_frame, bg=C["bg2"],
                           highlightthickness=1,
                           highlightbackground=C["border"])
            box.pack(side="left", padx=10, ipadx=18, ipady=10)
            tk.Label(box, text=label, font=self._f(9),
                     fg=C["text_hint"], bg=C["bg2"]).pack()
            tk.Label(box, text=val, font=self._f(22, "bold"),
                     fg=C["text"], bg=C["bg2"]).pack()

        tk.Button(f, text="PLAY AGAIN",
                  font=self._f(13, "bold"),
                  bg=C["accent"], fg=C["text"],
                  activebackground=C["accent_hover"],
                  activeforeground=C["text"],
                  relief="flat", padx=28, pady=8,
                  cursor="hand2",
                  command=self._build_name_screen).pack(pady=20)

    # ──────────────────────────────────────────────────────────
    #  GAME LOGIC
    # ──────────────────────────────────────────────────────────
    def _start_game(self):
        name = self.player_name.get().strip()
        if not name:
            return
        self.secret      = random.randint(1, 50)
        self.guess_count = 0
        self.secs_left   = TOTAL_SECONDS
        self._running    = True
        self._start_time = time.time()

        self._build_game_screen()
        self._tick()

    def _tick(self):
        if not self._running:
            return
        elapsed = int(time.time() - self._start_time)
        self.secs_left = max(0, TOTAL_SECONDS - elapsed)

        mins = self.secs_left // 60
        secs = self.secs_left % 60
        self.timer_lbl.config(text=f"{mins}:{secs:02d}")

        # colour the timer label
        if self.secs_left > 120:
            self.timer_lbl.config(fg=C["text"])
        elif self.secs_left > 60:
            self.timer_lbl.config(fg=C["bar_yellow"])
        else:
            self.timer_lbl.config(fg=C["bar_red"])

        # progress bar
        pct = self.secs_left / TOTAL_SECONDS
        bar_col = (C["bar_green"] if pct > 0.5
                   else C["bar_yellow"] if pct > 0.25
                   else C["bar_red"])
        self.timer_bar.config(bg=bar_col)
        self.timer_bar.place(x=0, y=0, relwidth=pct, height=5)

        if self.secs_left <= 0:
            self._running = False
            time_used = TOTAL_SECONDS - self.secs_left
            self._build_end_screen(won=False, time_used=time_used)
            return

        self._timer_job = self.after(500, self._tick)

    def _submit_guess(self):
        if not self._running:
            return

        raw = self.guess_var.get().strip()
        try:
            val = int(raw)
            if not (1 <= val <= 50):
                raise ValueError
        except ValueError:
            self.fb_main.config(text="Enter a number between 1 and 50!",
                                fg=C["accent"])
            self.fb_sub.config(text="")
            self.guess_var.set("")
            return

        self.guess_count += 1
        self.count_lbl.config(text=f"Guesses made:  {self.guess_count}")
        self.guess_var.set("")
        self.guess_entry.focus_set()

        if val == self.secret:
            self._running = False
            if self._timer_job:
                self.after_cancel(self._timer_job)
            time_used = int(time.time() - self._start_time)
            self._build_end_screen(won=True, time_used=time_used)
            return

        diff = abs(val - self.secret)
        emoji, msg, color_key, sub = get_feedback(diff)
        col = C[color_key]

        self.fb_emoji.config(text=emoji)
        self.fb_main.config(text=msg, fg=col)
        self.fb_sub.config(text=sub)
        self._load_meme(color_key)

    # ──────────────────────────────────────────────────────────
    #  #CFG-MEMES  ── swap in your own images here
    # ──────────────────────────────────────────────────────────
    def _load_meme(self, color_key: str):
        """
        To add meme images:
          1. pip install Pillow
          2. Fill in MEME_PATHS at the top of this file
          3. Uncomment the block below

        The image will be displayed below the feedback text.
        Max display size is 200×150 px (auto-resized).
        """
        path = MEME_PATHS.get(color_key, "")
        if not path:
            self.meme_lbl.config(image="", text="")
            return

        # ── UNCOMMENT when Pillow is installed and paths are set ──
        # from PIL import Image, ImageTk
        # try:
        #     img = Image.open(path)
        #     img.thumbnail((200, 150), Image.LANCZOS)
        #     photo = ImageTk.PhotoImage(img)
        #     self.meme_lbl.config(image=photo, text="")
        #     self.meme_lbl.image = photo   # keep reference!
        # except Exception as e:
        #     self.meme_lbl.config(image="", text=f"[meme: {e}]",
        #                          fg=C["text_hint"])
        pass


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = GuessGame()
    app.mainloop()