const form = document.getElementById("queryForm");
const socket = new WebSocket("ws://192.168.1.28:8765");
var chat = document.getElementById("chat");
var loadCount = 1;
var load;

function scrollDown() {
    chat.scrollTop = chat.scrollHeight - chat.clientHeight;
}

form.addEventListener("submit", e => {
    e.preventDefault();
    const query = document.getElementById("query").value;

    if(query == "") {
        return;
    }

    var msg = document.createElement("div");
    msg.id = "userMsg";
    msg.classList.add("msg");
    msg.innerHTML = query;
    chat.appendChild(msg);
    scrollDown();

    var loading = document.createElement("div");
    loading.id = "loadingMsg";
    loading.classList.add("msg");
    loadCount = 1;
    loading.innerHTML = "⬤";
    chat.appendChild(loading);
    
    load = setInterval(() => {
        loadCount = loadCount%3 + 1;
        loading.innerHTML = "⬤" + " ⬤".repeat(loadCount-1);
    }, 1000);
    
    socket.send(query);
    document.getElementById("query").value = "";
});

socket.addEventListener("message", e => {
    console.log(e.data);
    const data = JSON.parse(e.data);
    if(data.form == "content") {
        clearInterval(load);
        chat.removeChild(document.getElementById("loadingMsg"));

        var msg = document.createElement("div");
        msg.id = "frokMsg";
        msg.classList.add("msg");
        msg.innerHTML = data.message.replaceAll("\n", "<br>");
        chat.appendChild(msg);
        scrollDown();
    } else if(data.form == "command" && data.message == "dog") {
        document.getElementById("image").style.opacity = 1;
    } else if(data.form == "command" && data.message == "fred") {
        document.getElementById("image").style.backgroundImage = "url('images/fred.jpg')";
    }
});