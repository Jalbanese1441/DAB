import discord
from discord.ext import commands
import os
import subprocess
import time
import json
import pickle
# Clears the console
cls = lambda: os.system("cls")


# This formats the ($cmd) command so that it can be run
def formatCommand(c):
    CMDcommand = ""
    # Combines multiple commands to be entered at once
    for i in range(len(c)):
        if i+1 == len(c): CMDcommand += str(c[i])
        else: CMDcommand += str(c[i]+" & ")
    return CMDcommand


# Takes in a command (or a list of commands) and enters them into the terminal
def cmd(CMDcommand):
    p = subprocess.run(['cmd', '/c', CMDcommand], capture_output=True, text=True)
    # If the command runs successfully it returns its result, if not then it returns an error code
    # I WILL NEED TO LOG THIS
    if p.returncode != 0:
        return "Error:\n"+str(p.stderr)
    return p.stdout


# command name, repo link, file path, file name, list of id's
def newRepo(name, link, file_name, ids):
    # The flowing is a command that is added to the start of a python file so the program can get it's pid
    addMe = ["import os", "os.getpid()", "f=open(\"pid.txt\",\"w+\")", "f.write(str(os.getpid()))", "f.close()"]
    subprocess.run(['cmd', '/c', f"git clone {link}"]) # Clones the repo
    time.sleep(3) # jic
    tmp = link.split("/")
    folderName = str(tmp[-1])
    # location is the exact location of the file on the computer
    location = str(os.path.abspath(os.getcwd())) + "\\" + folderName + "\\" + str(file_name)  # full path of program
    tmp = location
    tmp = tmp.replace(file_name, "")  # Gets the path of the folder
    # Checks to see if the file the user specified exists
    if not os.path.exists(location):
        return f"{file_name} not found"

    # Saves the content of the file to a list
    f = open(location, "r")
    tmpList = f.readlines()
    f.close()

    # Overwrites the file with the new code
    # When the program launches it will generate a text file with it's pid in it
    # This is so that the user can kill the process later
    f = open(location, "w")
    for line in addMe:
        f.write(line)
        f.write("\n")
    f.writelines(tmpList)
    f.close()

    # Checks to see if there is a pipenv that needs to be set up and sets it up
    if os.path.exists(tmp + "pipfile"):
        n = tmp + "pipfile"
        subprocess.run(['cmd', '/c', f"cd {n} & pipenv install"])
    # Updates the dictionary
    global gitData
    gitData[name] = [link, file_name, tmp, ids]
    with open('gitData.json', 'w') as f:
        json.dump(gitData, f)
    return f"{link} was successfully saves under the following command: {name}"


# activate takes in a command name and will activate the corresponding python file
def activate(command):
    global gitData, runningProcesses
    #(f"all data inside gitData:\n{gitData}")
    info = gitData[command]
    #print(f"gitData command\n{gitData.get(command)}")
    #print(f"given info is\n{info}")
    path = info[2]  # path of the folder
    fileName = info[1]

    # If the program has already set up the file then it can just run the launcher script
    if os.path.exists(f"{command}ProgramLauncher.bat"):
        subprocess.run(['cmd', '/c', f"cd {path} & {fileName}ProgramLauncher.bat"])

    # If a pipfile exists then it will be installed before running the script
    if os.path.exists(path + "pipfile"):
        n = path + "pipfile"
        subprocess.run(['cmd', '/c', f"cd {n} & pipenv install"])
        time.sleep(2)
        # We have to run the file using this method because if you launch it
        # using Python, sometimes the program doesn't output its pid
        f = open(f"{command}ProgramLauncher.bat", "w+")
        f.write(f"cd \"{path}\"\n")
        f.write("pipenv install\n")
        f.write(f"pipenv run \"{fileName}\"\n")
        f.write("exit")
        f.close()

    else:
        # Make the launcher script for the file
        f = open(f"{command}ProgramLauncher.bat", "w+")
        f.write(f"cd \"{path}\"\n")
        f.write(f"\"{fileName}\"\n")
        f.write("exit")
        f.close()

    # Runs the launcher file
    subprocess.run(['cmd', '/c', f"start {command}ProgramLauncher.bat"])
    # Waits a few seconds for the script to execute
    time.sleep(2)
    #print("Full file path is:", fullFilePath)
    # This look keeps looking for the programs pid
    if not os.path.exists(path+"pid.txt"):
        for i in range(40):
            if os.path.exists(path+"pid.txt"):
                break
            if i == 39:
                # If the program can't find the pid file then an error has occurred
                return "An error has occurred when trying to run the program"
            time.sleep(1)
    f = open(path+"pid.txt", "r")
    pid = int(f.read())
    f.close()
    # This stores all running processes
    # Key: command name, value: pid
    runningProcesses[command] = pid
    return f"{command} was successfully activated"


