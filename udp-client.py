import socket 
import asyncio
from time import gmtime, strftime
from datetime import datetime

port = 25566

def get_ip():
    """Gets the local IP of the current machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('10.255.255.255', 1)) # random IP address, doesn't have to be reachable
            return s.getsockname()[0] # get the outgoing IP address on the machine
        except:
            return '127.0.0.1'

class UDPChatProgram(asyncio.DatagramProtocol):
    name = None
    invalid = '!!Invalid Username!!'
    ip_addr = None
    connection_time = None
    history = []

    def __init__(self):
        """
        This is the constructor for the Chat Program itself
        """
        self.on_con_lost = asyncio.get_running_loop().create_future()
        self.name = input("Enter a username : ")
        self.ip_addr = get_ip()
        self.connection_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
    def add_message_to_history(self,message):
        """
        This function removes the oldest message from the history list and appends the latest message.
        """
        if len(self.history) == 10:
            self.history.pop(0)
        self.history.append(message)

    def send_history(self,addr):
        """
        This function send all of the saved history to a specified (address,port)
        """
        for item in history:
            self.transport.sendto(name_data.encode(), ('255.255.255.255', port))

    def connection_made(self, transport):
        """
        When the connection is created, this will start asking the user for messages
        """
        self.transport = transport

        # Send the name to all other peers
        name_data = self.name+"||!!"+self.name+"!!"
        self.transport.sendto(name_data.encode(), ('255.255.255.255', port))

        # Starts receiving messages as a task in the asyncio loop
        asyncio.create_task(self.send_messages())

    async def send_messages(self):
        """
        This method loops forever and accepts new inputs from the user and then it broadcasts them.
        If the message is the empty string, then the program quits
        """
        loop = asyncio.get_running_loop()
        while True:
            # Get the message from the user
            message = await loop.run_in_executor(None, input)
            if not message:
                self.transport.close()
                break
            message = self.name+"||"+message

            # Broadcast the message
            self.transport.sendto(message.encode(), ('255.255.255.255', port))

    def connection_lost(self, exc):
        """
        This method is called when the transport is closed
        """
        self.on_con_lost.set_result(True)

    def datagram_received(self, data, addr):
        """
        This method is called when a datagram is recieved
        """
        data = data.decode()
        name, data = data.split('||')

        # Determine if the names match as well as the IPs
        if(data == "!!"+self.name+"!!" and self.ip_addr != addr[0]):

            invalid_name = self.name+"||"+self.invalid
            self.transport.sendto(invalid_name.encode(), addr)

        # Determine if the message is !!Invalid Username!! and the IPs match
        elif(data == self.invalid and self.ip_addr != addr[0]):

            self.transport.close()
            print("This username is taken")

        # All other messages will be filtered through here
        elif(data != self.invalid):
            self.add_message_to_history(name,"-",strftime("%Y-%m-%d %H:%M:%S", gmtime())+":",data)
            print(name,"-",strftime("%Y-%m-%d %H:%M:%S", gmtime())+":",data)

    def error_received(self, exc):
        """
        This method is called if there is an error
        """
        print('Error received:', exc)

async def main():
    """
    CHANGE MAIN TO REFLECT OUR PROTOCOL
    """
    # Sets up the socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    sock.bind(('', port))
    
    # Creates the transport and protocol
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(UDPChatProgram, sock=sock)

    # Wait for the connection to be closed
    try:
        await protocol.on_con_lost
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
