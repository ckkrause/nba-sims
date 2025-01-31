from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import csv
from HBA_Sim import Team, Player, loadTeam, sim_quarter, buildTeamStats, saveGame

# Setup root
root = Tk()
root.title("Hypothetical Basketball")
root.configure(background='black')
root.state('zoomed')	

def UI_welcome():
	# Set style
	s = ttk.Style()
	s.configure('new.TFrame', background='black')

	# Create frame
	mainframe = ttk.Frame(root, style='new.TFrame', width=root.winfo_width(), height=root.winfo_height())
	mainframe.grid(row=0, column=0, sticky=(N, W, E, S))
	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)

	# Creat widgets
	subtitle = Label(mainframe, text="Welcome to...", bg='black', fg='white')
	subtitle.grid(row=2, column=1, sticky="s")
	subtitle.config(font=('Consolas', 20))

	title = Label(mainframe, text="HYPOTHETICAL BASKETBALL", bg='black', fg='white')
	title.grid(row=3, column=1, sticky="n")
	title.config(font=('Consolas', 35))

	new_game_button = Button(mainframe, text="New Game", bg='gray', fg='white', width=10, command=lambda:UI_new_game(mainframe))
	new_game_button.grid(row=4, column=1, sticky="s")
	new_game_button.config(font=('Consolas', 20))
	new_game_button.grid_configure(pady=25)

	load_game_button = Button(mainframe, text="Load Game", bg='gray', fg='white', width=10)
	load_game_button.grid(row=5, column=1, sticky="n")
	load_game_button.config(font=('Consolas', 20))

	# Configure mainframe grid
	mainframe.grid_columnconfigure((0, 1, 2), weight=1)
	mainframe.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

