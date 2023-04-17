import csv
from flask import Flask, render_template, request, redirect, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.ext import Extension
import s3_utils
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

base_url = 'https://rehearsal-dinner.herokuapp.com/'

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

csv_filename = s3_utils.csv_filename


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

guests_by_pair = generate_guest_data(csv_filename)  # Add this line

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
    if guest_name in guests:
        return guests[guest_name]["rsvpStatus"]
    return 'pending'

def update_guest_rsvp(pair_id, guest_name, rsvp_status, guests_by_pair):
    # Update the rsvp status for the guest with the given pair_id and guest name
    if pair_id in guests_by_pair and guest_name in guests_by_pair[pair_id]:
        guests_by_pair[pair_id][guest_name]["rsvpStatus"] = rsvp_status

def update_guest_data(guests_by_pair):
    with open('guests.csv', mode='r') as infile:
        reader = csv.DictReader(infile)
        data = [row for row in reader]

    updated_rows = []

    for row_data in data:
        pair_id = row_data['pair_id']
        guest_name = row_data['name']
        if pair_id in guests_by_pair and guest_name in guests_by_pair[pair_id]:
            row_data.update(guests_by_pair[pair_id][guest_name])

        updated_rows.append(row_data)

    with open('guests.csv', mode='w', newline='') as csvfile:
        fieldnames = ['pair_id', 'name', 'rsvpStatus', 'appetizer', 'entree', 'dessert']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in updated_rows:
            writer.writerow(row)




@app.route('/<pair_id>', methods=['GET', 'POST'])
def guest_page(pair_id):
    print(f"Handling request for pair_id: {pair_id}")  # Add this line
    try:
        # Look up the guests associated with this pair ID
        guests = guests_by_pair[pair_id]

        # Get guest names from the guests dictionary
        guest_names = list(guests.keys())
        print(f"Guests for pair_id {pair_id}: {guest_names}")  # Add this line

        # If the request method is "POST", redirect to the menu page
        if request.method == "POST":
            return redirect(url_for('menu', pair_id=pair_id))

        # If the request method is "GET", render the guest page template with the appropriate data
        return render_template("index.html", pair_id=pair_id, guest_name1=guest_names[0],
                               guest_name2=guest_names[1], get_guest_rsvp=get_guest_rsvp)

    except KeyError:
        # If the pair ID is not found, render an error page
        print(f"Error: Invalid pair_id: {pair_id}")  # Add this line
        return render_template('error.html', error_message="Invalid pair ID")

@app.route('/', methods=['GET', 'POST'])
def index():

    pair_id = request.args.get('pair_id')  # Remove the default pair ID
    if pair_id is None:
        pair_id = "5980"  # Set the default pair ID here

    guest_name1, guest_name2 = get_guest_names(pair_id)

    if request.method == "POST":
        print("Entered POST block in index function")  # Added print statement

        # Get the RSVP status from the form
        rsvp_status1 = request.form.get("rsvpStatus1")
        print(f"Updating RSVP status for {guest_name1} to {rsvp_status1}")

        rsvp_status2 = request.form.get("rsvpStatus2")
        print(f"Updating RSVP status for {guest_name2} to {rsvp_status2}")

        # Update the guest data for the guest whose RSVP status was submitted
        if rsvp_status1 is not None:
            update_guest_rsvp(pair_id, guest_name1, rsvp_status1 == "yes", guests_by_pair)
            print(f"Updating RSVP status for {guest_name1} to {rsvp_status1}")
        if rsvp_status2 is not None:
            update_guest_rsvp(pair_id, guest_name2, rsvp_status2 == "yes", guests_by_pair)
            print(f"Updating RSVP status for {guest_name2} to {rsvp_status2}")

        # Update the CSV file after updating guest data
            # Update the CSV file after updating guest data
            print("Updating guest data in CSV file")
            update_guest_data(guests_by_pair)
            s3_utils.upload_csv_to_s3()  # upload the updated guests.csv to S3

        # Redirect to the menu page after submitting the RSVP status
        return redirect(url_for('menu', pair_id=pair_id))

    # Render the index page if the request method is GET
    return render_template("index.html", pair_id=pair_id, guest_name1=guest_name1,
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
    pair_id = request.args.get('pair_id', "5980")  # default pair ID
    if pair_id is None:
        pair_id = request.args.get('pair_id', "5980")  # default pair ID

    if request.method == "POST":
        # Process form submission and update the menu choices
        guest_name1, guest_name2 = get_guest_names(pair_id)
        guest1_choices = {
            "appetizer": request.form.get(f"{guest_name1}-appetizer"),
            "entree": request.form.get(f"{guest_name1}-entree"),
            "dessert": request.form.get(f"{guest_name1}-dessert")
        }
        guest2_choices = {
            "appetizer": request.form.get(f"{guest_name2}-appetizer"),
            "entree": request.form.get(f"{guest_name2}-entree"),
            "dessert": request.form.get(f"{guest_name2}-dessert")
        }
        guests_by_pair[pair_id][guest_name1]['appetizer'] = guest1_choices["appetizer"]
        guests_by_pair[pair_id][guest_name1]['entree'] = guest1_choices["entree"]
        guests_by_pair[pair_id][guest_name1]['dessert'] = guest1_choices["dessert"]
        guests_by_pair[pair_id][guest_name2]['appetizer'] = guest2_choices["appetizer"]
        guests_by_pair[pair_id][guest_name2]['entree'] = guest2_choices["entree"]
        guests_by_pair[pair_id][guest_name2]['dessert'] = guest2_choices["dessert"]

        # Update the CSV file after updating guest data
        print("Updating guest data in CSV file")
        update_guest_data(guests_by_pair)
        s3_utils.upload_csv_to_s3()  # upload the updated guests.csv to S3

        # Redirect to a success or confirmation page, or just reload the menu page
        return redirect(url_for('final', pair_id=pair_id))

    guest_name1, guest_name2 = get_guest_names(pair_id)
    return render_template('menu.html', guest_name1=guest_name1, guest_name2=guest_name2, menu_items=menu_items, pair_id=pair_id)


@app.route('/final')
def final():

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
