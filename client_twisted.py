from twisted.internet import reactor, protocol

class ClientProtocol(protocol.Protocol):
    def connectionMade(self):
        print("Connected to the server")
        self.sendMessage("Hello server!")
        self.factory.client_instance = self

    def connectionLost(self, reason):
        print("Connection lost:", reason)

    def dataReceived(self, data):
        # Handle received data from the server
        # Extract relevant information from the data
        # Update game state or perform actions accordingly
        pass

    def sendMessage(self, message):
        self.transport.write(message.encode())

    def send_message_to_server(self, message):
        if self.factory.client_instance:
            self.factory.client_instance.sendMessage(message)

    def connect_to_server(address, player, player_list):
        client_factory = protocol.ClientFactory()
        client_factory.protocol = lambda: ClientProtocol(player, player_list)
        reactor.connectTCP(address, 4321, client_factory)

# def run_client():
#     client_factory = protocol.ClientFactory()
#     client_factory.protocol = ClientProtocol
#     client_factory.client_instance = None
#     reactor.connectTCP("127.0.0.1", 4321, client_factory)
#     reactor.run()

    # return client_factory

# # Start the client connection
# client_factory = run_client()

print("sending to server.")
