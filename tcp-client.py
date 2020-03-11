import struct
import asyncio
import argparse

async def receive_str(reader):
    length = await reader.read(struct.calcsize('<i'))
    length = struct.unpack('<i', length)[0]
    string = await reader.read(length)
    string = string.decode()
    return string

async def send_str(string,writer):
    string = string.encode()
    data = struct.pack('<i', len(string)) 
    data += struct.pack(str(len(string))+'s', string)
    writer.write(data)
    await writer.drain()

async def receive_messages(reader):
    while True:
        try:
            name    = await receive_str(reader)
            message = await receive_str(reader)
            time    = await receive_str(reader)
            print(name,"-",time+":",message)
        except struct.error:
            break

async def send_message(writer):
    loop = asyncio.get_running_loop()
    while True:
        try:
            message = await loop.run_in_executor(None,input)
            if not message:
                writer.close()
                break
            await send_str(message,writer)
        except:
            pass

async def get_messages(writer,reader):

    # loop that does rececing messages 
    # sending messages as well
    # two coroutines at the same time
    # infinte loop for both  
    # create two task 
    send_task    =  asyncio.create_task(send_message(writer))   
    receive_task =  asyncio.create_task(receive_messages(reader))
    await send_task
    receive_task.cancel()
    try: 
        await receive_task    
    except asyncio.CancelledError: 
        pass

async def client(address,port):
    reader, writer = await asyncio.open_connection(address, port)
    name_taken = True

    #checking the  version number 
    Version_Number = 1
    writer.write(struct.pack('<i', Version_Number))
    await writer.drain()
    version_verify = await reader.read(struct.calcsize("<?"))
    version_verify = struct.unpack("<?", version_verify)[0]
    if not version_verify:
        print("Outdated Version")
        writer.close()

    #getting the username from the client
    while name_taken:
        username = input("Enter a username: ")
        await send_str(username,writer)

        #checks to make sure the name is not taken 
        #if name is taken it will ask again for 
        name_taken = await reader.read(struct.calcsize('<?'))
        name_taken = struct.unpack('<?', name_taken)[0]    
    
    number_of_messages = await reader.read(struct.calcsize('<i'))
    number_of_messages = struct.unpack('<i', number_of_messages)[0]

    for _ in range(number_of_messages): 
        name = await receive_str(reader)
        message = await receive_str(reader)
        time = await receive_str(reader)
        print(name,"-",time+":",message)

    await asyncio.create_task(get_messages(writer,reader))  

def main():
    parser = argparse.ArgumentParser(description='Start the Chat Client')
    parser.add_argument('address', help='Set the server address you want to connect to')
    parser.add_argument('--port', type=int, help='Set the port number to use', default=25565)
    
    args = parser.parse_args()
    asyncio.run(client(args.address, args.port))
    
if __name__ == "__main__":
    main()
    
