import csv
from flask import Flask, render_template, request, redirect, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.ext import Extension

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

base_url = 'https://yourwebsite.com/invitation/'

# Add MenuItem class definition
class MenuItem:
    def __init__(self, id, name, description, category):
        self.id = id
        self.name = name
        self.description = description
        self.category = category

# Create menu items
menu_items = [
    MenuItem(1, 'Appetizer 1', 'Delicious appetizer 1', 'appetizer'),
    MenuItem(2, 'Appetizer 2', 'Delicious appetizer 2', 'appetizer'),
    MenuItem(3, 'Appetizer 3', 'Delicious appetizer 3', 'appetizer'),
    MenuItem(4, 'Entree 1', 'Delicious entree 1', 'entree'),
    MenuItem(5, 'Entree 2', 'Delicious entree 2', 'entree'),
    MenuItem(6, 'Entree 3', 'Delicious entree 3', 'entree'),
    MenuItem(7, 'Dessert 1', 'Delicious dessert 1', 'dessert'),
    MenuItem(8, 'Dessert 2', 'Delicious dessert 2', 'dessert'),
    MenuItem(9, 'Dessert 3', 'Delicious dessert 3', 'dessert')
]



def generate_guest_urls(csv_filename):
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        urls = {}
        for row in reader:
            pair_id = row['pair_id']
            urls[pair_id] = base_url + pair_id
    return urls

csv_filename = 'guests.csv'
guest_urls = generate_guest_urls(csv_filename)

for pair_id, url in guest_urls.items():
    print(f"Pair  {pair_id}: {url}")

def generate_guest_data(csv_filename):
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        guests_by_pair = {}
        for row in reader:
            pair_id = row['pair_id']
            guest_name = row['name']
            rsvp_status = row['rsvpStatus']
            appetizer = row.get('appetizer', '')
            entree = row.get('entree', '')
            dessert = row.get('dessert', '')
            if pair_id not in guests_by_pair:
                guests_by_pair[pair_id] = {}
            guests_by_pair[pair_id][guest_name] = {"rsvpStatus": rsvp_status, "appetizer": appetizer, "entree": entree, "dessert": dessert}
    return guests_by_pair


def get_guest_names(pair_id=None):
    # If pair_id is not specified, return the first pair
    if pair_id is None:
        pair_id = next(iter(guests_by_pair.keys()))

    # Get the guests with the specified pair_id
    guests = guests_by_pair[pair_id]

    # If there are two guests, return their names
    if len(guests) == 2:
        return list(guests.keys())
    # Otherwise, return default names
    else:
        return "John Doe", "Jane Doe"

def get_guest_rsvp(guest_name, guests):
    for guest in guests:
        if guest["name"] == guest_name:
            return guest["rsvpStatus"]
    return None

def update_guest_rsvp(pair_id, guest_name, rsvp_status, guests_by_pair):
    # Update the rsvp status for the guest with the given pair_id and guest name
    if pair_id in guests_by_pair and guest_name in guests_by_pair[pair_id]:
        guests_by_pair[pair_id][guest_name]["rsvpStatus"] = rsvp_status

def update_guest_data(guests_by_pair):
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['pair_id', 'name', 'rsvpStatus', 'appetizer', 'entree', 'dessert'])
        writer.writeheader()
        for pair_id, guests in guests_by_pair.items():
            for guest_name, guest_data in guests.items():
                writer.writerow({
                    'pair_id': pair_id,
                    'name': guest_name,
                    'rsvpStatus': guest_data["rsvpStatus"],
                    'appetizer': guest_data.get("appetizer", ""),
                    'entree': guest_data.get("entree", ""),
                    'dessert': guest_data.get("dessert", "")
                })


