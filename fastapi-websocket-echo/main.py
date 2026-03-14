from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebSocket Test</title>
        </head>
        <body>
            <h2>WebSocket Echo Test</h2>

            <input id="messageInput" type="text" placeholder="Enter message">
            <button onclick="sendMessage()">Send</button>

            <h3>Messages</h3>
            <ul id="messages"></ul>

            <script>
                const ws = new WebSocket("ws://localhost:8000/ws");

                ws.onmessage = function(event) {
                    const li = document.createElement("li");
                    li.textContent = event.data;
                    document.getElementById("messages").appendChild(li);
                };

                function sendMessage() {
                    const input = document.getElementById("messageInput");
                    ws.send(input.value);
                    input.value = "";
                }
            </script>
        </body>
        </html>
"""
@app.get("/")
async def main_app():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_demo(webSocket: WebSocket):
    await webSocket.accept()
    try:
        while True:
            data = await webSocket.receive_text()
            response = "Server Received: " + data
            await webSocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")

