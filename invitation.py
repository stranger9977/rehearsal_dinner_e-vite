from tkinter import *

root = Tk()
root.title("Rehearsal Dinner Invitation")

date_label = Label(root, text="Date: October 15, 2023")
date_label.pack()

time_label = Label(root, text="Time: 6:00 PM")
time_label.pack()

location_label = Label(root, text="Location: The Grand Ballroom")
location_label.pack()

meal_frame = Frame(root)
meal_frame.pack()

meal_label = Label(meal_frame, text="Select your meal option:")
meal_label.pack(side=LEFT)

var = StringVar()

option1 = Radiobutton(meal_frame, text="Beef Tenderloin", variable=var, value="Beef Tenderloin")
option1.pack(side=LEFT)

option2 = Radiobutton(meal_frame, text="Grilled Salmon", variable=var, value="Grilled Salmon")
option2.pack(side=LEFT)

option3 = Radiobutton(meal_frame, text="Vegetable Lasagna", variable=var, value="Vegetable Lasagna")
option3.pack(side=LEFT)

def submit():
    meal_choice = var.get()
    # Code to send email with meal choice goes here

submit_button = Button(root, text="Submit", command=submit)
submit_button.pack()

root.mainloop()