def UI_new_game(past_mainframe):
	selected_team = 1 # Tracks what team is currently has the focus for team selection purposes
	# Boolean variables to track if a team has been chosen or not
	selected_team_1 = [-1, -1, -1]
	selected_team_2 = [-1, -1, -1]

	#
	# Helper function to update selected team
	#
	def helper_update_selected_team(team_button):
		nonlocal selected_team

		if int(team_button) == 1:
			selected_team = 1
		elif int(team_button) == 2:
			selected_team = 2

	#
	# Helper function to update team info display as user navigates through team selection
	#
	def helper_display_team_info(team_index):
		nonlocal team_stats_subframe, selected_team_1, selected_team_2	

		with open('TeamDatabase.csv') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=',')
			
			for row in csv_reader:
				if int(row["idn"]) == int(team_index) + 1:
					nonlocal selected_team

					if selected_team == 1:
						# Update boolean tracker
						selected_team_1[0] = int(row["idn"])

						# Update button text
						nonlocal T1, T1_name
						T1.config(text=str("TEAM 1: " + row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")")
						T1_name.config(text=str(row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")")
						selected_team_1[1] = str(row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")"

						# Update player information in team stats panel
						nonlocal T1_P1, T1_P2, T1_P3, T1_P4, T1_P5
						roster = [row["p1"], row["p2"], row["p3"], row["p4"], row["p5"], row["p6"], row["p7"], row["p8"], row["p9"], row["p10"]]
						selected_team_1[2] = roster
						j = 0
						T1_ovr_total = 0
						T1_off_total = 0
						T1_def_total = 0

						while j < 7:
							with open('PlayerDatabase.csv') as csv_file2:
								csv_reader2 = csv.DictReader(csv_file2, delimiter=',')
								for row2 in csv_reader2:
									if int(row2["idn"]) == int(roster[j]):
										if j == 0:
											T1_P1.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 1:
											T1_P2.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 2:
											T1_P3.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 3:
											T1_P4.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 4:
											T1_P5.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										T1_ovr_total += int(row2["ovr"])
										T1_off_total = T1_off_total + int(row2["ratePost"]) + int(row2["rateDrive"]) + int(row2["rateMid"]) + int(row2["rateThree"]) + int(row2["ratePass"])
										T1_def_total = T1_def_total + int(row2["ratePostD"]) + int(row2["ratePerimD"]) + (int(row2["rateSteal"]) * 5) + (int(row2["rateBlock"]) * 10)
							j += 1

						nonlocal T1_ovr, T1_off, T1_def
						T1_ovr.config(text="OVR | " + str(int(T1_ovr_total / 7)))
						T1_off.config(text="OFF | " + str(int(T1_off_total / 35)))
						T1_def.config(text="DEF | " + str(int(T1_def_total / 28)))

					elif selected_team == 2:
						# Update boolean tracker
						selected_team_2[0] = int(row["idn"])

						# Update button text
						nonlocal T2, T2_name
						T2.config(text=str("TEAM 2: " + row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")")
						T2_name.config(text=str(row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")")
						selected_team_2[1] = str(row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")"

						# Update player information in team stats panel
						nonlocal T2_P1, T2_P2, T2_P3, T2_P4, T2_P5
						roster = [row["p1"], row["p2"], row["p3"], row["p4"], row["p5"], row["p6"], row["p7"], row["p8"], row["p9"], row["p10"]]
						selected_team_2[2] = roster
						j = 0
						T2_ovr_total = 0
						T2_off_total = 0
						T2_def_total = 0
						
						while j < 7:
							with open('PlayerDatabase.csv') as csv_file2:
								csv_reader2 = csv.DictReader(csv_file2, delimiter=',')
								for row2 in csv_reader2:
									if int(row2["idn"]) == int(roster[j]):
										if j == 0:
											T2_P1.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 1:
											T2_P2.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 2:
											T2_P3.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 3:
											T2_P4.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										elif j == 4:
											T2_P5.config(text=str(row2["name"]) + " | " + str(row2["pos"]) + " | " + str(row2["ovr"]) + " OVR")
										T2_ovr_total += int(row2["ovr"])
										T2_off_total = T2_off_total + int(row2["ratePost"]) + int(row2["rateDrive"]) + int(row2["rateMid"]) + int(row2["rateThree"]) + int(row2["ratePass"])
										T2_def_total = T2_def_total + int(row2["ratePostD"]) + int(row2["ratePerimD"]) + (int(row2["rateSteal"]) * 5) + (int(row2["rateBlock"]) * 10)
							j += 1

						nonlocal T2_ovr, T2_off, T2_def
						T2_ovr.config(text="OVR | " + str(int(T2_ovr_total / 7)))
						T2_off.config(text="OFF | " + str(int(T2_off_total / 35)))
						T2_def.config(text="DEF | " + str(int(T2_def_total / 28)))

		helper_display_begin_game_button()

	#
	# If both teams are selected, display a BEGIN GAME button (by gridding a prexisting button)
	#
	def helper_display_begin_game_button():
		nonlocal selected_team_1, selected_team_2, begin_game

		if (selected_team_1[0] != -1) and (selected_team_2[0] != -1):
			begin_game.grid(row=9, column=5)


	# Clear screen
	past_mainframe.grid_forget()

	# Set style
	s = ttk.Style()
	s.configure('new.TFrame', background='black')

	# Create frame
	mainframe = ttk.Frame(root, style='new.TFrame', width=root.winfo_width(), height=root.winfo_height(), padding="0 0 0 0")
	mainframe.grid(row=0, column=0, sticky=(N, W, E, S))
	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)

	# Creat listbox widget for all available teams
	team_list = Listbox(mainframe, font='Consolas')
	team_list.grid(row=0, column=0, rowspan=10, sticky=(N, S, E, W))
	team_list.grid_configure(padx=10, pady=10)

	# Populate team_list from TeamDatabase.csv
	with open('TeamDatabase.csv') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		i = 0
		for row in csv_reader:
			team_name = str(row["city"]) + " " + str(row["name"]) + " (" + str(row["year"]) + ")"
			team_list.insert(i, team_name)
			i += 1

	# Setup team_list event to update team_stats as teams are selected
	team_list.bind("<<ListboxSelect>>", lambda _: helper_display_team_info(team_list.curselection()[0]))

	# Creat a button widget for selecting Team 1
	T1 = Button(mainframe, text="TEAM 1", width=40, command=lambda:helper_update_selected_team(1))
	T1.grid(row=0, column=2, sticky=(N, S, E, W))
	T1.grid_configure(padx=10, pady=10)
	T1.config(font=('Consolas', 12))

	# Creat a button widget for selecting Team 2
	T2 = Button(mainframe, text="TEAM 2", width=40, command=lambda:helper_update_selected_team(2))
	T2.grid(row=0, column=4, sticky=(N, S, E, W))
	T2.grid_configure(padx=10, pady=10)
	T2.config(font=('Consolas', 12))

	# If both teams are selected, create a BEGIN GAME button widget
	begin_game = Button(mainframe, text="BEGIN GAME >>>", bg="Light green", width=16, height=2, command=lambda:UI_set_lineups(mainframe, selected_team_1, selected_team_2))
	begin_game.config(font=('Consolas', 12, 'bold'))

	# Create a subframe to organize all widgets to display team stats
	team_stats_subframe = ttk.Frame(mainframe)
	team_stats_subframe.grid(row=1, column=1, rowspan=8, columnspan=5, stick=(N, S, E, W))

	#
	# Pre-load widgets to display team stats
	#
	T1_name = Label(team_stats_subframe, text="", width=30)
	T1_name.grid(row=0, column=1, stick='s')
	T1_name.config(font=('Consolas', 20, 'bold'))

	T2_name = Label(team_stats_subframe, text="", width=30)
	T2_name.grid(row=0, column=2, stick='s')
	T2_name.config(font=('Consolas', 20, 'bold'))

	T1_ovr = Label(team_stats_subframe, text="")
	T1_ovr.grid(row=1, column=1, stick='s')
	T1_ovr.config(font=('Consolas', 22, 'bold'))

	T2_ovr = Label(team_stats_subframe, text="")
	T2_ovr.grid(row=1, column=2, stick='s')
	T2_ovr.config(font=('Consolas', 22, 'bold'))

	T1_off = Label(team_stats_subframe, text="")
	T1_off.grid(row=2, column=1)
	T1_off.config(font=('Consolas', 18))

	T2_off = Label(team_stats_subframe, text="")
	T2_off.grid(row=2, column=2)
	T2_off.config(font=('Consolas', 18))

	T1_def = Label(team_stats_subframe, text="")
	T1_def.grid(row=3, column=1, sticky='n')
	T1_def.config(font=('Consolas', 18))

	T2_def = Label(team_stats_subframe, text="")
	T2_def.grid(row=3, column=2, sticky='n')
	T2_def.config(font=('Consolas', 18))

	T1_P1 = Label(team_stats_subframe, text="", bg='light gray')
	T1_P1.grid(row=4, column=0, columnspan=2, stick=(N, S, E, W))
	T1_P1.config(font=('Consolas', 12))

	T1_P2 = Label(team_stats_subframe, text="")
	T1_P2.grid(row=5, column=0, columnspan=2)
	T1_P2.config(font=('Consolas', 12))

	T1_P3 = Label(team_stats_subframe, text="", bg='light gray')
	T1_P3.grid(row=6, column=0, columnspan=2, stick=(N, S, E, W))
	T1_P3.config(font=('Consolas', 12))

	T1_P4 = Label(team_stats_subframe, text="")
	T1_P4.grid(row=7, column=0, columnspan=2)
	T1_P4.config(font=('Consolas', 12))

	T1_P5 = Label(team_stats_subframe, text="", bg='light gray')
	T1_P5.grid(row=8, column=0, columnspan=2, stick=(N, S, E, W))
	T1_P5.config(font=('Consolas', 12))

	T2_P1 = Label(team_stats_subframe, text="", bg='light gray')
	T2_P1.grid(row=4, column=2, columnspan=2, stick=(N, S, E, W))
	T2_P1.config(font=('Consolas', 12))

	T2_P2 = Label(team_stats_subframe, text="")
	T2_P2.grid(row=5, column=2, columnspan=2)
	T2_P2.config(font=('Consolas', 12))

	T2_P3 = Label(team_stats_subframe, text="", bg='light gray')
	T2_P3.grid(row=6, column=2, columnspan=2, stick=(N, S, E, W))
	T2_P3.config(font=('Consolas', 12))

	T2_P4 = Label(team_stats_subframe, text="")
	T2_P4.grid(row=7, column=2, columnspan=2)
	T2_P4.config(font=('Consolas', 12))

	T2_P5 = Label(team_stats_subframe, text="", bg='light gray')
	T2_P5.grid(row=8, column=2, columnspan=2, stick=(N, S, E, W))
	T2_P5.config(font=('Consolas', 12))

	'''
	# Display player card
	img = ImageTk.PhotoImage(Image.open("Cards\\Jordan.jpg"))
	photo = Label(team_stats_subframe, image=img, background='black')
	photo.image = img
	photo.grid(column=0, row=0, rowspan=4)
	
	img2 = ImageTk.PhotoImage(Image.open("Cards\\Payton.jpg"))
	photo2 = Label(team_stats_subframe, image=img2, background='black')
	photo2.image = img2
	photo2.grid(column=3, row=0, rowspan=4)
	'''

	# Configure subframe grid
	team_stats_subframe.grid_columnconfigure((0, 1, 2, 3), weight=1)
	team_stats_subframe.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

	# Configure mainframe grid
	mainframe.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
	mainframe.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)

def UI_set_lineups(past_mainframe, team_1_info, team_2_info):
	
	def helper_player_info_panel(teams, t_index, player):
		#
		# Helper function to update defensive matchup assignments.
		# 	Updates both a player's isDefending pointer and the opposing player's defender pointer
		#
		# 	TODO: Some more work needs to be done in here to clear out-of-date pointers from past matchup assignments
		#
		def helper_set_matchup():
			if t_index == 0:
				roster = teams[1].getRoster(2)
				player.isDefending = roster[matchup.current()]
				roster[matchup.current()].defender = player
				matchup.current(matchup.current())
			elif t_index == 1:
				roster = teams[0].getRoster(2)
				player.isDefending = roster[matchup.current()]
				roster[matchup.current()].defender = player
				matchup.current(matchup.current())
			helper_check_start()

		#
		# Helper fuction to update player usage.
		#
		def helper_set_usage(usage):
			player.usage = int(usage)
			helper_check_start()

		#
		# Helper function to update player rebUsage
		#
		def helper_set_rebUsage(rebUsage):
			player.rebUsage = int(rebUsage)
			helper_check_start()

		#
		# Helper function to update onCrt indicator variable.
		# 	Also responsible for displaying/hiding the matchup and usage widgets as the onCrt check is toggled.
		#
		def popup_change_lineup():
				def change_lineup(substitute):
					if player.onCrt == 1:
						player.onCrt = 0
						substitute.onCrt = 1

						substitute.isDefending = player.isDefending
						substitute.defender = player.defender

						player.isDefending = None
						player.defender = None

						matchup.grid_forget()
						usage_slider.grid_forget()
						rebUsage_slider.grid_forget()

						popup.destroy()
						display_boxscore()
					elif player.onCrt == 0:
						player.onCrt = 1
						substitute.onCrt = 0

						player.isDefending = substitute.isDefending
						player.defender = substitute.defender

						substitute.isDefending = None
						substitute.defender = None

						matchup.grid(row=15, columnspan=2)
						usage_slider.grid(row=16, columnspan=2)
						rebUsage_slider.grid(row=17, columnspan=2)

						popup.destroy()
						display_boxscore()
						helper_check_start()

				popup = Toplevel()
				popup.geometry("400x200")
				popup.title("Adjust Lineup")
				
				if player.onCrt == 1:
					text = "Who will replace " + player.name + "?:"
				elif player.onCrt == 0:
					text = "Who will " + player.name + " replace?:"

				l = Label(popup, text=text)
				l.grid(row=0, column=0, padx=50)
				l.config(font=('Consolas', 14, 'bold'))
				
				if player.onCrt == 1:
					bench = teams[t_index].getRoster(3)
				elif player.onCrt == 0:
					bench = teams[t_index].getRoster(2)

				names = []
				for p in bench:
					names.append(p.name)

				benchbox = ttk.Combobox(popup, values=names)
				benchbox.grid(row=1, padx=50)
				benchbox.config(font=('Consolas', 11))

				enter = Button(popup, text="Save & Exit", command=lambda:change_lineup(bench[benchbox.current()]))
				enter.grid(row=2, sticky=(S), padx=50)
				enter.config(font=('Consolas', 11, 'bold'))

		def popup_game_parameters():
			def helper_toggle_team(t_index):
				# Update the toggle_team button
				nonlocal local_t_index
				nonlocal local_t_index_2
				if t_index == 1:
					local_t_index = 0
					local_t_index_2 = 1
				elif t_index == 0:
					local_t_index = 1
					local_t_index_2 = 0

				# Clear subframe
				for widget in player_data_subframe.winfo_children():
					widget.destroy()

				#
				# Header row widgets
				#
				p_name = Label(player_data_subframe, text="Player", borderwidth=1, relief="solid")
				p_name.grid(row=0, column=0, stick=(E, W))
				p_name.config(font=('Consolas', 11, 'bold'))

				defending = Label(player_data_subframe, text="Matchup", borderwidth=1, relief="solid")
				defending.grid(row=0, column=1, stick=(E, W))
				defending.config(font=('Consolas', 11, 'bold'))

				usage = Label(player_data_subframe, text="Usage", borderwidth=1, relief="solid")
				usage.grid(row=0, column=2, stick=(E, W))
				usage.config(font=('Consolas', 11, 'bold'))

				rebUsage = Label(player_data_subframe, text="Rebound Usage", borderwidth=1, relief="solid")
				rebUsage.grid(row=0, column=3, stick=(E, W))
				rebUsage.config(font=('Consolas', 11, 'bold'))

				#
				# Create player data widgets
				#
				row = 1
				roster = teams[t_index].getRoster(2)
				for p in roster:
					p_name = Label(player_data_subframe, text=p.name + " | " + p.pos)
					p_name.grid(row=row, column=0)
					p_name.config(font=('Consolas', 11))

					p_defending = Label(player_data_subframe, text="")
					if p.isDefending is not None: p_defending.config(text=p.isDefending.name)
					p_defending.grid(row=row, column=1)
					p_defending.config(font=('Consolas', 11))

					p_usage = Label(player_data_subframe, text=p.usage)
					p_usage.grid(row=row, column=2)
					p_usage.config(font=('Consolas', 11))

					p_rebUsage = Label(player_data_subframe, text=p.rebUsage)
					p_rebUsage.grid(row=row, column=3)
					p_rebUsage.config(font=('Consolas', 11))

					row += 1

				error_msg.config(text=display_errors())

			#
			# Error message handling
			#
			def display_errors():
				nonlocal local_t_index_2
				err = helper_error_checker(local_t_index_2)

				if err[0] == 0:
					text = ""
				elif err[0] == 1:
					text = "Error! Usage must total to 100. Currently usage total is " + str(err[1]) + "."
				elif err[0] == 2:
					text = "Error! Rebound usage must total to 100. Currently rebound usage total is " + str(err[1]) + "."
				elif err[0] == 3:
					text = "Error! All players must be assigned a defensive matchup."

				return text


			popup = Toplevel()
			popup.geometry("800x450")
			popup.title("Game Parameters")

			player_data_subframe = ttk.Frame(popup)
			player_data_subframe.grid(row=1, column=0, rowspan=5, columnspan=4, stick=(N, S, E, W))

			#
			# Button widgets to refresh/change the display
			#
			if t_index == 1:
				local_t_index = 0
				local_t_index_2 = 1
			elif t_index == 0:
				local_t_index = 1
				local_t_index_2 = 0
			toggle_team = Button(popup, text="Toggle Team", command=lambda:helper_toggle_team(local_t_index))
			toggle_team.grid(row=7, column=1, stick=(E, W))
			toggle_team.config(font=('Consolas', 11, 'bold'))

			refresh = Button(popup, text="Refresh Data", command=lambda:helper_toggle_team(local_t_index_2))
			refresh.grid(row=7, column=0)
			refresh.config(font=('Consolas', 11, 'bold'))

			#
			# Error message label
			#
			error_msg = Label(popup, text=display_errors(), fg="red")
			error_msg.grid(row=7, column=2)
			error_msg.config(font=('Consolas', 11))

			helper_toggle_team(local_t_index_2)

			player_data_subframe.grid_columnconfigure((0, 1, 2, 3), weight=1)
			player_data_subframe.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

			popup.grid_columnconfigure((0, 1, 2, 3), weight=1)
			popup.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

		#
		# Helper function to check for various errors in the game parameters.
		# Handles one team at a time.
		# Builds an error message array. Index 0 indicates the error code, index 1 indicates relevant information
		#
		#	Return 0 	No errors
		#	Return 1 	Usage does not total to 100
		#	Return 2 	RebUsage does not total to 100
		#	Return 3 	Not all players have a defensive assignment set
		#
		def helper_error_checker(t):
			tot_usage = 0
			tot_rebUsage = 0
			matchup_tally = 0

			roster = teams[t].getRoster(2)

			for p in roster:
				tot_usage += int(p.usage)
				tot_rebUsage += int(p.rebUsage)
				if p.isDefending is not None: matchup_tally += 1

			error = [None, None]

			if tot_usage != 100:
				error[0] = 1
				error[1] = tot_usage
			elif tot_rebUsage != 100:
				error[0] = 2
				error[1] = tot_rebUsage
			elif matchup_tally != 5:
				error[0] = 3
				error[1] = (5 - matchup_tally)
			else:
				error[0] = 0
				error[1] = 0

			return error

		def helper_grade_translate(mode, r):
			if mode == 1: # Translate steal rating from 0-20
				return r * 5
			if mode == 2: # Translate block rating from 0-10
				return r * 10
			if mode == 3: # Translate weighted defensive rating to unweighted
				return int(r / 0.8)
			if mode == 4: # Translate three rating from weighted score to unweighted
				return r
			if mode == 5: # Translate inches to X'Y" format
				feet = str(int(r / 12))
				inches = str(r % 12)
				return feet + "'" + inches + "\""

		def helper_check_start():
			t1_errs = helper_error_checker(0)
			t2_errs = helper_error_checker(1)

			if t1_errs[0] == 0 and t2_errs[0] == 0:
				start_sim.grid(row=37, column=1)

		# Clear subframe
		for widget in player_stats_subframe.winfo_children():
			widget.destroy()

		#
		# Player name & card
		#
		p_name = Label(player_stats_subframe, text=player.name + " | #" + player.num + " | " + player.pos, width=35)
		p_name.grid(row=13, columnspan=2, stick=(N))
		p_name.config(font=('Consolas', 14, 'bold'))

		try:
			img2 = ImageTk.PhotoImage(Image.open("Cards\\" + str(player.idn) + ".jpg"))
			photo2 = Label(player_stats_subframe, image=img2, background='black')
			photo2.image = img2
			photo2.grid(row=0, column=0, rowspan=12, columnspan=2)
		except FileNotFoundError:
			pass

		#
		# Interactive widgets to adjust player lineups, matchups, and usages
		#

		# 'On Court' check box
		onCrt_check = Checkbutton(player_stats_subframe, text="On Court", command=popup_change_lineup)
		onCrt_check.grid(row=14, columnspan=2)
		onCrt_check.config(font=('Consolas', 11))
		if player.onCrt == 1: onCrt_check.select()

		# Defensive matchup combobox
		# Get the list of on-court players for the opposing team
		if t_index == 0: 
			roster = teams[1].getRoster(2)
		elif t_index == 1:
			roster = teams[0].getRoster(2)
		
		# Get the list on names of on-court players for the opposing team
		names = []
		for p in roster:
			names.append(p.name)

		# Create the combobox
		matchup = ttk.Combobox(player_stats_subframe, values=names)
		matchup.config(font=('Consolas', 11))
		matchup.bind("<<ComboboxSelected>>", lambda _: helper_set_matchup())

		# If the player has an existing matchup assignment, set the default value to that player
		if player.onCrt==1: matchup.grid(row=15, columnspan=2)
		if player.isDefending is not None:
			i = 0
			for p in roster:
				if player.isDefending == p: matchup.current(i)
				i += 1

		# Usage scale slider widgets
		usage = IntVar()
		usage_slider = Scale(player_stats_subframe, variable=usage, from_=5, to=35, label="Usage", orient=HORIZONTAL, length=225, command=helper_set_usage)
		usage_slider.config(font=('Consolas', 11))

		if player.onCrt==1: usage_slider.grid(row=16, columnspan=2)
		usage_slider.set(player.usage)

		rebUsage = IntVar()
		rebUsage_slider = Scale(player_stats_subframe, variable=rebUsage, from_=5, to=35, label="Rebound Usage", orient=HORIZONTAL, length=225, command=helper_set_rebUsage)
		rebUsage_slider.config(font=('Consolas', 11))

		if player.onCrt==1: rebUsage_slider.grid(row=17, columnspan=2)
		rebUsage_slider.set(player.rebUsage)

		#
		# Player ability grade widgets
		#
		row = 18
		x = 40
		x_indent = 60
		gap = 40
		font_heading = 12
		font_body = 11

		ovr = Label(player_stats_subframe, text=player.ovr + " OVR")
		ovr.grid(row=row, columnspan=2, stick=(S))
		ovr.config(font=('Consolas', 14, 'bold'))

		separator = ttk.Separator(player_stats_subframe, orient='horizontal')
		separator.grid(row=row+1, columnspan=2, stick=(E, W))

		#
		# Offensive ratings
		#
		off = Label(player_stats_subframe, text="Offense")
		off.grid(row=row+2, column=0, padx=x, stick=(W))
		off.config(font=('Consolas', font_heading, 'bold'))

		off_inside = Label(player_stats_subframe, text="Inside: " + str(player.ratePost))
		off_inside.grid(row=row+3, column=0, padx=x_indent, stick=(W))
		off_inside.config(font=('Consolas', font_body))

		off_playmake = Label(player_stats_subframe, text="Play Making: " + str(player.rateDrive))
		off_playmake.grid(row=row+4, column=0, padx=x_indent, stick=(W))
		off_playmake.config(font=('Consolas', font_body))

		off_mid = Label(player_stats_subframe, text="Mid: " + str(player.rateMid))
		off_mid.grid(row=row+5, column=0, padx=x_indent, stick=(W))
		off_mid.config(font=('Consolas', font_body))

		off_three = Label(player_stats_subframe, text="Three: " + str(player.rateThree))
		off_three.grid(row=row+6, column=0, padx=x_indent, stick=(W))
		off_three.config(font=('Consolas', font_body))

		off_FT = Label(player_stats_subframe, text="Free Throw: " + str(player.rateFT))
		off_FT.grid(row=row+7, column=0, padx=x_indent, stick=(W))
		off_FT.config(font=('Consolas', font_body))

		separator = ttk.Separator(player_stats_subframe, orient='horizontal')
		separator.grid(row=row+8, columnspan=2, stick=(E, W))

		#
		# Defensive ratings
		#
		def_ = Label(player_stats_subframe, text="Defense")
		def_.grid(row=row+9, column=0, padx=x, stick=(W))
		def_.config(font=('Consolas', font_heading, 'bold'))

		def_inside = Label(player_stats_subframe, text="Inside D: " + str(helper_grade_translate(3, player.ratePostD)))
		def_inside.grid(row=row+10, column=0, padx=x_indent, stick=(W))
		def_inside.config(font=('Consolas', font_body))

		def_perim = Label(player_stats_subframe, text="Perimeter D: " + str(helper_grade_translate(3, player.ratePerimD)))
		def_perim.grid(row=row+11, column=0, padx=x_indent, stick=(W))
		def_perim.config(font=('Consolas', font_body))

		separator = ttk.Separator(player_stats_subframe, orient='horizontal')
		separator.grid(row=row+12, columnspan=2, stick=(E, W))

		#
		# Skill ratings
		#
		skills = Label(player_stats_subframe, text="Skills")
		skills.grid(row=row+13, column=0, padx=x, stick=(W))
		skills.config(font=('Consolas', font_heading, 'bold'))

		reb = Label(player_stats_subframe, text="Rebound: " + str(player.rateReb))
		reb.grid(row=row+14, column=0, padx=x_indent, stick=(W))
		reb.config(font=('Consolas', font_body))

		passing = Label(player_stats_subframe, text="Pass: " + str(player.ratePass))
		passing.grid(row=row+15, column=0, padx=x_indent, stick=(W))
		passing.config(font=('Consolas', font_body))

		block = Label(player_stats_subframe, text="Block: " + str(helper_grade_translate(2, player.rateBlock)))
		block.grid(row=row+16, column=0, padx=x_indent, stick=(W))
		block.config(font=('Consolas', font_body))

		steal = Label(player_stats_subframe, text="Steal: " + str(helper_grade_translate(1, player.rateSteal)))
		steal.grid(row=row+17, column=0, padx=x_indent, stick=(W))
		steal.config(font=('Consolas', font_body))

		#
		# Energy ratings
		#
		enrg = Label(player_stats_subframe, text="Energy")
		enrg.grid(row=row+2, column=1, padx=x - gap, stick=(W))
		enrg.config(font=('Consolas', font_heading, 'bold'))

		currEnrg = Label(player_stats_subframe, text="Current: " + str(player.energy))
		currEnrg.grid(row=row+3, column=1, padx=x_indent - gap, stick=(W))
		currEnrg.config(font=('Consolas', font_body))

		enrgLoss = Label(player_stats_subframe, text="Depletion: " + str(player.enrgLoss))
		enrgLoss.grid(row=row+4, column=1, padx=x_indent - gap, stick=(W))
		enrgLoss.config(font=('Consolas', font_body))

		enrgGain = Label(player_stats_subframe, text="Recovery: " + str(player.enrgGain))
		enrgGain.grid(row=row+5, column=1, padx=x_indent - gap, stick=(W))
		enrgGain.config(font=('Consolas', font_body))

		#
		# Consistency ratings
		#
		consist = Label(player_stats_subframe, text="Consistency")
		consist.grid(row=row+9, column=1, padx=x - gap, stick=(W))
		consist.config(font=('Consolas', font_heading, 'bold'))

		heatOVar = Label(player_stats_subframe, text="Offensive Consistency: " + str(player.heatOVar))
		heatOVar.grid(row=row+10, column=1, padx=x_indent - gap, stick=(W))
		heatOVar.config(font=('Consolas', font_body))

		heatDVar = Label(player_stats_subframe, text="Defensive Consistency: " + str(player.heatDVar))
		heatDVar.grid(row=row+11, column=1, padx=x_indent - gap, stick=(W))
		heatDVar.config(font=('Consolas', font_body))

		#
		# Physical attributes
		#
		attributes = Label(player_stats_subframe, text="Physical Attributes")
		attributes.grid(row=row+13, column=1, padx=x - gap, stick=(W))
		attributes.config(font=('Consolas', font_heading, 'bold'))

		height = Label(player_stats_subframe, text="Height: " + str(helper_grade_translate(5, player.height)))
		height.grid(row=row+14, column=1, padx=x_indent - gap, stick=(W))
		height.config(font=('Consolas', font_body))

		length = Label(player_stats_subframe, text="Length: " + str(helper_grade_translate(5, player.length)))
		length.grid(row=row+15, column=1, padx=x_indent - gap, stick=(W))
		length.config(font=('Consolas', font_body))

		speed = Label(player_stats_subframe, text="Speed: " + str(helper_grade_translate(2, player.speed)))
		speed.grid(row=row+16, column=1, padx=x_indent - gap, stick=(W))
		speed.config(font=('Consolas', font_body))

		phys = Label(player_stats_subframe, text="Physicality: " + str(helper_grade_translate(2, player.phys)))
		phys.grid(row=row+17, column=1, padx=x_indent - gap, stick=(W))
		phys.config(font=('Consolas', font_body))

		separator = ttk.Separator(player_stats_subframe, orient='horizontal')
		separator.grid(row=row+18, columnspan=2, stick=(E, W))

		# Buttons for opening game parameters pop up and starting simulation of next quarter
		popup_params = Button(player_stats_subframe, text="View Game Parameters", command=popup_game_parameters)
		popup_params.grid(row=row+19, column=0)
		popup_params.config(font=('Consolas', 12, 'bold'))

		
		start_sim = Button(player_stats_subframe, text="Start", bg="Light green", command=lambda:sim_game())
		start_sim.config(font=('Consolas', 12, 'bold'))

		t1_errs = helper_error_checker(0)
		t2_errs = helper_error_checker(1)

		if t1_errs[0] == 0 and t2_errs[0] == 0:
			start_sim.grid(row=row+19, column=1)

	# Helper function to calculate FG%. Also checks for divide by zero errors.
	def percentCalc(makes, attempts):
		if attempts == 0:
			return "0.000"
		else:
			return format((makes / attempts), '.3f')

	teams = loadTeam(team_1_info[0], team_2_info[0])

	# Clear screen
	past_mainframe.destroy()

	# Set style
	s = ttk.Style()
	s.configure('new.TFrame', background='black')

	# Create frame
	mainframe = ttk.Frame(root, style='new.TFrame', width=root.winfo_width(), height=root.winfo_height(), padding="5 5 5 5")
	mainframe.grid(row=0, column=0, sticky=(N, W, E, S))

	# Create a subframe to organize all widgets to display the box score
	boxscore_subframe = ttk.Frame(mainframe, padding="5 5 10 10")
	boxscore_subframe.grid(row=0, column=0, columnspan=2, stick=(N, S, E, W))

	# Create a subframe for the player stats panel
	player_stats_subframe = ttk.Frame(mainframe, padding="5 5 10 10")
	player_stats_subframe.grid(row=0, column=2, columnspan=1, stick=(N, S, E, W))

	# Create title widget
	title = Label(boxscore_subframe, text=(team_1_info[1] + " vs " + team_2_info[1]))
	title.grid(row=0, column=0, columnspan=20, stick=(N, S, E, W))
	title.config(font=('Consolas', 16, 'bold'))

	def display_boxscore():
		# Clear subframe
		for widget in boxscore_subframe.winfo_children():
			widget.destroy()

		# Populate player stats in the boxscore
		row = 1
		combined_rosters = []

		for team in teams:
			# Create boxscore widgets
			font_size = 8

			T_MP = Label(boxscore_subframe, text="MP", borderwidth=1, relief="solid")
			T_MP.grid(row=row, column=1, stick=(N, S, E, W))
			T_MP.config(font=('Consolas', font_size, 'bold'))

			T_FG = Label(boxscore_subframe, text="FG", borderwidth=1, relief="solid")
			T_FG.grid(row=row, column=2, stick=(N, S, E, W))
			T_FG.config(font=('Consolas', font_size, 'bold'))

			T_FGA = Label(boxscore_subframe, text="FGA", borderwidth=1, relief="solid")
			T_FGA.grid(row=row, column=3, stick=(N, S, E, W))
			T_FGA.config(font=('Consolas', font_size, 'bold'))

			T_FGP = Label(boxscore_subframe, text="FG%", borderwidth=1, relief="solid")
			T_FGP.grid(row=row, column=4, stick=(N, S, E, W))
			T_FGP.config(font=('Consolas', font_size, 'bold'))

			T_TP = Label(boxscore_subframe, text="3P", borderwidth=1, relief="solid")
			T_TP.grid(row=row, column=5, stick=(N, S, E, W))
			T_TP.config(font=('Consolas', font_size, 'bold'))

			T_TPA = Label(boxscore_subframe, text="3PA", borderwidth=1, relief="solid")
			T_TPA.grid(row=row, column=6, stick=(N, S, E, W))
			T_TPA.config(font=('Consolas', font_size, 'bold'))

			T_TPP = Label(boxscore_subframe, text="3P%", borderwidth=1, relief="solid")
			T_TPP.grid(row=row, column=7, stick=(N, S, E, W))
			T_TPP.config(font=('Consolas', font_size, 'bold'))

			T_FT = Label(boxscore_subframe, text="FT", borderwidth=1, relief="solid")
			T_FT.grid(row=row, column=8, stick=(N, S, E, W))
			T_FT.config(font=('Consolas', font_size, 'bold'))

			T_FTA = Label(boxscore_subframe, text="FTA", borderwidth=1, relief="solid")
			T_FTA.grid(row=row, column=9, stick=(N, S, E, W))
			T_FTA.config(font=('Consolas', font_size, 'bold'))

			T_FTP = Label(boxscore_subframe, text="FT%", borderwidth=1, relief="solid")
			T_FTP.grid(row=row, column=10, stick=(N, S, E, W))
			T_FTP.config(font=('Consolas', font_size, 'bold'))

			T_ORB = Label(boxscore_subframe, text="ORB", borderwidth=1, relief="solid")
			T_ORB.grid(row=row, column=11, stick=(N, S, E, W))
			T_ORB.config(font=('Consolas', font_size, 'bold'))

			T_DRB = Label(boxscore_subframe, text="DRB", borderwidth=1, relief="solid")
			T_DRB.grid(row=row, column=12, stick=(N, S, E, W))
			T_DRB.config(font=('Consolas', font_size, 'bold'))

			T_TRB = Label(boxscore_subframe, text="TRB", borderwidth=1, relief="solid")
			T_TRB.grid(row=row, column=13, stick=(N, S, E, W))
			T_TRB.config(font=('Consolas', font_size, 'bold'))

			T_AST = Label(boxscore_subframe, text="AST", borderwidth=1, relief="solid")
			T_AST.grid(row=row, column=14, stick=(N, S, E, W))
			T_AST.config(font=('Consolas', font_size, 'bold'))

			T_STL = Label(boxscore_subframe, text="STL", borderwidth=1, relief="solid")
			T_STL.grid(row=row, column=15, stick=(N, S, E, W))
			T_STL.config(font=('Consolas', font_size, 'bold'))

			T_BLK = Label(boxscore_subframe, text="BLK", borderwidth=1, relief="solid")
			T_BLK.grid(row=row, column=16, stick=(N, S, E, W))
			T_BLK.config(font=('Consolas', font_size, 'bold'))

			T_TOV = Label(boxscore_subframe, text="TOV", borderwidth=1, relief="solid")
			T_TOV.grid(row=row, column=17, stick=(N, S, E, W))
			T_TOV.config(font=('Consolas', font_size, 'bold'))

			T_PF = Label(boxscore_subframe, text="PF", borderwidth=1, relief="solid")
			T_PF.grid(row=row, column=18, stick=(N, S, E, W))
			T_PF.config(font=('Consolas', font_size, 'bold'))

			T_PTS = Label(boxscore_subframe, text="PTS", borderwidth=1, relief="solid")
			T_PTS.grid(row=row, column=19, stick=(N, S, E, W))
			T_PTS.config(font=('Consolas', font_size, 'bold'))

			row += 1
			roster = team.getRoster(2) + team.getRoster(3)
			combined_rosters += roster

			for player in roster:

				if (row % 2) == 0:
					row_bg = 'light gray'
				else:
					row_bg = 'white'

				MP = Label(boxscore_subframe, text=player.MP, bg=row_bg)
				MP.grid(row=row, column=1, stick=(N, S, E, W))
				MP.config(font=('Consolas', font_size))

				FG = Label(boxscore_subframe, text=player.FG, bg=row_bg)
				FG.grid(row=row, column=2, stick=(N, S, E, W))
				FG.config(font=('Consolas', font_size))

				FGA = Label(boxscore_subframe, text=player.FGA, bg=row_bg)
				FGA.grid(row=row, column=3, stick=(N, S, E, W))
				FGA.config(font=('Consolas', font_size))

				FGP = Label(boxscore_subframe, text=percentCalc(player.FG, player.FGA), bg=row_bg)
				FGP.grid(row=row, column=4, stick=(N, S, E, W))
				FGP.config(font=('Consolas', font_size))

				TP = Label(boxscore_subframe, text=player.TP, bg=row_bg)
				TP.grid(row=row, column=5, stick=(N, S, E, W))
				TP.config(font=('Consolas', font_size))

				TPA = Label(boxscore_subframe, text=player.TPA, bg=row_bg)
				TPA.grid(row=row, column=6, stick=(N, S, E, W))
				TPA.config(font=('Consolas', font_size))

				TPP = Label(boxscore_subframe, text=percentCalc(player.TP, player.TPA), bg=row_bg)
				TPP.grid(row=row, column=7, stick=(N, S, E, W))
				TPP.config(font=('Consolas', font_size))

				FT = Label(boxscore_subframe, text=player.FT, bg=row_bg)
				FT.grid(row=row, column=8, stick=(N, S, E, W))
				FT.config(font=('Consolas', font_size))

				FTA = Label(boxscore_subframe, text=player.FTA, bg=row_bg)
				FTA.grid(row=row, column=9, stick=(N, S, E, W))
				FTA.config(font=('Consolas', font_size))

				FTP = Label(boxscore_subframe, text=percentCalc(player.FT, player.FTA), bg=row_bg)
				FTP.grid(row=row, column=10, stick=(N, S, E, W))
				FTP.config(font=('Consolas', font_size))

				ORB = Label(boxscore_subframe, text=player.ORB, bg=row_bg)
				ORB.grid(row=row, column=11, stick=(N, S, E, W))
				ORB.config(font=('Consolas', font_size))

				DRB = Label(boxscore_subframe, text=player.DRB, bg=row_bg)
				DRB.grid(row=row, column=12, stick=(N, S, E, W))
				DRB.config(font=('Consolas', font_size))

				TRB = Label(boxscore_subframe, text=int(player.ORB + player.DRB), bg=row_bg)
				TRB.grid(row=row, column=13, stick=(N, S, E, W))
				TRB.config(font=('Consolas', font_size))

				AST = Label(boxscore_subframe, text=player.AST, bg=row_bg)
				AST.grid(row=row, column=14, stick=(N, S, E, W))
				AST.config(font=('Consolas', font_size))

				STL = Label(boxscore_subframe, text=player.STL, bg=row_bg)
				STL.grid(row=row, column=15, stick=(N, S, E, W))
				STL.config(font=('Consolas', font_size))

				BLK = Label(boxscore_subframe, text=player.BLK, bg=row_bg)
				BLK.grid(row=row, column=16, stick=(N, S, E, W))
				BLK.config(font=('Consolas', font_size))

				TOV = Label(boxscore_subframe, text=player.TOV, bg=row_bg)
				TOV.grid(row=row, column=17, stick=(N, S, E, W))
				TOV.config(font=('Consolas', font_size))

				PF = Label(boxscore_subframe, text=player.PF, bg=row_bg)
				PF.grid(row=row, column=18, stick=(N, S, E, W))
				PF.config(font=('Consolas', font_size))

				PTS = Label(boxscore_subframe, text=player.PTS, bg=row_bg)
				PTS.grid(row=row, column=19, stick=(N, S, E, W))
				PTS.config(font=('Consolas', font_size))

				# Insert seperators between starters/bench & before team totals 
				if row == 6 or row == 12 or row == 27 or row == 33:
					separator = ttk.Separator(boxscore_subframe, orient='horizontal')
					separator.grid(row=(row + 1), column=0, columnspan=20, stick=(E, W))
					row += 1

				row += 1

			buildTeamStats(team)

			# Display team totals line
			tot_FG = Label(boxscore_subframe, text=team.FG)
			tot_FG.grid(row=row, column=2)
			tot_FG.config(font=('Consolas', font_size))

			tot_FGA = Label(boxscore_subframe, text=team.FGA)
			tot_FGA.grid(row=row, column=3)
			tot_FGA.config(font=('Consolas', font_size))

			tot_FGP = Label(boxscore_subframe, text=percentCalc(team.FG, team.FGA))
			tot_FGP.grid(row=row, column=4)
			tot_FGP.config(font=('Consolas', font_size))

			tot_TP = Label(boxscore_subframe, text=team.TP)
			tot_TP.grid(row=row, column=5)
			tot_TP.config(font=('Consolas', font_size))

			tot_TPA = Label(boxscore_subframe, text=team.TPA)
			tot_TPA.grid(row=row, column=6)
			tot_TPA.config(font=('Consolas', font_size))

			tot_TPP = Label(boxscore_subframe, text=percentCalc(team.TP, team.TPA))
			tot_TPP.grid(row=row, column=7)
			tot_TPP.config(font=('Consolas', font_size))

			tot_FT = Label(boxscore_subframe, text=team.FT)
			tot_FT.grid(row=row, column=8)
			tot_FT.config(font=('Consolas', font_size))

			tot_FTA = Label(boxscore_subframe, text=team.FTA)
			tot_FTA.grid(row=row, column=9)
			tot_FTA.config(font=('Consolas', font_size))

			tot_FTP = Label(boxscore_subframe, text=percentCalc(team.FT, team.FTA))
			tot_FTP.grid(row=row, column=10)
			tot_FTP.config(font=('Consolas', font_size))

			tot_ORB = Label(boxscore_subframe, text=team.ORB)
			tot_ORB.grid(row=row, column=11)
			tot_ORB.config(font=('Consolas', font_size))

			tot_DRB = Label(boxscore_subframe, text=team.DRB)
			tot_DRB.grid(row=row, column=12)
			tot_DRB.config(font=('Consolas', font_size))

			tot_TRB = Label(boxscore_subframe, text=int(team.ORB + team.DRB))
			tot_TRB.grid(row=row, column=13)
			tot_TRB.config(font=('Consolas', font_size))

			tot_AST = Label(boxscore_subframe, text=team.AST)
			tot_AST.grid(row=row, column=14)
			tot_AST.config(font=('Consolas', font_size))

			tot_STL = Label(boxscore_subframe, text=team.STL)
			tot_STL.grid(row=row, column=15)
			tot_STL.config(font=('Consolas', font_size))

			tot_BLK = Label(boxscore_subframe, text=team.BLK)
			tot_BLK.grid(row=row, column=16)
			tot_BLK.config(font=('Consolas', font_size))

			tot_TOV = Label(boxscore_subframe, text=team.TOV)
			tot_TOV.grid(row=row, column=17)
			tot_TOV.config(font=('Consolas', font_size))

			tot_PF = Label(boxscore_subframe, text=team.PF)
			tot_PF.grid(row=row, column=18)
			tot_PF.config(font=('Consolas', font_size))

			tot_PTS = Label(boxscore_subframe, text=team.PTS)
			tot_PTS.grid(row=row, column=19)
			tot_PTS.config(font=('Consolas', font_size))

			row += 8

		# Create player name button widgets
		#		I tried very hard to find a cleaner way to do this using a for loop and list of button pointers, but never got it working.
		#		Sometimes brute force is quicker.
		p1_name = Button(boxscore_subframe, text=combined_rosters[0].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[0]))
		p1_name.grid(row=2, column=0, stick=(N, S, E, W))
		p1_name.config(font=('Consolas', font_size))

		p2_name = Button(boxscore_subframe, text=combined_rosters[1].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[1]))
		p2_name.grid(row=3, column=0, stick=(N, S, E, W))
		p2_name.config(font=('Consolas', font_size))

		p3_name = Button(boxscore_subframe, text=combined_rosters[2].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[2]))
		p3_name.grid(row=4, column=0, stick=(N, S, E, W))
		p3_name.config(font=('Consolas', font_size))

		p4_name = Button(boxscore_subframe, text=combined_rosters[3].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[3]))
		p4_name.grid(row=5, column=0, stick=(N, S, E, W))
		p4_name.config(font=('Consolas', font_size))

		p5_name = Button(boxscore_subframe, text=combined_rosters[4].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[4]))
		p5_name.grid(row=6, column=0, stick=(N, S, E, W))
		p5_name.config(font=('Consolas', font_size))

		p6_name = Button(boxscore_subframe, text=combined_rosters[5].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[5]))
		p6_name.grid(row=8, column=0, stick=(N, S, E, W))
		p6_name.config(font=('Consolas', font_size))

		p7_name = Button(boxscore_subframe, text=combined_rosters[6].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[6]))
		p7_name.grid(row=9, column=0, stick=(N, S, E, W))
		p7_name.config(font=('Consolas', font_size))

		p8_name = Button(boxscore_subframe, text=combined_rosters[7].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[7]))
		p8_name.grid(row=10, column=0, stick=(N, S, E, W))
		p8_name.config(font=('Consolas', font_size))

		p9_name = Button(boxscore_subframe, text=combined_rosters[8].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[8]))
		p9_name.grid(row=11, column=0, stick=(N, S, E, W))
		p9_name.config(font=('Consolas', font_size))

		p10_name = Button(boxscore_subframe, text=combined_rosters[9].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 0, combined_rosters[9]))
		p10_name.grid(row=12, column=0, stick=(N, S, E, W))
		p10_name.config(font=('Consolas', font_size))

		p11_name = Button(boxscore_subframe, text=combined_rosters[10].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[10]))
		p11_name.grid(row=23, column=0, stick=(N, S, E, W))
		p11_name.config(font=('Consolas', font_size))

		p12_name = Button(boxscore_subframe, text=combined_rosters[11].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[11]))
		p12_name.grid(row=24, column=0, stick=(N, S, E, W))
		p12_name.config(font=('Consolas', font_size))

		p13_name = Button(boxscore_subframe, text=combined_rosters[12].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[12]))
		p13_name.grid(row=25, column=0, stick=(N, S, E, W))
		p13_name.config(font=('Consolas', font_size))

		p14_name = Button(boxscore_subframe, text=combined_rosters[13].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[13]))
		p14_name.grid(row=26, column=0, stick=(N, S, E, W))
		p14_name.config(font=('Consolas', font_size))

		p15_name = Button(boxscore_subframe, text=combined_rosters[14].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[14]))
		p15_name.grid(row=27, column=0, stick=(N, S, E, W))
		p15_name.config(font=('Consolas', font_size))

		p16_name = Button(boxscore_subframe, text=combined_rosters[15].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[15]))
		p16_name.grid(row=29, column=0, stick=(N, S, E, W))
		p16_name.config(font=('Consolas', font_size))

		p17_name = Button(boxscore_subframe, text=combined_rosters[16].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[16]))
		p17_name.grid(row=30, column=0, stick=(N, S, E, W))
		p17_name.config(font=('Consolas', font_size))

		p18_name = Button(boxscore_subframe, text=combined_rosters[17].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[17]))
		p18_name.grid(row=31, column=0, stick=(N, S, E, W))
		p18_name.config(font=('Consolas', font_size))

		p19_name = Button(boxscore_subframe, text=combined_rosters[18].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[18]))
		p19_name.grid(row=32, column=0, stick=(N, S, E, W))
		p19_name.config(font=('Consolas', font_size))

		p20_name = Button(boxscore_subframe, text=combined_rosters[19].name, bg=row_bg, command=lambda:helper_player_info_panel(teams, 1, combined_rosters[19]))
		p20_name.grid(row=33, column=0, stick=(N, S, E, W))
		p20_name.config(font=('Consolas', font_size))

		#
		# Display Q-Scores table
		#
		nonlocal qScores1, qScores2
		q_row = 15
		q_font = 10

		q1 = Label(boxscore_subframe, text="Q1")
		q1.grid(row=q_row+1, column=1, stick=(S))
		q1.config(font=('Consolas', q_font, 'bold'))

		q2 = Label(boxscore_subframe, text="Q2")
		q2.grid(row=q_row+1, column=2, stick=(S))
		q2.config(font=('Consolas', q_font, 'bold'))

		q3 = Label(boxscore_subframe, text="Q3")
		q3.grid(row=q_row+1, column=3, stick=(S))
		q3.config(font=('Consolas', q_font, 'bold'))

		q4 = Label(boxscore_subframe, text="Q4")
		q4.grid(row=q_row+1, column=4, stick=(S))
		q4.config(font=('Consolas', q_font, 'bold'))

		q_final = Label(boxscore_subframe, text="FINAL")
		q_final.grid(row=q_row+1, column=5, stick=(S))
		q_final.config(font=('Consolas', q_font, 'bold'))

		q_team1 = Label(boxscore_subframe, text=teams[0].name)
		q_team1.grid(row=q_row+2, column=0, stick=(S))
		q_team1.config(font=('Consolas', q_font, 'bold'))

		separator = ttk.Separator(boxscore_subframe, orient='horizontal')
		separator.grid(row=q_row+3, columnspan=6, stick=(E, W))

		q_team2 = Label(boxscore_subframe, text=teams[1].name)
		q_team2.grid(row=q_row+4, column=0, stick=(N))
		q_team2.config(font=('Consolas', q_font, 'bold'))

		t1_q1_score = Label(boxscore_subframe, text=qScores1[0])
		t1_q1_score.grid(row=q_row+2, column=1, stick=(S))
		t1_q1_score.config(font=('Consolas', q_font))

		t1_q2_score = Label(boxscore_subframe, text=qScores1[1])
		t1_q2_score.grid(row=q_row+2, column=2, stick=(S))
		t1_q2_score.config(font=('Consolas', q_font))

		t1_q3_score = Label(boxscore_subframe, text=qScores1[2])
		t1_q3_score.grid(row=q_row+2, column=3, stick=(S))
		t1_q3_score.config(font=('Consolas', q_font))

		t1_q4_score = Label(boxscore_subframe, text=qScores1[3])
		t1_q4_score.grid(row=q_row+2, column=4, stick=(S))
		t1_q4_score.config(font=('Consolas', q_font))

		t1_final_score = Label(boxscore_subframe, text=str(qScores1[0] + qScores1[1] + qScores1[2] + qScores1[3]))
		t1_final_score.grid(row=q_row+2, column=5, stick=(S))
		t1_final_score.config(font=('Consolas', q_font))

		t2_q1_score = Label(boxscore_subframe, text=qScores2[0])
		t2_q1_score.grid(row=q_row+4, column=1, stick=(N))
		t2_q1_score.config(font=('Consolas', q_font))

		t2_q2_score = Label(boxscore_subframe, text=qScores2[1])
		t2_q2_score.grid(row=q_row+4, column=2, stick=(N))
		t2_q2_score.config(font=('Consolas', q_font))

		t2_q3_score = Label(boxscore_subframe, text=qScores2[2])
		t2_q3_score.grid(row=q_row+4, column=3, stick=(N))
		t2_q3_score.config(font=('Consolas', q_font))

		t2_q4_score = Label(boxscore_subframe, text=qScores2[3])
		t2_q4_score.grid(row=q_row+4, column=4, stick=(N))
		t2_q4_score.config(font=('Consolas', q_font))

		t2_final_score = Label(boxscore_subframe, text=str(qScores2[0] + qScores2[1] + qScores2[2] + qScores2[3]))
		t2_final_score.grid(row=q_row+4, column=5, stick=(N))
		t2_final_score.config(font=('Consolas', q_font))

	q = 0
	qScores1 = [0, 0, 0, 0]
	qScores2 = [0, 0, 0, 0]

	def sim_game():
		nonlocal q, qScores1, qScores2
		q += 1
		if q <= 4:
			sim_quarter(teams[0], teams[1])
			buildTeamStats(teams[0])
			buildTeamStats(teams[1])

			if q == 1:
				qScores1[0] = teams[0].PTS
				qScores2[0] = teams[1].PTS
			elif q == 2:
				qScores1[1] = teams[0].PTS - qScores1[0]
				qScores2[1] = teams[1].PTS - qScores2[0]
			elif q == 3:
				qScores1[2] = teams[0].PTS - qScores1[1] - qScores1[0]
				qScores2[2] = teams[1].PTS - qScores2[1] - qScores2[0]
			elif q == 4:
				qScores1[3] = teams[0].PTS - qScores1[2] - qScores1[1] - qScores1[0]
				qScores2[3] = teams[1].PTS - qScores2[2] - qScores2[1] - qScores2[0]

			display_boxscore()

			if q == 4: saveGame(qScores1, qScores2, teams[0], teams[1])

	# Configure boxscore_subframe grid
	boxscore_subframe.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), weight=1)
	boxscore_subframe.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34), weight=1)

	# Configure player_stats_subframe grid
	player_stats_subframe.grid_columnconfigure((0, 1), weight=1)
	player_stats_subframe.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40), weight=1)

	# Configure mainframe grid
	mainframe.grid_columnconfigure((0, 1, 2), weight=1)
	mainframe.grid_rowconfigure((0), weight=1)

	display_boxscore()

UI_welcome()

# Start mainloop
root.mainloop()