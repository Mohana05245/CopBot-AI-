function getCurrentTime() {

    const now = new Date();

    let hours = now.getHours();

    let minutes = now.getMinutes();

    const ampm = hours >= 12 ? "PM" : "AM";

    hours = hours % 12;

    hours = hours ? hours : 12;

    minutes = minutes < 10 ? "0" + minutes : minutes;

    return `${hours}:${minutes} ${ampm}`;
}

function updateAllTimes() {

    const timeElements = document.querySelectorAll(".chat-time");

    timeElements.forEach((element) => {

        if (
            element.innerText === "Just now" ||
            element.innerText.trim() === ""
        ) {

            element.innerText = getCurrentTime();
        }
    });

    const liveClock = document.getElementById("live-clock");

    if (liveClock) {

        liveClock.innerText = getCurrentTime();
    }
}

window.onload = function () {

    updateAllTimes();

    const chatBox = document.getElementById("chat-box");

    if (chatBox) {

        chatBox.scrollTop = chatBox.scrollHeight;
    }
};

setInterval(updateAllTimes, 1000);