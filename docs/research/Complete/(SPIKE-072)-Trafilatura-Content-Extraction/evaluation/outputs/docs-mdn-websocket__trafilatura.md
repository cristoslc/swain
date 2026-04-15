---
title: WebSocket
url: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
hostname: mozilla.org
description: The WebSocket object provides the API for creating and managing a WebSocket connection to a server, as well as for sending and receiving data on the connection.
sitename: developer.mozilla.org
date: 2024-09-25
---
# WebSocket

##
Baseline
Widely available
*

This feature is well established and works across many devices and browser versions. It’s been available across browsers since July 2015.

* Some parts of this feature may have varying levels of support.

**Note:** This feature is available in [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API).

The `WebSocket`

object provides the API for creating and managing a [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) connection to a server, as well as for sending and receiving data on the connection.

To construct a `WebSocket`

, use the [ WebSocket()](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket) constructor.

**Note:**
The `WebSocket`

API has no way to apply [backpressure](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Concepts#backpressure), therefore when messages arrive faster than the application can process them, the application will either fill up the device's memory by buffering those messages, become unresponsive due to 100% CPU usage, or both. For an alternative that provides backpressure automatically, see [ WebSocketStream](https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream).

[Constructor](https://developer.mozilla.org#constructor)

`WebSocket()`

-
Returns a newly created

`WebSocket`

object.

[Instance properties](https://developer.mozilla.org#instance_properties)

`WebSocket.binaryType`

-
The binary data type used by the connection.

Read only`WebSocket.bufferedAmount`

-
The number of bytes of queued data.

Read only`WebSocket.extensions`

-
The extensions selected by the server.

Read only`WebSocket.protocol`

-
The sub-protocol selected by the server.

Read only`WebSocket.readyState`

-
The current state of the connection.

Read only`WebSocket.url`

-
The absolute URL of the WebSocket.


[Instance methods](https://developer.mozilla.org#instance_methods)

`WebSocket.close()`

-
Closes the connection.

`WebSocket.send()`

-
Enqueues data to be transmitted.


[Events](https://developer.mozilla.org#events)

Listen to these events using `addEventListener()`

or by assigning an event listener to the `oneventname`

property of this interface.

`close`

-
Fired when a connection with a

`WebSocket`

is closed. Also available via the`onclose`

property `error`

-
Fired when a connection with a

`WebSocket`

has been closed because of an error, such as when some data couldn't be sent. Also available via the`onerror`

property. `message`

-
Fired when data is received through a

`WebSocket`

. Also available via the`onmessage`

property. `open`

-
Fired when a connection with a

`WebSocket`

is opened. Also available via the`onopen`

property.

[Examples](https://developer.mozilla.org#examples)

```
// Create WebSocket connection.
const socket = new WebSocket("ws://localhost:8080");
// Connection opened
socket.addEventListener("open", (event) => {
socket.send("Hello Server!");
});
// Listen for messages
socket.addEventListener("message", (event) => {
console.log("Message from server ", event.data);
});
```


[Specifications](https://developer.mozilla.org#specifications)

| Specification |
|---|
# the-websocket-interface |