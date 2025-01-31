# ROAD MAP:
#	[X] 1. Load pre-made teams
#	[X] 2. Save files
#		[X] a. Between quarters
#		[X] b. Between games
#	[ ] 3. Small upgrades
#			. Add heat tracker to the boxscore
#			. Bonus
#			. FT rating
#			. Individual fouling rate
#			. Height & length factor (every inch larger gives +1 bonus).
#			. Upgrade heat to also represent player variance/consistency
#	[ ] 4. Major updates
#			. Help-side defense
#			. Offensive & defensive schemes
#			. Player career progression
#			. Tournament/season structures
#			. Pseudo-announcer play-by-play
#
# TODO:
#
# TO FIX:
#
# DONE:
#	. Implement basic box score tracking
#	. Implement steal & block
#	. Change pass success/fail to grant an assist rather than a represent the good pass/TO binary
#	. Build out rebounding code
#	. Implement free throws
#	. Implement and-1's
#	. Begin to ~correctly~ loop the possession simulation (maybe kinda close already?) - use a pseudo clock tracker
#	. Work on attributes tied to quarters:
#		. Minutes played
#		. Fatigue. Likely need to add a on/off floor tracker, update accordingly. Separate rates for fatigue and recovery?
#	. Implement turnovers and fouls outside of the current narrow applications
#	. Add a 'heat meter'
#	. Is the fatigue system calibrated correctly? Shooting percentages seem very high...
#		. Maybe self corrects with generally worse level of players & subbing? (YEP)
#	. Add player database and ability to load chosen players (DO NOT START until player attributes are very locked in)
#	Phantom points? Player totals != to team total

from random import randrange
import os
import csv
import time

# Player class: stores tendency and rate data, tracks player stats for the box score.
# TODO:
#	Add basic info fields like number, position, etc.
class Player:
	def __init__(self, idn, name, num, pos, ovr, usage, rebUsage, defender, height, length, speed, phys, tendPost, tendDrive, tendMid, tendThree, tendPass, ratePost, rateDrive, rateMid, rateThree, ratePass, rateReb, ratePostD, ratePerimD, rateSteal, rateBlock, rateFT, tendPF, energy, enrgLoss, enrgGain, heatOVar, heatDVar, heatPost, heatDrive, heatMid, heatThree, heatPostD, heatPerimD, heatPass, heatReb):
		# Basic info fields
		self.idn = idn
		self.name = name
		self.num = num
		self.pos = pos
		self.ovr = ovr

		# Physical attributes
		self.height = height # in inches
		self.length = length # in inches
		self.speed = speed # rated 0-10
		self.phys = phys # rated 0-10

		# Tracking fields
		self.onCrt = 1
		self.usage = usage
		self.rebUsage = rebUsage
		self.defender = defender
		self.isDefending = None

		# Tendency fields give how likely a player is to take a certain action. Must total to 100.
		self.tendPost = tendPost 
		self.tendDrive = tendDrive
		self.tendMid = tendMid
		self.tendThree = tendThree
		self.tendPass = tendPass # Universally set to 50 (currently). Works well for now, could experiment with adjusting it.

		# Offensive rate fields give how likely a player is to be successful when they take a particular action. Modified by defender's rating. In the range 0-100.
		self.ratePost = ratePost
		self.rateDrive = rateDrive
		self.rateMid = rateMid
		self.rateThree = rateThree
		
		self.ratePass = ratePass 
		self.rateReb = rateReb 

		# Defensive rate fields modify an offensive player's action success checks. 
		self.ratePostD = int(ratePostD * 0.8)
		self.ratePerimD = int(ratePerimD * 0.8)
		self.rateSteal = rateSteal # In range 0-20
		self.rateBlock = rateBlock # In range 0-10

		# Fouling
		self.rateFT = rateFT # Rated 0-100
		self.tendPF = tendPF # Calculated by the formula (shooting PF / (shooting PF + off PF)) * PF per 100. This quantity is later adjusted by opponent usage.

		# Energy stats. Updated each quarter.
		self.energy = energy
		self.enrgLoss = enrgLoss # Rated 1-20
		self.enrgGain = enrgGain # Rated 1-10

		# Heat variance for offense and defense. A measure of how consistent/streaky a player is.
		#		Low variance players will stick close to their rating, even on a bad night. Streaky players can swing high or low.
		self.heatOVar = heatOVar
		self.heatDVar = heatDVar

		# Heat stats. Tracked in real-time
		self.heatPost = heatPost
		self.heatDrive = heatDrive
		self.heatMid = heatMid
		self.heatThree = heatThree
		self.heatPostD = heatPostD
		self.heatPerimD = heatPerimD
		self.heatPass = heatPass
		self.heatReb = heatReb

		# Box Score stats
		self.MP = 0
		self.FG = 0
		self.FGA = 0
		self.TP = 0
		self.TPA = 0
		self.FT = 0
		self.FTA = 0
		self.ORB = 0
		self.DRB = 0
		self.AST = 0
		self.STL = 0
		self.BLK = 0
		self.TOV = 0
		self.PF = 0
		self.PTS = 0

# Team class: stores a group of players on a team. Tracks team stats for the box score 
class Team:
	def __init__(self, idn, city, name, year, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10):
		self.idn = idn
		self.city = city
		self.name = name
		self.year = year
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3
		self.p4 = p4
		self.p5 = p5
		self.p6 = p6
		self.p7 = p7
		self.p8 = p8
		self.p9 = p9
		self.p10 = p10

		# Box Score stats
		self.MP = " "
		self.FG = 0
		self.FGA = 0
		self.TP = 0
		self.TPA = 0
		self.FT = 0
		self.FTA = 0
		self.ORB = 0
		self.DRB = 0
		self.AST = 0
		self.STL = 0
		self.BLK = 0
		self.TOV = 0
		self.PF = 0
		self.PTS = 0
		self.energy = " "

	# Helper function that returns the team's roster (or a specified subset of the roster) in a list.
	#	Mode 1		Return full roster (10 players)
	#	Mode 2 		Return players on court (5 players)
	#	Mode 3 		Return players off court (bench, 5 players)
	#	
	def getRoster(self, mode):
		if mode == 1:
			roster = [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10]
			return roster
		if mode == 2:
			roster = [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10]
			starters = []
			for x in roster:
				if x.onCrt == 1:
					starters.append(x)
			return starters
		if mode == 3:
			roster = [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10]
			bench = []
			for x in roster:
				if x.onCrt == 0:
					bench.append(x)
			return bench

# Box Score class: compiles team and player stats into a box score.
class BoxScore:
	def __init__(self, t1, t2):
		self.t1 = t1
		self.t2 = t2

	def printBoxScore(self, t1, t2):
		roster = t1.getRoster(1)

		print("                         MP  FG FGA   FG%   3P 3PA   3P%   FT FTA  FT%  ORB  DRB  TRB  AST  STL  BLK  TOV  PF  PTS | ENRG  HEAT  COLD")
		print("                         ------------------------------------------------------------------------------------------|-----------------")
		
		# Print the roster with the on-court players on the top of the list
		for x in roster:
			if x.onCrt == 1:
				statLinePrinter(x)
		print("                         ------------------------------------------------------------------------------------------------------------")
		for x in roster:
			if x.onCrt == 0:
				statLinePrinter(x)

		print("                         ------------------------------------------------------------------------------------------------------------")
		statLinePrinter(t1)
		print("\n")

	def printScoreChart(self, t1, t2, qScores1, qScores2):
		print("                         Q1 | Q2 | Q3 | Q4 | FINAL")
		print("                         ------------------|------")		
		print(t1.name.rjust(24), p(qScores1[0]), " ", p(qScores1[1]), " ", p(qScores1[2]), " ", p(qScores1[3]), "|", p(t1.PTS))
		print(t2.name.rjust(24), p(qScores2[0]), " ", p(qScores2[1]), " ", p(qScores2[2]), " ", p(qScores2[3]), "|", p(t2.PTS))
		print("\n")


# Helper function that compiles team stats from all its players.
def buildTeamStats(t):
	roster = t.getRoster(1)

	# Reset stats between each call
	t.FGA = 0
	t.FG = 0
	t.TP = 0
	t.TPA = 0
	t.FT = 0
	t.FTA = 0
	t.ORB = 0
	t.DRB = 0
	t.AST = 0
	t.STL = 0
	t.BLK = 0
	t.TOV = 0
	t.PF = 0
	t.PTS = 0

	# Sum up player stats
	for x in roster:
		t.FGA += x.FGA
		t.FG += x.FG
		t.TP += x.TP
		t.TPA += x.TPA
		t.FT += x.FT
		t.FTA += x.FTA
		t.ORB += x.ORB
		t.DRB += x.DRB
		t.AST += x.AST
		t.STL += x.STL
		t.BLK += x.BLK
		t.TOV += x.TOV
		t.PF += x.PF
		t.PTS += x.PTS

# Helper fuction to return the total value of a player's heat scores.
def totalHeat(p):
	hTotal = 0
	cTotal = 0
	scores = [p.heatPost, p.heatDrive, p.heatMid, p.heatThree, p.heatPostD, p.heatPerimD, p.heatPass, p.heatReb]

	for x in scores:
		if gradeHeat(x) == "Hot 1": hTotal += 1
		elif gradeHeat(x) == "Hot 2": hTotal += 2
		elif gradeHeat(x) == "Hot 3": hTotal += 3

		if gradeHeat(x) == "Cold 1": cTotal -= 1
		elif gradeHeat(x) == "Cold 2": cTotal -= 2
		elif gradeHeat(x) == "Cold 3": cTotal -= 3

	totals = [hTotal, cTotal]
	return totals

