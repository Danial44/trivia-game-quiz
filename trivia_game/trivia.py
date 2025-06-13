import tkinter as tk
import random
from tkinter import messagebox, simpledialog

try:
    import pygame
    pygame.init()
    pygame.mixer.init()
    SOUND_ENABLED = True
    correct_sound = pygame.mixer.Sound("correct.wav")
    wrong_sound = pygame.mixer.Sound("wrong.wav")
except Exception:
    SOUND_ENABLED = False
    correct_sound = None
    wrong_sound = None

QUESTIONS = [
    {"q": "What is the capital of France?", "a": "paris"},
    {"q": "What is the capital of Japan?", "a": "tokyo"},
    {"q": "Which country is known for the Taj Mahal?", "a": "india"},
    {"q": "Which language is primarily spoken in Brazil?", "a": "portuguese"},
    {"q": "What is the currency of the UK?", "a": "pound"},
    {"q": "What is the capital of Canada?", "a": "ottawa"},
    {"q": "Where is the Great Barrier Reef located?", "a": "australia"},
    {"q": "Which country invented pizza?", "a": "italy"},
    {"q": "Which city is known as the Big Apple?", "a": "new york"},
    {"q": "What is the tallest mountain in the world?", "a": "everest"},
    {"q": "What is 5 + 7?", "a": "12"},
    {"q": "What planet is known as the Red Planet?", "a": "mars"},
    {"q": "Who wrote 'Hamlet'?", "a": "shakespeare"},
    {"q": "How many continents are there?", "a": "7"},
    {"q": "What is the largest ocean?", "a": "pacific"},
    {"q": "In which year did WW2 end?", "a": "1945"},
    {"q": "Which gas do plants absorb?", "a": "carbon dioxide"},
    {"q": "What is the square root of 81?", "a": "9"},
    {"q": "What is H2O?", "a": "water"},
    {"q": "What is the capital of South Korea?", "a": "seoul"},
    {"q": "What is the national animal of China?", "a": "panda"},
    {"q": "Which country has the most population?", "a": "china"},
    {"q": "Which desert is the largest in the world?", "a": "sahara"},
    {"q": "What is the capital of Egypt?", "a": "cairo"},
    {"q": "What is the official language of Argentina?", "a": "spanish"},
]

class TriviaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("💾 TRIVIA TERMINAL 💾")
        self.root.geometry("700x500")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)

        self.player_name = simpledialog.askstring("Enter Name", "What is your Name?", parent=self.root)
        if not self.player_name:
            self.player_name = "Anonymous"

        self.root.after(100, self.flicker_effect)

        self.score = 0
        self.q_index = 0
        self.questions = random.sample(QUESTIONS, 10)

        self.title_label = tk.Label(root, text=f"▶ TRIVIA - {self.player_name} ◀", font=("Courier New", 26, "bold"),
                                    fg="#00FF41", bg="#0a0a0a")
        self.title_label.pack(pady=20)

        self.question_label = tk.Label(root, text="", font=("Courier New", 16),
                                       fg="#00FFFF", bg="#0a0a0a", wraplength=600, justify="center")
        self.question_label.pack(pady=10)

        self.answer_entry = tk.Entry(root, font=("Courier New", 14), width=30, justify="center",
                                     bg="#1a1a1a", fg="#39ff14", insertbackground="#39ff14", relief="sunken",
                                     highlightthickness=2, highlightbackground="#39ff14")
        self.answer_entry.pack(pady=10)

        self.submit_button = tk.Button(root, text="SUBMIT", font=("Courier New", 12, "bold"),
                                       bg="#00ff99", fg="#0f0f0f", activebackground="#00cc99",
                                       relief="raised", bd=3, command=self.check_answer)
        self.submit_button.pack(pady=10)

        self.feedback_label = tk.Label(root, text="", font=("Courier New", 14),
                                       fg="#ffcc00", bg="#0a0a0a")
        self.feedback_label.pack(pady=10)

        self.score_label = tk.Label(root, text="SCORE: 0", font=("Courier New", 12),
                                    fg="#ffff00", bg="#0a0a0a")
        self.score_label.pack()

        self.replay_button = tk.Button(root, text="PLAY AGAIN", font=("Courier New", 12, "bold"),
                                       bg="#ff3399", fg="#0f0f0f", activebackground="#cc0066",
                                       command=self.reset_game)
        self.replay_button.pack(pady=10)
        self.replay_button.place_forget()

        self.next_question()

    def flicker_effect(self):
        color = random.choice(["#00FF41", "#00aa33", "#005511", "#00FF41"])
        self.title_label.config(fg=color)
        self.root.after(200, self.flicker_effect)

    def next_question(self):
        if self.q_index < len(self.questions):
            question = self.questions[self.q_index]["q"]
            self.question_label.config(text=f"Q{self.q_index + 1}: {question}")
            self.answer_entry.delete(0, tk.END)
            self.feedback_label.config(text="")
        else:
            self.question_label.config(text="💀 GAME OVER 💀")
            self.answer_entry.place_forget()
            self.submit_button.place_forget()
            self.feedback_label.config(text=f"FINAL SCORE: {self.score}/{len(self.questions)}")
            self.replay_button.place(relx=0.5, rely=0.8, anchor="center")
            self.save_score_to_file()

    def check_answer(self):
        user_ans = self.answer_entry.get().strip().lower()
        correct_ans = self.questions[self.q_index]["a"]
        if user_ans == correct_ans:
            self.score += 1
            self.feedback_label.config(text="✔ Correct!", fg="#00ff00")
            if SOUND_ENABLED and correct_sound:
                correct_sound.play()
        else:
            self.feedback_label.config(text=f"✖ Wrong! Ans: {correct_ans}", fg="#ff4444")
            if SOUND_ENABLED and wrong_sound:
                wrong_sound.play()

        self.score_label.config(text=f"SCORE: {self.score}")
        self.q_index += 1
        self.root.after(1200, self.next_question)

    def reset_game(self):
        self.score = 0
        self.q_index = 0
        self.questions = random.sample(QUESTIONS, 10)
        self.answer_entry.place(relx=0.5, rely=0.5, anchor="center")
        self.submit_button.place(relx=0.5, rely=0.6, anchor="center")
        self.answer_entry.pack(pady=10)
        self.submit_button.pack(pady=10)
        self.replay_button.place_forget()
        self.score_label.config(text="SCORE: 0")
        self.next_question()

    def save_score_to_file(self):
        try:
            with open("quiz_scores.txt", "a") as f:
                f.write(f"{self.player_name} Scored {self.score}/{len(self.questions)}\n")
        except Exception as e:
            print("Error writing to file:", e)

if __name__ == "__main__":
    root = tk.Tk()
    game = TriviaGame(root)
    root.mainloop()