# Updates and saved the cmdStorage dictionary
def addCommand(name, lastCommand, ids):
    # command name, command, list of authorised users
    global cmdStorage
    cmdStorage[name] = [lastCommand, ids]
    with open('cmdStorage.json', 'w') as f:
        json.dump(cmdStorage, f)


def killProc(pid, name):  # Kills a process when give a pid
    p = subprocess.run(['cmd', '/c', f"taskkill /F /PID {pid}"], capture_output=True, text=True)
    # Occasionally the program logs the wrong pid, if this happens then thr program will reread the pid file
    if p.returncode != 0:
        global gitData
        path = str(gitData[name][2])+"pid.txt"
        if not os.path.exists(path):
            return "error"
        f = open(path, "r")
        pid = int(f.read())
        f.close()
        subprocess.run(['cmd', '/c', f"taskkill /F /PID {pid}"])


# Fully deletes a repo and removes it's commands from the bot
def delRepo(name, path):
    global runningProcesses, gitData
    if name in runningProcesses:  # Kills the program is it's running
        pid = runningProcesses[name]
        print("Pid is")
        print(pid)
        if killProc(pid, name) == "error":
            return f"{name} refused to die"
        del runningProcesses[name] # Removes it from the dictionary
    currentlyInstalled = os.path.exists(path)
    # Removes the folder if it exits
    time.sleep(3)
    if currentlyInstalled:
        os.system(f"rmdir /S /Q {path}")
        while currentlyInstalled:
            currentlyInstalled = os.path.isdir(path)
        # If there is only one value is left then the file has to be deleted.
        # Else it will cause errors when trying read a blank file
        if len(gitData.keys()) == 1:
            if os.path.exists('gitData.json'):
                os.remove('gitData.json')
        else:
            with open('gitData.json', 'w') as f:  # Overwrites the the json file
                json.dump(gitData, f)
    # Removes the launcher
    if os.path.exists(f"{name}ProgramLauncher.bat"):
        os.remove(f"{name}ProgramLauncher.bat")
    del gitData[name]  # Removes the vale form the dictionary


# Checks to see if the user is an admin
def isAdmin(id):
    if str(id) in userSettings[2:]:
        return True
    else:
        return False


# Checks to see if the user can use a command
def isAuthorised(id, ids, commandID):
    if str(id) in userSettings[2:]:  # Admins can use any command
        return True
    if "all" in commandID:  # "all" means that every user can run the command
        return True
    # Uses set’s and property to check if the user has an id that is authorised
    idSet = set(ids)
    cidSet = set(commandID)
    if (idSet & cidSet):
        return True
    else:
        return False


# This function and the next two are used to test to see if a synchronous command is running
# and prevent another one from being run
# cip - command in progress
def checkcip():
    global cip
    if cip: return True
    else: return False


def Fcip():
    global cip
    cip = False


def Tcip():
    global cip
    cip = True

# Using a .pkl file makes it harder to modify form cmd but
# you should only give cmd access to those who you trust
# Saves the information to the file
def saveInfo():
    global userSettings
    with open('User_settings.pkl', 'wb') as f:
     pickle.dump(userSettings, f)


# This extracts the users settings as well as the admins from the file
def getInfo():
    global userSettings
    with open('User_settings.pkl', 'rb') as f:
         userSettings = pickle.load(f)


def deleteLog():  # Deletes the log files
    if os.path.exists("log.txt"):
        os.remove("log.txt")



