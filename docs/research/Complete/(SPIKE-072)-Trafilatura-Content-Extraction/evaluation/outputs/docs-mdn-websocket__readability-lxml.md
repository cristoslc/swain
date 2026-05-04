The `WebSocket` object provides the API for creating and managing a [WebSocket](/en-US/docs/Web/API/WebSockets_API) connection to a server, as well as for sending and receiving data on the connection.

To construct a `WebSocket`, use the [`WebSocket()`](/en-US/docs/Web/API/WebSocket/WebSocket) constructor.

**Note:**
The `WebSocket` API has no way to apply [backpressure](/en-US/docs/Web/API/Streams_API/Concepts#backpressure), therefore when messages arrive faster than the application can process them, the application will either fill up the device's memory by buffering those messages, become unresponsive due to 100% CPU usage, or both. For an alternative that provides backpressure automatically, see [`WebSocketStream`](/en-US/docs/Web/API/WebSocketStream).

[EventTarget](/en-US/docs/Web/API/EventTarget)[WebSocket](/en-US/docs/Web/API/WebSocket)