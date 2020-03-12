import socket 
import asyncio
from time import gmtime, strftime, sleep

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

    def __init__(self):
        """
        This is the constructor for the Chat Program itself
        """
        self.on_con_lost = asyncio.get_running_loop().create_future()
        self.name = input("Enter a username : ")
        self.ip_addr = get_ip()
        

    def connection_made(self, transport):
        """
        When the connection is created, this will start asking the user for messages
        """
        self.transport = transport
        name_data = self.name+"||!!"+self.name+"!!"
        self.transport.sendto(name_data.encode(), ('255.255.255.255', port))
        # Starts receiving messages as a task in the asyncio loop
        asyncio.create_task(self.send_messages())

    async def send_messages(self):
        """
        Loop forever getting new inputs from the user and then broadcasting them.
        If the input is the empty string (i.e. just an enter) than it stops the program.
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
        Method called whenever the transport is closed.
        """
        self.on_con_lost.set_result(True)

    def datagram_received(self, data, addr):
        """
        Method called whenever a datagram is recieved.
        """
        data = data.decode()
        name, data = data.split('||')
        if(data == "!!"+self.name+"!!" and self.ip_addr != addr[0]):
            invalid_name = self.name+"||"+self.invalid
            self.transport.sendto(invalid_name.encode(), ('255.255.255.255', port))
        elif(data == self.invalid):
            self.transport.close()
            print("This username is taken")
        else:
            print(name,"-",strftime("%Y-%m-%d %H:%M:%S", gmtime())+":",data)

    def error_received(self, exc):
        """
        Method called whenever there is an error with the underlying communication.
        """
        print('Error received:', exc)

async def main():
    """
    CHANGE MAIN TO REFLECT OUR PROTOCOL
    """
    # Setup the socket we will be using - enable broadcase and recieve message on the given port
    # Normally, this wouldn't be necessary, but with broadcasting it is needed
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    sock.bind(('', port))

    
    
    # Create the transport and protocol with our pre-made socket
    # If not provided, you would instead use local_addr=(...) and/or remote_addr=(...)
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(UDPChatProgram, sock=sock)

    # Wait for the connection to be closed/lost
    try:
        await protocol.on_con_lost
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