# Helper fuction to print properly formatted box score lines.
def statLinePrinter(m):
	TRB = m.ORB + m.DRB
	if type(m) is not Team: 
		totals = totalHeat(m)
	else:
		totals = ["", ""]
	print(m.name.rjust(24), p(m.MP), "", p(m.FG), "", p(m.FGA), "", percentCalc(m.FG, m.FGA), "", p(m.TP), "", p(m.TPA), "", percentCalc(m.TP, m.TPA), "", p(m.FT), "", p(m.FTA), percentCalc(m.FT, m.FTA), "", p(m.ORB), " ", p(m.DRB), " ", 
		p(TRB), " ", p(m.AST), " ", p(m.STL), " ", p(m.BLK), " ", p(m.TOV), "", p(m.PF), "", p(m.PTS), "  ", p(m.energy).ljust(3), "  ", p(totals[0]), "  ", p(totals[1]))

# Helper function to help statLinePrinter format stats that could be one or two digits long. Has a stupid name because I had to type it a million times.
def p(x):
	if len(str(x)) == 1:
		return str(x).ljust(2)
	else:
		return str(x).format(2)

# Helper function to calculate FG%. Also checks for divide by zero errors.
def percentCalc(makes, attempts):
	if attempts == 0:
		return "0.000"
	else:
		return format((makes / attempts), '.3f')

# Function to determine who has a ball by checking a random integer against the team's usage rates (totalling 100)
def checkUsage(team, mode):
	onCrt = team.getRoster(2) # get a list of the players on the floor

	x = randrange(100) + 1

	# 'Who-has-the-ball' usage
	if mode == 0:
		if x <= onCrt[0].usage:
			return onCrt[0]
		y = onCrt[0].usage + onCrt[1].usage
		if x <= y:
			return onCrt[1]
		y += onCrt[2].usage
		if x <= y:
			return onCrt[2]
		y += onCrt[3].usage
		if x <= y:
			return onCrt[3]
		return onCrt[4]

	# Rebound usage
	if mode == 1:
		if x <= onCrt[0].rebUsage:
			return onCrt[0]
		y = onCrt[0].rebUsage + onCrt[1].rebUsage
		if x <= y:
			return onCrt[1]
		y += onCrt[2].rebUsage
		if x <= y:
			return onCrt[2]
		y += onCrt[3].rebUsage
		if x <= y:
			return onCrt[3]
		return onCrt[4]

# Function to determine what action a player takes by checking a random integer against the player's tendency rates (totalling 100)
def checkAction(player, bonus):
	x = randrange(100) + 1 + bonus

	if x <= player.tendPost:
		return 1
	y = player.tendPost + player.tendDrive
	if x <= y:
		return 2
	y += player.tendMid
	if x <= y:
		return 3
	y += player.tendThree
	if x <= y:
		return 4
	return 5

# Function to determine who controls a rebound. Determines which player from each team is competing for the board, then compares their REB ratings to determine who gets the board.
def checkRebound(off, deff):
	x = randrange(100) + 1
	oReb = checkUsage(off, 1)
	dReb = checkUsage(deff, 1)

	DC = (dReb.rateReb + dReb.heatReb - (oReb.rateReb - oReb.heatReb / 3) + 75) # Adjust values in this line to tweak how common offensive rebounds are
	x = randrange(100) + 1

	if x < DC: # defensive rebound
		dReb.DRB += 1
		dReb.heatReb += 1
		deff.DRB += 1
		oReb.heatReb -= 1
		logPBP(off, oReb, dReb, "DRB", "", x, DC, None)
		return 2
	else: # offensive rebound
		oReb.ORB += 1
		if oReb.heatReb <= 15: oReb.heatReb += 3
		off.ORB += 1
		dReb.heatReb -= 3
		logPBP(off, oReb, dReb, "ORB", "", x, DC, None)
		return 3

# Function to simulate a set of free throws.
# TODO:
#	. Currently checks against mid range rating for success. Switch to a dedicated FT rating?
#	. Does not account for bonus currently
def checkFreeThrow(off, deff, player, attempts):
	i = 1
	makes = 0
	# For each attempt, check against the player's mid range shooting rating. Update stats as appropriate.
	while i <= attempts:
		ft = randrange(100) + 1

		# Update attempts
		player.FTA += 1
		off.FTA += 1

		if ft < player.rateFT: # If made, update makes and points
			player.FT += 1
			player.PTS += 1
			makes += 1
			if i == attempts:
				attemptsStr = str(attempts) + "FTA"
				makesStr = str(makes) + "FT"
				logPBP(off, player, None, attemptsStr, makesStr, "", "", None)
				return 1
		i += 1

	attemptsStr = str(attempts) + "FTA"
	makesStr = str(makes) + "FT"
	logPBP(off, player, None, attemptsStr, makesStr, "", "", None)
	return checkRebound(off, deff)

# Helper function to find the height or length difference between two players
# Returns the *PERCENTAGE POINT* bonus or penalty that p1 receives for the difference
# Bonus/penalty is 1% for every 2 inches difference
def heightLengthDiff(mode, p1, p2):
	if mode == "height":
		return int(p1.height - p2.height / 2)

	elif mode == "length":
		return int(p1.length - p2.length / 2)
	elif mode == "both":
		return int(((p1.height + p1.length) - (p2.height + p2.length)) / 2)

# Helper function to set the difficulty of a shot (the target # under which a lower random generated value results in a made shot)
#	type 	shot type
#	pO 		offensive player
#	pD 		defensive player
def setDifficulty(type, pO, pD):
	if type == "post":
		return (pO.ratePost + pO.phys + pO.heatPost) - (pD.ratePostD + pD.phys + pD.heatPostD) + heightLengthDiff("height", pO, pD)
	elif type == "drive":
		return (pO.rateDrive + pO.speed + pO.heatDrive) - (pD.ratePerimD + pD.speed + pD.heatPerimD) + heightLengthDiff("length", pO, pD)
	elif type == "mid":
		return (pO.rateMid + pO.phys + pO.speed + pO.heatMid) - (((pD.ratePostD + pD.ratePerimD) / 2) + pD.phys + pD.speed + ((pD.heatPostD + pD.heatPerimD) / 2)) + heightLengthDiff("both", pO, pD)
	elif type == "three":
		return (pO.rateThree + pO.speed + pO.heatThree) - (pD.ratePerimD + pD.speed + pD.heatPerimD)

