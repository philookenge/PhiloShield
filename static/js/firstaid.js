const firstAidContainer =
    document.getElementById("firstAidContainer");

const firstAidGuides = [
    {
        icon: "❤️",
        title: "Adult or Teen CPR",
        steps: [
            "Check that the area is safe.",
            "Tap the person and shout to check for a response.",
            "Call 911 or ask someone nearby to call.",
            "If the person is not breathing normally, place both hands in the center of the chest.",
            "Push hard and fast continuously until emergency help arrives or the person begins breathing.",
            "Use an AED if one is available and follow its spoken instructions."
        ]
    },
    {
        icon: "🩸",
        title: "Severe Bleeding",
        steps: [
            "Call 911 for severe or uncontrolled bleeding.",
            "Use gloves or a clean barrier when possible.",
            "Apply firm, steady pressure directly over the wound using clean cloth or gauze.",
            "Keep pressing until help arrives.",
            "If blood soaks through, add more cloth on top. Do not remove the original layer.",
            "Do not remove an object that is deeply stuck in the wound."
        ]
    },
    {
        icon: "🤧",
        title: "Choking",
        steps: [
            "Ask whether the person is choking.",
            "If the person can cough or speak, encourage coughing.",
            "If the person cannot breathe, speak, or cough, call 911 immediately.",
            "Follow the emergency dispatcher’s instructions.",
            "Do not perform a blind finger sweep inside the mouth.",
            "If the person becomes unresponsive, begin CPR and use an AED if available."
        ]
    },
    {
        icon: "🔥",
        title: "Burns",
        steps: [
            "Move the person away from the source of the burn.",
            "Cool the burn under cool running water for at least 20 minutes.",
            "Do not use ice, butter, oils, or creams.",
            "Remove jewellery or loose clothing near the burn unless it is stuck to the skin.",
            "Cover the burn loosely with a clean, non-stick dressing.",
            "Call 911 for severe, electrical, chemical, large, deep, facial, hand, foot, joint, or airway burns."
        ]
    },
    {
        icon: "🦴",
        title: "Possible Broken Bone",
        steps: [
            "Keep the injured area still.",
            "Do not try to straighten the bone.",
            "Support the injured area in the position you found it.",
            "Apply a wrapped cold pack near the injury if this does not cause movement.",
            "Call 911 for an open fracture, severe bleeding, loss of feeling, or an injured neck, back, hip, or thigh."
        ]
    },
    {
        icon: "💓",
        title: "Possible Heart Attack",
        steps: [
            "Call 911 immediately.",
            "Have the person stop activity and rest.",
            "Keep the person calm and loosen tight clothing.",
            "Do not drive the person yourself unless emergency services are unavailable.",
            "If the person becomes unresponsive and is not breathing normally, begin CPR.",
            "Use an AED if one is available."
        ]
    },
    {
        icon: "🧠",
        title: "Possible Stroke — F.A.S.T.",
        steps: [
            "Face: Ask the person to smile. Look for one-sided drooping.",
            "Arms: Ask the person to raise both arms. Look for one arm drifting downward.",
            "Speech: Ask the person to repeat a simple sentence. Listen for slurred or unusual speech.",
            "Time: Call 911 immediately if any sign is present.",
            "Note the time when symptoms first appeared.",
            "Do not give food, drinks, or medicine unless emergency professionals instruct you."
        ]
    }, {
        icon: "⚡",
        title: "Electric Shock",
        steps: [
            "Do not touch the person if they are still connected to electricity.",
            "Turn off the power source if it is safe to do so.",
            "Call 911 for serious electric shock.",
            "If the person is unresponsive and not breathing normally, begin CPR.",
            "Treat visible burns with cool running water after the power is disconnected.",
            "Keep the person still and wait for emergency help."
        ]
    },
    {
        icon: "☀️",
        title: "Heat Stroke",
        steps: [
            "Call 911 immediately.",
            "Move the person to a cooler or shaded place.",
            "Remove unnecessary outer clothing.",
            "Cool the person with wet cloths, fans, or cool water.",
            "Do not give food or drinks if the person is confused or unconscious.",
            "Stay with the person until emergency help arrives."
        ]
    },
    {
        icon: "🥶",
        title: "Hypothermia",
        steps: [
            "Move the person to a warm, dry place.",
            "Remove wet clothing carefully.",
            "Wrap the person in blankets or dry clothing.",
            "Warm the center of the body first.",
            "Do not rub the arms or legs.",
            "Call 911 if the person is confused, very sleepy, or stops shivering."
        ]
    },
    {
        icon: "🐝",
        title: "Severe Allergic Reaction",
        steps: [
            "Call 911 immediately.",
            "Help the person use their prescribed epinephrine auto-injector if available.",
            "Have the person lie down unless breathing is difficult.",
            "Do not give food or drink.",
            "Watch for breathing problems.",
            "Begin CPR if the person becomes unresponsive and is not breathing normally."
        ]
    },
    {
        icon: "🐍",
        title: "Snake or Animal Bite",
        steps: [
            "Move away from the animal and make sure the area is safe.",
            "Call 911 for venomous bites, severe bleeding, or breathing problems.",
            "Keep the injured person calm and still.",
            "Wash minor animal bites with soap and water.",
            "Do not cut the wound or try to suck out venom.",
            "Do not apply ice or a tight tourniquet to a snake bite."
        ]
    },
    {
        icon: "⚠️",
        title: "Poisoning",
        steps: [
            "Call 911 if the person is unconscious, having trouble breathing, or having a seizure.",
            "Do not make the person vomit.",
            "Do not give food or drink unless a professional instructs you.",
            "Move away from fumes or chemicals if it is safe.",
            "Keep the product container or label for emergency responders.",
            "Follow instructions from emergency services or Poison Control."
        ]
    }

];


function displayFirstAidGuides() {
    firstAidContainer.innerHTML =
        "<section class='first-aid-warning'>" +
        "<strong>Important:</strong> Call 911 for a life-threatening " +
        "emergency. This guide does not replace professional training " +
        "or instructions from emergency dispatchers." +
        "</section>";

    firstAidGuides.forEach(function (guide, index) {
        const guideCard = document.createElement("section");
        guideCard.className = "first-aid-card";

        const stepsHtml = guide.steps
            .map(function (step) {
                return "<li>" + step + "</li>";
            })
            .join("");

        guideCard.innerHTML =
            "<button class='first-aid-title' " +
            "onclick='toggleFirstAidGuide(" + index + ")'>" +
            "<span>" + guide.icon + " " + guide.title + "</span>" +
            "<span id='firstAidArrow" + index + "'>＋</span>" +
            "</button>" +

            "<div class='first-aid-details' " +
            "id='firstAidDetails" + index + "'>" +
            "<ol>" + stepsHtml + "</ol>" +
            "<a class='call-button' href='tel:911'>📞 Call 911</a>" +
            "</div>";

        firstAidContainer.appendChild(guideCard);
    });
}


function toggleFirstAidGuide(index) {
    const details =
        document.getElementById("firstAidDetails" + index);

    const arrow =
        document.getElementById("firstAidArrow" + index);

    const isOpen = details.classList.contains("open");

    document
        .querySelectorAll(".first-aid-details")
        .forEach(function (item) {
            item.classList.remove("open");
        });

    document
        .querySelectorAll("[id^='firstAidArrow']")
        .forEach(function (item) {
            item.textContent = "＋";
        });

    if (!isOpen) {
        details.classList.add("open");
        arrow.textContent = "−";
    }
}


displayFirstAidGuides();
