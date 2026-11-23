
document.addEventListener("DOMContentLoaded", function () {

    // Set the earliest selectable departure date to today.
    const dateInput = document.getElementById("travel-date");

    if (dateInput) {
        const today = new Date();
        const localDate = [
            today.getFullYear(),
            String(today.getMonth() + 1).padStart(2, "0"),
            String(today.getDate()).padStart(2, "0")
        ].join("-");

        dateInput.min = localDate;
    }

    // Homepage flight search form.
    const searchForm = document.getElementById("flightSearchForm");

    if (searchForm) {
        searchForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const departure = document
                .getElementById("departure").value.trim();

            const arrival = document
                .getElementById("arrival").value.trim();

            const date = document
                .getElementById("travel-date").value;

            const message = document.getElementById("search-message");

            if (!departure || !arrival || !date) {
                message.textContent =
                    "Please complete all flight search fields.";
                return;
            }

            if (departure.toLowerCase() === arrival.toLowerCase()) {
                message.textContent =
                    "Departure and destination must be different.";
                return;
            }

            if (date < localDateToday()) {
                message.textContent =
                    "Please select today or a future date.";
                return;
            }

            message.textContent =
                "Your search details are valid. Live flight results will be connected in the next development stage.";
        });
    }

});


function localDateToday() {
    const today = new Date();

    return [
        today.getFullYear(),
        String(today.getMonth() + 1).padStart(2, "0"),
        String(today.getDate()).padStart(2, "0")
    ].join("-");
}
