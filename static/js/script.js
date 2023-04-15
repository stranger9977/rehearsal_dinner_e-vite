document.addEventListener('DOMContentLoaded', function() {
    // Replace this with the actual data fetched from your server or a data source
    const guests = [
        {
            name: 'Guest 1',
            rsvpStatus: false
        },
        {
            name: 'Guest 2',
            rsvpStatus: false
        }
    ];

    // Function to display the personalized guest information on the landing page
    function displayGuests() {
        const guestContainer = document.querySelector('.guest-box');
        guestContainer.innerHTML = '';

        guests.forEach(guest => {
            const guestDiv = document.createElement('div');
            guestDiv.classList.add('guest');

            const guestName = document.createElement('h3');
            guestName.textContent = guest.name;
            guestDiv.appendChild(guestName);

            const rsvpSelect = document.createElement('select');
            rsvpSelect.innerHTML = `
                <option value="" disabled selected>RSVP</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
            `;
            rsvpSelect.addEventListener('change', function(event) {
                guest.rsvpStatus = event.target.value === 'yes';
            });
            guestDiv.appendChild(rsvpSelect);

            guestContainer.appendChild(guestDiv);
        });
    }

    displayGuests();

    // Add more functions here to handle other dynamic aspects of your website
});
