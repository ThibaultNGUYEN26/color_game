from tkinter import Tk, Frame, Label, Entry, StringVar, Button
import random
import sqlite3

bg_color = "#03045e"
font_color = "#CAF0F8"

colors = {
	"WHITE": "#FFFFFF",
	"BLACK": "#000000",
	"BLUE": "#0000FF",
	"RED": "#FF0000",
	"YELLOW": "#FFFF00",
	"GREEN": "#008000",
	"PURPLE": "#800080",
	"BROWN": "#5A2A2A",
	"PINK": "#FF69B4",
	"ORANGE": "#FFA500",
	"GRAY": "#808080",
}

def play():
	menu_frame.place_forget()
	main_frame.place(x=0, y=0)
	update_countdown()

def play_again():
    global points, countdown_time, game_over_label
    points = 0
    points_var.set(f"Points: {points}")
    countdown_time = 31
    countdown_var.set(f"Time left: {countdown_time}")
    update_color_label()

    if game_over_label:
        game_over_label.place_forget()
    play_again_btn.place_forget()
    user_input.place(relx=0.5, y=window_height * 0.8, anchor="center")
    color_label.place(relx=0.5, rely=0.5, anchor="center")
    countdown_label.config(fg=font_color)
    main_frame.place(x=0, y=0)
    update_countdown()

    root.unbind('<Return>')


def pick_random_color():
	global current_text_color_hex
	color_name, text_color_hex = random.choice(list(colors.items()))
	while True:
		_, text_color_hex = random.choice(list(colors.items()))
		if text_color_hex != current_text_color_hex:
			break
	current_text_color_hex = text_color_hex
	color_label.config(text=color_name, fg=text_color_hex)

def update_color_label():
	pick_random_color()
	entry_value.set("")

def add_point():
	global points
	points += 1
	points_var.set(f"Points: {points}")

current_text_color_hex = ""

hex_to_name = {v: k for k, v in colors.items()}

def on_write(*args):
	global trace_id, current_text_color_hex

	entry_value.trace_vdelete("w", trace_id)
	new_value = entry_value.get().upper()[:6]
	entry_value.set(new_value)
	trace_id = entry_value.trace("w", on_write)

	if new_value == hex_to_name[current_text_color_hex]:
		add_point()
		update_color_label()
		entry_value.set("")

def update_countdown():
	global countdown_time
	countdown_time -= 1
	countdown_var.set(f"Time left: {countdown_time}")
	if (countdown_time <= 3):
		countdown_label.config(fg="red")
	else:
		countdown_label.config(fg=font_color)
	if countdown_time > 0:
		root.after(1000, update_countdown)
	else:
		end_game()

def update_record_if_best(score):
    c.execute('SELECT MAX(score) FROM records')
    result = c.fetchone()
    max_score = result[0] if result[0] is not None else 0
    if score > max_score:
        c.execute('INSERT INTO records (score, date) VALUES (?, datetime("now"))', (score,))
        conn.commit()

def get_best_record():
    c.execute('SELECT MAX(score) FROM records')
    result = c.fetchone()
    return result[0] if result[0] is not None else 0

def end_game():
    global game_over_label
    update_record_if_best(points)
    color_label.place_forget()
    user_input.place_forget()
    game_over_label = Label(main_frame, text="GAME OVER", fg="red", bg=bg_color, font=("Futura", window_width // 15))
    game_over_label.place(relx=0.5, rely=0.4, anchor="center")
    play_again_btn.place(relx=0.5, rely=0.6, anchor="center")
    root.bind('<Return>', lambda event: play_again())


def exit_game(event=None):
	root.destroy()

root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.7)
window_height = int(screen_height * 0.7)
x_position = (screen_width // 2) - (window_width // 2)
y_position = (screen_height // 2) - (window_height // 2)
root.title("Color Game")
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.config(bg=bg_color)

menu_frame = Frame(root, width=window_width, height=window_height, bg=bg_color)
menu_frame.place(x=0, y=0)

play_btn = Button(menu_frame, text="Play", command=play, font=("Futura bold", window_width // 35))
play_btn.place(relx=0.5, rely=0.5, anchor="center")

main_frame = Frame(root, width=window_width, height=window_height, bg=bg_color)

title = Label(root, text="STROOP EFFECT GAME", fg=font_color, bg=bg_color, font=("Futura bold", window_width // 35))
title.place(relx=0.5, y=window_height * 0.15, anchor="center")

entry_value = StringVar()
trace_id = entry_value.trace("w", lambda *args: None)
entry_value.trace_vdelete("w", trace_id)
trace_id = entry_value.trace("w", on_write)
user_input = Entry(main_frame, text="", fg="black", font=("Futura extra bold", window_width // 30), justify="center", textvariable=entry_value, validate="key")
user_input.place(relx=0.5, y=window_height * 0.8, anchor="center")
user_input.focus()

color_label = Label(main_frame, text="", fg=font_color, bg=bg_color, font=("Futura bold", window_width // 11))
color_label.place(relx=0.5, rely=0.5, anchor="center")

update_color_label()

countdown_time = 31
countdown_var = StringVar(value=f"Time left: {countdown_time}")

countdown_label = Label(main_frame, textvariable=countdown_var, fg=font_color, bg=bg_color, font=("futura bold", window_width // 55))
countdown_label.place(relx=0.83, y=window_height * 0.04)

points = 0
points_var = StringVar(value=f"Points: {points}")

points_label = Label(main_frame, textvariable=points_var, fg=font_color, bg=bg_color, font=("futura bold", window_width // 60))
points_label.place(relx=0.03, y=window_height * 0.04)

game_over_label = None
play_again_btn = Button(main_frame, text="Play Again", font=("Futura bold", window_width // 35), command=play_again)

conn = sqlite3.connect('color_game_records.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, score INTEGER, date TEXT)''')

best_record = get_best_record()

record_label_text = StringVar()
record_label_text.set(f"Best Record: {best_record}")

record_label = Label(main_frame, textvariable=record_label_text, fg="gold", bg=bg_color, font=("futura bold", window_width // 65))
record_label.place(relx=0.03, y=window_height * 0.09)

def close_connection():
    conn.commit()
    conn.close()

root.protocol("WM_DELETE_WINDOW", close_connection)

root.bind('<Escape>', exit_game)

root.mainloop()
