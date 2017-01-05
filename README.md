#Requirements 
python3, as usual.

#Usage
- Enter in your user/pw in lines 8 and 9 of the script. If necessary, alter the URL to get info on non-adnetwork campaigns.
- On the command line, run:

    `$ python3 change_log.py 12/1/2016`

(The date can be in typed in any standard format. The date allows the user to define the active period; in this example, "12/1/2016" means "This script will only look for IOs that END after 12/1/2016."

#What the script is doing
- Using the user-inputted date, the script retrieves user logs for all active IOs.
- The script goes through the logs and only looks for actions marked as "update," so that it filters out actions that aren't edits (ie. deletion, creation)
- From these remaining logs, the script looks only for edits made to the impression budget
- Final output is a CSV of all these logs with the following headers: IO, campaign, bid CPM, original impression budget, updated impression budget, date of change
