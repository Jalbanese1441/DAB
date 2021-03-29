# DAB
DAB - Discord or Desktop Access Bot is a Discord bot that allows multiple users to send commands to a sever. These commands can range from entering commands remotely into the serves terminal to remotely deploying and maintaining a program using GitHub. This program was made using python 3.9.2 and is designed to run on Windows 10. I choose the language and operation system to maximise the number of people who could use this bot. The only requirements are that you have Git installed and you download the Discord python library (https://pypi.org/project/discord.py/), Do Not use a pipenv to run the bot in. I may update this bot in the future to improve efficiency but that is still to be determined. For now, read the docs below to see all of the awesome things that this bot can do. The bot executes certain commands in order (synchronously) to prevent errors. Also, each command has a permission level that the user must meat to use that command, you can use discord roles as well as individual user ids to manages the command permissions. The bot also logs all deleted messages so you can see all of the commands entered into the bot. The Discord id that you enter in at the start of the program will always be the “main” or “head” id. It can never be demoted from admin. For a more in-depth explanation and to learn the inner workings of the program, take a look at the comments in the code.  Only allow people who you trust to have access to any admin command – Never give it to strangers.
The bot working like this:
$command, command arguments, more command arguments, ect
-	You must put a comma followed by a space before you enter the next argument, do not include commas in your arguments. If the argument is for a command name, try not to use spaces, it can sometimes cause the program to save the wrong command name.

## General Commands (Commands anyone can access all of  time):
$ping – return a message if the bot is active <br/>
$admins – return a list of all users and roles with admin privileges <br/>
$id – Return the id of the user <br/>
$all ids – Returns the ids of the users roles <br/>
$running – returns a list of all running processes (that were stated by the program) <br/>

## General Admin Commands (Commands administrators can access all the time):
$kill all – Kills all programs that were started by the bot <br/>
$restart DAB – Restarts the bot and kills all of the programs that it opened <br/>
$kill DAB – Kills the bot and all programs that it opened<br/>
$is logging – Returns True if the program is logging deleted messages<br/>
$del log – Deletes the log file (Can only be done by the “main” admin) <br/>
$disable logging – Disables the logging of deleted messages (Can only be done by the “main” admin) <br/>
$enable logging – Enables the logging of deleted messages (Can only be done by the “main” admin) <br/>
$lock – Prevents synchronous commands (one at a time, in order) from being run by telling the program that one is progress <br/>
$unlock – Allows commands to be executed asynchronous, it unlocks the bot<br/>


## Synchronous Admin Commands (Commands that must be run one at a time that need admin permission):
$add admin, id – Adds a user id or role to the list of admin ids (id is the argument) <br/>
$remove admin, id – Removes that id from the list of admins, it can’t remove the “main” admin<br/>

$cmd, commad1, commad2, ect – This command takes your command(s) and feeds them right into the terminal of the host computer and sends you the output. Each command entered as an argument will be run after the first if the first one succeeds. For example $cmd, echo hi – outputs “hi”, $cmd, cd some-folder-name, dir – will print out the contents of that folder. Example: $cmd, echo hi – returns “hi” <br/>

$savec, command name, id1, id2, ect – This command saves the last $cmd command that was run. The command name will be the name that you will use to refer back to it later, do not include spaces in it as it occasionally throws an error. The rest of the arguments are the user ids or id’s of the roles that the users who are aloud to use the command. If you want it accessible by everyone just enter “all” as the argument for id. Only administrators can add, modify or remove a command. Think the following commands like $saved cmd command, argument. Continuing on with the previous example,  $savec, test, all – This will save the command as “test”. Any uses who types “$test” will get “hi” <br/>

$saved, run – runs the command (if the user is authorised) <br/>
$saved $cmd command, del – Deletes the command that was saved using $savec<br/>

$gr, name, link to repo, file name, id1, id2, ect -  This clones a repostoiy form GitHub using git and saves it so the program can access it. Name is the name of the command that you will use to interact with the program later, the second argument is the exact link to the GitHb repository, the third argument is the name of the file that will be run. This file must be a python file (.py) and can’t contain any spaces. If the program requires libraries you can install them using $cmd. If the program runs off a pipenv the program will automatically handle it. The forth and last argument are the ids of the uses / roles who will be able to access it. Just like before you can add “all” to the list of ids and everyone will be able to access the command. Also, just like before, it’s $command name, argument. Anyone who has access to the command will be able to delete, restart, reinstall and check to see if the program is running. <br/>
For example: <br/>
$gr, test, https://github.com/Taggagii/Web-Application, app.py, all <br/>
This clones a repo that I worked on that contains a pipenv. This repo can be run by using $test, run and “all” will let any user do it <br/>


$saved $gr command, run – Runs the file specified from the $gr command in the file name section. It if needs a pipenv, the program will automatically detect it and use it<br/>

$saved $gr command, kill – Kills the program is it’s running<br/>
$saved $gr command, restart – restarts the program<br/>
$saved $gr command, active – Tells you if the program is currently active<br/>
$saved $gr command, del – Deletes the command and the repository from the server<br/>
$saved $gr command, reinstall – Wipes then reinstall the program, useful if you updated the GitHub repository<br/>


