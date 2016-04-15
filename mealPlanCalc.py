from getpass import getpass
from lxml import html
from tabulate import tabulate
import requests
import datetime
import time

print("\nWarning: Accounts for 19 meals per week when calculating number \nof extra meals left, not 15.\n")
print("Warning2: Extra Swipes computation assumes no more swipes will be \nused today\n")

username = raw_input("IdentiKey: ") 
password = getpass()

print("\nGrabbing data from oncampus.colorado.edu and computing.....\n")

# login, get source code, and parse baby parse
postData = {'name':username,'pass':password,'form_build_id':'form-zG6dUs38S-tjnsscR7LxH41YSlm2pYLyuHNBqEJjlEs','form_id':'user_login','op':'Log in'}
logIn = requests.post('https://oncampus.colorado.edu/user/login', data=postData)
dashboardMarkup = logIn.text
tree = html.fromstring(dashboardMarkup)
diningBalances = tree.xpath('//div[@class="dashboard-dining-balances"]/text()')
name = tree.xpath('//div[@class="field-content"]/text()')

#-----------------------------------------------------------------------

# gets current date and puts it into usable list of ints (y, m, d)
currentTime = int(time.strftime("%H"))
currentDate = time.strftime("%Y/%m/%d")
currentDate = currentDate.split("/")
for i in range(len(currentDate)):
	currentDate[i] = int(currentDate[i])

# calculates number of days between end of semester and the current date
date1 = datetime.date(currentDate[0], currentDate[1], currentDate[2])
date2 = datetime.date(2016, 5, 6) # <--- change date for end of semester here ---
deltaDate = date2 - date1
deltaDate = deltaDate.days
dayOfWeek = datetime.datetime(currentDate[0], currentDate[1],currentDate[2]).weekday()

# if there is an error when making this a float, it means it's a string 
# being turned into an int, and either the server returned a wrong 
# password page or the HTML of the page has been changed.
try:
	munchMoney = float(diningBalances[3][2:])
except:
	exitStr = "Wrong Password! (or this script doesn't work anymore)"

# thurs 3, Friday 4. Saturday 5, Sunday 6, Monday 0, tuesday 1, Wednsday 2
# loops through the days until Wednsday and finds the number of meals left
predictedMealsUsed = 0
_dayOfWeek = dayOfWeek
while _dayOfWeek != 2:
	if _dayOfWeek == 5 or _dayOfWeek == 6:
		predictedMealsUsed += 2
	else:
		predictedMealsUsed += 3
	_dayOfWeek += 1
	if _dayOfWeek == 7: 
		_dayOfWeek = 0

# final variables for output
mealsLeft = diningBalances[2]
extraMeals = int(mealsLeft) - predictedMealsUsed
# ensures no division of zero
if (deltaDate != 0):
	munchMoneyPerDay = munchMoney/deltaDate
else:
	munchMoneyPerDay = munchMoney

# calculates number of days until munchMoneyPerDay >= 1.5
extraDays = 0
if (deltaDate != 0):
	mMPDNew = munchMoney/(deltaDate - extraDays)
else:
	mMPDNew = munchMoney
while mMPDNew < 1.5:
	extraDays += 1
	mMPDNew = munchMoney/(deltaDate - extraDays)
	
# munch money that should be used before Monday
if deltaDate%7!=0:
	weeksLeft = deltaDate/7+1
else:
	weeksLeft = deltaDate/7
useByMon = munchMoney/weeksLeft

# Munch money per day (past)
date3 = datetime.date(2016, 1, 11)
deltaDate2 = date1 - date3
deltaDate2 = deltaDate2.days
munchMoneyUsed = 150.0 - munchMoney
mMPDPast = munchMoneyUsed/deltaDate2

# Ratio of past to new munch money per day
ratio = mMPDPast/munchMoneyPerDay
#-----------------------------------------------------------------------

# output strings being put into variables
usernameStr = "Computed balances for:"
mealPlanBalanceStr = "Meal plan balance:"
extraSwipesStr = "Extra meals:"
totalMunchMoneyStr = "Munch money left:"
munchMoneyStr = "Munch money per day until end of semester:"
daysLeftStr = "# of days left in semester:"
extraDaysStr = "# of days until munch money per day is 1.5:"
munchMoneyWkStr = "Munch money that can be used by Mon:"
mMPDPastStr = "Munch money per day (past):"
ratioStr = "Ratio of past to new munch money per day (good if <=1) :"

table = [
		[usernameStr, name[0]], 
		[mealPlanBalanceStr, mealsLeft], 
		[extraSwipesStr, extraMeals],
		[totalMunchMoneyStr, "$"+str(munchMoney)],
		[munchMoneyStr, "$"+"%.2f"%munchMoneyPerDay],
		[mMPDPastStr, "$"+"%.2f"%mMPDPast],
		[ratioStr, "%.2f"%ratio],
		[munchMoneyWkStr, "$"+"%.2f"%useByMon],
		[daysLeftStr, str(deltaDate)+" days"],
		[extraDaysStr, str(extraDays)+" days"]
		]

print tabulate(table)
