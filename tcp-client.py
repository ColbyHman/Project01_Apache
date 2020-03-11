import struct
import asyncio

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
    name = await receive_str(reader)
    message = await receive_str(reader)
    time = await receive_str(reader)

    print(name,"-",time+":",message)

async def send_message(writer,message):
    if not message:
        writer.close()
        return writer
    await send_str(message,writer)
    return writer

async def get_messages(writer,reader):
    loop = asyncio.get_running_loop()

    while not writer.is_closing():
        loop.create_task(receive_messages(reader))
        try:
            message = await loop.run_in_executor(None,input)
            writer = loop.create_task(send_message(writer,message))
        except:
            pass

async def tcp_client():
    reader, writer = await asyncio.open_connection("apache", 25565)
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
        await receive_messages(reader)

    asyncio.create_task(get_messages(writer,reader))   
        
asyncio.run(tcp_client())
    
    
    
