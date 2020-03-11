import struct
import asyncio

#not receiving messages constantly
#receives everytime it sends a message 

async def receive_messages(reader):
    length = await reader.read(struct.calcsize('<i'))
    length = struct.unpack('<i', length)[0]
    name = await reader.read(length)
    name = name.decode()


    length = await reader.read(struct.calcsize('<i'))
    length = struct.unpack('<i', length)[0]
    message = await reader.read(length)
    message = message.decode()
    

    length = await reader.read(struct.calcsize('<i'))
    length = struct.unpack('<i', length)[0]
    time = await reader.read(length)
    time = time.decode()

    print(name,",",time,":",message)

async def get_messages(writer,reader):
    loop = asyncio.get_running_loop()
    #loop that does rececing messages 
    #sending messages asa well
    #two courtines at the same time
    # infinte loop for both  
    #create two task 
    while True:
        try:
            name, message, time = await receive_messages(reader)
            message = await loop.run_in_executor(None,input)

        except:
            pass
        if not message:
            writer.close()
            break
        message = message.encode()
        data = struct.pack('<i', len(message))
        data += struct.pack(str(len(message))+'s', message)
        writer.write(data)
        await writer.drain()

async def tcp_client():
    reader, writer = await asyncio.open_connection("apache.cslab.moravian.edu", 25565)
    name_taken = True

    #checking the  version number 
    Version_Number = 1
    writer.write(struct.pack('<i', Version_Number))
    await writer.drain()
    version_verify = await reader.read(struct.calcsize("<?"))
    version_verify = struct.unpack("<?", version_verify)[0]
    print(version_verify)
    if not version_verify:
        print("Outdated Version")
        writer.close()

    #getting the username from the client
    while name_taken:
        username = input("Enter a username: ")
        username = username.encode()
        data = struct.pack('<i', len(username))
        data += struct.pack(str(len(username))+'s', username)
        writer.write(data)
        await writer.drain()

        #checks to make sure the name is not taken 
        #if name is taken it will ask again for 
        name_taken = await reader.read(struct.calcsize('<?'))
        name_taken = struct.unpack('<?', name_taken)[0]
    print(name_taken)
    
    
    number_of_messages = await reader.read(struct.calcsize('<i'))
    number_of_messages = struct.unpack('<i', number_of_messages)[0]

    for _ in range(number_of_messages): 
        await receive_messages(reader)

    asyncio.create_task(get_messages(writer,reader))   
        
asyncio.run(tcp_client())
    
    
    
