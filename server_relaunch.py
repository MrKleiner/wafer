
# Even though the name sez "relaunch" - this actually does both restarting AND starting
# CGI scripts and their child processess are all children of the server software
# and therefore they all die when the server software is restarted/stopped
# which means that there should be no hanging hobo processes no matter what

# Important: this script should only 

from pathlib import Path




