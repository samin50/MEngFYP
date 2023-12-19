import os
import customtkinter
os.environ['XDG_RUNTIME_DIR'] = '/run/user/1000'
os.environ["DISPLAY"] = ":0"
def button_callback():
    print("button pressed")

app = customtkinter.CTk()
app.title("my app")
app.attributes("-fullscreen", True)
app.config(cursor="none")
app.geometry("1024x600")

button = customtkinter.CTkButton(app, text="my button", command=button_callback)
button.grid(row=0, column=0, padx=20, pady=20)

app.mainloop()
