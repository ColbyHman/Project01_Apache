import struct
import socket
import asyncio
from time import gmtime, strftime, sleep

now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
history = [("Jeff", "Test Message", now)]
users = {}

async def send_str(string,writer):
    string = string.encode()
    data = struct.pack('<i', len(string)) 
    data += struct.pack(str(len(string))+'s', string)
    writer.write(data)
    await writer.drain()

async def add_message_to_history(message):
    """
    This function removes the oldest message from the history list and appends the latest message.
    """
    if len(history) == 10:
        history.pop(0)
    history.append(message)

async def get_message(reader):
    length = await reader.read(struct.calcsize('<i'))
    length = struct.unpack('<i', length)[0]
    incoming = await reader.read(length)
    incoming = incoming.decode()
    return incoming

async def send_messages(username, reader):
    """
    This function receives messages from a client and sends them to all other clients
    """
    try:
        while True:
            try:
                message = await get_message(reader)
                message = (username,message,strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                print(message)
                await add_message_to_history(message)
                for name in users.keys():
                    user_writer = users.get(name)
                    await send_str(message[0], user_writer)
                    await send_str(message[1], user_writer)
                    await send_str(message[2], user_writer)
            except:
                pass
    finally:
        print(username,"is disconnecting!")
        user_writer = users.get(username)
        user_writer.close()
        await user_writer.wait_closed()
        print(username,"disconnected!")
        break
        user_writer = users.pop(username)
        print(username,"closed!")

    

async def handle_connection(reader, writer):
    """
    This function handles the connection between the server and the client.
    It will make sure the version number is correct and that the desired username is unqiue.
    Once the user is allowed to be in the chat, the server will send the client the 10 most recent messages.
    The format will be a tuple : (Name, Timestamp, Message).
    """
    version = 1
    name_taken = True

    # Verifies proper version number of the user attempting to connect
    version_number = await reader.read(struct.calcsize('<i'))
    version_number = struct.unpack("<i",version_number)[0]
    if version_number != 1:
        writer.write(struct.pack('<?',False))
    else:
        writer.write(struct.pack('<?',True))
    await writer.drain()
    
    # Verifies that the user's desired username is not already in use
    while name_taken:
        length = await reader.read(struct.calcsize("<i"))
        length = struct.unpack('<i', length)[0]
        username = await reader.read(length)
        username = username.decode()
        if username not in users.keys():
            name_taken = False
            writer.write(struct.pack('<?', name_taken))
            await writer.drain()
            users[username] = writer
            break
        else:
            name_taken = True
            writer.write(struct.pack('<?', name_taken))
            await writer.drain()

    writer.write(struct.pack('<i', len(history)))
    await writer.drain()

    # Checks if there are messages in the history
    # For each item in the history, it will send the name, message, 
    # and time of the message to the new client
    if history:
        for item in history:
            print(item)
            name = item[0]
            await send_str(name,writer)

            message = item[1]
            await send_str(message,writer)

            time = item[2]
            await send_str(time,writer)
            
    asyncio.create_task(send_messages(username, reader))

    
    

async def main():
    server = await asyncio.start_server(handle_connection, '', 25565)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())

