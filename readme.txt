Notes:
This is a thing I just hacked together and some people expressed interest in it, so I made it available on git. It's really bare bones.


How to Use:

To get this program working:

1) Edit the text file: ./config/config

2) Enter username/password of the email address you want to use (I created a throwaway specifically to do this)

3) Run through the data buouys and figure out the region you want (southwest_usa is saved in there)

4) Look at the region in a browser and figure out the location you want. I selected "La Jolla" which appears in two of the bouy names. It searches through the location names for your search key and it is case dependent so "La Jolla" matches but "la jolla" does not.

5) Enter your cell number and SMS provider domain (see wikipedia for filling it out)

6) Run the program ./Ocean_Data.py to see if texts you

7) Set up the program to run at an interval (once daily). I use cron.