# This stores the users settings as well as all of the id's of the admins
# Admins have access to every command as well as access special commands
# [enable logging, wipe logs on bot startup, main bot admin, bot admin2, admin3, ect]
userSettings = []


cmdStorage = {}
# cmdStorage stores the command name as the key and the value is a list.
# The first element of the list is the command that is entered into cmd, the second element of the list
# is another list containing all authorised id's and user id's who can access the command
# If you want to let anyone use the command, add in "all" into the list of authorized id's
# Only administrators can add, modify or remove a command
# EX: cmdStorage = {"command name": ["the command it's self", ["the list of authorised id's"]]}


gitData = {}
# This stores information regarding GitHub repository's
# The key is the command name and the value is a nested list like cmdStorage
# The first element of the value is the link, then the name of the file to run, then the folder path
# the last element if the nested list of authorised user id's


# running processes is a dictionary that will store the pid of all running processes
# Key: command name, value: pid
runningProcesses = {}


#If this is the first time the program is being run then the setup will run
if not os.path.exists("User_settings.pkl"):
    while True:
        cls()
        print("SOME BASIC DESCRIPTION OF THR PROGRAM HERE")
        print("Do you want to enable logging? (y/n)")
        userChoice = input()
        if userChoice == "y" or userChoice == "n":
         if userChoice == "y": userSettings.append(True)
         else: userSettings.append(False)
         cls()
         print("Do you want to wipe logs every time this program restarts? (y/n)")
         userChoice = input()
         if userChoice == "y" or userChoice == "n":
             if userChoice=="y": userSettings.append(True)
             else: userSettings.append(False)
         else:
             print(f"\"{userChoice}\" is not a valid option, please enter \'n\' or \'y\'")
             print("Press enter to re-enter your choice")
             input()
             continue
         cls()
         print("Please enter the Discord user id of the bot administrator:\n(Who do you want to have full control of the bot)")
         print("This can be changed by deleting the \"User_settings.pkl\" file")
         botAdmin = input()
         userSettings.append(botAdmin)
         saveInfo()  # Saves the data
         cls()
         print("User choices saved!\nPress enter to continue")
         input()
         break
        else:
            print(f"\"{userChoice}\" is not a valid option, please enter \'n\' or \'y\'")
            print("Press enter to re-enter your choice")
            input()

else: getInfo()  # Retrieves that data

# Deletes the logs on startup if the user specified it
if userSettings[1]:
    deleteLog()

# If an existing dictionary exists it will loaded
if os.path.exists('gitData.json'):
    with open('gitData.json') as f:
        data = f.read()
    gitData = json.loads(data)


if os.path.exists('cmdStorage.json'):
    with open('cmdStorage.json') as f:
        data = f.read()
    cmdStorage = json.loads(data)

# takenCommands is a list of bot commands, this is used to ensure that the user can't override a bot command
takenCommands = ["id", "all ids", "gr", "running", "kill all", "run", "kill", "active", "cmd", "savec",
                   "ping", "restart DAB", "kill DAB", "admins"]
lastCommand = None  # This stores the command that was last executed
formattedCommand = ""
# cip - command in progress is a boolean that tells the program if a synchronous command is currently running
# This is a global value that can be checked to see if a synchronous process is already running
print("Starting DAB...")
cip = False
bot = commands.Bot(command_prefix='$')
client = discord.Client()


@bot.event  # This runs when the bot becomes active
async def on_ready():
    print("DAB is active!")


@bot.event
async def on_message_delete(message):
   # print("Message deleted\n", message)
    # If logging is enabled then the deleted message wil be logged
   # This way between Discord and the logs there is a full record of every command that was entered
    if userSettings[0]:
        #now = datetime.now()
        # d = now.strftime("%d/%m/%Y %H:%M:%S")
        # The file will always be appended to and not overwritten
        f = open("log.txt", "a")
        f.write(f"Date: {message.created_at}, id of user: {message.author}\nMessage:\n{message.content}")
        f.close()


