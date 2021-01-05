db_file             = r"temperatures.db" #Name and location of .db file, default temperatures.db
get_url             = "" #URL where current temperature reading from Inkbird can be retreived
post_url            = "http://log.brewfather.net/stream?id=xSTT0qS2oQkv0i" #Your Brewfather Post URL, normally starting with http://log.brewfather.net/stream?id=
upload_frequency    = 5#60*15 #in seconds (brewfather minumum is 15 minutes, 60*15)