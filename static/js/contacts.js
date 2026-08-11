const saveContactButton = document.getElementById("saveContact");
const savedContacts = document.getElementById("savedContacts");

let contacts =
    JSON.parse(localStorage.getItem("emergencyContacts")) || [];

saveContactButton.addEventListener("click", function () {
    const contactName =
        document.getElementById("contactName").value.trim();

    const contactPhone =
        document.getElementById("contactPhone").value.trim();

    if (contactName === "" || contactPhone === "") {
        alert("Please enter a contact name and phone number.");
        return;
    }

    const newContact = {
        name: contactName,
        phone: contactPhone
    };

    contacts.push(newContact);

    localStorage.setItem(
        "emergencyContacts",
        JSON.stringify(contacts)
    );

    document.getElementById("contactName").value = "";
    document.getElementById("contactPhone").value = "";

    displayContacts();

    alert("Emergency contact saved successfully!");
});


function displayContacts() {
    savedContacts.innerHTML =
        "<h2>Saved Emergency Contacts</h2>";

    contacts.forEach(function (contact, index) {
        const contactCard = document.createElement("div");

        contactCard.innerHTML =
            "<p><strong>Name:</strong> " + contact.name + "</p>" +
            "<p><strong>Phone:</strong> " + contact.phone + "</p>" +
            "<a class='call-button' href='tel:" + contact.phone + "'>" +
            "📞 Call</a>" +
            "<button onclick='deleteContact(" + index + ")'>" +
            "Delete</button>";


        savedContacts.appendChild(contactCard);
    });
}


function deleteContact(index) {
    contacts.splice(index, 1);

    localStorage.setItem(
        "emergencyContacts",
        JSON.stringify(contacts)
    );

    displayContacts();
}


window.addEventListener("load", function () {
    displayContacts();
});