@bot.event
async def on_message(message):  # Runs every time a message is sent
    # We need to be able to access all global values, while this may not necessarily be necessary
    # it ensures that all references to these values are of the global context
    global lastCommand, cmdStorage, takenCommands, gitData, cmdStorage, runningProcesses
    global logging, clearLogs, botAdmin, userSettings
    # Removes the command prefix and breaks in into parts to be worked with
    if message.content.startswith('$'):
        command = str(message.content).removeprefix("$")
        commandParts = command.split(", ")


        # kills all processes that the programs started then restarts the bot
        if commandParts[0] == "restart DAB":
            if not isAdmin(message.author.id):
                await message.channel.send("You don't have access to that command")
                return
            await message.channel.send("DAB is going to restart...")
            await message.channel.send("Shutting down other programs")
            for k, v, in runningProcesses.items():
                if killProc(v, k) == "error":
                    await message.channel.send(f"An error has occurred while trying to kill {v}")
            await message.channel.send(f"Restarting DAB")
            await message.channel.send(f"DAB should be back in less then 30 seconds")
            # If the restart file exists it will be run, else it will make the file then run it
            if os.path.exists('restart.bat'):
                # os.startfile allows for asynchronous execution
                os.startfile('restart.bat')
            else:
                f = open("restart.bat", "w+")
                f.write("@echo off\n")
                f.write("echo Restarting DAB\n")
                f.write("timeout /t 10 /nobreak\n")
                f.write(f"start {os.path.abspath(__file__)}\n")
                f.write("exit")
                f.close()
                # os.startfile allows for asynchronous execution
                os.startfile('restart.bat')
            print("Restarting DAB")
            exit(0)


        if commandParts[0] == "kill DAB":  # Kills DAB
            if not isAdmin(message.author.id):
                await message.channel.send("You don't have access to that command")
                return
            await message.channel.send("Shutting down DAB...")
            await message.channel.send("Shutting down other programs")
            for k, v, in runningProcesses.items():
                if killProc(v, k) == "error":
                    await message.channel.send(f"An error has occurred while trying to kill {v}")
            await message.channel.send("DAB is going to sleep now, bye")
            exit(0)


        if commandParts[0] == "ping":  # Simply tells the user that the bot is still active
            await message.channel.send("Bot is active")
            return


        if commandParts[0] == "is logging":
            if not isAdmin(message.author.id):
                await message.channel.send("You don't have access to that command")
                return
            await message.channel.send(userSettings[0])
            return


        # Deletes the log file if and only if the "main" or "head" admin says so
        if commandParts[0] == "del log":
            if str(message.author.id) == str(userSettings[2]):
                deleteLog()
                await message.channel.send("The log file has been deleted")
            else:
                await message.channel.send("You are not authorised to do that")
            return


        # Disables logging if the main admin says so
        if commandParts[0] == "disable logging":
            if str(message.author.id) == str(userSettings[2]):
                userSettings[0] = False
                await message.channel.send("Logging has been disabled")
            else:
                await message.channel.send("You are not authorised to do that")
            return


        # Enables logging if the main admin says so
        if commandParts[0] == "enable logging":
            if str(message.author.id) == str(userSettings[2]):
                userSettings[0] = True
                await message.channel.send("Logging has been enabled")
            else:
                await message.channel.send("You are not authorised to do that")
            return

        # The bot usually executes commands asynchronously but certain commands can break when running asynchronously
        # For example if you were able to run two $gr commands at the same time on the same repo it would
        # be pointless as that repo would already exist
        # lock tells the program that a task is in progress
        if commandParts[0] == "lock":
            if not isAdmin(message.author.id):
                await message.channel.send("You don't have access to that command")
                return
            Tcip()
            await message.channel.send("An asynchronous precess has been registered")
            return

        # unlock tells the program that there is no command in progress
        # This can be used to override the asynchronous protection or unlock the program is locked
        # using the command above
        if commandParts[0] == "unlock":
            if not isAdmin(message.author.id):
                await message.channel.send("You don't have access to that command")
                return
            Fcip()
            await message.channel.send("Asynchronous processes have been overridden")
            return

        if commandParts[0] == "admins":  # Lists al of the bot admins
            await message.channel.send("Admins are:")
            tmp = [str(admin) for admin in userSettings[2:]]  # Converts contents to a list
            await message.channel.send(tmp)  # Prints the contents
            return

        if commandParts[0] == "add admin":  # Adds the given id to the list of bot admins
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            if isAdmin(message.author.id):
                if len(commandParts) == 2:
                    if commandParts[1] in userSettings:  # Checks to see if they are already a bot admin
                        await message.channel.send(f"{commandParts[1]} is already a bot admin")
                        Fcip()
                        return
                    userSettings.append(commandParts[1])
                    saveInfo()
                    await message.channel.send(f"{commandParts[1]} is now a bot admin")
                else:
                    await message.channel.send("You didn't enter an id")
            else:
                await message.channel.send("Error, you do not have access to that command")
            Fcip()
            return

        # Removes the given id to the list of bot admins so long as it's not the original admin
        if commandParts[0] == "remove admin":
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            if isAdmin(message.author.id):
                if len(commandParts) == 2:
                    # prevents the user from removing the "head" admin
                    if commandParts[1] == userSettings[2]:
                        await message.channel.send("You can't remove that admin")
                        Fcip()
                        return
                    if commandParts[1] not in userSettings:  # Check to see if they are actually an admin
                        await message.channel.send(f"{commandParts[1]} is not an admin")
                        Fcip()
                        return
                    # Removes the admin and saves the list
                    idx = userSettings.index(commandParts[1])
                    del userSettings[idx]
                    saveInfo()
                    await message.channel.send(f"{commandParts[1]} is no longer a bot admin")
                else:
                    await message.channel.send("You didn't enter an id")
            else:
                await message.channel.send("Error, you do not have access to that command")
            Fcip()
            return


        # Tells the user their id
        if commandParts[0] == "id":
            await message.channel.send(f"Your id is: {message.author.id}")
            return # Without the return statement it tells the user there id and that their command was not valid


        # Returns a list of the names of the rolls and their id's to the user
        if commandParts[0] == "all ids":
            tmp = [f"Id name: {i}, id: {i.id}" for i in message.author.roles]
            await message.channel.send(f"All of your channel id's are:\n{tmp}")
            return


        if commandParts[0] == "gr":  # allows the user to add download a repository from github
            if not isAdmin(message.author.id): # Makes sure the user as an admin
                await message.channel.send("You don't have access to that command")
                return
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            if len(commandParts) < 4:
                await message.channel.send("Error, you need a command name (for future reference), the link to "
                    "the repo, the name of the file to run and a list of authorised id's")
                Fcip()
                return

            if commandParts[1] in takenCommands:  # checks to see if the command is a bot command
                await message.channel.send("That command is a bot command")
                Fcip()
                return

            if commandParts[1] in cmdStorage.keys():
                await message.channel.send("That command is a cmd command command")
                Fcip()
                return

            if commandParts[1] in gitData.keys():
                await message.channel.send("That command already exists")
                Fcip()
                return


            await message.channel.send("Cloning repo, this can take up to a few minutes depending on your server's internet speeds")
            # name, link, file_name, ids
            res = newRepo(commandParts[1], commandParts[2], commandParts[3], commandParts[4:])
            await message.channel.send(res)
            Fcip()
            return


        # This will print out a list of all programs that were started by this program and are still active
        if commandParts[0] == "running":
            if len(runningProcesses) == 0:
                await message.channel.send("There are no active processes")
            else:
                await message.channel.send("The following is a list of programs that was started by this bot and are still active")
                for key in runningProcesses.keys():  # Prints all running prcoesses
                    await message.channel.send(key)
            return


        if commandParts[0] == "kill all":  # Kill all running programs that were started by the bot
            if not isAdmin(message.author.id): # Checks to see if the user is authoreied to use the command
                await message.channel.send("You don't have access to that command")
                return
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            if len(runningProcesses) == 0:
                await message.channel.send("There are no active processes")
            else:
                await message.channel.send("Killing the following processes:")
                for key in runningProcesses.keys():  # Prints all running processes
                    await message.channel.send(key)
                # Iterates thought every value in the dictionary and kills it
                for k, v, in runningProcesses.items():
                    if killProc(v, k) == "error":
                        await message.channel.send(f"An error has occurred while trying to kill {v}")
                        Fcip()
                        return
                runningProcesses.clear()  # Removes the values from the dictionary
                await message.channel.send("Processes have been killed")
            Fcip()
            return


        if commandParts[0] in gitData:  # Runs the program associated with the command

            # Tests to see if the user has access to that command
            tmp = gitData[commandParts[0]][3]  # Extracts the list of ids to search for
            tmp2 = [str(i.id) for i in message.author.roles]  # Gets a list of the ids of the roles that the user has
            if not isAuthorised(message.author.id, tmp2, tmp):
                await message.channel.send("You do not have access to that command")
                return

            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            # Checks to make sure the user entered the proper amount of arguments
            if len(commandParts) != 2:
                await message.channel.send("You entered an invalid number of arguments")
                Fcip()
                return

            if commandParts[1] == "run":  # Runs the program
                if commandParts[0] in runningProcesses:  # Checks to see if the program is already running
                    await message.channel.send(f"{commandParts[0]} is already active")
                    Fcip()
                    return
                await message.channel.send("starting program...")
                res = activate(commandParts[0])
                await message.channel.send(res)
                Fcip()
                return

            elif commandParts[1] == "active":  # Tells the user if their process if running or not
                if commandParts[0] in runningProcesses:
                    await message.channel.send(f"{commandParts[0]} is running")
                else:
                    await message.channel.send(f"{commandParts[0]} is not currently running")
                Fcip()
                return

            elif commandParts[1] == "kill":
                # await message.channel.send(str(runningProcesses[commandParts[0]])) # For testing
                if commandParts[0] in runningProcesses:
                    pid = runningProcesses[commandParts[0]]
                    if killProc(pid, commandParts[0]) == "error":
                        await message.channel.send(f"{commandParts[0]} refused to die")
                        Fcip()
                        return
                    await message.channel.send(f"{commandParts[0]} has been killed")
                    del runningProcesses[commandParts[0]]  # Removes the value from the dictionary
                else:
                    await message.channel.send(f"{commandParts[0]} was already dead")
                Fcip()
                return

            elif commandParts[1] == "restart":  # This closes then restarts the program
                await message.channel.send("Restarting the program...")
                if commandParts[0] in runningProcesses:
                    pid = runningProcesses[commandParts[0]]
                    if killProc(pid, commandParts[0]) == "error":
                        await message.channel.send(f"{commandParts[0]} refused to die")
                        Fcip()
                        return
                    time.sleep(1.5)
                    res = activate(commandParts[0])
                    await message.channel.send(res)
                    await message.channel.send("Program restarted")
                else:
                    await message.channel.send("Program was never running")
                Fcip()
                return

            elif commandParts[1] == "del":  # Deletes the repository
                await message.channel.send("Deleting the program...")
                res = delRepo(commandParts[0], gitData[commandParts[0]][2])
                if not res is None:  # Only prints output if there is an error
                    await message.channel.send(res)
                await message.channel.send("Program has been deleted")
                Fcip()
                return

            elif commandParts[1] == "reinstall":  # This deletes and reinstall the repo
                await message.channel.send("Reinstalling program...")
                # This stores all all values for later use because we are
                # going to remove all dictionary entries regarding the command
                # I realise that this is not the most efficient way of accomplishing this
                # but my hope is that by laying out each element of the list you
                # can get a better idea of how this program works
                dictList = gitData[commandParts[0]]
                tmpList = [None]*4 # Preps the list for all of the values
                tmpList[0] = commandParts[0]  # Command name
                tmpList[1] = dictList[0]  # Link
                tmpList[2] = dictList[1]  # Name of python file
                tmpList[3] = dictList[3]  # List of authored id's
                # Deletes the old repo and it's associated dictionary entries
                res = delRepo(commandParts[0], gitData[commandParts[0]][2])
                if not res is None: # Only prints output if there is an error
                    await message.channel.send(res)
                time.sleep(1)
                # name, link, file_name, ids
                res = newRepo(tmpList[0], tmpList[1], tmpList[2], tmpList[3])
                await message.channel.send("Program has been reinstalled")
                await message.channel.send(res)
                dictList.clear()
                tmpList.clear()
                Fcip()
                return

            else:
                await message.channel.send("You didn't enter any arguments")
                Fcip()
                return


        # Allows the user to send commands into the terminal
        if commandParts[0] == "cmd":
            if not isAdmin(message.author.id):  # Checks to see if the user is authorised to use the command
                await message.channel.send("You don't have access to that command")
                return
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            # The program will throw an error if it tries to return an empty message
            if commandParts[1] == "cls":
                await message.channel.send("Cls won't clear the bot's chats")
                Fcip()
                return
            if len(commandParts) < 2:  # This checks to see if the command has enough arguments
                await message.channel.send("Not valid, you didn't include a command")
                Fcip()
                return

            formattedCommand = formatCommand(commandParts[1:])  # Formats the command for the terminal

            await message.channel.send(cmd(formattedCommand))
            lastCommand = formattedCommand
            Fcip()
            return


        elif commandParts[0] == "savec":
            if not isAdmin(message.author.id):  # Checks to see if the user is authoreied to use the command
                await message.channel.send("You don't have access to that command")
                return
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()

            if len(commandParts) < 3:  # This checks to see if the command has enough arguments
                await message.channel.send("Not valid, you need to have a name and at least one id")
                Fcip()
                return

            if lastCommand is None:  # Checks to see if there is a command to save
                await message.channel.send("No command to save, press enter to continue")
                Fcip()
                return

            if commandParts[1] in takenCommands:  # checks to see if the command is a bot command
                await message.channel.send("That command is a bot command")
                Fcip()
                return

            if commandParts[1] in gitData.keys():
                await message.channel.send("That command is a git repo command")
                Fcip()
                return

            if commandParts[1] in cmdStorage.keys():
                await message.channel.send("That command already exists")
                Fcip()
                return

            if commandParts[0] == "savec":
                if commandParts[1] in cmdStorage :
                    await message.channel.send("That command already exists, if you want to overwrite change \"savec\" to \"saveco\"")
                    Fcip()
                    return

                else:
                    addCommand(commandParts[1], lastCommand,
                               commandParts[2:])  # Saves the command in the cmdStorage dictionary
                    # command name, command, list of authorised users
                    await message.channel.send(f"Commad \"{lastCommand}\" saved as {commandParts[1]}")
                    Fcip()
                    return


        elif commandParts[0] in cmdStorage:
            if checkcip():  # Checks to see if a synchronous command is currently running"
                await message.channel.send("A synchronous command is currently running")
                return
            else:
                Tcip()
            if len(commandParts) <= 1:
                await message.channel.send("You have to enter command arguments")
                Fcip()
                return
            # Tests to see if the user has access to that command
            tmp = cmdStorage[commandParts[0]][1]  # Extracts the list of ids to search for
            tmp2 = [str(i.id) for i in message.author.roles]  # Gets a list of the ids of the roles that the user has
            if isAuthorised(message.author.id, tmp2, tmp):
                if commandParts[1] == "run":  # Runs the command
                    tmp = cmdStorage[commandParts[0]][0]  # Extracts the command from the dictionary
                    await message.channel.send("Command ran!\nOutput is:\n"+str(cmd(tmp)))
                    Fcip()
                    return

            else:
                await message.channel.send("You don't have access to that command")
                Fcip()
                return
            if not isAdmin(message.author.id):  # Checks to see if the user is authorised to use the command
                await message.channel.send("You don't have access to that command")
                Fcip()
                return
            if commandParts[1] == "del":  # Deletes the command
                if len(cmdStorage)-1 == 0:  # Tests to see if this is the last command
                    # If it is then the storage file must be deleted
                    if os.path.exists('cmdStorage.json'):
                        os.remove('cmdStorage.json')
                del cmdStorage[commandParts[0]]  # Deletes the command from the storage
                await message.channel.send("The command has been deleted")
                Fcip()
                return
            await message.channel.send("You didn't enter any proper arguments")
            Fcip()
            return

        else:
            await message.channel.send("That is not a proper command")
            Fcip()
            return

bot.run('Bot token here')