csv_filename = 'guests.csv'
guests_by_pair = generate_guest_data(csv_filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_pair_id = request.args.get('pair_id', "5980")  # default pair ID
    guest_name1, guest_name2 = get_guest_names(selected_pair_id)

    if request.method == "POST":
        # Get the RSVP status from the form
        rsvp_status1 = request.form.get("rsvpStatus1")
        rsvp_status2 = request.form.get("rsvpStatus2")
        rsvp_guest = request.form.get("rsvp_guest")

        # Update the guest data for the guest whose RSVP status was submitted
        guests_by_pair = generate_guest_data(csv_filename)
        if rsvp_status1 is not None:
            update_guest_rsvp(selected_pair_id, guest_name1, rsvp_status1 == "yes", guests_by_pair)
            print(f"Updating RSVP status for {guest_name1} to {rsvp_status1}")
        if rsvp_status2 is not None:
            update_guest_rsvp(selected_pair_id, guest_name2, rsvp_status2 == "yes", guests_by_pair)
            print(f"Updating RSVP status for {guest_name2} to {rsvp_status2}")

        # Update the CSV file after updating guest data
        print("Updating guest data in CSV file")
        update_guest_data(guests_by_pair)

        # Redirect to thank you page
        return redirect(url_for('menu', selected_pair_id=selected_pair_id))

    return render_template("index.html", selected_pair_id=selected_pair_id, guest_name1=guest_name1,
                           guest_name2=guest_name2, get_guest_rsvp=get_guest_rsvp)

def get_guest_menu_choices(pair_id):
    # Get the guests with the specified pair_id
    guests = guests_by_pair[pair_id]

    # If there are two guests, return their menu choices
    if len(guests) == 2:
        guest1_choices = {
            "appetizer": request.form.get(f"{guests[0]['name']}-appetizer"),
            "entree": request.form.get(f"{guests[0]['name']}-entree"),
            "dessert": request.form.get(f"{guests[0]['name']}-dessert")
        }
        guest2_choices = {
            "appetizer": request.form.get(f"{guests[1]['name']}-appetizer"),
            "entree": request.form.get(f"{guests[1]['name']}-entree"),
            "dessert": request.form.get(f"{guests[1]['name']}-dessert")
        }
        return guest1_choices, guest2_choices
    # Otherwise, return None
    else:
        return None


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    global guests_by_pair
    selected_pair_id = request.args.get('selected_pair_id', "5980")

    if request.method == "POST":
        # Process form submission and update the menu choices
        guest_name1, guest_name2 = get_guest_names(selected_pair_id)
        # Process form submission and update the menu choices
        guests_by_pair[selected_pair_id][guest_name1]['appetizer'] = request.form.get(f"{guest_name1}-appetizer")
        guests_by_pair[selected_pair_id][guest_name1]['entree'] = request.form.get(f"{guest_name1}-entree")
        guests_by_pair[selected_pair_id][guest_name1]['dessert'] = request.form.get(f"{guest_name1}-dessert")

        guests_by_pair[selected_pair_id][guest_name2]['appetizer'] = request.form.get(f"{guest_name2}-appetizer")
        guests_by_pair[selected_pair_id][guest_name2]['entree'] = request.form.get(f"{guest_name2}-entree")
        guests_by_pair[selected_pair_id][guest_name2]['dessert'] = request.form.get(f"{guest_name2}-dessert")

        # Update the CSV file after updating guest data
        print("Updating guest data in CSV file")
        update_guest_data(guests_by_pair)

        # Redirect to a success or confirmation page, or just reload the menu page
        return redirect(url_for('final', selected_pair_id=selected_pair_id))

    guest_name1, guest_name2 = get_guest_names(selected_pair_id)
    return render_template('menu.html', guest_name1=guest_name1, guest_name2=guest_name2, menu_items=menu_items)

@app.route('/final')
def final():
    guests_by_pair = generate_guest_data(csv_filename)

    # Filter the guests who have RSVP'd "yes" and have submitted their menu choices
    confirmed_guests = []
    for pair_id, guests in guests_by_pair.items():
        for guest_name, guest_data in guests.items():
            if guest_data["rsvpStatus"]:
                guest_menu_choices = {
                    'appetizer': guest_data.get('appetizer'),
                    'entree': guest_data.get('entree'),
                    'dessert': guest_data.get('dessert')
                }
                if all(guest_menu_choices.values()):
                    confirmed_guests.append({"name": guest_name, **guest_data, "menuChoices": guest_menu_choices})

    return render_template("final.html", guests=confirmed_guests)


if __name__ == '__main__':
    app.run(debug=True)
