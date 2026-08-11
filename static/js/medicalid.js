const medicalIdForm = document.getElementById("medicalIdForm");
const medicalIdMessage = document.getElementById("medicalIdMessage");
const savedMedicalId = document.getElementById("savedMedicalId");

const fullName = document.getElementById("fullName");
const dateOfBirth = document.getElementById("dateOfBirth");
const bloodType = document.getElementById("bloodType");
const allergies = document.getElementById("allergies");
const medications = document.getElementById("medications");
const conditions = document.getElementById("conditions");
const emergencyContact = document.getElementById("emergencyContact");
const emergencyPhone = document.getElementById("emergencyPhone");
const organDonor = document.getElementById("organDonor");


medicalIdForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const medicalData = {
        fullName: fullName.value.trim(),
        dateOfBirth: dateOfBirth.value,
        bloodType: bloodType.value,
        allergies: allergies.value.trim(),
        medications: medications.value.trim(),
        conditions: conditions.value.trim(),
        emergencyContact: emergencyContact.value.trim(),
        emergencyPhone: emergencyPhone.value.trim(),
        organDonor: organDonor.value
    };

    localStorage.setItem(
        "philoShieldMedicalId",
        JSON.stringify(medicalData)
    );

    medicalIdMessage.innerHTML =
        "✅ Medical ID saved successfully.";

    displayMedicalId();
});


function displayMedicalId() {
    const savedData =
        localStorage.getItem("philoShieldMedicalId");

    if (!savedData) {
        savedMedicalId.innerHTML = "";
        return;
    }

    const medicalData = JSON.parse(savedData);

    savedMedicalId.innerHTML =
        "<div class='medical-id-card'>" +

        "<h2>🪪 Saved Medical ID</h2>" +

        "<p><strong>Name:</strong> " +
        safeValue(medicalData.fullName) +
        "</p>" +

        "<p><strong>Date of Birth:</strong> " +
        safeValue(medicalData.dateOfBirth) +
        "</p>" +

        "<p><strong>Blood Type:</strong> " +
        safeValue(medicalData.bloodType) +
        "</p>" +

        "<p><strong>Allergies:</strong> " +
        safeValue(medicalData.allergies) +
        "</p>" +

        "<p><strong>Medications:</strong> " +
        safeValue(medicalData.medications) +
        "</p>" +

        "<p><strong>Medical Conditions:</strong> " +
        safeValue(medicalData.conditions) +
        "</p>" +

        "<p><strong>Emergency Contact:</strong> " +
        safeValue(medicalData.emergencyContact) +
        "</p>" +

        "<p><strong>Emergency Phone:</strong> " +
        safeValue(medicalData.emergencyPhone) +
        "</p>" +

        "<p><strong>Organ Donor:</strong> " +
        safeValue(medicalData.organDonor) +
        "</p>" +

        "<button type='button' onclick='editMedicalId()'>" +
        "✏️ Edit Medical ID</button>" +

        "<button type='button' onclick='deleteMedicalId()'>" +
        "🗑️ Delete Medical ID</button>" +

        "</div>";
}


function safeValue(value) {
    if (!value) {
        return "Not provided";
    }

    return value;
}


function editMedicalId() {
    const savedData =
        localStorage.getItem("philoShieldMedicalId");

    if (!savedData) {
        return;
    }

    const medicalData = JSON.parse(savedData);

    fullName.value = medicalData.fullName || "";
    dateOfBirth.value = medicalData.dateOfBirth || "";
    bloodType.value = medicalData.bloodType || "";
    allergies.value = medicalData.allergies || "";
    medications.value = medicalData.medications || "";
    conditions.value = medicalData.conditions || "";
    emergencyContact.value =
        medicalData.emergencyContact || "";
    emergencyPhone.value =
        medicalData.emergencyPhone || "";
    organDonor.value =
        medicalData.organDonor || "";

    medicalIdMessage.innerHTML =
        "✏️ Edit your information, then press Save Medical ID.";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function deleteMedicalId() {
    const confirmed =
        confirm("Delete your saved Medical ID?");

    if (!confirmed) {
        return;
    }

    localStorage.removeItem("philoShieldMedicalId");

    medicalIdForm.reset();

    savedMedicalId.innerHTML = "";

    medicalIdMessage.innerHTML =
        "🗑️ Medical ID deleted.";
}


displayMedicalId();
