const saveButton = document.getElementById("savePlan");
const savedFamilyList = document.getElementById("savedFamilyList");

let familyMembers =
    JSON.parse(localStorage.getItem("familyMembers")) || [];

saveButton.addEventListener("click", function () {
    const memberName =
        document.getElementById("memberName").value.trim();

    const memberPhone =
        document.getElementById("memberPhone").value.trim();

    const meetingPlace =
        document.getElementById("meetingPlace").value.trim();

    if (memberName === "" || memberPhone === "") {
        alert("Please enter a name and phone number.");
        return;
    }

    const newMember = {
        name: memberName,
        phone: memberPhone
    };

    familyMembers.push(newMember);

    localStorage.setItem(
        "familyMembers",
        JSON.stringify(familyMembers)
    );

    localStorage.setItem("meetingPlace", meetingPlace);

    document.getElementById("memberName").value = "";
    document.getElementById("memberPhone").value = "";

    displayFamilyMembers();

    alert("Family member saved successfully!");
});


function displayFamilyMembers() {
    savedFamilyList.innerHTML = "<h2>Saved Family Members</h2>";

    familyMembers.forEach(function (member, index) {
        const memberCard = document.createElement("div");

        memberCard.innerHTML =
            "<p><strong>Name:</strong> " + member.name + "</p>" +
            "<p><strong>Phone:</strong> " + member.phone + "</p>" +
            "<button onclick='deleteFamilyMember(" + index + ")'>" +
            "Delete</button>";

        savedFamilyList.appendChild(memberCard);
    });
}


window.addEventListener("load", function () {
    document.getElementById("meetingPlace").value =
        localStorage.getItem("meetingPlace") || "";

    displayFamilyMembers();
});
function deleteFamilyMember(index) {
    familyMembers.splice(index, 1);

    localStorage.setItem(
        "familyMembers",
        JSON.stringify(familyMembers)
    );

    displayFamilyMembers();
}