# 
# Function to simulate a single possession. 
#	1. Determines who has the ball using checkUsage
#	2. Determines what action the player takes using checkAction
#	3. Determines if the action is successful by checking a random integer against player rates using a elif ladder
# Off 		= Team object for offensive team
# Deff 		= Team object for defensive team (def is not an allowable variable name :( )
# astBonus	= Bonus adjustment applied to checkAction and action success checks. Simulates that a good pass leads to a good shot.
# lastPass	= Player object for player who made the previous pass. Used in tracking assists.
#
# Return Codes:
#	1: Bucket scored. Run posession w/ other team.
#	2: Missed shot / shot blocked. Return result of checkRebound;
#		2: Defensive rebound
#		3: Offensive rebound
#	4: Turnover. Run fast break.
#	Note: FTs return either 1 in the case of the final FT being made, or 2/3 for who recovers the rebound on a miss.
#
def sim_possession(off, deff, astBonus, lastPass):
	p = checkUsage(off, 0)
	while (p is lastPass): p = checkUsage(off, 0) # Check that a player cannot pass to themselves
	action = checkAction(p, astBonus)
	x = randrange(100) + 1 + astBonus + abs(p.energy) - abs(p.defender.energy)
	p.defender.tendPF = ((p.usage - 20) / (35 - 5)) + 1 # Formula developed by Justin Moore. Causes players guarding ball-heavy players to foul slightly more often.

	# Post shot
	if action == 1:
		DC = setDifficulty("post", p, p.defender)
		
		# If shot is made...
		if x < DC:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.PTS += 2

			# Update heat trackers
			p.heatPost += 2
			p.defender.heatPostD -= 2

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "post", "FG", x, DC, lastPass)
			return 1 # return made shot

		# If shot is blocked...
		elif x < DC + p.defender.rateBlock:
			# Update player stats
			p.FGA += 1

			# Update defender stats
			p.defender.BLK += 1

			# Update heat trackers
			p.heatPost -= 2
			p.defender.heatPostD += 4

			logPBP(off, p, p.defender, "post", "FGA-BLK", x, DC + p.defender.rateBlock, lastPass)
			return randrange(1) + 2 # return block, randomly determine 50/50

		# If shot is missed, foul on shot...
		# tendPF * 0.66, assuming 1/3 are And-1 fouls.
		elif x < DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66):
			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatPost += 1
			p.heatPostD -= 1

			logPBP(off, p, p.defender, "post", "FGA-2FT", x, DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66), lastPass)
			return checkFreeThrow(off, deff, p, 2) # return checkFreeThrow, which returns checkRebound

		# If shot is made, foul on shot (and-1)...
		elif x < DC + p.defender.rateBlock + p.defender.tendPF:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.PTS += 2

			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatPost += 3
			p.defender.heatPostD -= 3

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "post", "FG-1FT", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkFreeThrow(off, deff, p, 1) # return checkFreeThrow, which returns checkRebound

		# Shot is missed
		else:
			# Update player stats
			p.FGA += 1

			# Update heat trackers
			p.heatPost -= 2
			p.defender.heatPostD += 2

			logPBP(off, p, p.defender, "post", "FGA", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkRebound(off, deff) # return checkRebound

	# Drive / playmake / off the dribble
	elif action == 2:
		DC = setDifficulty("drive", p, p.defender)

		# If shot is made...
		if x < DC:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.PTS += 2

			# Update heat trackers
			p.heatDrive += 2
			p.defender.heatPerimD -= 2

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "playmake", "FG", x, DC, lastPass)
			return 1 # return made shot

		# If shot is blocked...
		elif x < DC + p.defender.BLK:
			# Update player stats
			p.FGA += 1

			# Update defender stats
			p.defender.BLK += 1

			# Update heat trackers
			p.heatDrive -= 2
			p.defender.heatPerimD += 4

			logPBP(off, p, p.defender, "playmake", "FGA-BLK", x, DC + p.defender.BLK, lastPass)
			return randrange(1) + 2 # return block, randomly determine 50/50

		# If shot is missed, foul on shot...
		# tendPF * 0.66, assuming 1/3 are And-1 fouls.
		elif x < DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66):
			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatDrive += 1
			p.heatPerimD -= 1

			logPBP(off, p, p.defender, "playmake", "FGA-2FT", x, DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66), lastPass)
			return checkFreeThrow(off, deff, p, 2) # return checkFreeThrow, which returns checkRebound

		# If shot is made, foul on shot (and-1)...
		elif x < DC + p.defender.rateBlock + p.defender.tendPF:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.PTS += 2

			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatDrive += 3
			p.defender.heatPerimD -= 3

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "playmake", "FG-1FT", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkFreeThrow(off, deff, p, 1) # return checkFreeThrow, which returns checkRebound

		# Shot is missed
		else:
			# Update player stats
			p.FGA += 1

			# Update heat trackers
			p.heatDrive -= 2
			p.defender.heatPerimD += 2

			logPBP(off, p, p.defender, "playmake", "FGA", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkRebound(off, deff) # return checkRebound

	# Mid-range shot
	elif action == 3:
		DC = setDifficulty("mid", p, p.defender)

		# If shot is made...
		if x < DC:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.PTS += 2

			# Update heat trackers
			p.heatMid += 2
			p.defender.heatPerimD -= 1
			p.defender.heatPostD -= 1

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "mid", "FG", x, DC, lastPass)
			return 1 # return made shot

		# If shot is blocked...
		elif x < DC + p.defender.BLK:
			# Update player stats
			p.FGA += 1

			# Update defender stats
			p.defender.BLK += 1

			# Update heat trackers
			p.heatMid -= 2
			p.defender.heatPostD += 2
			p.defender.heatPerimD += 2

			logPBP(off, p, p.defender, "mid", "FGA-BLK", x, DC + p.defender.BLK, lastPass)
			return randrange(1) + 2 # return block, randomly determine 50/50

		# If shot is missed, foul on shot...
		# tendPF * 0.66, assuming 1/3 are And-1 fouls.
		elif x < DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66):
			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatMid += 1
			p.heatPostD -= 1
			p.heatPerimD -= 1

			logPBP(off, p, p.defender, "mid", "FGA-2FT", x, DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66), lastPass)
			return checkFreeThrow(off, deff, p, 2) # return checkFreeThrow, which returns checkRebound

		# If shot is made, foul on shot (and-1)...
		elif x < DC + p.defender.rateBlock + p.defender.tendPF:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.PTS += 2

			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatMid += 3
			p.defender.heatPostD -= 2
			p.defender.heatPerimD -= 2

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "mid", "FGM-1FT", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkFreeThrow(off, deff, p, 1) # return checkFreeThrow, which returns checkRebound

		# Shot is missed
		else:
			# Update player stats
			p.FGA += 1

			# Update heat trackers
			p.heatMid -= 2
			p.defender.heatPostD += 1
			p.defender.heatPerimD += 1

			logPBP(off, p, p.defender, "mid", "FGA", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkRebound(off, deff) # return checkRebound

	# Three point shot
	elif action == 4:
		DC = setDifficulty("three", p, p.defender)

		# If shot is made...
		if x < DC:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.TPA += 1
			p.TP += 1
			p.PTS += 3

			# Update heat trackers
			p.heatThree += 2
			p.defender.heatPerimD -= 2

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "three", "FG", x, DC, lastPass)
			return 1 # return made shot

		# If shot is blocked...
		elif x < DC + p.defender.BLK:
			# Update player stats
			p.FGA += 1
			p.TPA += 1

			# Update defender stats
			p.defender.BLK += 1

			# Update heat trackers
			p.heatThree -= 2
			p.defender.heatPerimD += 4

			logPBP(off, p, p.defender, "three", "FGA-BLK", x, DC + p.defender.BLK, lastPass)
			return randrange(1) + 2 # return block, randomly determine 50/50

		# If shot is missed, foul on shot...
		# tendPF * 0.66, assuming 1/3 are And-1 fouls.
		elif x < DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66):
			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatThree += 1
			p.heatPerimD -= 1

			logPBP(off, p, p.defender, "three", "FGA-2FT", x, DC + p.defender.rateBlock + int(p.defender.tendPF * 0.66), lastPass)
			return checkFreeThrow(off, deff, p, 3) # return checkFreeThrow, which returns checkRebound

		# If shot is made, foul on shot (and-1)...
		elif x < DC + p.defender.rateBlock + p.defender.tendPF:
			# Update player stats
			p.FGA += 1
			p.FG += 1
			p.TPA += 1
			p.TP += 1
			p.PTS += 3

			# Update defender stats
			p.defender.PF += 1

			# Update heat trackers
			p.heatThree += 3
			p.defender.heatPerimD -= 3

			# Check for assist
			if (lastPass is not None): 
				lastPass.AST = lastPass.AST + 1
				if lastPass.heatPass <= 15: lastPass.heatPass += 5

			logPBP(off, p, p.defender, "three", "FG-1FT", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkFreeThrow(off, deff, p, 1) # return checkFreeThrow, which returns checkRebound

		# Shot is missed
		else:
			# Update player stats
			p.FGA += 1
			p.TPA += 1

			# Update heat trackers
			p.heatThree -= 2
			p.defender.heatPerimD += 2

			logPBP(off, p, p.defender, "three", "FGA", x, DC + p.defender.rateBlock + p.defender.tendPF, lastPass)
			return checkRebound(off, deff) # return checkRebound

	# Pass
	else:
		DC = p.ratePass + p.heatPass

		# If less than player pass rating, whoever receives the pass gains a bonus and this player gets an AST if they score
		if x < DC:
			logPBP(off, p, p.defender, "pass++", "", x, DC, lastPass)
			return sim_possession(off, deff, -15, p)

		# Check for steal
		elif x < DC + p.defender.rateSteal:
			# Update player stats
			p.TOV += 1

			# Update defender stats
			p.defender.STL += 1

			# Update heat trackers
			p.heatPass -= 4
			p.defender.heatPostD += 2
			p.defender.heatPerimD += 2

			logPBP(off, p, p.defender, "pass", "STL", x, DC + p.defender.rateSteal, lastPass)
			return 4 # return turnover

		# Check for reach-in foul
		elif x < DC + p.defender.rateSteal + p.defender.tendPF:
			# Update defender stats
			p.defender.PF += 1

			logPBP(off, p, p.defender, "pass", "PF", x, DC + p.defender.rateSteal + p.defender.tendPF, lastPass)
			return sim_possession(off, deff, 0, p)

		else:
			logPBP(off, p, p.defender, "pass", "", x, DC + p.defender.rateSteal + p.defender.tendPF, lastPass)
			return sim_possession(off, deff, 0, p)

# Function to simulate a quarter of play. 
#	t1 = team 1
# 	t2 = team 2
#	
# Clock stats at 2 to account for the time the first possession takes. Every clock increment following is the time the next possession takes.
def sim_quarter(t1, t2):
	clock = 2 # starts at two to account for time the first possession takes.
	off = t1
	deff = t2
	temp = None
	bonus = 0
	player = None

	# Track posessions using a pseudo-clock tracker. Standard time for regular possessions, less time for 'fastbreaks'.
	while clock <= 90:
		i = sim_possession(off, deff, bonus, player)

		if (i == 1): # Made shot. Switch teams for next possession. Increment clock.
			clock += 2
			temp = off
			off = deff
			deff = temp
		elif (i == 2): # Defensive rebound. Switch teams for next possession. Increment clock.
			clock += 2
			temp = off
			off = deff
			deff = temp
		elif (i == 3): # Offensive rebound. Keep teams. Increment clock.
			clock += 2
		elif (i == 4): # Turn over. Switch teams. Increment clock lesser amount.
			clock += 1
			temp = off
			off = deff
			deff = temp

	# Update minutes played, fatigue, and heat trackers
	roster1 = t1.getRoster(1)
	roster2 = t2.getRoster(1)

	for x in roster1:
		if x.onCrt == 1:
			x.MP += 12 # update minutes
			aggUsage = (x.usage + (x.rebUsage * 0.66) + x.isDefending.usage) / 3 # Calculate aggregate usage by averaging the weighted values of usage, rebound usage, and their defensive assignment's usage

			# Update energ
			if aggUsage <= 10:
				x.energy -= x.enrgLoss
			elif aggUsage > 10 and aggUsage <= 15:
				x.energy -= x.enrgLoss * 2
			elif aggUsage > 15 and aggUsage <= 20:
				x.energy -= x.enrgLoss * 4
			elif aggUsage > 20 and aggUsage <= 25:
	 			x.energy -= x.enrgLoss * 6
			elif aggUsage > 25 and aggUsage <= 30:
	 			x.energy -= x.enrgLoss * 8
			else:
				x.energy -= x.enrgLoss * 10
		else:
			x.energy += x.enrgGain
			if x.energy > 0: x.energy = 0

			# Update heat trackers
			if x.heatPost < 0: x.heatPost = min(0, x.heatPost + 6) 
			else: x.heatPost = max(0, x.heatPost - 6)
			if x.heatDrive < 0: x.heatDrive = min(0, x.heatDrive + 6) 
			else: x.heatDrive = max(0, x.heatDrive - 6)
			if x.heatMid < 0: x.heatMid = min(0, x.heatMid + 6) 
			else: x.heatMid = max(0, x.heatMid - 6)
			if x.heatThree < 0: x.heatThree = min(0, x.heatThree + 6) 
			else: x.heatThree = max(0, x.heatThree - 6)
			
			if x.heatPostD < 0: x.heatPostD = min(0, x.heatPostD + 6) 
			else: x.heatPostD = max(0, x.heatPostD - 6)
			if x.heatPerimD < 0: x.heatPerimD = min(0, x.heatPerimD + 6) 
			else: x.heatPerimD = max(0, x.heatPerimD - 6)
			
			if x.heatPass < 0: x.heatPass = min(0, x.heatPass + 6) 
			else: x.heatPass = max(0, x.heatPass - 6)
			if x.heatReb < 0: x.heatReb = min(0, x.heatReb + 6) 
			else: x.heatReb = max(0, x.heatReb - 6)

	# Do it again for the other team
	for x in roster2:
		if x.onCrt == 1:
			x.MP += 12 # update minutes
			aggUsage = (x.usage + int(x.rebUsage * 0.66) + x.isDefending.usage) / 3 # Calculate aggregate usage by averaging the weighted values of usage, rebound usage, and their defensive assignment's usage

			# Update energ
			if aggUsage <= 10:
				x.energy -= x.enrgLoss
			elif aggUsage > 10 and aggUsage <= 15:
				x.energy -= x.enrgLoss * 2
			elif aggUsage > 15 and aggUsage <= 20:
				x.energy -= x.enrgLoss * 4
			elif aggUsage > 20 and aggUsage <= 25:
	 			x.energy -= x.enrgLoss * 6
			elif aggUsage > 25 and aggUsage <= 30:
	 			x.energy -= x.enrgLoss * 8
			else:
				x.energy -= x.enrgLoss * 10
		else:
			x.energy += x.enrgGain
			if x.energy > 0: x.energy = 0

			# Update heat trackers
			if x.heatPost < 0: x.heatPost = min(0, x.heatPost + 6) 
			else: x.heatPost = max(0, x.heatPost - 6)
			if x.heatDrive < 0: x.heatDrive = min(0, x.heatDrive + 6) 
			else: x.heatDrive = max(0, x.heatDrive - 6)
			if x.heatMid < 0: x.heatMid = min(0, x.heatMid + 6) 
			else: x.heatMid = max(0, x.heatMid - 6)
			if x.heatThree < 0: x.heatThree = min(0, x.heatThree + 6) 
			else: x.heatThree = max(0, x.heatThree - 6)
			
			if x.heatPostD < 0: x.heatPostD = min(0, x.heatPostD + 6) 
			else: x.heatPostD = max(0, x.heatPostD - 6)
			if x.heatPerimD < 0: x.heatPerimD = min(0, x.heatPerimD + 6) 
			else: x.heatPerimD = max(0, x.heatPerimD - 6)
			
			if x.heatPass < 0: x.heatPass = min(0, x.heatPass + 6) 
			else: x.heatPass = max(0, x.heatPass - 6)
			if x.heatReb < 0: x.heatReb = min(0, x.heatReb + 6) 
			else: x.heatReb = max(0, x.heatReb - 6)

	buildTeamStats(t1)
	buildTeamStats(t2)

# Function to simulate a full game of play. Keeps track of the score by quarter.
def sim_game(qScores1, qScores2, t1, t2):
	boxScore = BoxScore(t1, t2)

	i = determineQ(qScores1, qScores2) + 1
	while i <= 4:
		os.system('cls' if os.name == 'nt' else 'clear')
		print("\n   Preparing to simulate Quarter", i)
		time.sleep(1)
		print("   .")
		time.sleep(1)
		print("   .")
		time.sleep(1)
		print("   .")
		os.system('cls' if os.name == 'nt' else 'clear')

		sim_quarter(t1, t2)

		buildTeamStats(t1)
		buildTeamStats(t2)

		if i == 1:
			qScores1[0] = t1.PTS
			qScores2[0] = t2.PTS
		elif i == 2:
			qScores1[1] = t1.PTS - qScores1[0]
			qScores2[1] = t2.PTS - qScores2[0]
		elif i == 3:
			qScores1[2] = t1.PTS - qScores1[1] - qScores1[0]
			qScores2[2] = t2.PTS - qScores2[1] - qScores2[0]
		elif i == 4:
			qScores1[3] = t1.PTS - qScores1[2] - qScores1[1] - qScores1[0]
			qScores2[3] = t2.PTS - qScores2[2] - qScores2[1] - qScores2[0]

		if i != 4:
			print("\n   QUARTER", i)
			updateLineup_UI(boxScore, qScores1, qScores2, t1, t2)
			updateLineup_UI(boxScore, qScores2, qScores1, t2, t1)
			updateUsage_UI(1, boxScore, qScores1, qScores2, t1, t2)
			updateUsage_UI(1, boxScore, qScores2, qScores1, t2, t1)
			updateRebUsage_UI(1, boxScore, qScores1, qScores2, t1, t2)
			updateRebUsage_UI(1, boxScore, qScores2, qScores1, t2, t1)
			setDefender_UI(1, boxScore, qScores1, qScores2, t1, t2)
			setDefender_UI(1, boxScore, qScores2, qScores1, t2, t1)

		roster1 = t1.getRoster(2)
		roster2 = t2.getRoster(2)
		
		i += 1

	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n   FINAL")
	boxScore.printBoxScore(t1, t2)
	boxScore.printScoreChart(t1, t2, qScores1, qScores2)
	boxScore.printBoxScore(t2, t1)

	saveGame(qScores1, qScores2, t1, t2)

# Sim a large amount of games and compare the number of wins for each team.
# TO FIX:
#	. Currently doesn't work because player objects do not reset their stats between games.
def mass_sim(t1, t2):
	t1W = 0
	t2W = 0
	tie = 0

	i = 1
	while i <= 10:
		sim_game(t1, t2)

		if t1.PTS < t2.PTS:
			t2W += 1
		elif t1.PTS > t2.PTS:
			t1W += 1
		else:
			tie += 1
		i += 1

	print(t1.name, t1W, percentCalc(t1W, 100))
	print(t2.name, t2W, percentCalc(t2W, 100))

#
#		SAVE FILES SECTION
#
# TODO:
#	. Build a save file mechanism that can do the following:
#		. Save game information between quarters and lets users resume partial games
#			. Must save:
#				. Player info & stats
#				. Team info & stats
#		. Load a game that was saved while in progress
#		. Save team/player information after games to allow multi-game simulations where heat/energy are persistent, and stats are tracked over many games

# Saves the current state of the game in two files:
#	1. ??-Q#-P = player data
#	2. ??-Q#-T = team data
def saveGame(qScores1, qScores2, t1, t2):
	# Prompt user for file name
	print("\n   Please enter a name for the save file:")
	usrIn = input()

	q = determineQ(qScores1, qScores2)
	pFile = str("Save Files\\" + usrIn + "-Q" + str(q) + "-P.csv")
	tFile = str("Save Files\\" + usrIn + "-Q" + str(q) + "-T.csv")
	PBPfile = str("Save Files\\" + usrIn + "-Q" + str(q) + "-PBP.csv")

	savePBPLog(PBPfile) # Save the play-by-play log file

	# Create save file for player data
	with open(pFile, 'w', newline='') as f:
		writer = csv.writer(f)

		# Write header to file
		header = ["idn", "name", "num", "pos", "ovr", 
			"usage", "rebUsage", "defender", 
			"height", "length", "speed", "phys", 
			"tendPost", "tendDrive", "tendMid", "tendThree", "tendPass", 
			"ratePost", "rateDrive", "rateMid", "rateThree", "ratePass", "rateReb", "ratePostD", "ratePerimD", "rateSteal", "rateBlock", 
			"rateFT", "tendPF",
			"energy", "enrgLoss", "enrgGain", 
			"heatOVar", "heatDVar",
			"heatPost", "heatDrive", "heatMid", "heatThree", "heatPostD", "heatPerimD", "heatPass", "heatReb", 
			"MP", "FG", "FGA", "TP", "TPA", "FT", "FTA", "ORB", "DRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
		writer.writerow(header)

		# Write team 1 player data
		roster = t1.getRoster(1)
		for x in roster:
			row = [x.idn, x.name, x.num, x.pos, x.ovr, 
				x.usage, x.rebUsage, x.defender, 
				x.height, x.length, x.speed, x.phys,
				x.tendPost, x.tendDrive, x.tendMid, x.tendThree, x.tendPass, 
				x.ratePost, x.rateDrive, x.rateMid, gradeTranslate(4, x.rateThree), x.ratePass, x.rateReb, x.ratePostD, x.ratePerimD, x.rateSteal, x.rateBlock, 
				x.rateFT, x.tendPF,
				x.energy, x.enrgLoss, x.enrgGain, 
				x.heatOVar, x.heatDVar,
				x.heatPost, x.heatDrive, x.heatMid, x.heatThree, x.heatPostD, x.heatPerimD, x.heatPass, x.heatReb, 
				x.MP, x.FG, x.FGA, x.TP, x.TPA, x.FT, x.FTA, x.ORB, x.DRB, x.AST, x.STL, x.BLK, x.TOV, x.PF, x.PTS]
			writer.writerow(row)

		# Write team 2 player data
		roster = t2.getRoster(1)
		for x in roster:
			row = [x.idn, x.name, x.num, x.pos, x.ovr, 
				x.usage, x.rebUsage, x.defender,
				x.height, x.length, x.speed, x.phys, 
				x.tendPost, x.tendDrive, x.tendMid, x.tendThree, x.tendPass, 
				x.ratePost, x.rateDrive, x.rateMid, gradeTranslate(4, x.rateThree), x.ratePass, x.rateReb, x.ratePostD, x.ratePerimD, x.rateSteal, x.rateBlock, 
				x.rateFT, x.tendPF,
				x.energy, x.enrgLoss, x.enrgGain, 
				x.heatOVar, x.heatDVar,
				x.heatPost, x.heatDrive, x.heatMid, x.heatThree, x.heatPostD, x.heatPerimD, x.heatPass, x.heatReb, 
				x.MP, x.FG, x.FGA, x.TP, x.TPA, x.FT, x.FTA, x.ORB, x.DRB, x.AST, x.STL, x.BLK, x.TOV, x.PF, x.PTS]
			writer.writerow(row)

	# Create a save file for team data
	with open(tFile, 'w', newline='') as f:
		writer = csv.writer(f)

		# Write header to file
		header = ["idn", "city", "name", "year",
			"Q1", "Q2", "Q3", "Q4", 
			"MP", "FG", "FGA", "TP", "TPA", "FT", "FTA", "ORB", "DRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
		writer.writerow(header)

		# Write team 1 team data
		row = [t1.idn, t1.city, t1.name, t1.year,
			qScores1[0], qScores1[1], qScores1[2], qScores1[3], 
			t1.MP, t1.FG, t1.FGA, t1.TP, t1.TPA, t1.FT, t1.FTA, t1.ORB, t1.DRB, t1.AST, t1.STL, t1.BLK, t1.TOV, t1.PF, t1.PTS]
		writer.writerow(row)

		# Write team 2 team data
		row = [t2.idn, t2.city, t2.name, t2.year,
			qScores2[0], qScores2[1], qScores2[2], qScores2[3],
			t2.MP, t2.FG, t2.FGA, t2.TP, t2.TPA, t2.FT, t2.FTA, t2.ORB, t2.DRB, t2.AST, t2.STL, t2.BLK, t2.TOV, t2.PF, t2.PTS]
		writer.writerow(row)

	# Exit
	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n   Game saved successfully")
	time.sleep(1)
	print("\n   Exiting")
	time.sleep(1)
	print("   .")
	time.sleep(1)
	print("   .")
	time.sleep(1)
	print("   .")
	exit()

# Helper function to load up a player object with the info and stats given in 'row', which is pulled from a CSV file
def playerLoader(mode, row):
	p = Player(int(row["idn"]), row["name"], row["num"], row["pos"], row["ovr"], int(row["usage"]), int(row["rebUsage"]), None, int(row["height"]), int(row["length"]), int(row["speed"]), int(row["phys"]), int(row["tendPost"]), int(row["tendDrive"]), int(row["tendMid"]), int(row["tendThree"]), int(row["tendPass"]), int(row["ratePost"]), int(row["rateDrive"]), int(row["rateMid"]), int(row["rateThree"]), int(row["ratePass"]), int(row["rateReb"]), int(row["ratePostD"]), int(row["ratePerimD"]), int(row["rateSteal"]), int(row["rateBlock"]), int(row["rateFT"]), int(row["tendPF"]), int(row["energy"]), int(row["enrgLoss"]), int(row["enrgGain"]), int(row["heatOVar"]), int(row["heatDVar"]), int(row["heatPost"]), int(row["heatDrive"]), int(row["heatMid"]), int(row["heatThree"]), int(row["heatPostD"]), int(row["heatPerimD"]), int(row["heatPass"]), int(row["heatReb"]))
	
	if mode == 1:
		p.MP = int(row["MP"])
		p.FG = int(row["FG"])
		p.FGA = int(row["FGA"])
		p.TP = int(row["TP"])
		p.TPA = int(row["TPA"])
		p.FT = int(row["FT"])
		p.FTA = int(row["FTA"])
		p.ORB = int(row["ORB"])
		p.DRB = int(row["DRB"])
		p.AST = int(row["AST"])
		p.STL = int(row["STL"])
		p.BLK = int(row["BLK"])
		p.PF = int(row["PF"])
		p.PTS = int(row["PTS"])

	return p

def loadGame():
	# Prompt user for the name of the files to load in the format NAME-Q# (no file path, no -P or -T)
	#	TODO: 	Could be more user friendly to give a list of existing save files to choose from?
	#			Some sort of administrator mode/garbage collector may be needed as save files begin to pile up
	#
	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n   Please enter the name of the save file to load")
	usrIn = input()

	pFile = str("D:\\Code\\Sim_Basketball\\Save Files\\" + usrIn + "-P.csv")
	tFile = str("D:\\Code\\Sim_Basketball\\Save Files\\" + usrIn + "-T.csv")

	# Load the info from the team save file
	with open(tFile, "r") as tFile:
		reader = csv.DictReader(tFile, delimiter=',')
		i = 1
		for row in reader:
			if i == 1: 
				t1 = Team(row["idn"], row["city"], row["name"], row["year"], None, None, None, None, None, None, None, None, None, None)
				t1.FG = int(row["FG"])
				t1.FGA = int(row["FGA"])
				t1.TP = int(row["TP"])
				t1.TPA = int(row["TPA"])
				t1.FT = int(row["FT"])
				t1.FTA = int(row["FTA"])
				t1.ORB = int(row["ORB"])
				t1.DRB = int(row["DRB"])
				t1.AST = int(row["AST"])
				t1.STL = int(row["STL"])
				t1.BLK = int(row["BLK"])
				t1.PF = int(row["PF"])
				t1.PTS = int(row["PTS"])
				qScores1 = [int(row["Q1"]), int(row["Q2"]), int(row["Q3"]), int(row["Q4"])]
			if i == 2: 
				t2 = Team(row["idn"], row["city"], row["name"], row["year"], None, None, None, None, None, None, None, None, None, None)
				t2.FG = int(row["FG"])
				t2.FGA = int(row["FGA"])
				t2.TP = int(row["TP"])
				t2.TPA = int(row["TPA"])
				t2.FT = int(row["FT"])
				t2.FTA = int(row["FTA"])
				t2.ORB = int(row["ORB"])
				t2.DRB = int(row["DRB"])
				t2.AST = int(row["AST"])
				t2.STL = int(row["STL"])
				t2.BLK = int(row["BLK"])
				t2.PF = int(row["PF"])
				t2.PTS = int(row["PTS"])
				qScores2 = [int(row["Q1"]), int(row["Q2"]), int(row["Q3"]), int(row["Q4"])]
			i += 1

	# Load the info from the player save file
	j = 0
	#while j < 20:
	with open(pFile) as pFile:
		reader = csv.DictReader(pFile, delimiter=',')
		for row in reader:
			if j == 0:
				t1.p1 = playerLoader(1, row)
				t1.p1.onCrt = 1
			elif j == 1:
				t1.p2 = playerLoader(1, row)
				t1.p2.onCrt = 1
			elif j == 2:
				t1.p3 = playerLoader(1, row)
				t1.p3.onCrt = 1
			elif j == 3:
				t1.p4 = playerLoader(1, row)
				t1.p4.onCrt = 1
			elif j == 4:
				t1.p5 = playerLoader(1, row)
				t1.p5.onCrt = 1
			elif j == 5:
				t1.p6 = playerLoader(1, row)
				t1.p6.onCrt = 0
			elif j == 6:
				t1.p7 = playerLoader(1, row)
				t1.p7.onCrt = 0
			elif j == 7:
				t1.p8 = playerLoader(1, ow)
				t1.p8.onCrt = 0
			elif j == 8:
				t1.p9 = playerLoader(1, row)
				t1.p9.onCrt = 0
			elif j == 9:
				t1.p10 = playerLoader(1, row)
				t1.p10.onCrt = 0
			if j == 10:
				t2.p1 = playerLoader(1, row)
				t2.p1.onCrt = 1
			elif j == 11:
				t2.p2 = playerLoader(1, row)
				t2.p2.onCrt = 1
			elif j == 12:
				t2.p3 = playerLoader(1, row)
				t2.p3.onCrt = 1
			elif j == 13:
				t2.p4 = playerLoader(1, row)
				t2.p4.onCrt = 1
			elif j == 14:
				t2.p5 = playerLoader(1, row)
				t2.p5.onCrt = 1
			elif j == 15:
				t2.p6 = playerLoader(1, row)
				t2.p6.onCrt = 0
			elif j == 16:
				t2.p7 = playerLoader(1, row)					
				t2.p7.onCrt = 0
			elif j == 17:
				t2.p8 = playerLoader(1, row)
				t2.p8.onCrt = 0
			elif j == 18:
				t2.p9 = playerLoader(1, row)
				t2.p9.onCrt = 0
			elif j == 19:
				t2.p10 = playerLoader(1, row)
				t2.p10.onCrt = 0
			j += 1

	# Start simulating the game where the save file left off
	# TODO: TO make this work we need a boxscore and qscores
	boxScore = BoxScore(t1, t2)
	q = determineQ(qScores1, qScores2)

	updateLineup_UI(boxScore, qScores1, qScores2, t1, t2)
	updateLineup_UI(boxScore, qScores2, qScores1, t2, t1)
	setDefender_UI(1, boxScore, qScores1, qScores2, t1, t2)
	setDefender_UI(1, boxScore, qScores2, qScores1, t2, t1)
	updateUsage_UI(1, boxScore, qScores1, qScores2, t1, t2)
	updateUsage_UI(1, boxScore, qScores2, qScores1, t2, t1)
	updateRebUsage_UI(1, boxScore, qScores1, qScores2, t1, t2)
	updateRebUsage_UI(1, boxScore, qScores2, qScores1, t2, t1)
	sim_game(qScores1, qScores2, t1, t2)

PBPlog = [] # Global variable to hold the PBP log as it's built.

# Function that records a play-by-play events of the game in global variable PBPlog.
def logPBP(off, p, d, action, result, x, DC, AST):
	if AST is not None: AST = AST.name
	row = [off.name, p.name, "", action, result, x, DC, AST]
	if d is not None: row[2] = d.name
	PBPlog.append(row)

# Record the PBP log in to a CSV save file
def savePBPLog(fileName):
	# Open CSV log file
	with open(fileName, 'a', newline='') as f:
		writer = csv.writer(f)

		global PBPlog
		for x in PBPlog:
			writer.writerow(x)

#
#		UI SECTION
#
# TODO:
#	COMMENT:
#		buildTeam
#		startup_UI
#	Clean up buildTeam w/ comments and proper use of screenInput
#
# TO FIX:
#
# DONE:
#	The substitution cycle doesn't show the correct players in the correct order
#	Move the setDefense function to a style similar to the setLineup function.
#	Game simulation relies on p1-p5. Needs to change to run off of getRoster(2), which gives the on court players.
#	Find a way to show the quarter scoreboard from inside the UI functions. Passing the lists needed would be fine... answer with less hassle? (who cares)
#	Update the boxscore to show stats for all 10 players
#	Don't run the update lineup/set defender UIs after the 4th quarter
#	Sort boxscore with on-court players on top
#	One player can be set to guard multiple people
#	One player can be in the lineup multiple times
#	Add usage adjustments. Usage does not total 100 after lineup adjustments.
#	When a player is subbed out, set the player they were defending 'defender' attribute to None
#	When a player's defender is subbed out, set the player's isDefending to 0.
#	Display heat scores & check they're working correctly
#	Add a 'terminate from anywhere' option
#	Add rebound heat
#	Account for bad input
#	Add rebound usage adjustments
#	Add the heat badges to the boxscore
#	Add an 'info' page you can navigate to to show a player's ratings, energy, heat, etc.
#	Add premade teams
#	Add save states

# Helper function to screen user input for unexpected values. Checks that a given string can be converted to an integer between min and max.
# Return codes:
#	0 	Input is good
#	1 	Input is not a digit
#	2 	Input is outside of required range
def screenInput(usrIn, min, max):
	if usrIn == 'X' or usrIn == 'x':
		os.system('cls' if os.name == 'nt' else 'clear')
		print("\n   Exiting")
		time.sleep(1)
		print("   .")
		time.sleep(1)
		print("   .")
		time.sleep(1)
		print("   .")
		exit()
	elif usrIn == 'S' or usrIn == 's': # Check specific to the 'save game' option
		return 0
	elif usrIn == 'I' or usrIn == 'i': # Check specific to the info screen
		return 0
	elif usrIn.isdigit() is False:
		print("\n   ERROR! Input must be a number [", min, "] to [", max, "].\n   Enter [0] to return to previous screen.")
		input()
		return 1
	elif int(usrIn) < min or int(usrIn) > max:
		print("\n   ERROR! Input must be a number [", min, "] to [", max, "].\n   Enter [0] to return to previous screen.")
		input()
		return 2
	else:
		return 0

# Helper function to determine what quarter in the game it is based on the statistically miniscule chance that both teams score 0 points in a quarter
# Returns the number of quarters COMPLETED so far in the given game.
def determineQ(qScores1, qScores2):
	i = 0

	# Check for None-type error (pre-game save)
	if qScores1 is None or qScores2 is None:
		return i
	# Else determine what quarter it is
	while i < 4:
		if int(qScores1[i]) == 0 and int(qScores2[i]) == 0:
			return i
		i += 1
	return 4

def buildTeam_UI(t1):
	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n   Where is your team based?")
	t1.city = input()

	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n   What is your team name?")
	t1.name = input()

	j = 1
	while j <= 10:
		os.system('cls' if os.name == 'nt' else 'clear')
		print("\n   Current Roster:")
		roster = t1.getRoster(1)
		for x in roster:
			if x is not None:
				print ("     ", x.name)

		print("\n   Enter player ID number:\n   The first 5 players entered will be starters.")
		usrIn = input()

		with open('PlayerDatabase.csv') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if int(row["idn"]) == int(usrIn):
					if j == 0:
						t1.p1 = playerLoader(0, row)
						t1.p1.onCrt = 1
					elif j == 1:
						t1.p2 = playerLoader(0, row)
						t1.p2.onCrt = 1
					elif j == 2:
						t1.p3 = playerLoader(0, row)
						t1.p3.onCrt = 1
					elif j == 3:
						t1.p4 = playerLoader(0, row)
						t1.p4.onCrt = 1
					elif j == 4:
						t1.p5 = playerLoader(0, row)
						t1.p5.onCrt = 1
					elif j == 5:
						t1.p6 = playerLoader(0, row)
						t1.p6.onCrt = 0
					elif j == 6:
						t1.p7 = playerLoader(0, row)
						t1.p7.onCrt = 0
					elif j == 7:
						t1.p8 = playerLoader(0, row)
						t1.p8.onCrt = 0
					elif j == 8:
						t1.p9 = playerLoader(0, row)
						t1.p9.onCrt = 0
					elif j == 9:
						t1.p10 = playerLoader(0, row)
						t1.p10.onCrt = 0
		j += 1

# UI function to set defensive assignments
#	mode 			2 for not printing the boxscore (for game-setup use), 1 for printing the boxscore (between quarters use)
#	boxScore 		boxscore object for the current game
#	t1 				team 1
#	t2 				team 2
#
def setDefender_UI(mode, boxScore, qScores1, qScores2, t1, t2):
	usrIn = -1
	# Process defensive assignments until the user indicates they are done by entering 0.
	while usrIn != 0:
		os.system('cls' if os.name == 'nt' else 'clear')

		# Print box score if called in mode 1
		if mode == 1:
			print("\n")
			boxScore.printBoxScore(t1, t2)
			boxScore.printScoreChart(t1, t2, qScores1, qScores2)
			boxScore.printBoxScore(t2, t1)

		# Print players currently on the floor
		print("\n   Currently on the court for the", t1.name + ":")
		print("     ", "Player".center(24), "Defender".center(24))
		print("    ------------------------------------------------")
		roster1 = t1.getRoster(2)
		j = 1
		for x in roster1:
			if x.defender is not None:
				print("     [", j, "]", x.name.center(24), x.defender.name.center(24))
			else:
				print("     [", j, "]", x.name.center(24))
			j += 1

		# Prompt user to set defensive matchups
		print("\n   Enter a number [1] - [5] to assign that player's defender.\n   Enter [I] to view player info.\n   Enter [S] to save the game and exit. \n   Enter [0] when done to proceed.")
		usrIn = input()
		if screenInput(usrIn, 0, 5) != 0: usrIn = -1
		if usrIn == 'I' or usrIn == 'i': 
			playerInfo_UI(t1)
			usrIn = -1
		elif usrIn == 'S' or usrIn == 's':
			saveGame(qScores1, qScores2, t1, t2)
		else:
			usrIn = int(usrIn)

		# If the user would like to make defensive changes...
		if usrIn > 0:
			os.system('cls' if os.name == 'nt' else 'clear')
			# Print box score
			if mode == 1:
				print("\n")
				boxScore.printBoxScore(t1, t2)
				#boxScore.printScoreChart(t1, t2, qScores1, qScores2)
				boxScore.printBoxScore(t2, t1)

			# Prompt user to enter the new defender
			print("\n   Currently on the court for the", t1.name + ":")
			print("     ", "Player".center(24))
			print("    ------------------------")
			roster2 = t2.getRoster(2)
			k = 1
			for x in roster2:
				print("     [", k, "]", x.name.center(24))
				k += 1
			select = int(usrIn) - 1
			print("\n   Who will defend", roster1[select].name, "?\n   Enter a number [1] - [5], or enter [0] to remove defensive assignment.")
			usrIn = input()
			if screenInput(usrIn, 0, 5) != 0: usrIn = -1
			usrIn = int(usrIn)

			if usrIn == 0 and roster1[select].defender is not None:
				roster1[select].defender.isDefending = None
				roster1[select].defender = None
			elif usrIn <= 5 and usrIn != -1 and roster2[usrIn - 1].isDefending is not None:
				print("\n   ERROR! That player already has a defensive assignment.\n   Enter [0] to return to previous screen.")
				input()
				usrIn = -1
			elif usrIn != -1:
				# Make adjustments to defenders
				if roster1[select].defender is not None: roster1[select].defender.isDefending = None
				roster1[select].defender = roster2[usrIn - 1]
				roster2[usrIn - 1].isDefending = roster1[select]

		# Check that all defenders are assigned before allowing user to proceed
		elif usrIn != -1:
			for x in roster1:
				if x.defender is None:
					print("\n   ERROR! Defensive assignments incomplete.\n   Enter [0] to return to previous screen.")
					input()
					usrIn = -1
				break

# UI function to make lineup adjustments
#	boxScore 	The boxscore object for the current game
#	t1 			team 1
#	t2 			team 2
#
def updateLineup_UI(boxScore, qScores1, qScores2, t1, t2):
	usrIn = -1
	# Process substitutions until the user indicates they are done by entering 0.
	while usrIn != 0:
		# Print box score
		os.system('cls' if os.name == 'nt' else 'clear')
		print("\n")
		boxScore.printBoxScore(t1, t2)
		boxScore.printScoreChart(t1, t2, qScores1, qScores2)
		boxScore.printBoxScore(t2, t1)

		# Print players currently on the floor
		print("\n   Currently on the court for the", t1.name + ":")
		print("     ", "Player".center(24))
		print("     ", "------------------------")
		roster1 = t1.getRoster(2)
		j = 1
		for x in roster1:
			print("     [", j, "]", x.name.center(24))
			j += 1

		# Prompt user to substitute players
		print("\n   To substitute a player enter a number [1] - [5].\n   Enter [I] to view player info.\n   Enter [S] to save the game and exit.\n   Enter [0] to proceed.")
		usrIn = input()
		if screenInput(usrIn, 0, 5) != 0: usrIn = -1
		if usrIn == 'I' or usrIn == 'i': 
			playerInfo_UI(t1)
			usrIn = -1
		elif usrIn == 'S' or usrIn == 's':
			saveGame(qScores1, qScores2, t1, t2)
		else:
			usrIn = int(usrIn)

		# If player wishes to make substitutions...
		if usrIn > 0:
			# Print box score
			os.system('cls' if os.name == 'nt' else 'clear')
			print("\n")
			boxScore.printBoxScore(t1, t2)
			boxScore.printScoreChart(t1, t2, qScores1, qScores2)
			boxScore.printBoxScore(t2, t1)

			# Print full roster
			print("\n   Avaialable players for the", t1.name + ":")
			print("       ", "Player".center(24),)
			print("    ", "---------------------------")
			roster2 = t1.getRoster(1)
			j = 1
			for x in roster2:
				print("     [", j, "]", x.name.center(24))
				j += 1

			# Prompt user to enter the new player
			replace = int(usrIn) - 1
			print("\n   Who will replace", roster1[replace].name, "?\n   Enter a number [1] - [10]:")
			usrIn = input()
			if screenInput(usrIn, 1, 10) != 0: usrIn = -1
			usrIn = int(usrIn)

			# Check that the player is not on the court already
			if usrIn != -1 and roster2[usrIn - 1].onCrt == 1:
				print("\n   ERROR! That player is already on the court.\n   Enter [0] to return to previous screen.")
				input()
				usrIn = -1
			elif usrIn != -1:
				# Make roster adjustments
				roster1[replace].onCrt = 0
				if roster1[replace].defender is not None: roster1[replace].defender.isDefending = None
				roster1[replace].defender = None
				if roster1[replace].isDefending is not None: roster1[replace].isDefending.defender = None
				roster1[replace].isDefending = None

				roster2[usrIn - 1].onCrt = 1

# UI function to make usage adjustments
#	mode 			2 for not printing the boxscore (for game-setup use), 1 for printing the boxscore (between quarters use)
def updateUsage_UI(mode, boxScore, qScores1, qScores2, t1, t2):
	usrIn = -1
	# Process usage adjustments until the user indicates they are done by entering 0.
	while usrIn != 0:
		os.system('cls' if os.name == 'nt' else 'clear')

		if mode == 1:
			# Print box score
			print("\n")
			boxScore.printBoxScore(t1, t2)
			boxScore.printScoreChart(t1, t2, qScores1, qScores2)
			boxScore.printBoxScore(t2, t1)

		# Print players currently on the floor
		print("\n   Currently on the court for the", t1.name + ":")
		print("     ", "Player".center(24), "Usage".center(24))
		print("     ", "------------------------")
		roster1 = t1.getRoster(2)
		j = 1
		for x in roster1:
			print("     [", j, "]", x.name.center(24), str(x.usage).center(20))
			j += 1

		# Prompt user to substitute players
		print("\n   To adjust a player's usage enter a number [1] - [5].\n   On-court players' usage MUST total to 100.\n   Enter [I] to view player info.\n   Enter [S] to save the game and exit.\n   Enter [0] to proceed.")
		usrIn = input()
		if screenInput(usrIn, 0, 5) != 0: usrIn = -1
		if usrIn == 'I' or usrIn == 'i': 
			playerInfo_UI(t1)
			usrIn = -1
		elif usrIn == 'S' or usrIn == 's':
			saveGame(qScores1, qScores2, t1, t2)
		else:
			usrIn = int(usrIn)
			select = usrIn - 1

		# Check that usage totals 100 before allowing user to proceed...
		if usrIn == 0:
			totalUsage = roster1[0].usage + roster1[1].usage + roster1[2].usage + roster1[3].usage + roster1[4].usage
			if totalUsage != 100:
				print("\n   ERROR! On-court players' usage MUST total to 100. Current total is", totalUsage, ".\n   Enter [0] to return to previous screen.")
				input()
				usrIn = -1

		# If player wishes to make usage changes...
		elif usrIn > 0:
			os.system('cls' if os.name == 'nt' else 'clear')

			if mode == 1:
				# Print box score
				print("\n")
				boxScore.printBoxScore(t1, t2)
				#boxScore.printScoreChart(t1, t2, qScores1, qScores2)
				boxScore.printBoxScore(t2, t1)

			# Print selected player & usage
			print("     ", "Player".center(24), "Usage".center(24))
			print("     ", "------------------------")
			print("     ", roster1[select].name.center(24), str(roster1[select].usage).center(18))

			# Prompt user to enter a new usage value (between 5 and 35)
			print("\n   Enter a new usage value. Minimum usage 5, maximum 35.")
			usrIn = input()
			if screenInput(usrIn, 5, 35) != 0: usrIn = -1
			usrIn = int(usrIn)
			if usrIn >= 5 and usrIn <= 35:
				roster1[select].usage = usrIn
			elif usrIn != -1:
				print("\n   ERROR! Usage must be between 5 and 35.\n   Enter [0] to return to previous screen.")
				input()
				usrIn = -1

# UI function to make rebound usage adjustments
#	mode 			2 for not printing the boxscore (for game-setup use), 1 for printing the boxscore (between quarters use)
def updateRebUsage_UI(mode, boxScore, qScores1, qScores2, t1, t2):
	usrIn = -1
	# Process usage adjustments until the user indicates they are done by entering 0.
	while usrIn != 0:
		os.system('cls' if os.name == 'nt' else 'clear')

		if mode == 1:
			# Print box score
			print("\n")
			boxScore.printBoxScore(t1, t2)
			boxScore.printScoreChart(t1, t2, qScores1, qScores2)
			boxScore.printBoxScore(t2, t1)

		# Print players currently on the floor
		print("\n   Currently on the court for the", t1.name + ":")
		print("     ", "Player".center(24), "Rebound Usage".center(24))
		print("     ", "------------------------")
		roster1 = t1.getRoster(2)
		j = 1
		for x in roster1:
			print("     [", j, "]", x.name.center(24), str(x.rebUsage).center(20))
			j += 1

		# Prompt user to substitute players
		print("\n   To adjust a player's usage enter a number [1] - [5].\n   On-court players' usage MUST total to 100.\n   Enter [I] to view player info.\n   Enter [S] to save the game and exit.\n   Enter [0] to proceed.")
		usrIn = input()
		if screenInput(usrIn, 0, 5) != 0: usrIn = -1
		if usrIn == 'I' or usrIn == 'i': 
			playerInfo_UI(t1)
			usrIn = -1
		elif usrIn == 'S' or usrIn == 's':
			saveGame(qScores1, qScores2, t1, t2)
		else:
			usrIn = int(usrIn)
			select = usrIn - 1

		# Check that usage totals 100 before allowing user to proceed...
		if usrIn == 0:
			totalRebUsage = roster1[0].rebUsage + roster1[1].rebUsage + roster1[2].rebUsage + roster1[3].rebUsage + roster1[4].rebUsage
			if totalRebUsage != 100:
				print("\n   ERROR! On-court players' rebound usage MUST total to 100. Current total is", totalRebUsage, ".\n   Enter [0] to return to previous screen.")
				input()
				usrIn = -1

		# If player wishes to make usage changes...
		elif usrIn > 0:
			os.system('cls' if os.name == 'nt' else 'clear')
			
			if mode == 1:
				# Print box score
				print("\n")
				boxScore.printBoxScore(t1, t2)
				#boxScore.printScoreChart(t1, t2, qScores1, qScores2)
				boxScore.printBoxScore(t2, t1)

			# Print selected player & usage
			print("Select", select)
			print("     ", "Player".center(24), "Rebound Usage".center(24))
			print("     ", "------------------------")
			print("     ", roster1[select].name.center(24), str(roster1[select].rebUsage).center(18))

			# Prompt user to enter a new usage value (between 5 and 35)
			print("\n   Enter a new rebound usage value. Minimum rebound usage 5, maximum 35.")
			usrIn = input()
			if screenInput(usrIn, 5, 35) != 0: usrIn = -1
			usrIn = int(usrIn)
			if usrIn >= 5 and usrIn <= 35:
				roster1[select].rebUsage = usrIn
			elif usrIn != -1:
				print("\n   ERROR! Rebound usage must be between 5 and 35.\n   Enter [0] to return to previous screen.")
				input()
				usrIn = -1

# Helper function to translate heat scores into ranks from Cold 3 to Hot 3
def gradeHeat(r):
	if r <= -15: return "Cold 3"
	elif r <= -10: return "Cold 2"
	elif r <= -5: return "Cold 1"
	elif r < 5: return ""
	elif r <= 10: return "Hot 1"
	elif r <= 15: return "Hot 2"
	else: return "Hot 3"

# Helper function to translate non-[0-100] stats in to a [0-100] format
def gradeTranslate(mode, r):
	if mode == 1: # Translate steal rating from 0-20
		return r * 5
	if mode == 2: # Translate block rating from 0-10
		return r * 10
	if mode == 3: # Translate weighted defensive rating to unweighted
		return int(r * 1.2)
	if mode == 4: # Translate three rating from weighted score to unweighted
		return r
	if mode == 5: # Translate inches to X'Y" format
		feet = str(int(r / 12))
		inches = str(r % 12)
		return feet + "'" + inches + "\""

# UI function that displays information about a selected player; basic info, current stats, ability scores, heat scores.
def playerInfo_UI(t):
	# Print full roster
	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n   " + t.name, "Roster")
	print("       ", "Player".center(24),)
	print("    ", "---------------------------")
	
	roster2 = t.getRoster(1)
	j = 1
	for x in roster2:
		print("     [", j, "]", x.name.center(24))
		j += 1
	
	print("\n   Enter a number [1] - [10] to view their info card. Enter [0] to return to the previous screen.")
	usrIn = input()
	if screenInput(usrIn, 0, 10) != 0: usrIn = -1
	usrIn = int(usrIn)
	
	if usrIn > 0:
		p = roster2[usrIn - 1]

		os.system('cls' if os.name == 'nt' else 'clear')
		print("\n     PLAYER INFORMATION CARD")
		print("\n    ", p.name, "#" + p.num, p.pos, "\n    ", t.city, t.name)
		
		print("\n     CURRENT STAT LINE")
		print("                         MP  FG FGA   FG%   3P 3PA   3P%   FT FTA  FT%  ORB  DRB  TRB  AST  STL  BLK  TOV  PF  PTS | ENRG  HEAT  COLD")
		print("                         ------------------------------------------------------------------------------------------|-----------------")
		statLinePrinter(p)

		print("\n    PLAYER ABILITY GRADES & HEAT")
		print("\n    " + "Overall Rating:", p.ovr)
		print("\n    " + "Offense")
		print("      " + "Inside:".ljust(12), p.ratePost, "   " + gradeHeat(p.heatPost))
		print("      " + "Play Making:".ljust(12), p.rateDrive, "   " + gradeHeat(p.heatDrive))
		print("      " + "Mid:".ljust(12), p.rateMid, "   " + gradeHeat(p.heatMid))
		print("      " + "Three:".ljust(12), gradeTranslate(4, p.rateThree), "   " + gradeHeat(p.heatThree))
		print("      " + "Free Throw:".ljust(12), p.rateFT)

		print("\n    " + "Defense")
		print("      " + "Inside D:".ljust(12), gradeTranslate(3, p.ratePostD), "   " + gradeHeat(p.heatPostD))
		print("      " + "Perimeter D:".ljust(12), gradeTranslate(3, p.ratePerimD), "   " + gradeHeat(p.heatPerimD))

		print("\n    " + "Skills".ljust(12))
		print("      " + "Rebound:".ljust(12), p.rateReb, "   " + gradeHeat(p.heatReb))
		print("      " + "Pass:".ljust(12), p.ratePass, "   " + gradeHeat(p.heatPass))
		print("      " + "Block:".ljust(12), gradeTranslate(2, p.rateBlock))
		print("      " + "Steal:".ljust(12), gradeTranslate(1, p.rateSteal))

		print("\n    " + "Physical Attributes".ljust(12))
		print("      " + "Height:".ljust(12), gradeTranslate(5, p.height))
		print("      " + "Wingspan:".ljust(12), gradeTranslate(5, p.length))
		print("      " + "Speed:".ljust(12), gradeTranslate(2, p.speed))
		print("      " + "Physicality:".ljust(12), gradeTranslate(2, p.phys))

		print("\n    " + "Energy")
		print("      " + "Current:".ljust(12), p.energy)
		print("      " + "Depeletion:".ljust(12), p.enrgLoss)
		print("      " + "Recovery:".ljust(12), p.enrgGain)

		print("\n    " + "Consistency")
		print("      " + "Note:  Values closer to zero indicate a more consistent player. Larger values indicate a player who can get very hot or cold.")
		print("      " + "Offensive Consistency:".ljust(24), p.heatOVar)
		print("      " + "Defensive Consistency:".ljust(24), p.heatDVar)


	print("\n   Enter [0] to return to the previous screen.")
	usrIn = input()
	if screenInput(usrIn, 0, 0) != 0: usrIn = -1
	usrIn = int(usrIn)

# Helper function to load a pre-made team selected by the user
def loadTeam(t1_idn, t2_idn):
	num_teams_built = 0 # Tracker for how many teams have been loaded (both teams are done with one call of this func)
	# Initialize t1 & t2 objects
	t1 = Team(None, None, None, None, None, None, None, None, None, None, None, None, None, None)
	t2 = Team(None, None, None, None, None, None, None, None, None, None, None, None, None, None)

	# Load the selected team
	# Open the CSV file and begin looping through the rows of data
	with open('TeamDatabase.csv') as csv_file1:
		csv_reader1 = csv.DictReader(csv_file1, delimiter=',')
		for row1 in csv_reader1:

			# If the row's IDN matches either team's IDN...
			if int(row1["idn"]) == t1_idn or int(row1["idn"]) == t2_idn:
				# Fill out a list of IDN's for that team's players
				roster = [row1["p1"], row1["p2"], row1["p3"], row1["p4"], row1["p5"], row1["p6"], row1["p7"], row1["p8"], row1["p9"], row1["p10"]]

				# Check if we're building T1 or T2; fill in the basic info for that team
				if num_teams_built == 0:
					t1.idn = int(row1["idn"])
					t1.city = row1["city"]
					t1.name = row1["name"]
					t1.year = row1["year"]
				elif num_teams_built == 1:
					t2.idn = int(row1["idn"])
					t2.city = row1["city"]
					t2.name = row1["name"]
					t2.year = row1["year"]

				# Load the players in the team
				# Open the CSV and begin looping through the rows of data
				#	Do this 10 times, once for each player on the team.
				j = 0
				while j < 10:
					with open('PlayerDatabase.csv') as csv_file2:
						csv_reader2 = csv.DictReader(csv_file2, delimiter=',')
						for row in csv_reader2:
							
							# If the row's IDN matches the given player's IDN...
							if int(row["idn"]) == int(roster[j]):
								
								# For the current player we're building (P1-P10), load that player object with the data in the current row.
								#	Assign the player object to the correct team, T1 or T2
								if j == 0:
									if num_teams_built == 0:
										t1.p1 = playerLoader(0, row)
										t1.p1.onCrt = 1
									elif num_teams_built == 1:
										t2.p1 = playerLoader(0, row)
										t2.p1.onCrt = 1
								elif j == 1:
									if num_teams_built == 0:
										t1.p2 = playerLoader(0, row)
										t1.p2.onCrt = 1
									elif num_teams_built == 1:
										t2.p2 = playerLoader(0, row)
										t2.p2.onCrt = 1
								elif j == 2:
									if num_teams_built == 0:
										t1.p3 = playerLoader(0, row)
										t1.p3.onCrt = 1
									elif num_teams_built == 1:
										t2.p3 = playerLoader(0, row)
										t2.p3.onCrt = 1
								elif j == 3:
									if num_teams_built == 0:
										t1.p4 = playerLoader(0, row)
										t1.p4.onCrt = 1
									elif num_teams_built == 1:
										t2.p4 = playerLoader(0, row)
										t2.p4.onCrt = 1
								elif j == 4:
									if num_teams_built == 0:
										t1.p5 = playerLoader(0, row)
										t1.p5.onCrt = 1
									elif num_teams_built == 1:
										t2.p5 = playerLoader(0, row)
										t2.p5.onCrt = 1
								elif j == 5:
									if num_teams_built == 0:
										t1.p6 = playerLoader(0, row)
										t1.p6.onCrt = 0
									elif num_teams_built == 1:
										t2.p6 = playerLoader(0, row)
										t2.p6.onCrt = 0
								elif j == 6:
									if num_teams_built == 0:
										t1.p7 = playerLoader(0, row)
										t1.p7.onCrt = 0
									elif num_teams_built == 1:
										t2.p7 = playerLoader(0, row)
										t2.p7.onCrt = 0
								elif j == 7:
									if num_teams_built == 0:
										t1.p8 = playerLoader(0, row)
										t1.p8.onCrt = 0
									elif num_teams_built == 1:
										t2.p8 = playerLoader(0, row)
										t2.p8.onCrt = 0
								elif j == 8:
									if num_teams_built == 0:
										t1.p9 = playerLoader(0, row)
										t1.p9.onCrt = 0
									elif num_teams_built == 1:
										t2.p9 = playerLoader(0, row)
										t2.p9.onCrt = 0
								elif j == 9:
									if num_teams_built == 0:
										t1.p10 = playerLoader(0, row)
										t1.p10.onCrt = 0
									elif num_teams_built == 1:
										t2.p10 = playerLoader(0, row)
										t2.p10.onCrt = 0
					j += 1 # iterate j to search for the next player on the team
				num_teams_built += 1 # iterate to build the second team, or exit the loops

	# TODO: Is this call necessary? Maybe just retrun to HBA_UI, move on to lineups/matchups/usages, then back to sim_game
	# gameController(0, t1, t2) # Once the teams are built, call gameController

	#buildTeamStats(t1)
	#buildTeamStats(t2)
	teams = [t1, t2]
	return teams

# Helper function that calls all the necessary functions to start a game
#	q 	the number of quarters ALREADY PLAYED in a game 
#
# TODO:
#	Could be expanded to be called in sim_game as well
def gameController(q, team1, team2):
	setDefender_UI(2, None, None, None, team1, team2)
	setDefender_UI(2, None, None, None, team2, team1)
	updateUsage_UI(2, None, None, None, team1, team2)
	updateUsage_UI(2, None, None, None, team2, team1)
	updateRebUsage_UI(2, None, None, None, team1, team2)
	updateRebUsage_UI(2, None, None, None, team2, team1)

	qScores1 = [0, 0, 0, 0]
	qScores2 = [0, 0, 0, 0]
	sim_game(qScores1, qScores2, team1, team2)

def startup_UI():
	print("\n          Welcome to...")
	print("   HYPOTHETICAL BASKETBALL!\n")
	print("   What would you like to do?")
	print("     [1] Simulate new game\n     [2] Load save file\n     [0] Exit\n")

	usrIn = input()

	if int(usrIn) == 1: # Simulate new game
		os.system('cls' if os.name == 'nt' else 'clear')
		print("\n     [1] Choose teams\n     [2] Custom teams\n     Enter [X] at any time to exit\n")
		usrIn = input()
		if int(usrIn) == 1:	# Game w/ premade teams
			team1 = loadTeam("one")
			team2 = loadTeam("two")
			gameController(0, team1, team2)
		elif int(usrIn) == 2: 	# Game w/ custom teams
			team1 = Team(-1, "", "", "", None, None, None, None, None, None, None, None, None, None)
			team2 = Team(-1, "", "", "", None, None, None, None, None, None, None, None, None, None)
			buildTeam_UI(team1)
			buildTeam_UI(team2)
			gameController(0, team1, team2)
	elif int(usrIn) == 2: 	# Load game from save file
		loadGame()

#startup_UI()