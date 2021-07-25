import tkinter as tk
from PIL import ImageTk,Image
import math, time, pickle, os, subprocess, requests
from urllib import request, error

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
        return

class pill:
    def __init__(self, name, container, icon_shape, icon_colour, qty, dosage_days, dosage_times, dosage_amount):
        self.name = name #name of pill
        self.container = container #container containing the pill
        self.icon_shape = icon_shape #number specifying the pill icon's shape
        self.icon_colour = icon_colour #number specifying the pill icon's colour
        self.qty = qty #amount of pills remaining in the dispenser
        self.dosage_days = dosage_days #list of 7 bool values corresponding to days of the week when the pills are to be taken
        self.dosage_times = dosage_times #list of 4 bool values corresponding to times of the day (morning, afteroon, evening, night) when the pills are to be taken
        self.dosage_amount = dosage_amount #int specifying the number of pills to be taken each time
        return
    def get_icon_id(self):
        if self.icon_shape == -1:
            return 0
        return 6 * self.icon_shape + self.icon_colour + 1
    def get_exhaust_days(self): #get the number of days from today before the pills run out
        cons_d = sum(self.dosage_times) * self.dosage_amount
        cons_w = max(sum(self.dosage_days) * cons_d,1) #max is for zero handling
        weeks = math.floor(self.qty / cons_w)
        exhaust_days = 7 * weeks
        remainder = self.qty % cons_w
        for i in range(7):
            remainder -= int(self.dosage_days[(time.localtime(time.time()).tm_wday + i) % 7]) * cons_d
            if remainder > 0:
                exhaust_days += 1
        return exhaust_days
    def get_exhaust_date(self): #get the number of date when the pills will run out
        current_time = time.time()
        exhaust_date = self.get_exhaust_days() * 24 * 60 * 60 + current_time
        return time.localtime(exhaust_date)

class user:
    def __init__(self, email, userID, first_name, last_name, share_user1, share_user2, share_user3):
        self.email = email
        self.userID = userID
        self.first_name = first_name
        self.last_name = last_name
        self.share_user1 = share_user1
        self.share_user2 = share_user2
        self.share_user3 = share_user3
        return

class dosage_table: #basically a 3D array containing the number of each pill to be dispensed on each day at each time
    def __init__(self, pill_list):
        self.count = len(pill_list) - 1
        self.table = [[[0] * 4 for i in range(7)] for j in range(self.count)] #table[pill][day][time], eg. table[3][4][2] will reference the number of pills[3] that is to be dispensed on Friday Evening
        self.total_pills = [[0] * 4 for i in range(7)] #table[day][time] that stores the total number of pills to be dispensed at that time
        for index in range(self.count):
            temp_day = [0] * 4
            for i in range(4):
                if pill_list[index].dosage_times[i]:
                    temp_day[i] = pill_list[index].dosage_amount
            for i in range(7):
                if pill_list[index].dosage_days[i]:
                    self.table[index][i] = temp_day
                    for j in range(4):
                        self.total_pills[i][j] += temp_day[j]
                else:
                    self.table[index][i] = [0,0,0,0]
        return
    def update_single(self, pill, index): #update table[index] with pill details
        if index >= self.count:
            return False
        for i in range(7):
            for j in range(4):
                self.total_pills[i][j] -= self.table[index][i][j]
        temp_day = [0] * 4
        for i in range(4):
            if pill.dosage_times[i]:
                temp_day[i] = pill.dosage_amount
        for i in range(7):
            if pill.dosage_days[i]:
                self.table[index][i] = temp_day
                for j in range(4):
                    self.total_pills[i][j] += temp_day[j]
            else:
                self.table[index][i] = [0,0,0,0]
        return True
    def update_all(self, pill_list): #update table[index] with pill_list[] details
        self.count = len(pill_list) - 1
        self.table = [[[0] * 4 for i in range(7)] for j in range(self.count)]
        self.total_pills = [[0] * 4 for i in range(7)]
        for index in range(self.count):
            temp_day = [0] * 4
            for i in range(4):
                if pill_list[index].dosage_times[i]:
                    temp_day[i] = pill_list[index].dosage_amount
            for i in range(7):
                if pill_list[index].dosage_days[i]:
                    self.table[index][i] = temp_day
                    for j in range(4):
                        self.total_pills[i][j] += temp_day[j]
                else:
                    self.table[index][i] = [0,0,0,0]
        return
    def add_pill(self, pill): #appends 2D list to the table with new pill details
        temp_day = [0] * 4
        temp_week = []
        for i in range(4):
            if pill.dosage_times[i]:
                temp_day[i] = pill.dosage_amount
        for i in range(7):
            if pill.dosage_days[i]:
                temp_week.append(temp_day)
                for j in range(4):
                    self.total_pills[i][j] += temp_day[j]
            else:
                self.table[index][i] = [0,0,0,0]
        self.table.append(temp_week)
        self.count += 1
    def delete_pill(self, index): #deletes 2D list at index from the table
        for i in range(7):
            for j in range(4):
                self.total_pills[i][j] -= self.table[index][i][j]
        self.table.pop(index)
        self.count -= 1
        return
    def get_dosage(self, index, day, time): #returns a list of the number of each pill to be dispensed at the specified day and time 
        dosage_list = []
        for i in range(self.count):
            dosage_list.append(self.table[i][day][time])
        return dosage_list
    def has_dose(self, day, time):
        test = self.total_pills[day][time] != 0
        return test

class day_time: #stores hour and minute 
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute
        return
    def to_string(self):
        return f"{str(self.hour).zfill(2)}:{str(self.minute).zfill(2)}"
    def from_string(self, string):
        colon_index = string.find(":")
        self.hour = int(string[0:colon_index])
        self.minute = int(string[colon_index+1:])
        return
    def is_valid(self):
        if self.hour >= 24 or self.minute >= 60:
            return False
        return True

class pill_dose:
    def __init__(self, unix_day, time):
        self.day = unix_day
        self.time = time
        return
    def get_day(self):
        return ((time.localtime((self.day) * 86400 - time.localtime().tm_gmtoff).tm_wday) + 1) % 7
    def get_date(self):
        return time.localtime((self.day ) * 86400 - time.localtime().tm_gmtoff).tm_mday
    def get_month(self):
        return time.localtime((self.day) * 86400 - time.localtime().tm_gmtoff).tm_mon

class offline_data_storage: #stores user data for saving
    def __init__(self, pills, time_settings, mode, missed_doses, doses_taken, saved_day, exhaust_setting):
        self.pills = pills
        self.time_setting = time_settings
        self.mode = mode
        self.missed_doses = missed_doses
        self.doses_taken = doses_taken
        self.day = saved_day
        self.exhaust = exhaust_setting
        return

class online_settings_storage:
    def __init__(self, wifi_name, username, password):
        self.wifi_name = wifi_name
        self.username = username
        self.password = password

#Saves data into "user_data" file, called everytime data is modified
def save_offline_data():
    temp_storage = offline_data_storage(pills, time_settings, app_mode, missed_doses, dose_taken_day, saved_day, exhaust_setting)
    with open("user_data.p", "wb") as file:
        pickle.dump(temp_storage, file)
    return

#Reads data from "user_data" file, called upon application startup
def load_offline_data():
    global pills, time_settings, app_mode, dosage_info, missed_doses, dose_taken_day, saved_day, exhaust_setting
    try: #if file is found, load data
        with open("user_data.p", "rb") as file:
            temp_storage = pickle.load(file)
            pills = temp_storage.pills
            time_settings = temp_storage.time_setting
            app_mode = temp_storage.mode
            exhaust_setting = temp_storage.exhaust
            current_day = int((time.time() + time.localtime().tm_gmtoff)/ 86400)
            for entry in temp_storage.missed_doses:
                if entry.day <= current_day:
                    missed_doses.append(entry)
            dose_taken_day = temp_storage.doses_taken
            saved_day = temp_storage.day
            dosage_info = dosage_table(pills)
            update_time_thresholds()
        return True
    except FileNotFoundError: #if file is not found, create empty file
        pill_1 = pill("Aspirin", 1, 1, 2, 100, [True, True, True, True, True, True, True],[True, False, False, True], 1) #For testing only
        pill_2 = pill("Omeprazole", 2, 2, 4, 100, [False, True, True, True, True, True, False],[True, True, True, False], 2) #For testing only
        pill_3 = pill("Vitamin C", 3, 0, 1, 100, [True, True, True, True, True, True, True],[True, False, False, False], 3) #For testing only
        pills = [pill_1, pill_2, pill_3, add_pill]
        dosage_info = dosage_table(pills)
        time_settings = [day_time(8,0), day_time(12,30), day_time(17,0), day_time(21,0)]
        update_time_thresholds()
        return False
    return

def save_online_settings():
    temp_storage = online_settings
    with open("online_settings.p", "wb") as file:
        pickle.dump(temp_storage, file)
    return

def load_online_settings():
    global online_settings
    try:
        with open("online_settings.p", "rb") as file:
            temp_settings = pickle.load(file)
            online_settings.wifi_name = "" if temp_settings.wifi_name else temp_settings.wifi_name
            online_settings.username = temp_settings.username
            online_settings.password = temp_settings.password
        return True
    except FileNotFoundError:
        online_settings.wifi_name = False
        online_settings.username = False
        online_settings.password = False
        return False
    return

#Initial startup button
def start_button(): 
    global at_main, app_mode
    start_page_button.configure(command="")
    load_offline_data()
    if app_mode == 0:
        setup_page.lift()
    elif app_mode == 1:
        configure_app(True)
    elif app_mode == 2:
        start_page_button.configure(image=start_image_loading)
        start_page_message.place(relx=0.5, rely=0.75, relwidth=0.8, relheight=0.12, anchor="n")
        start_page_message.configure(text="Loading...")
        window.update_idletasks()
        if load_online_settings():
            online_status = check_internet()
            if not online_status:
                if online_settings.wifi_name:
                    if try_internet_connect(online_settings.wifi_name):
                        if check_internet():
                            online_status = True
                        else:
                            #Connected but no internet
                            wifi_message_label.configure(text=f"Connected to {online_settings.wifi_name} but no internet")
                            online_status = False
                    else:
                        #Unable to connect to specified wifi network
                        wifi_message_label.configure(text=f"Unable to connect to {online_settings.wifi_name}")
                        online_status = False
                else:
                    #No saved wifi name
                    online_status = False
            if not online_status:
                goto_wifi_page_button()
            else:
                attempt_login(online_settings.username, online_settings.password, True, False)
            configure_app(True)
        else: #Online settings file not found
            #TODO: Add error page/ disable back button for login/wifi pages
            if check_internet():
                goto_login_page_button()
            else:
                goto_wifi_page_button(True)
    return

#Modify buttons based on app_mode
def configure_app(gotomain = False):
    global app_mode
    if app_mode == 1:
        m_status_frame.place_configure(relheight=0.1)
        m_time_label.configure(font=("Trebuchet MS",16))
        m_date_label.configure(font=("Trebuchet MS",16))
        m_pill_frame.place_configure(relheight=0.225, rely=0.1)
        m_quantity_frame.place_configure(relheight=0.225, rely=0.325)
        m_history_frame.place_configure(relheight=0.225, rely=0.55)
        m_settings_frame.place_configure(relheight=0.225, rely=0.775)
        m_account_frame.place_forget()
        main_lines[0].place_configure(rely=0.1)
        main_lines[1].place_configure(rely=0.325)
        main_lines[2].place_configure(rely=0.55)
        main_lines[3].place_configure(rely=0.775)
        main_lines[4].place_forget()
        m_settings_frame.configure(bg=colours["main_account_bg"])
        m_setting_button.configure(bg=colours["main_account_bg"])
        s_wifi_button.place_forget()
        s_mode_button.place(relx=0.5, rely=0.6, relheight=0.2, relwidth=1, anchor="n")
    elif app_mode == 2:
        m_status_frame.place_configure(relheight=0.05)
        m_pill_frame.place_configure(relheight=0.19, rely=0.05)
        m_quantity_frame.place_configure(relheight=0.19, rely=0.24)
        m_history_frame.place_configure(relheight=0.19, rely=0.43)
        m_account_frame.place(relwidth=0.45, relheight=0.19, relx=1, rely=0.62, anchor="ne")
        m_settings_frame.place_configure(relheight=0.19, rely=0.81)
        main_lines[0].place_configure(rely=0.05)
        main_lines[1].place_configure(rely=0.24)
        main_lines[2].place_configure(rely=0.43)
        main_lines[3].place_configure(rely=0.62)
        main_lines[4].place(relwidth=0.45, height=2, relx=1, rely=0.81, anchor="e")
        m_settings_frame.configure(bg=colours["main_settings_bg"])
        m_setting_button.configure(bg=colours["main_settings_bg"])
        s_mode_button.place_forget()
        s_wifi_button.place(relx=0.5, rely=0.6, relheight=0.2, relwidth=1, anchor="n")
    if gotomain:
        goto_main_page_button()
    return

def check_internet():
    for tries in range(5):
        time.sleep(0.2)
        try:
            url = "https://www.google.com/"
            request.urlopen(url)
            return True
        except error.URLError:
            #Connected but no internet
            pass
    return False

def try_connect_internet(name):
    try:
        command = f'cmd /c \"netsh wlan connect ssid={name} name={name}\"'
        out = subprocess.check_output(command)
        return True
    except:
        return False
    return False

def connect_wifi(name, password):
    global online_settings, app_mode
    if name == "":
        wifi_message_label.configure(text=f"Please select a Wifi network")
        return
    online_status = False
    profiles = [line.strip()[23:] for line in subprocess.check_output(f'cmd /c \"netsh wlan show profiles\"').decode('ascii').splitlines() if line.strip().startswith("All User Profile")]
    if name not in profiles:
        if password == "":
            create_new_connection(name, password)
            if try_connect_internet(name):
                pass
            else:
                wifi_password_entry.configure(state="normal", bg=colours["wifi_entry_u"], activebackground=colours["wifi_entry_u"])
                wifi_message_label.configure(text=f"Please enter password")
                return
        else:
            create_new_connection(name, password)
    wifi_message_label.configure(text=f"Connecting...")
    if try_connect_internet(name):
        if check_internet():
            online_status = True
            wifi_message_label.configure(text=f"Connected")
            online_settings.wifi_name = name
            save_online_settings()
            if app_mode == 2:
                goto_setting_page_button()
            else:
                goto_login_page_button()
        else:
            online_status = False
            wifi_message_label.configure(text=f"Connected to {name} but no internet")
    else:
        #Unable to connect to specified wifi network
        if password == "":
            create_new_connection(name, password)
            if try_connect_internet(name):
                pass
            else:
                wifi_password_entry.configure(state="normal", bg=colours["wifi_entry_u"], activebackground=colours["wifi_entry_u"])
                wifi_message_label.configure(text=f"Please enter password")
                return
        else:
            create_new_connection(name, password)
            if check_internet():
                online_status = True
                wifi_message_label.configure(text=f"Connected")
                goto_login_page_button()
            else:
                online_status = False
                wifi_message_label.configure(text=f"Connected to {name} but no internet")
        wifi_message_label.configure(text=f"Unable to connect to {name}")
        online_status = False
    return

def create_new_connection(name, password):
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
	<name>"""+name+"""</name>
	<SSIDConfig>
		<SSID>
			<name>"""+name+"""</name>
		</SSID>
	</SSIDConfig>
	<connectionType>ESS</connectionType>
	<connectionMode>auto</connectionMode>
	<MSM>
		<security>
			<authEncryption>
				<authentication>WPA2PSK</authentication>
				<encryption>AES</encryption>
				<useOneX>false</useOneX>
			</authEncryption>
			<sharedKey>
				<keyType>passPhrase</keyType>
				<protected>false</protected>
				<keyMaterial>"""+password+"""</keyMaterial>
			</sharedKey>
		</security>
	</MSM>
</WLANProfile>"""
    command = "netsh wlan add profile filename=\""+name+".xml\""+""
    with open(name+".xml", 'w') as file:
        file.write(config)
    subprocess.run(command)
    return

#Setup page: Set up application in offline mode
def setup_offline_button_command():
    global app_mode
    app_mode = 1
    configure_app(True)
    return

#Setup page: Set up application in online mode
def setup_online_button_command():
    if check_internet():
        goto_login_page_button()
    else:
        goto_wifi_page_button()
    return

def wifi_page_update(clear):
    global wifi_networks
    if clear:
        wifi_selected.set("")
        wifi_password_entry.configure(text="", state="disabled", bg=colours["wifi_entry_d"], activebackground=colours["wifi_entry_d"])
    else:
        wifi_selected.set(online_settings.wifi_name)
    networks = subprocess.check_output(f'cmd /c \"netsh wlan show network\"').decode('ascii')
    wifi_networks = [line[line.find(":") + 2:] for line in networks.splitlines() if line.startswith("SSID")]
    wifi_name_button["menu"].delete(0, "end")
    for network in wifi_networks:
        wifi_name_button["menu"].add_command(label=network, command=tk._setit(wifi_selected, network))
    return

def goto_wifi_page_button(clear=True):
    wifi_page_update(clear)
    wifi_page.lift()
    return

def login_page_update():
    login_username_entry.configure(text=online_settings.username)
    login_username_entry.configure(text=online_settings.password)
    return

def goto_login_page_button():
    login_message_label.configure(text="")
    login_page.lift()
    return

def attempt_login(email, password, load_data, go_to_main = False):
    global user_user, app_mode, online_settings
    URL = "https://orbital-cygnus.herokuapp.com/login.php"
    PARAMS = {"email":email, "password":password}
    output = requests.post(URL, data = PARAMS).text
    if output == "Email or Password wrong":
        login_message_label.configure(text="Incorrect email or password")
        return False
    else:
        login_message_label.configure(text="Log In Successful")
        window.update_idletasks()
        data = output.split("#")
        online_settings.username = email
        online_settings.password = password
        save_online_settings()
        app_mode = 2
        save_offline_data()
        user_user.email = email
        user_user.userID = data[0]
        user_user.first_name = data[1]
        user_user.last_name = data[2]
        if load_data:
            login_message_label.configure(text="Loading Data")
            window.update_idletasks()
            load_online_data(data[0])
        if go_to_main:
            configure_app(True)
        return True
    return

def load_online_data(id):
    global pills, user_user, time_settings
    URL = "https://orbital-cygnus.herokuapp.com/pillDetails.php"
    pill_count = 0
    pills = [add_pill]
    for count in range(6):
        PARAMS = {"id":id, "container":count + 1}
        output = requests.post(URL, data = PARAMS).text.split("#")
        if output[0] != "NIL":
            URL2 = "https://orbital-cygnus.herokuapp.com/getDosage.php"
            PARAMS2 = {"id":id, "container":count + 1}
            dosage_output = requests.post(URL2, data = PARAMS2).text.split("#")
            dosage_days = [bool(int(f"{int(dosage_output[0]):07b}"[i])) for i in range(7)]
            dosage_times = [bool(int(f"{int(dosage_output[1]):04b}"[i])) for i in range(4)]
            pills.insert(pill_count,pill(output[0],count + 1,int(output[3]),int(output[2]),int(output[1]),dosage_days,dosage_times,int(dosage_output[2])))
            pill_count += 1
        else:
            pass
    URL = "https://orbital-cygnus.herokuapp.com/getTime.php"
    PARAMS = {"id":id}
    output = requests.post(URL, data = PARAMS).text.split("#")
    time_settings = [day_time(int(elem[:2]),int(elem[4:])) for elem in output]
    update_time_thresholds()
    #TODO: Load sharing emails
    return

def wifi_back_button():
    if app_mode == 0:
        setup_page.lift()
    elif app_mode == 1 or app_mode == 2:
        goto_setting_page_button()
        setting_wifi_button()
    return

def login_back_button():
    if app_mode == 0:
        goto_wifi_page_button(False)
    elif app_mode == 1:
        goto_setting_page_button()
    elif app_mode == 2:
        goto_account_page_button()
    return

def wifi_selection_change():
    wifi_password_entry.configure(text="", state="disabled", bg=colours["wifi_entry_d"], activebackground=colours["wifi_entry_d"])
    return

#Main page: Called every 5 seconds to update time in main page
def main_time_update():
    global dose_taken_day, saved_day
    temp_time = time.localtime()
    yday = temp_time.tm_yday
    temp_day = int((time.time() + time.localtime().tm_gmtoff) / 86400)
    if temp_day != saved_day:
        day_diff = temp_day - saved_day
        if (day_diff > 3):
            start_secs = int((time.time() + time.localtime().tm_gmtoff)) - 86400 * 3
            for i in range(3):
                start_time = time.localtime(start_secs)
                for j in range(4):
                    if dosage_info.has_dose((time.localtime(start_secs).tm_wday + 1) % 7,j):
                        missed_doses.append(pill_dose(int((time.time() + time.localtime().tm_gmtoff) / 86400), j))
                        if len(missed_doses) > 10:
                            missed_doses.pop(0)
                start_secs += 86400
        else:
            for i in range(4):
                if dose_taken_day[i] == 0:
                    if dosage_info.has_dose((saved_day + 5) % 7 ,i):
                        missed_doses.append(pill_dose(int((time.time() + time.localtime().tm_gmtoff) / 86400), i))
                        if len(missed_doses) > 10:
                            missed_doses.pop(0)
            if day_diff > 1:
                start_secs = int((time.time() + time.localtime().tm_gmtoff)) - 86400 * (day_diff - 1)
                for i in range(day_diff - 1):
                    start_time = time.localtime(start_secs)
                    for j in range(4):
                        if dosage_info.has_dose((time.localtime(start_secs).tm_wday + 1) % 7,j):
                            missed_doses.append(pill_dose(int((time.time() + time.localtime().tm_gmtoff) / 86400), j))
                            if len(missed_doses) > 10:
                                missed_doses.pop(0)
                    start_secs += 86400
        dose_taken_day = [0] * 4
        saved_day = temp_day
        save_offline_data()
        #Update database
    for count in range(4):
        curr_day_sec = int((time.time() + time.localtime().tm_gmtoff) % 86400)
        if dose_taken_day[count] == 0 and curr_day_sec > time_thresholds[count][1]:
            if dosage_info.has_dose((time.localtime().tm_wday + 1) % 7,count):
                dose_taken_day[count] = -1
                missed_doses.append(pill_dose(int((time.time() + time.localtime().tm_gmtoff) / 86400), count))
                if len(missed_doses) > 10:
                    missed_doses.pop(0)  
            else:
                dose_taken_day[count] = 2
            save_offline_data()
            #Update database
    if at_main == True:
        m_time_label.configure(text=time.strftime(" %H:%M"))
        m_date_label.configure(text=time.strftime("%a, %d %B"))
        exhaust = False
        for index in range(len(pills) - 1):
            if pills[index].get_exhaust_days() < exhaust_setting * 7:
                exhaust = True
            if exhaust:
                m_quantity_alert.place(relwidth = 0.2, relheight=0.5, relx=0.75, rely=0.5, anchor="w")
            else:
                m_quantity_alert.place_forget()
    m_time_label.after(5000, main_time_update)
    return

#Go to dispense page
def goto_dispense_page_button():
    global at_main
    at_main = False
    dispense_page_update()
    dispense_page.lift()
    #hardware dispense function
    return

#Go to pill page
def goto_pill_page_button():
    global at_main
    pill_page.lift()
    pill_update_pill_icons()
    at_main = False
    return

#Go to quantity page
def goto_quantity_page_button():
    global at_main
    quantity_page_update()
    quantity_page.lift()
    at_main = False
    return

#Go to history page
def goto_history_page_button():
    global at_main
    history_page_update()
    history_page.lift()
    at_main = False
    return

#Go to settings page
def goto_setting_page_button():
    global at_main
    setting_time_button()
    settings_page.lift()
    at_main = False
    return

#Go to account page
def goto_account_page_button():
    global at_main
    account_page_update()
    account_page.lift()
    account_general_button()
    at_main = False
    return

#Go to main page
def goto_main_page_button():
    global at_main
    at_main = True
    main_time_update()
    main_page.lift()
    return

#Open numpad page: 
def open_numpad_button(page, title, button, mode): #mode == 0: normal; 1: math; 2: time
    global current_entry_button, current_page, numpad_operator, numpad_mode
    numpad_mode = mode
    numpad_page.lift()
    n_entry.delete(0,"end")
    n_entry.insert(0,button.cget("text"))
    n_entry.icursor("end")
    n_title.configure(text=title)
    numpad_operator = 0
    current_entry_button = button
    current_page = page
    if mode == 1:
        n_button_special_1.configure(state="normal", text="+", command=lambda: numpad_math_button(1))
        n_button_special_2.configure(state="normal", text="−", command=lambda: numpad_math_button(-1))
    elif mode == 2:
        n_button_special_1.configure(state="normal", text=":", command=numpad_colon_button)
        n_button_special_2.configure(state="disabled", text="")
    else:
        n_button_special_1.configure(state="disabled", text="")
        n_button_special_2.configure(state="disabled", text="")
    return

#Numpad page: Writes the corresponding number to the entry bar
def numpad_type_button(number):
    n_entry.icursor("end")
    if numpad_mode == 1:
        if len(n_entry.get()) < 8:
            n_entry.insert("end", number)
        return
    elif numpad_mode == 2:
        colon_index = n_entry.get().find(":")
        if len(n_entry.get()) < colon_index + 3:
            n_entry.insert("end", number)
        return
    else:
        n_entry.insert("end", number)
    return

#Numpad page: Writes a ":" to the entry bar, only when numpad is in time mode
def numpad_colon_button():
    n_entry.icursor("end")
    n_entry_length = len(n_entry.get())
    if ":" not in n_entry.get() and n_entry_length < 6 and n_entry_length > 0:
        n_entry.insert("end", ":")
    return

#Numpad page: Backspace
def numpad_backspace_button():
    global numpad_operator
    n_entry.icursor("end")
    index = n_entry.index("end")
    if index > 0 and (n_entry.get()[index-1] == "+" or n_entry.get()[index-1] == "−"):
        numpad_operator = 0
    n_entry.delete(index-1, index) 
    return

#Numpad page: Performs math on the text in the entry bar
def numpad_math():
    global numpad_operator
    entry_string = n_entry.get()
    plus_index = entry_string.find("+")
    minus_index = entry_string.find("−")
    operator_index = max(plus_index, minus_index)
    number_1 = int(entry_string[:operator_index])
    number_2 = int(entry_string[operator_index + 1:])
    result = number_1 + number_2 if numpad_operator == 1 else number_1 - number_2 if numpad_operator == -1 else 0
    result = max(0, result)
    n_entry.delete(0,"end")
    n_entry.insert(0,result)
    numpad_operator = 0
    return result

#Numpad page: Writes either "+" or "−" to the entry bar
def numpad_math_button(type): #type == -1: minus, type == 1: plus
    global numpad_operator
    n_entry.icursor("end")
    if len(n_entry.get()) != 0:
        if numpad_operator != 0:
            numpad_math()
        n_entry.insert("end", "+" if type == 1 else "−" if type == -1 else "")
        numpad_operator = type
        n_button_enter.configure(text="=")
    return

#Numpad page: The enter button has 2 settings, when numpad is in math mode and an math operator is in the entry box, it performs the sum/difference calculation. Else, it saves the number in entry to the button that opened the numpad
def numpad_enter_button():
    global numpad_operator
    n_entry.icursor("end")
    if numpad_operator != 0:
        numpad_math()
        numpad_operator = 0
        n_button_enter.configure(text="Save")
    else:
        if numpad_mode == 2:
            time_valid = True
            if n_entry.get() != "":
                temp_string = n_entry.get()
            else:
                n_message.configure(text="Please enter a time")
                return
            colon_index = temp_string.find(":")
            temp_time = day_time(0,0)
            if colon_index == -1 or colon_index == len(temp_string) - 1:
                temp_time.hour = int(temp_string.strip(":"))
            else:
                temp_time.from_string(temp_string)
            if temp_time.is_valid():
                n_entry.delete(0,"end")
                n_entry.insert(0,temp_time.to_string())
            else:
                n_message.configure(text="Incorrect time format")
                return
        current_entry_button.configure(text=n_entry.get())
        #<especially bad code>
        if current_entry_button == pd_qty_button:
            pills[current_pill].qty = int(n_entry.get())
            save_offline_data()
            pill_detail_page_update(current_pill)
            #TODO: update charts
            if app_mode == 2:
                URL = "https://orbital-cygnus.herokuapp.com/updatePillDetails.php"
                PARAMS = {"id":user_user.userID, "container":current_pill + 1, "name":pills[current_pill].name, "quantity":pills[current_pill].qty, "colour":pills[current_pill].icon_colour, "shape":pills[current_pill].icon_shape}
                output = requests.post(URL, data = PARAMS).text
                if output == "Updated Successfully":
                    pd_message_label.configure(text="Quantity Successfully Updated!")
                else:
                    pd_message_label.configure(text="Error: Unable to update quantity.")
        #<\especially bad code>
        current_page.lift()
    return

#Numpad page: Does not save recent edits to the button that opened the numpad
def numpad_cancel_button():
    current_page.lift()
    return

#Open keyboard page: Page to return to after closing keyboard, label: Label that contains input title, button: Button that stores input text
def open_keyboard_button(page, label, button): 
    global current_entry_button, current_page
    keyboard_page.lift()
    k_entry.delete(0,"end")
    k_entry.insert(0,button.cget("text"))
    k_entry.icursor("end")
    k_title.configure(text=label.cget("text"))
    current_entry_button = button
    current_page = page
    return

#Keyboard Page: Takes in ASCII value, and bool values for CAPS and Shift, returns corresponding characeter 
def capitalise(asc, c, s):
    if (c != s) and (asc >= ord('a') and asc <= ord('z')):
        return asc - 32
    if s:
        if asc == ord('`'):
            return ord('~')
        if asc == ord('1'):
            return ord('!')
        if asc == ord('2'):
            return ord('@')
        if asc == ord('3'):
            return ord('#')
        if asc == ord('4'):
            return ord('$')
        if asc == ord('5'):
            return ord('%')
        if asc == ord('6'):
            return ord('^')
        if asc == ord('7'):
            return ord('&')
        if asc == ord('8'):
            return ord('*')
        if asc == ord('9'):
            return ord('(')
        if asc == ord('0'):
            return ord(')')
        if asc == ord('-'):
            return ord('_')
        if asc == ord('='):
            return ord('+')
        if asc == ord('['):
            return ord('{')
        if asc == ord(']'):
            return ord('}')
        if asc == ord('\\'):
            return ord('|')
        if asc == ord(';'):
            return ord(':')
        if asc == ord('\''):
            return ord('"')
        if asc == ord(','):
            return ord('<')
        if asc == ord('.'):
            return ord('>')
        if asc == ord('/'):
            return ord('?')
    return asc

#Keyboard Page: Takes in ASCII value of the key that was pressed
def keyboard_type_button(asc):
    global shift, capslock
    if shift or capslock:
        asc = capitalise(asc, capslock, shift)
    if len(k_entry.get()) < 40:
        k_entry.insert("insert", chr(asc))

    if shift:
        shift = False
        k_button_shift.configure(relief="solid")
    return

#Keyboard Page: Backspace key
def keyboard_backspace_button():
    index = k_entry.index("insert")
    k_entry.delete(index-1, index) 
    return

#Keyboard Page: Delete key
def keyboard_delete_button():
    index = k_entry.index("insert")
    k_entry.delete(index)
    return

#Keyboard Page: Clear key: clears entry field
def keyboard_clear_button():
    k_entry.delete(0, "end")
    return

#Keyboard Page: CAPS key: switches CAPSLOCK on/off
def keyboard_capslock_button():
    global capslock
    if capslock:
        k_button_caps.configure(relief="solid")
    else:
        k_button_caps.configure(relief="sunken")
    capslock = not capslock
    return

#Keyboard Page: Shift key: switches Shift on/off
def keyboard_shift_button():
    global shift
    shift = not shift
    if shift:
        k_button_shift.configure(relief="sunken")
    else:
        k_button_shift.configure(relief="solid")
    return

#Keyboard Page: Enter key: updates button that stores the input text and returns to previous page
def keyboard_enter_button():
    current_entry_button.configure(text=k_entry.get())
    current_page.lift()
    return

#Keyboard Page: Cancel key: returns to previous page, input values are lost
def keyboard_cancel_button():
    current_page.lift()
    return

def update_time_window():
    global current_window, current_day
    curr_day_sec = int(time.time() + time.localtime().tm_gmtoff) % 86400
    current_day = (time.localtime().tm_wday + 1) % 7
    for i in range(4):
        if curr_day_sec >= time_thresholds[i][0] and curr_day_sec <= time_thresholds[i][1] and dose_taken_day[i] == 0:
            current_window = i
            return
    current_window = -1
    return

#Dispense Page: Update pill icons, dosage amounts based on current time
def dispense_page_update():
    update_time_window()
    day_text = time.strftime("%A")
    times_text_list = ["Morning", "Afternoon", "Evening", "Night"]
    if current_window == -1:
        d_name_label.configure(text=f"Dispense")
    else:
        d_name_label.configure(text=f"Dispense for {day_text} {times_text_list[current_window]}")
    pills_no = len(pills) - 1
    for count in range(6):
        d_amount_frames[count].place_forget()
        if count < pills_no:
            d_amount_frames[count].place(relx=(1.04 - pills_no * 0.16) / 2 + 0.16 * count, rely=0.2, relwidth=0.12, relheight = 0.6, anchor="nw")
            d_icons[count].configure(image=pill_images_small[pills[count].get_icon_id()])
            if current_window == -1:
                d_amount_button[count].configure(text="0")
            else:
                d_amount_button[count].configure(text=dosage_info.table[count][current_day][current_window])
        else:
            d_amount_frames[count].place_forget()
    return

#Dispense Page: Increase the number of the specified pill to be dispensed by one
def dispense_page_increase_button(pill_index):
    current_amount = int(d_amount_button[pill_index].cget("text"))
    d_amount_button[pill_index].configure(text=min(current_amount + 1,5))
    return

#Dispense Page: Decrease the number of the specified pill to be dispensed by one
def dispense_page_decrease_button(pill_index):
    current_amount = int(d_amount_button[pill_index].cget("text"))
    d_amount_button[pill_index].configure(text=max(current_amount - 1,0))
    return

#Dispense Page: Dispense the specified number of pills
def dispense_dipense_button():
    global pills, dose_taken_day
    #Hardware stuff
    for i in range(len(pills) - 1):
        current_disp = int(d_amount_button[i].cget("text"))
        if current_disp != 0:
            pills[i].qty = max(pills[i].qty - current_disp, 0)
            if app_mode == 2:
                URL = "https://orbital-cygnus.herokuapp.com/updatePillDetails.php"
                PARAMS = {"id":user_user.userID, "container":i + 1, "name":pills[i].name, "quantity":pills[i].qty, "colour":pills[i].icon_colour, "shape":pills[i].icon_shape}
                output = requests.post(URL, data = PARAMS).text
                if output == "Updated Successfully":
                    pass
                else:
                    pass
    day = time.localtime().tm_wday
    if current_window != -1:
        dose_taken_day[current_window] = 1
    #Update database
    return

#Pill Page: Switches to left pill
def pill_left_nav_button():
    global current_pill
    length = len(pills)
    if length == 7:
        length = 6
    current_pill = (current_pill - 1) % length
    pill_update_pill_icons()
    return

#Pill Page: Switches to right pill
def pill_right_nav_button():
    global current_pill
    length = len(pills)
    if length == 7:
        length = 6
    current_pill = (current_pill + 1) % len(pills)
    pill_update_pill_icons()
    return

#Pill Page: Update current pill displayed on the pill navigation page
def pill_update_pill_icons():
    if current_pill !=  len(pills) - 1:
        p_pill_name_label.configure(text=f"{pills[current_pill].container}: {pills[current_pill].name}")
    else:
        first_empty = min(set(range(1,6))-set([p.container for p in pills]))
        p_pill_name_label.configure(text=f"Add Pill to Container {first_empty}")
    p_pill_button.configure(image=pill_images[pills[current_pill].get_icon_id()])
    p_message_label.configure(text="")
    return

#Pill Detail Page: Update page with current pill information 
def pill_detail_page_update(pill_index):
    pd_pill_name_button.configure(text=pills[pill_index].name)
    pd_pill_button.configure(image=pill_images_small[pills[pill_index].get_icon_id()])
    pd_qty_button.configure(text=pills[pill_index].qty)
    exhaust_date = pills[pill_index].get_exhaust_date()
    empty_date = time.strftime("%d %b %Y", exhaust_date)
    pd_empty_label.configure(text=f"Empty On {empty_date}")
    pd_container_label.configure(text=f"Stored in Container {pills[current_pill].container}")
    pd_chart_bar.place_configure(relheight=0.8 * min(1.05, pills[pill_index].get_exhaust_days() / 120))
    return

#Go to pill detail page
def goto_pill_detail_page_button(pill_index):
    global current_pill
    if pill_index != len(pills) - 1:
        pill_detail_page_update(pill_index)
        pill_detail_page.lift()
        pd_message_label.configure(text="")
    else:
        first_empty = min(set(range(1,6))-set([p.container for p in pills]))
        pills.insert(first_empty - 1,pill("New Pill",first_empty,0,0,0,[True,True,True,True,True,True,True],[True,False,False,False],1))
        current_pill = first_empty - 1
        if app_mode == 2:
            URL = "https://orbital-cygnus.herokuapp.com/updatePillDetails.php"
            PARAMS = {"id":user_user.userID, "container":current_pill + 1, "name":pills[current_pill].name, "quantity":pills[current_pill].qty, "colour":pills[current_pill].icon_colour, "shape":pills[current_pill].icon_shape}
            output = requests.post(URL, data = PARAMS).text
            if output == "Updated Successfully":
                p_message_label.configure(text="Pill Successfully Created!")
            else:
                p_message_label.configure(text="Error: Unable to create pill.")
                return
            URL = "https://orbital-cygnus.herokuapp.com/addDosage.php"
            PARAMS = {"id":user_user.userID, "container":current_pill + 1, "dosagedays":127, "dosagetimes":8, "dosageamount":1, "shape":pills[current_pill].icon_shape}
            output = requests.post(URL, data = PARAMS).text
            if output == "Added Successfully":
                p_message_label.configure(text="Pill Successfully Created!")
            else:
                p_message_label.configure(text="Error: Unable to create pill.")
                return
        dosage_info.add_pill(pills[current_pill])
        goto_pill_edit_page_button()
        pill_edit_pill_edit_button()
    return

#Pill Edit Page: Enable pill icon buttons
def pill_edit_page_icons_enable(shape_id, colour_id):
    pe_icon_shape_buttons[0].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(0))
    pe_icon_shape_buttons[1].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(1))
    pe_icon_shape_buttons[2].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(2))
    pe_icon_shape_buttons[3].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(3))
    pe_icon_shape_buttons[4].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(4))
    pe_icon_shape_buttons[5].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(5))
    pe_icon_shape_buttons[6].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_shape_button(6))
    pe_icon_shape_buttons[shape_id].configure(relief="sunken", bg=colours["pe_content_entry"], activebackground=colours["pe_content_entry"], borderwidth=2)
    
    pe_icon_colour_buttons[0].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_colour_button(0))
    pe_icon_colour_buttons[1].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_colour_button(1))
    pe_icon_colour_buttons[2].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_colour_button(2))
    pe_icon_colour_buttons[3].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_colour_button(3))
    pe_icon_colour_buttons[4].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_colour_button(4))
    pe_icon_colour_buttons[5].configure(relief="flat", bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], borderwidth=2, command=lambda:pill_edit_pill_colour_button(5))
    pe_icon_colour_buttons[colour_id].configure(relief="sunken", bg=colours["pe_content_entry"], activebackground=colours["pe_content_entry"], borderwidth=2)

    return

#Pill Edit Page: Disable pill icon buttons
def pill_edit_page_icons_disable(shape_id, colour_id):
    for i in range(7):
        if i == shape_id:
            pe_icon_shape_buttons[i].configure(relief="sunken", bg=colours["pe_content_entry"], activebackground=colours["pe_content_entry"], borderwidth=2, command="")
        else:
            pe_icon_shape_buttons[i].configure(relief="sunken", bg=colours["pe_content_bg"], activebackground=colours["pe_content_bg"], borderwidth=0, command="")
    for i in range(6):
        if i == colour_id:
            pe_icon_colour_buttons[i].configure(relief="sunken", bg=colours["pe_content_entry"], activebackground=colours["pe_content_entry"], borderwidth=2, command="")
        else:
            pe_icon_colour_buttons[i].configure(relief="sunken", bg=colours["pe_content_bg"], activebackground=colours["pe_content_bg"], borderwidth=0, command="")
    return

#Pill Edit Page: Update page with current_pill's information
def pill_edit_page_update():
    pe_pill_name_button.configure(text=pills[current_pill].name)
    pe_icon_button.configure(image=pill_images_small[pills[current_pill].get_icon_id()])
    return

#Go to Pill Edit Page
def goto_pill_edit_page_button():
    pill_edit_page_update()
    pill_edit_page_icons_disable(pills[current_pill].icon_shape, pills[current_pill].icon_colour)
    pill_edit_page.lift()
    pill_edit_pill_button()
    return

#Pill Edit Page: Enable editing of pill information, namely, pill name, icon_colour and icon_shape
def pill_edit_pill_edit_button():
    global temp_pill, pe_editing
    pe_pill_edit_button.configure(state="disabled")
    pe_pill_save_button.configure(state="normal")
    pe_pill_cancel_button.configure(state="normal")
    pe_pill_name_button.configure(state="normal", cursor="xterm")
    temp_pill.name = pills[current_pill].name
    temp_pill.icon_colour = pills[current_pill].icon_colour
    temp_pill.icon_shape = pills[current_pill].icon_shape
    pill_edit_page_icons_enable(pills[current_pill].icon_shape, pills[current_pill].icon_colour)
    pe_editing = True
    return

#Pill Edit Page: Save changes to pill information
def pill_edit_pill_save_button():
    global pe_editing
    pe_pill_edit_button.configure(state="normal")
    pe_pill_save_button.configure(state="disabled")
    pe_pill_cancel_button.configure(state="disabled")
    temp_pill.name = pe_pill_name_button.cget("text")
    pills[current_pill].name = temp_pill.name
    pills[current_pill].icon_colour = temp_pill.icon_colour
    pills[current_pill].icon_shape = temp_pill.icon_shape
    save_offline_data()
    pe_pill_name_button.configure(state="disabled", cursor="left_ptr", text=pills[current_pill].name)
    pill_edit_page_icons_disable(pills[current_pill].icon_shape, pills[current_pill].icon_colour)
    pe_pill_message_label.configure(text="")
    pe_editing = False
    if app_mode == 2:
        URL = "https://orbital-cygnus.herokuapp.com/updatePillDetails.php"
        PARAMS = {"id":user_user.userID, "container":current_pill + 1, "name":pills[current_pill].name, "quantity":pills[current_pill].qty, "colour":pills[current_pill].icon_colour, "shape":pills[current_pill].icon_shape}
        output = requests.post(URL, data = PARAMS).text
        if output == "Updated Successfully":
            pe_pill_message_label.configure(text="Updated Successfully!")
        else:
            pe_pill_message_label.configure(text="Error: Unable to save changes")
            #TODO: Error handling
    return

#Pill Edit Page: Discard changes to pill information
def pill_edit_pill_cancel_button():
    global pe_editing
    pe_pill_edit_button.configure(state="normal")
    pe_pill_save_button.configure(state="disabled")
    pe_pill_cancel_button.configure(state="disabled")
    pe_pill_name_button.configure(state="disabled", cursor="left_ptr", text=pills[current_pill].name)
    pill_edit_page_icons_disable(pills[current_pill].icon_shape, pills[current_pill].icon_colour)
    pe_icon_button.configure(image=pill_images_small[pills[current_pill].get_icon_id()])
    pe_pill_message_label.configure(text="")
    pe_editing = False
    return

#Pill Edit Page: Set pill_shape to the corresponding shape_id
def pill_edit_pill_shape_button(shape_id):
    global temp_pill
    pe_icon_shape_buttons[temp_pill.icon_shape].configure(relief="flat", bg=colours["pe_content_bg"])
    temp_pill.icon_shape = shape_id
    pe_icon_shape_buttons[shape_id].configure(relief="sunken", bg=colours["pe_content_entry"])
    pe_icon_button.configure(image=pill_images_small[temp_pill.get_icon_id()])
    return

#Pill Edit Page: Set pill_colour to the corresponding colour_id
def pill_edit_pill_colour_button(colour_id):
    global temp_pill
    pe_icon_colour_buttons[temp_pill.icon_colour].configure(relief="flat", bg=colours["pe_content_bg"])
    temp_pill.icon_colour = colour_id
    pe_icon_colour_buttons[colour_id].configure(relief="sunken", bg=colours["pe_content_entry"])
    pe_icon_button.configure(image=pill_images_small[temp_pill.get_icon_id()])
    return

#Pill Edit Page: Update schedule page's day buttons with dosage_days information
def pill_edit_schedule_day_buttons_update(day, dosage_days):
    if dosage_days[day]:
        pe_schedule_days_buttons[day].configure(relief="sunken", bg=colours["pe_content_entry"], borderwidth=2)
    else:
        pe_schedule_days_buttons[day].configure(relief="ridge", bg=colours["pe_content_bg"], borderwidth=2)
    return

#Pill Edit Page: Update schedule page's time buttons with dosage_times information
def pill_edit_schedule_time_buttons_update(time, dosage_times):
    if dosage_times[time]:
        pe_schedule_times_buttons[time].configure(relief="sunken", bg=colours["pe_content_entry"], borderwidth=2)
    else:
        pe_schedule_times_buttons[time].configure(relief="ridge", bg=colours["pe_content_bg"], borderwidth=2)
    return

#Pill Edit Page: Toggles specified day setting value
def pill_edit_schedule_days_button(day):
    global temp_pill
    temp_pill.dosage_days[day] = not temp_pill.dosage_days[day]
    pill_edit_schedule_day_buttons_update(day, temp_pill.dosage_days)
    return

#Pill Edit Page: Toggles specified time setting value
def pill_edit_schedule_times_button(time):
    global temp_pill
    temp_pill.dosage_times[time] = not temp_pill.dosage_times[time]
    pill_edit_schedule_time_buttons_update(time, temp_pill.dosage_times)
    return

#Pill Edit Page: Enables buttons
def pill_edit_schedule_buttons_enable():
    pe_schedule_days_buttons[0].configure(command=lambda:pill_edit_schedule_days_button(0))
    pe_schedule_days_buttons[1].configure(command=lambda:pill_edit_schedule_days_button(1))
    pe_schedule_days_buttons[2].configure(command=lambda:pill_edit_schedule_days_button(2))
    pe_schedule_days_buttons[3].configure(command=lambda:pill_edit_schedule_days_button(3))
    pe_schedule_days_buttons[4].configure(command=lambda:pill_edit_schedule_days_button(4))
    pe_schedule_days_buttons[5].configure(command=lambda:pill_edit_schedule_days_button(5))
    pe_schedule_days_buttons[6].configure(command=lambda:pill_edit_schedule_days_button(6))
    
    pe_schedule_times_buttons[0].configure(command=lambda:pill_edit_schedule_times_button(0))
    pe_schedule_times_buttons[1].configure(command=lambda:pill_edit_schedule_times_button(1))
    pe_schedule_times_buttons[2].configure(command=lambda:pill_edit_schedule_times_button(2))
    pe_schedule_times_buttons[3].configure(command=lambda:pill_edit_schedule_times_button(3))

    pe_schedule_amount_decrease_button.configure(command=pill_edit_schedule_amount_decrease)
    pe_schedule_amount_increase_button.configure(command=pill_edit_schedule_amount_increase)

    return

#Pill Edit Page: Disables buttons
def pill_edit_schedule_buttons_disable():
    for count in range(7):
        pe_schedule_days_buttons[count].configure(command="")
    for count in range(4):
        pe_schedule_times_buttons[count].configure(command="")
    pe_schedule_amount_decrease_button.configure(command="")
    pe_schedule_amount_increase_button.configure(command="")
    return

#Pill Edit Page: Decrease the standard dosage amount for the current pill (max of 5)
def pill_edit_schedule_amount_decrease():
    global temp_pill
    if temp_pill.dosage_amount > 1:
        temp_pill.dosage_amount -= 1
    pe_schedule_amount_button.configure(text=temp_pill.dosage_amount)
    return

#Pill Edit Page: Increase the standard dosage amount for the current pill
def pill_edit_schedule_amount_increase():
    global temp_pill
    if temp_pill.dosage_amount < 5:
        temp_pill.dosage_amount += 1
    pe_schedule_amount_button.configure(text=temp_pill.dosage_amount)
    return

#Pill Edit Page: Enables editing of pill schedule information
def pill_edit_schedule_edit_button():
    global temp_pill, pe_editing
    pe_schedule_edit_button.configure(state="disabled")
    pe_schedule_save_button.configure(state="normal")
    pe_schedule_cancel_button.configure(state="normal")
    for count in range(7):
        temp_pill.dosage_days[count] = pills[current_pill].dosage_days[count]
    for count in range(4):
        temp_pill.dosage_times[count] = pills[current_pill].dosage_times[count]
    temp_pill.dosage_amount = pills[current_pill].dosage_amount
    pill_edit_schedule_buttons_enable()
    pe_editing = True
    return

#Pill Edit Page: Save changes to schedule information
def pill_edit_schedule_save_button():
    global pe_editing
    if sum(temp_pill.dosage_days) == 0:
        if sum(temp_pill.dosage_times) == 0:
            pe_schedule_message_label.configure(text="Please select at least 1 time and 1 day.")
        else:
            pe_schedule_message_label.configure(text="Please select at least 1 day.")
    else:
        if sum(temp_pill.dosage_times) == 0:
            pe_schedule_message_label.configure(text="Please select at least 1 time.")
        else:
            pe_schedule_edit_button.configure(state="normal")
            pe_schedule_save_button.configure(state="disabled")
            pe_schedule_cancel_button.configure(state="disabled")
            for count in range(7):
                pills[current_pill].dosage_days[count] = temp_pill.dosage_days[count]
            for count in range(4):
                pills[current_pill].dosage_times[count] = temp_pill.dosage_times[count]
            pills[current_pill].dosage_amount = temp_pill.dosage_amount
            dosage_info.update_single(pills[current_pill],current_pill)
            save_offline_data()
            pill_edit_schedule_buttons_disable()
            pe_schedule_message_label.configure(text="")
            pe_editing = False
            if app_mode == 2:
                URL = "https://orbital-cygnus.herokuapp.com/addDosage.php"
                dosagedays = 0
                for dosage in pills[current_pill].dosage_days:
                    dosagedays = dosagedays * 2 + int(dosage)
                dosagetimes = 0
                for dosage in pills[current_pill].dosage_times:
                    dosagetimes = dosagetimes * 2 + int(dosage)
                PARAMS = {"id":user_user.userID, "container":current_pill + 1, "dosagedays": dosagedays, "dosagetimes": dosagetimes, "dosageamount":pills[current_pill].dosage_amount}
                output = requests.post(URL, data = PARAMS).text
                if output == "Added Successfully":
                    pe_schedule_message_label.configure(text="Updated Successfully!")
                else:
                    pe_schedule_message_label.configure(text="Error: Unable to save changes.")
                #TODO: Error handling
    return

#Pill Edit Page: Discard changes to schedule information
def pill_edit_schedule_cancel_button():
    global pe_editing
    pe_schedule_edit_button.configure(state="normal")
    pe_schedule_save_button.configure(state="disabled")
    pe_schedule_cancel_button.configure(state="disabled")
    pe_schedule_amount_button.configure(text=pills[current_pill].dosage_amount)
    for count in range(7):
        pill_edit_schedule_day_buttons_update(count, pills[current_pill].dosage_days)
    for count in range(4):
        pill_edit_schedule_time_buttons_update(count, pills[current_pill].dosage_times)
    pill_edit_schedule_buttons_disable()
    pe_schedule_message_label.configure(text="")
    pe_editing = False
    return

#Pill Edit Page: Delete current pill
def pill_edit_delete_delete_button():
    pe_delete_delete_button.configure(state="disabled")
    pe_delete_confirm_button.configure(state="normal")
    pe_delete_message_label.configure(text=f"Confirm deletion of {pills[current_pill].name}?\nThis cannot be undone.")
    return

#Pill Edit Page: Confirm deletion of current pill
def pill_edit_delete_confirm_button():
    name = pills[current_pill].name
    pills.pop(current_pill)
    dosage_info.delete_pill(current_pill)
    save_offline_data()
    message = f"{name} deleted sucessfully."
    if app_mode == 2:
        URL = "https://orbital-cygnus.herokuapp.com/clearContainer.php"
        PARAMS = {"id":user_user.userID, "container":current_pill + 1}
        output = requests.post(URL, data = PARAMS).text
        if output == "Cleared Successfully":
            pass
        else:
            message = f"Error: Unable to delete {name}."
    goto_pill_page_button()
    p_message_label.configure(text=message)
    return

#Pill Edit Page: Go back to pill details page
def pill_edit_back_button():
    if pe_editing == False:
        goto_pill_detail_page_button(current_pill)
        return
    if current_pe_page == 0:
        pe_pill_message_label.configure(text="Would you like to save recent changes?")
        return
    if current_pe_page == 1:
        pe_schedule_message_label.configure(text="Would you like to save recent changes?")
    return

#Pill Edit page: Go to pill information subpage
def pill_edit_pill_button():
    global current_pe_page
    if pe_editing == False:
        pe_pill_button.configure(bg=colours["pe_menu_bn_p"])
        pe_schedule_button.configure(bg=colours["pe_menu_bn_u"])
        pe_delete_button.configure(bg=colours["pe_menu_bn_u"])
        current_pe_page = 0
        pe_pill_message_label.configure(text="")
        pe_pill_frame.lift()
        return
    if current_pe_page == 1:
        pe_schedule_message_label.configure(text="Would you like to save recent changes?")
    return

#Pill Edit Page: Go to pill schedule subpage
def pill_edit_schedule_button():
    global current_pe_page
    if pe_editing == False:
        pe_pill_button.configure(bg=colours["pe_menu_bn_u"])
        pe_schedule_button.configure(bg=colours["pe_menu_bn_p"])
        pe_delete_button.configure(bg=colours["pe_menu_bn_u"])
        pe_schedule_amount_button.configure(text=pills[current_pill].dosage_amount)
        for count in range(7):
            pill_edit_schedule_day_buttons_update(count, pills[current_pill].dosage_days)
        for count in range(4):
            pill_edit_schedule_time_buttons_update(count, pills[current_pill].dosage_times)
        current_pe_page = 1
        pe_schedule_pill_icon.configure(image=pill_images_small[pills[current_pill].get_icon_id()])
        pe_schedule_message_label.configure(text="")
        pe_schedule_frame.lift()
        return
    if current_pe_page == 0:
        pe_pill_message_label.configure(text="Would you like to save recent changes?")
    return

#Pill Edit Page: Go to pill delete subpage
def pill_edit_delete_button():
    global current_pe_page
    if pe_editing == False:
        pe_pill_button.configure(bg=colours["pe_menu_bn_u"])
        pe_schedule_button.configure(bg=colours["pe_menu_bn_u"])
        pe_delete_button.configure(bg=colours["pe_menu_bn_p"])
        pe_delete_label.configure(text=f"Delete {pills[current_pill].name}? This cannot be undone.")
        pe_delete_message_label.configure(text="")
        pe_delete_delete_button.configure(state="normal")
        pe_delete_confirm_button.configure(state="disabled")
        current_pe_page = 2
        pe_delete_pill_icon.configure(image=pill_images_small[pills[current_pill].get_icon_id()])
        pe_delete_frame.lift()
        return
    if current_pe_page == 0:
        pe_pill_message_label.configure(text="Would you like to save recent changes?")
        return
    if current_pe_page == 1:
        pe_schedule_message_label.configure(text="Would you like to save recent changes?")
    return

#
def pill_dispenser_open(index):
    #TODO hardware
    return

#Quantity Page: Updates information in quantity page
def quantity_page_update():
    for count in range(6):
        q_chart_bars[count].place_forget()
        if count < len(pills) - 1:
            q_chart_bars[count].place(relx=0.23 + 0.13 * count, rely=0.7, relheight = 0.8 * min(1.05, pills[count].get_exhaust_days() / 120), relwidth=0.08, anchor="sw")
            q_chart_icons[count].configure(image=pill_images_tiny[pills[count].get_icon_id()])
            q_chart_qty_labels[count].configure(text=pills[count].qty)
        else:
            q_chart_icons[count].configure(image="")
            q_chart_qty_labels[count].configure(text="")
    return

#History Page: Updates information in history page
def history_page_update():
    for i in range(5):
        if i < len(missed_doses):
            temp=missed_doses[-i-1]
            h_list_entry_day_labels[i].configure(text=f" {day_list[temp.get_day()]}, {temp.get_date()} {mon_list[temp.get_month() - 1]}")
            h_list_entry_time_labels[i].configure(text=f"  {time_list[temp.time]}")
            for j in range(5):
                if j < len(pills) - 1:
                    h_list_entry_pill_labels[i][j].configure(text=f"{dosage_info.table[j][temp.get_day()][temp.time]} × ", image=pill_images_tiny[pills[j].get_icon_id()])
                else:
                    h_list_entry_pill_labels[i][j].configure(text="", image="")
        else:
            h_list_entry_day_labels[i].configure(text="")
            h_list_entry_time_labels[i].configure(text="")
            for j in range(6):
                h_list_entry_pill_labels[i][j].configure(text="", image="")
    return

#Account Page: Update page with user details
def account_page_update():
    a_email_button.configure(text=user_user.email)
    a_userID_button.configure(text=user_user.userID)
    a_first_name_button.configure(text=user_user.first_name)
    a_last_name_button.configure(text=user_user.last_name)
    a_sharing_user1_button.configure(text=user_user.share_user1)
    a_sharing_user2_button.configure(text=user_user.share_user2)
    a_sharing_user3_button.configure(text=user_user.share_user3)
    return

#Account Page: Return to main page
def account_back_button():
    if a_editing == False:
        goto_main_page_button()
        return
    if current_a_page == 0:
        a_general_message.configure(text="Would you like to save recent changes?")
        return
    if current_a_page == 1:
        a_sharing_message.configure(text="Would you like to save recent changes?")
    return

#Account Page: Go to general account settings subpage
def account_general_button():
    global current_a_page
    if a_editing == False:
        a_general_button.configure(background=colours["a_menu_bn_p"])
        a_sharing_button.configure(background=colours["a_menu_bn_u"])
        a_password_button.configure(background=colours["a_menu_bn_u"])
        a_logout_button.configure(background=colours["a_menu_bn_u"])
        current_a_page = 0
        a_general_frame.lift()
        return
    if current_a_page == 1:
        a_sharing_message.configure(text="Would you like to save recent changes?")
    return

#Account Page: Go to account sharing settings subpage
def account_sharing_button():
    global current_a_page
    if a_editing == False:
        a_general_button.configure(background=colours["a_menu_bn_u"])
        a_sharing_button.configure(background=colours["a_menu_bn_p"])
        a_password_button.configure(background=colours["a_menu_bn_u"])
        a_logout_button.configure(background=colours["a_menu_bn_u"])
        current_a_page = 1
        a_sharing_frame.lift()
        return
    if current_a_page == 0:
        a_general_message.configure(text="Would you like to save recent changes?")
    return

#Account Page: Go to sccount password settings subpage
def account_password_button():
    global current_a_page
    if a_editing == False:
        a_general_button.configure(background=colours["a_menu_bn_u"])
        a_sharing_button.configure(background=colours["a_menu_bn_u"])
        a_password_button.configure(background=colours["a_menu_bn_p"])
        a_logout_button.configure(background=colours["a_menu_bn_u"])
        current_a_page = 2
        a_password_frame.lift()
        return
    if current_a_page == 0:
        a_general_message.configure(text="Would you like to save recent changes?")
        return
    if current_a_page == 1:
        a_sharing_message.configure(text="Would you like to save recent changes?")
    return

#Account Page: Go to logout subpage
def account_logout_button():
    global current_a_page
    if a_editing == False:
        a_general_button.configure(background=colours["a_menu_bn_u"])
        a_sharing_button.configure(background=colours["a_menu_bn_u"])
        a_password_button.configure(background=colours["a_menu_bn_u"])
        a_logout_button.configure(background=colours["a_menu_bn_p"])
        current_a_page = 3
        a_logout_frame.lift()
        a_logout_confirm_button.configure(state="disabled")
        a_logout_logout_button.configure(state="normal")
        a_logout_message.configure(text="")
        return
    if current_a_page == 0:
        a_general_message.configure(text="Would you like to save recent changes?")
        return
    if current_a_page == 1:
        a_sharing_message.configure(text="Would you like to save recent changes?")
    return

#Account Page: Enables editing of general account information
def account_general_edit_button():
    global temp_user, a_editing
    a_general_edit_button.configure(state="disabled")
    a_general_save_button.configure(state="normal")
    a_general_cancel_button.configure(state="normal")
    a_first_name_button.configure(state="normal", cursor="xterm")
    a_last_name_button.configure(state="normal", cursor="xterm")
    temp_user.first_name = a_first_name_button.cget("text")
    temp_user.last_name = a_last_name_button.cget("text")
    a_editing = True
    return

#Account Page: Saves changes to general account information
def account_general_save_button():
    global a_editing
    a_general_edit_button.configure(state="normal")
    a_general_save_button.configure(state="disabled")
    a_general_cancel_button.configure(state="disabled")
    a_first_name_button.configure(state="disabled", cursor="left_ptr")
    a_last_name_button.configure(state="disabled", cursor="left_ptr")
    a_editing = False
    a_general_message.configure(text="")
    if app_mode == 2:
        #Update database
        URL = "https://orbital-cygnus.herokuapp.com/updateName.php"
        PARAMS = {"id":user_user.userID, "firstname":a_first_name_button.cget("text"), "lastname":a_last_name_button.cget("text")}
        output = requests.post(URL, data = PARAMS).text
        if output == "Updated Successfully":
            a_general_message.configure(text="Updated Successfully!")
        else:
            a_general_message.configure(text="Error: Unable to save changes")
            a_first_name_button.configure(text=temp_user.first_name)
            a_last_name_button.configure(text=temp_user.last_name)
        pass
    return

#Account Page: Discards changes to general account information
def account_general_cancel_button():
    global a_editing
    a_general_edit_button.configure(state="normal")
    a_general_save_button.configure(state="disabled")
    a_general_cancel_button.configure(state="disabled")
    a_first_name_button.configure(state="disabled", cursor="left_ptr", text=temp_user.first_name)
    a_last_name_button.configure(state="disabled", cursor="left_ptr", text=temp_user.last_name)
    a_editing = False
    a_general_message.configure(text="")
    return

#Account Page: Enables editing of account sharing information
def account_sharing_edit_button():
    global temp_user, a_editing
    a_sharing_edit_button.configure(state="disabled")
    a_sharing_save_button.configure(state="normal")
    a_sharing_cancel_button.configure(state="normal")
    a_sharing_user1_button.configure(state="normal", cursor="xterm")
    a_sharing_user2_button.configure(state="normal", cursor="xterm")
    a_sharing_user3_button.configure(state="normal", cursor="xterm")
    temp_user.share_user1 = a_sharing_user1_button.cget("text")
    temp_user.share_user2 = a_sharing_user2_button.cget("text")
    temp_user.share_user3 = a_sharing_user3_button.cget("text")
    a_editing = True
    return

#Account Page: Saves changes to account sharing information
def account_sharing_save_button():
    global a_editing
    a_sharing_edit_button.configure(state="normal")
    a_sharing_save_button.configure(state="disabled")
    a_sharing_cancel_button.configure(state="disabled")
    a_sharing_user1_button.configure(state="disabled", cursor="left_ptr")
    a_sharing_user2_button.configure(state="disabled", cursor="left_ptr")
    a_sharing_user3_button.configure(state="disabled", cursor="left_ptr")
    a_editing = False
    a_sharing_message.configure(text="")
    #Update database
    return

#Account Page: Discards changes to account sharing information
def account_sharing_cancel_button():
    global a_editing
    a_sharing_edit_button.configure(state="normal")
    a_sharing_save_button.configure(state="disabled")
    a_sharing_cancel_button.configure(state="disabled")
    a_sharing_user1_button.configure(state="disabled", cursor="left_ptr", text=temp_user.share_user1)
    a_sharing_user2_button.configure(state="disabled", cursor="left_ptr", text=temp_user.share_user2)
    a_sharing_user3_button.configure(state="disabled", cursor="left_ptr", text=temp_user.share_user3)
    a_editing = False
    a_sharing_message.configure(text="")
    return

#Account Page: Change password
def account_password_change_button():
    global online_settings
    current_password = a_password_current_button.cget("text")
    new_password = a_password_new_button.cget("text")
    confirm_password = a_password_new_button.cget("text")
    if new_password != confirm_password:
        a_password_message.configure(text="Password does not match.")
    URL = "https://orbital-cygnus.herokuapp.com/checkPass.php"
    PARAMS = {"id":user_user.userID, "password":current_password}
    output = requests.post(URL, data = PARAMS).text
    if output == "Password Match":
        URL = "https://orbital-cygnus.herokuapp.com/updatePass.php"
        PARAMS = {"id":user_user.userID, "password":new_password}
        output = requests.post(URL, data = PARAMS).text
        if output == "Changed Successfully":
            a_password_message.configure(text="Password changed successfully!")
            a_password_current_button.configure(text="")
            a_password_new_button.configure(text="")
            a_password_confirm_button.configure(text="")
            online_settings.password = new_password
            save_online_settings()
        else:
            a_password_message.configure(text="Error: Unable to change password.")
    else:
        a_password_message.configure(text="Incorrect password.")
    return

#Account Page: Cancel password change
def account_password_cancel_button():
    a_password_current_button.configure(text="")
    a_password_new_button.configure(text="")
    a_password_confirm_button.configure(text="")
    return

#Account Page: Logout from current account
def account_logout_logout_button():
    a_logout_confirm_button.configure(state="normal")
    a_logout_logout_button.configure(state="disabled")
    a_logout_message.configure(text="Confirm logout?")
    return

#Account Page: Confirm logout
def account_logout_confirm_button():
    global app_mode, online_settings
    app_mode = 1
    save_offline_data()
    online_settings.username = ""
    online_settings.password = ""
    save_online_settings()
    configure_app(True)
    return

#Setting Page: Go back to main page
def setting_back_button():
    if s_editing == False:
        goto_main_page_button()
        return
    if current_s_page == 0:
        s_time_message.configure(text="Would you like to save recent changes?")
    if current_s_page == 1:
        s_notificaton_message.configure(text="Would you like to save recent changes?")
    return

#Setting Page: Go to time subpage
def setting_time_button():
    global current_s_page
    if s_editing == False:
        current_s_page = 0
        s_time_morning_button.configure(text=time_settings[0].to_string())
        s_time_afternoon_button.configure(text=time_settings[1].to_string())
        s_time_evening_button.configure(text=time_settings[2].to_string())
        s_time_night_button.configure(text=time_settings[3].to_string())
        s_time_frame.lift()
        s_time_button.configure(bg=colours["s_menu_bn_p"])
        s_notification_button.configure(bg=colours["s_menu_bn_u"])
        s_wifi_button.configure(bg=colours["s_menu_bn_u"])
        s_mode_button.configure(bg=colours["s_menu_bn_u"])
        s_time_message.configure(text="")
        return
    if current_s_page == 1:
        s_notificaton_message.configure(text="Would you like to save recent changes?")
    return

#Setting Page: Go to notification subpage
def setting_notification_button():
    global current_s_page
    if s_editing == False:
        current_s_page = 1
        s_wifi_button.configure(bg=colours["s_menu_bn_u"])
        s_notification_button.configure(bg=colours["s_menu_bn_p"])
        s_time_button.configure(bg=colours["s_menu_bn_u"])
        s_mode_button.configure(bg=colours["s_menu_bn_u"])
        s_exhaust_weeks.set(exhaust_setting)
        s_notification_frame.lift()
        return
    if current_s_page == 0:
        s_time_message.configure(text="Would you like to save recent changes?")
        return
    return

#Setting Page: Go to wifi subpage
def setting_wifi_button():
    global current_s_page
    if s_editing == False:
        current_s_page = 2
        s_wifi_button.configure(bg=colours["s_menu_bn_p"])
        s_notification_button.configure(bg=colours["s_menu_bn_u"])
        s_time_button.configure(bg=colours["s_menu_bn_u"])
        s_wifi_wifi_button.configure(text=online_settings.wifi_name)
        s_wifi_frame.lift()
        return
    if current_s_page == 0:
        s_time_message.configure(text="Would you like to save recent changes?")
    return

#Setting Page: Go to mode subpage
def setting_mode_button():
    global current_s_page
    if s_editing == False:
        current_s_page = 2
        s_mode_button.configure(bg=colours["s_menu_bn_p"])
        s_notification_button.configure(bg=colours["s_menu_bn_u"])
        s_time_button.configure(bg=colours["s_menu_bn_u"])
        s_mode_configure_button.configure(state="normal")
        s_mode_confirm_button.configure(state="disabled")
        s_mode_message.configure(text="")
        s_mode_frame.lift()
        return
    if current_s_page == 0:
        s_time_message.configure(text="Would you like to save recent changes?")
    return

def setting_mode_configure_button():
    s_mode_configure_button.configure(state="disabled")
    s_mode_confirm_button.configure(state="normal")
    s_mode_message.configure(text="Confirm change of app mode? This can be undone.")
    return

#Updates time_thresholds 2D array to store the lower and upper bounds of the time windows. I.e. if morning is set to 0830H, time_thresholds[0] will contain [0800, 0900] when time_margin = 30. Function called when time settings are updated
def update_time_thresholds():
    global time_thresholds
    for i in range(4):
        time_thresholds[i][0] = max(time_settings[i].hour * 3600 + time_settings[i].minute * 60 - time_margin[0] * 60, 0)
        time_thresholds[i][1] = min(time_settings[i].hour * 3600 + time_settings[i].minute * 60 + time_margin[1] * 60, 86399)
    return

#Setting Page: Enables editing of time settings
def setting_time_edit_button():
    global temp_user, s_editing
    s_time_edit_button.configure(state="disabled")
    s_time_save_button.configure(state="normal")
    s_time_cancel_button.configure(state="normal")
    s_time_morning_button.configure(state="normal", cursor="xterm")
    s_time_afternoon_button.configure(state="normal", cursor="xterm")
    s_time_evening_button.configure(state="normal", cursor="xterm")
    s_time_night_button.configure(state="normal", cursor="xterm")
    temp_times[0] = s_time_morning_button.cget("text")
    temp_times[1] = s_time_afternoon_button.cget("text")
    temp_times[2] = s_time_evening_button.cget("text")
    temp_times[3] = s_time_night_button.cget("text")
    s_editing = True
    return

#Settings Page: Saves changes to time settings
def setting_time_save_button():
    global s_editing, time_settings
    s_time_edit_button.configure(state="normal")
    s_time_save_button.configure(state="disabled")
    s_time_cancel_button.configure(state="disabled")
    s_time_morning_button.configure(state="disabled", cursor="left_ptr")
    s_time_afternoon_button.configure(state="disabled", cursor="left_ptr")
    s_time_evening_button.configure(state="disabled", cursor="left_ptr")
    s_time_night_button.configure(state="disabled", cursor="left_ptr")
    time_settings[0].from_string(s_time_morning_button.cget("text"))
    time_settings[1].from_string(s_time_afternoon_button.cget("text"))
    time_settings[2].from_string(s_time_evening_button.cget("text"))
    time_settings[3].from_string(s_time_night_button.cget("text"))
    update_time_thresholds()
    save_offline_data()
    s_editing = False
    s_time_message.configure(text="")
    if app_mode == 2:
        URL = "https://orbital-cygnus.herokuapp.com/addTime.php"
        PARAMS = {"id":user_user.userID, "mTime":time_settings[0].to_string(), "aTime":time_settings[1].to_string(), "eTime":time_settings[2].to_string(), "nTime":time_settings[3].to_string()}
        output = requests.post(URL, data = PARAMS).text
        if output == "Added Successfully":
            s_time_message.configure(text="Settings updated successfully!")
    #Update database
    return

#Setting Page: Discards changes to time settings
def setting_time_cancel_button():
    global s_editing
    s_time_edit_button.configure(state="normal")
    s_time_save_button.configure(state="disabled")
    s_time_cancel_button.configure(state="disabled")
    s_time_morning_button.configure(state="disabled", cursor="left_ptr", text=temp_times[0])
    s_time_afternoon_button.configure(state="disabled", cursor="left_ptr", text=temp_times[1])
    s_time_evening_button.configure(state="disabled", cursor="left_ptr", text=temp_times[2])
    s_time_night_button.configure(state="disabled", cursor="left_ptr", text=temp_times[3])
    s_editing = False
    s_time_message.configure(text="")
    return

#Setting Page: Enables editing of notification settings
def setting_notification_edit_button():
    global s_editing
    s_notificaton_edit_button.configure(state="disabled")
    s_notificaton_save_button.configure(state="normal")
    s_notificaton_cancel_button.configure(state="normal")
    s_notification_exhaust_button.configure(state="normal")
    s_editing = True
    return

#Settings Page: Saves changes to notification settings
def setting_notification_save_button():
    global s_editing, exhaust_setting
    s_notificaton_edit_button.configure(state="normal")
    s_notificaton_save_button.configure(state="disabled")
    s_notificaton_cancel_button.configure(state="disabled")
    s_notification_exhaust_button.configure(state="disabled")
    s_notificaton_message.configure(text="")
    exhaust_setting = s_exhaust_weeks.get()
    s_editing = False
    return

#Setting Page: Discards changes to notification settings
def setting_notification_cancel_button():
    global s_editing
    s_notificaton_edit_button.configure(state="normal")
    s_notificaton_save_button.configure(state="disabled")
    s_notificaton_cancel_button.configure(state="disabled")
    s_notification_exhaust_button.configure(state="disabled")
    s_editing = False
    s_exhaust_weeks.set(exhaust_setting)
    s_notificaton_message.configure(text="")
    return


#Pastel colours used: Blue "#98F3F9"; Green "#98F9CF"; Yellow "#F7EF99"; Orange "#F4D297"; Red "#F7B299"; Purple "#D9B1EF"
#Lighter colours used: Blue "#E5FFFF"; Green "#B7F4DA"; Yellow "#F7EF99"; Orange "#F4E3CD"; Red "#F2D1C6"; Purple "#D9B1EF"
#Darker colours used: Blue "#74F0F7"; Green "#60F2B0"; Yellow "#F2E14B"; Orange "#EFB85F"; Red "#F28E6D"; Purple "#D9B1EF"

numpad_mode = 0 #mode == 0: normal; 1: math; 2: time
numpad_operator = 0 #1: plus, -1: minus

shift = False #Stores if keyboard shift is activated
capslock = False #Stores if keyboard capslock is enabled

app_mode = 0 #0: Initial set up; 1: Offline mode; 2: Online mode

current_entry_button = None #Stores the button that opened the numpad/keyboard. Current button text will be copied to keyboard/numpad entry bar, reverse will be performed upon saving
current_page = None #Stores the page that the application is at when opening keyboard/numpad. Returns to that page upon exiting

temp_user = user("","","","","","","")
temp_pill = pill("",0,0,0,0,[False, False, False, False, False, False, False],[False, False, False, False], 0)
temp_times = ["","","",""]

add_pill = pill("Add Medicine", 0, -1, 0, 1, [False, False, False, False, False, False, False],[False, False, False, False], 1)

pills = [add_pill]
time_settings = []
time_thresholds = [[0] * 2 for time_count in range(4)]
time_margin = [30,60]
current_day = 0
current_window = -1

exhaust_setting = 4

dosage_info = []
missed_doses = []

saved_day = int((time.time() + time.localtime().tm_gmtoff) / 86400)

#0: default, -1: missed, 1: taken
dose_taken_day = [0] * 4

wifi_networks = []
online_settings = online_settings_storage(False,False,False)
user_user = user("","","","","","","")

at_main = False

current_pill = 0

current_pe_page = 0 #0: Pill; 1: Calendar; 2: Delete
pe_editing = False

current_a_page = 0 #0: General; 1: Sharing; 2: Password; 3: Logout
a_editing = False

current_s_page = 0
s_editing = False

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thusday", "Friday", "Saturday"]
mon_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
time_list = ["Morning", "Afternoon", "Evening", "Night"]

colours = {
    "start_bg": "#98F3F9",
    "setup_bg": "#98F3F9",
    "setup_ln": "#FFFFFF",
    "wifi_bg": "#98F3F9",
    "wifi_menu_bn_u": "#98F3F9",
    "wifi_menu_bn_p": "#74F0F7",
    "wifi_entry_d": "#AFA136",
    "wifi_entry_u": "#F7EF99",
    "wifi_entry_p": "#F7EF99",
    "wifi_bn_u": "#F7EF99",
    "wifi_bn_p": "#F2E14B",
    "login_bg": "#98F3F9",
    "login_menu_bn_u": "#98F3F9",
    "login_menu_bn_p": "#74F0F7",
    "login_entry_u": "#F7EF99",
    "login_entry_p": "#F7EF99",
    "login_bn_u": "#F7EF99",
    "login_bn_p": "#F2E14B",
    "main_dispense_bg": "#98F3F9",
    "main_status_bg": "#F2F2F2",
    "main_pill_bg": "#98F9CF",
    "main_quantity_bg": "#F7EF99",
    "main_history_bg": "#F4D297",
    "main_account_bg": "#F7B299",
    "main_settings_bg": "#D9B1EF",
    "main_ln": "#FFFFFF",
    "d_bg": "#98F3F9",
    "d_menu_bn_u": "#98F3F9",
    "d_menu_bn_p": "#74F0F7",
    "d_entry": "#F2E14B",
    "d_frame": "#F7EF99",
    "d_bn_u": "#F7EF99",
    "d_bn_p": "#F2E14B",
    "pn_bg": "#98F3F9",
    "pn_menu_bn_u": "#98F3F9",
    "pn_menu_bn_p": "#74F0F7",
    "pd_bg": "#98F3F9",
    "pd_menu_bn_u": "#98F3F9",
    "pd_menu_bn_p": "#74F0F7",
    "pd_bn_u": "#F7EF99",
    "pd_bn_p": "#F2E14B",
    "pd_ln": "#FFFFFF",
    "pd_bc": "#F7EF99",
    "pe_menu_bn_u": "#98F3F9",
    "pe_menu_bn_p": "#74F0F7",
    "pe_menu_ln": "#FFFFFF",
    "pe_content_bg": "#E5FFFF",
    "pe_content_entry": "#B5FFFF",
    "pe_content_bn_u": "#F7EF99",
    "pe_content_bn_p": "#F2E14B",
    "q_bg": "#98F3F9",
    "q_menu_bn_u": "#98F3F9",
    "q_menu_bn_p": "#74F0F7",
    "q_ln": "#FFFFFF",
    "q_bc": "#F7EF99",
    "h_bg": "#98F3F9",
    "h_menu_bn_u": "#98F3F9",
    "h_menu_bn_p": "#74F0F7",
    "h_ln": "#FFFFFF",
    "h_content_bg": "#F7EF99",
    "pd_bn_u": "#F7EF99",
    "pd_bn_p": "#F2E14B",
    "a_menu_bn_u": "#98F3F9",
    "a_menu_bn_p": "#74F0F7",
    "a_menu_ln": "#FFFFFF",
    "a_content_bg": "#E5FFFF",
    "a_content_entry": "#B5FFFF",
    "a_content_bn_u": "#F7EF99",
    "a_content_bn_p": "#F2E14B",
    "s_menu_bn_u": "#98F3F9",
    "s_menu_bn_p": "#74F0F7",
    "s_menu_ln": "#FFFFFF",
    "s_content_bg": "#E5FFFF",
    "s_content_entry": "#B5FFFF",
    "s_content_entry_p": "#74F0F7",
    "s_content_bn_u": "#F7EF99",
    "s_content_bn_p": "#F2E14B",
    "k_bg": "#F7EF99",
    "k_content": "#E5FFFF",
    "k_entry": "#B5FFFF",
    "k_ln": "#000000",
    "k_bn_u": "#F7EF99",
    "k_bn_p": "#F2E14B",
    "n_bg": "#F7EF99",
    "n_content": "#E5FFFF",
    "n_entry": "#B5FFFF",
    "n_ln": "#000000",
    "n_bn_u": "#F7EF99",
    "n_bn_p": "#F2E14B",
}

window = tk.Tk()
window.title("PillBot App")
window.geometry("800x480")
window.iconphoto(False, tk.PhotoImage(file="Resources/GUI_icon.png"))

start_image = ImageTk.PhotoImage(Image.open("Resources/start.png"))
start_image_loading = ImageTk.PhotoImage(Image.open("Resources/start_loading.png"))
online_image = ImageTk.PhotoImage(Image.open("Resources/online_icon.png"))
offline_image = ImageTk.PhotoImage(Image.open("Resources/offline_icon.png"))
dispense_image = ImageTk.PhotoImage(Image.open("Resources/dispense_icon.png"))
pill_image = ImageTk.PhotoImage(Image.open("Resources/pill_icon.png"))
quantity_image = ImageTk.PhotoImage(Image.open("Resources/bar_chart_icon.png"))
history_image = ImageTk.PhotoImage(Image.open("Resources/history_icon.png"))
person_image = ImageTk.PhotoImage(Image.open("Resources/person_icon.png"))
setting_image = ImageTk.PhotoImage(Image.open("Resources/setting_icon.png"))
alert_image = ImageTk.PhotoImage(Image.open("Resources/alert_icon.png"))
left_arrow_image = ImageTk.PhotoImage(Image.open("Resources/left_arrow.png"))
right_arrow_image = ImageTk.PhotoImage(Image.open("Resources/right_arrow.png"))
back_icon_image = ImageTk.PhotoImage(Image.open("Resources/back_arrow.png"))
pill_icon_simple_image = ImageTk.PhotoImage(Image.open("Resources/pill_icon_simple.png"))
calendar_image = ImageTk.PhotoImage(Image.open("Resources/calendar_icon.png"))
delete_image = ImageTk.PhotoImage(Image.open("Resources/delete_icon.png"))
person_small_image = ImageTk.PhotoImage(Image.open("Resources/person_small_icon.png"))
group_image = ImageTk.PhotoImage(Image.open("Resources/group_icon.png"))
lock_image = ImageTk.PhotoImage(Image.open("Resources/lock_icon.png"))
logout_image = ImageTk.PhotoImage(Image.open("Resources/logout_icon.png"))
wifi_image = ImageTk.PhotoImage(Image.open("Resources/wifi_icon.png"))
cloud_image = ImageTk.PhotoImage(Image.open("Resources/online_icon_small.png"))
notification_image = ImageTk.PhotoImage(Image.open("Resources/notification_icon.png"))
clock_image = ImageTk.PhotoImage(Image.open("Resources/clock_icon.png"))
checkbox_tick_image = ImageTk.PhotoImage(Image.open("Resources/checkbox_tick_icon.png"))
checkbox_cross_image = ImageTk.PhotoImage(Image.open("Resources/checkbox_cross_icon.png"))
checkbox_empty_image = ImageTk.PhotoImage(Image.open("Resources/checkbox_empty_icon.png"))
pill_images = []
pill_images_small = []
pill_images_tiny = []
pill_images.append(ImageTk.PhotoImage(Image.open("Resources/Pill_Icons/Add_Pill.png")))
pill_images_small.append(ImageTk.PhotoImage(Image.open("Resources/Pill_Icons/Add_Pill.png")))
pill_images_tiny.append(ImageTk.PhotoImage(Image.open("Resources/Pill_Icons/Add_Pill.png")))
for image_counter in range(42):
    with Image.open(f"Resources/Pill_Icons/Pill{math.floor(image_counter/6)}{image_counter % 6}.png") as temp_image:
        pill_images.append(ImageTk.PhotoImage(temp_image))
        temp_image.thumbnail((80,50))
        pill_images_small.append(ImageTk.PhotoImage(temp_image))
        temp_image.thumbnail((35,30))
        pill_images_tiny.append(ImageTk.PhotoImage(temp_image))
colour_images = []
for image_counter in range(6):
    with Image.open(f"Resources/Pill_Icons/Colour{image_counter}.png") as temp_image:
        temp_image.thumbnail((30,30))
        colour_images.append(ImageTk.PhotoImage(temp_image))

start_page = Page(window)
start_page.place(x=0, y=0, relwidth=1, relheight=1)
start_page_button = tk.Button(start_page, image=start_image, command = start_button, relief="sunken", borderwidth=0, bg=colours["start_bg"], activebackground=colours["start_bg"])
start_page_button.place(x=0, y=0, relwidth=1, relheight=1)
start_page_message = tk.Label(start_page, font=("Trebuchet MS",24), anchor="c", bg=colours["start_bg"], text="")


setup_page = Page(window, bg=colours["setup_bg"])
setup_page.place(x=0, y=0, relwidth=1, relheight=1)
setup_offline_frame = tk.Button(setup_page, relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], command=setup_offline_button_command)
setup_offline_frame.place(relwidth=0.5, relheight=1, relx=0, rely=0, anchor="nw")
setup_offline_button = tk.Button(setup_page, text="Offline Mode", relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], font=("Trebuchet MS",24,"underline"), image=offline_image, compound="top", command=setup_offline_button_command)
setup_offline_button.place(relwidth=0.5, relheight=0.5, relx=0, rely=0.15, anchor="nw")
setup_offline_desc=tk.Button(setup_page, text=f"All features except smartphone\nsyncing and data sharing", relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], font=("Trebuchet MS",16), command=setup_offline_button_command)
setup_offline_desc.place(relwidth=0.5, relheight=0.2, relx=0, rely=0.65, anchor="nw")
setup_online_frame = tk.Button(setup_page, relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], command=setup_online_button_command)
setup_online_frame.place(relwidth=0.5, relheight=1, relx=0.5, rely=0, anchor="nw")
setup_online_button = tk.Button(setup_page, text="Online Mode", relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], font=("Trebuchet MS",24,"underline"), image=online_image, compound="top", command=setup_online_button_command)
setup_online_button.place(relwidth=0.5, relheight=0.5, relx=0.5, rely=0.15, anchor="nw")
setup_online_desc=tk.Button(setup_page, text=f"Enables smartphone syncing\nand data sharing", relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], font=("Trebuchet MS",16), command=setup_online_button_command)
setup_online_desc.place(relwidth=0.5, relheight=0.2, relx=0.5, rely=0.65, anchor="nw")

setup_line = tk.Frame(setup_page, bg=colours["setup_ln"])
setup_line.place(width=2, relheight=1, relx=0.5, rely=0, anchor="n")


wifi_page = Page(window, bg=colours["wifi_bg"])
wifi_page.place(x=0, y=0, relwidth=1, relheight=1)

wifi_back_button = tk.Button(wifi_page, image=back_icon_image, bg=colours["wifi_menu_bn_u"], activebackground=colours["wifi_menu_bn_p"], relief="sunken", borderwidth=0, command = wifi_back_button)
wifi_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

wifi_selected = tk.StringVar()
wifi_selected.set("")
wifi_page_label = tk.Label(wifi_page, text="Connect to WiFi", bg=colours["wifi_bg"], font=("Trebuchet MS",24,"underline"))
wifi_page_label.place(relwidth=0.5, relheight=0.2, relx=0.5, rely=0.04, anchor="n")

wifi_name_frame = tk.Frame(wifi_page, bg=colours["wifi_bg"])
wifi_name_frame.place(relwidth=0.6, relheight=0.08, relx=0.5, rely=0.36, anchor="n")
wifi_name_label = tk.Label(wifi_name_frame, text="WiFi Name:", bg=colours["wifi_bg"], font=("Trebuchet MS",20), anchor="w")
wifi_name_label.place(relwidth=0.4, relheight=1, relx=0, rely=0)
wifi_name_button = tk.OptionMenu(wifi_name_frame, wifi_selected, "", *wifi_networks)
wifi_name_button.configure(bg=colours["wifi_entry_u"], activebackground=colours["wifi_entry_u"], font=("Trebuchet MS",18), anchor="w")
wifi_name_button["menu"].configure(bg=colours["wifi_entry_u"], activebackground=colours["wifi_entry_p"], activeforeground="black", font=("Trebuchet MS",16))
wifi_name_button.place(relwidth=0.6, relheight=1, relx=0.4, rely=0)

wifi_password_frame = tk.Frame(wifi_page, bg=colours["wifi_bg"])
wifi_password_frame.place(relwidth=0.6, relheight=0.08, relx=0.5, rely=0.48, anchor="n")
wifi_password_label = tk.Label(wifi_password_frame, text="Password:", bg=colours["wifi_bg"], font=("Trebuchet MS",20), anchor="w")
wifi_password_label.place(relwidth=0.4, relheight=1, relx=0, rely=0)
wifi_password_entry = tk.Button(wifi_password_frame, bg=colours["wifi_entry_d"], activebackground=colours["wifi_entry_d"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", command = lambda: open_keyboard_button(wifi_page, wifi_password_label, wifi_password_entry))
wifi_password_entry.place(relwidth=0.6, relheight=1, relx=0.4, rely=0)

wifi_message_frame = tk.Frame(wifi_page, bg=colours["wifi_bg"])
wifi_message_frame.place(relwidth=0.6, relheight=0.08, relx=0.5, rely=0.6, anchor="n")
wifi_message_label = tk.Label(wifi_message_frame, text="", bg=colours["wifi_bg"], font=("Trebuchet MS",18), fg="red", anchor="w")
wifi_message_label.place(relwidth=1, relheight=1, relx=0, rely=0)

wifi_refresh_button = tk.Button(wifi_page, text="Refresh", font=("Trebuchet MS", 18), bg=colours["wifi_bn_u"], relief="solid", borderwidth=2, activebackground=colours["wifi_bn_p"], command=lambda:wifi_page_update(False))
wifi_refresh_button.place(relx=0.35, rely=0.84, relwidth=0.2, relheight=0.08, anchor="n")

wifi_connect_button = tk.Button(wifi_page, text="Connect", font=("Trebuchet MS", 18), bg=colours["wifi_bn_u"], relief="solid", borderwidth=2, activebackground=colours["wifi_bn_p"], command=lambda:connect_wifi(wifi_selected.get(), wifi_password_entry.cget("text")))
wifi_connect_button.place(relx=0.65, rely=0.84, relwidth=0.2, relheight=0.08, anchor="n")


login_page = Page(window, bg=colours["login_bg"])
login_page.place(x=0, y=0, relwidth=1, relheight=1)

login_page_label = tk.Label(login_page, text="Log in to PillBot", bg=colours["login_bg"], font=("Trebuchet MS",24,"underline"))
login_page_label.place(relwidth=0.5, relheight=0.2, relx=0.5, rely=0.04, anchor="n")

login_back_button = tk.Button(login_page, image=back_icon_image, bg=colours["login_menu_bn_u"], activebackground=colours["login_menu_bn_p"], relief="sunken", borderwidth=0, command = login_back_button)
login_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

login_username_frame = tk.Frame(login_page, bg=colours["login_bg"])
login_username_frame.place(relwidth=0.6, relheight=0.08, relx=0.5, rely=0.36, anchor="n")
login_username_label = tk.Label(login_username_frame, text="Email:", bg=colours["login_bg"], font=("Trebuchet MS",20), anchor="w")
login_username_label.place(relwidth=0.4, relheight=1, relx=0, rely=0)
login_username_entry = tk.Button(login_username_frame, bg=colours["login_entry_u"], activebackground=colours["login_entry_u"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", command = lambda: open_keyboard_button(login_page, login_username_label, login_username_entry))
login_username_entry.place(relwidth=0.6, relheight=1, relx=0.4, rely=0)

login_password_frame = tk.Frame(login_page, bg=colours["login_bg"])
login_password_frame.place(relwidth=0.6, relheight=0.08, relx=0.5, rely=0.48, anchor="n")
login_password_label = tk.Label(login_password_frame, text="Password:", bg=colours["login_bg"], font=("Trebuchet MS",20), anchor="w")
login_password_label.place(relwidth=0.4, relheight=1, relx=0, rely=0)
login_password_entry = tk.Button(login_password_frame, bg=colours["login_entry_u"], activebackground=colours["login_entry_u"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", command = lambda: open_keyboard_button(login_page, login_password_label, login_password_entry))
login_password_entry.place(relwidth=0.6, relheight=1, relx=0.4, rely=0)

login_message_frame = tk.Frame(login_page, bg=colours["wifi_bg"])
login_message_frame.place(relwidth=0.6, relheight=0.08, relx=0.5, rely=0.6, anchor="n")
login_message_label = tk.Label(login_message_frame, text="", bg=colours["wifi_bg"], font=("Trebuchet MS",18), fg="red", anchor="w")
login_message_label.place(relwidth=1, relheight=1, relx=0, rely=0)

login_login_button = tk.Button(login_page, text="Login", font=("Trebuchet MS", 18), bg=colours["login_bn_u"], relief="solid", borderwidth=2, activebackground=colours["login_bn_p"], command=lambda:attempt_login(login_username_entry.cget("text"), login_password_entry.cget("text"), True, True))
login_login_button.place(relx=0.5, rely=0.84, relwidth=0.2, relheight=0.08, anchor="n")



main_page = Page(window, bg=colours["main_dispense_bg"])
main_page.place(relx=0, rely=0, relwidth=1, relheight=1)

m_dispense_frame = tk.Frame(main_page, bg=colours["main_dispense_bg"])
m_dispense_frame.place(relwidth=0.55, relheight=1, relx=0, rely=0, anchor="nw")
m_dispense_button = tk.Button(m_dispense_frame, bg=colours["main_dispense_bg"], image=dispense_image, text=" Dispense", compound="left", activebackground=colours["main_dispense_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",28), anchor="c", padx=20, command=goto_dispense_page_button)
m_dispense_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_status_frame = tk.Frame(main_page, bg=colours["main_status_bg"])
m_status_frame.place(relwidth=0.45, relheight=0.05, relx=1, rely=0, anchor="ne")

m_pill_frame = tk.Frame(main_page, bg=colours["main_pill_bg"])
m_pill_frame.place(relwidth=0.45, relheight=0.19, relx=1, rely=0.05, anchor="ne")
m_pill_button = tk.Button(m_pill_frame, bg=colours["main_pill_bg"], image=pill_image, text=" Medicine", compound="left", activebackground=colours["main_pill_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",26), anchor="w", padx=20, command=goto_pill_page_button)
m_pill_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_quantity_frame = tk.Frame(main_page, bg=colours["main_quantity_bg"])
m_quantity_frame.place(relwidth=0.45, relheight=0.19, relx=1, rely=0.24, anchor="ne")
m_quantity_button = tk.Button(m_quantity_frame, bg=colours["main_quantity_bg"], image=quantity_image, text=" Quantity", compound="left", activebackground=colours["main_quantity_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",26), anchor="w", padx=20, command=goto_quantity_page_button)
m_quantity_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")
m_quantity_alert = tk.Button(m_quantity_frame, bg=colours["main_quantity_bg"], image=alert_image, activebackground=colours["main_quantity_bg"], relief="sunken", borderwidth=0, anchor="c", command=goto_quantity_page_button)
m_quantity_alert.place(relwidth = 0.2, relheight=0.5, relx=0.75, rely=0.5, anchor="w")

m_history_frame = tk.Frame(main_page, bg=colours["main_history_bg"])
m_history_frame.place(relwidth=0.45, relheight=0.19, relx=1, rely=0.43, anchor="ne")
m_history_button = tk.Button(m_history_frame, bg=colours["main_history_bg"], image=history_image, text=" History", compound="left", activebackground=colours["main_history_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",26), anchor="w", padx=20, command=goto_history_page_button)
m_history_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_account_frame = tk.Frame(main_page, bg=colours["main_account_bg"])
m_account_frame.place(relwidth=0.45, relheight=0.19, relx=1, rely=0.62, anchor="ne")
m_account_button = tk.Button(m_account_frame, bg=colours["main_account_bg"], image=person_image, text=" Account", compound="left", activebackground=colours["main_account_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",26), anchor="w", padx=20, command=goto_account_page_button)
m_account_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_settings_frame = tk.Frame(main_page, bg=colours["main_settings_bg"])
m_settings_frame.place(relwidth=0.45, relheight=0.19, relx=1, rely=0.81, anchor="ne")
m_setting_button = tk.Button(m_settings_frame, bg=colours["main_settings_bg"], image=setting_image, text=" Settings", compound="left", activebackground=colours["main_settings_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",26), anchor="w", padx=20, command=goto_setting_page_button)
m_setting_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

#Status Frame

m_time_label = tk.Label(m_status_frame, bg=colours["main_status_bg"], text="", font=("Trebuchet MS",12), anchor="w")
m_time_label.place(relx=0, rely=0, relwidth=0.3, relheight=1)
m_date_label = tk.Label(m_status_frame, bg=colours["main_status_bg"], text="", font=("Trebuchet MS",12), anchor="c")
m_date_label.place(relx=0.5, rely=0, relwidth=0.4, relheight=1, anchor="n")

main_lines = []
for line_count in range(6):
    main_lines.append(tk.Frame(main_page, bg=colours["main_ln"]))
main_lines[0].place(relwidth=0.45, height=2, relx=1, rely=0.05, anchor="e")
main_lines[1].place(relwidth=0.45, height=2, relx=1, rely=0.24, anchor="e")
main_lines[2].place(relwidth=0.45, height=2, relx=1, rely=0.43, anchor="e")
main_lines[3].place(relwidth=0.45, height=2, relx=1, rely=0.62, anchor="e")
main_lines[4].place(relwidth=0.45, height=2, relx=1, rely=0.81, anchor="e")
main_lines[5].place(width=2, relheight=1, relx=0.55, rely=0, anchor="n")

#Dispense Page
dispense_page = Page(window, bg=colours["d_bg"])
dispense_page.place(relx=0, rely=0, relwidth=1, relheight=1)

d_back_button = tk.Button(dispense_page, image=back_icon_image, bg=colours["d_menu_bn_u"], activebackground=colours["d_menu_bn_p"], relief="sunken", borderwidth=0, command = goto_main_page_button)
d_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

d_name_label = tk.Label(dispense_page, text="", font=("Trebuchet MS", 24), bg=colours["pn_bg"])
d_name_label.place(relx=0.5, rely=0, relwidth=0.6, relheight=0.2, anchor="n")

d_amount_frames = []
for disp_count in range(6):
    d_amount_frames.append(tk.Frame(dispense_page, bg=colours["d_frame"], highlightbackground="white", highlightthickness=2))

d_amount_frames[0].place(relx = 0.04, rely = 0.2, relwidth = 0.12, relheight = 0.6, anchor="nw")
d_amount_frames[1].place(relx = 0.20, rely = 0.2, relwidth = 0.12, relheight = 0.6, anchor="nw")
d_amount_frames[2].place(relx = 0.36, rely = 0.2, relwidth = 0.12, relheight = 0.6, anchor="nw")
d_amount_frames[3].place(relx = 0.52, rely = 0.2, relwidth = 0.12, relheight = 0.6, anchor="nw")
d_amount_frames[4].place(relx = 0.68, rely = 0.2, relwidth = 0.12, relheight = 0.6, anchor="nw")
d_amount_frames[5].place(relx = 0.84, rely = 0.2, relwidth = 0.12, relheight = 0.6, anchor="nw")

d_icons = []
d_amount_button = []
d_amount_increase_button = []
d_amount_decrease_button = []
for disp_count in range(6):
    d_icons.append(tk.Label(d_amount_frames[disp_count], bg=colours["d_frame"], anchor="c"))
    d_icons[disp_count].place(relx = 0, rely = 0, relwidth = 1, relheight = 0.3, anchor="nw")

    d_amount_button.append(tk.Button(d_amount_frames[disp_count], bg=colours["d_entry"], activebackground=colours["d_entry"], borderwidth=2, relief="solid", text="0", padx=5, pady=10, font=("Trebuchet MS",22), anchor="c", disabledforeground="black", state ="disabled"))
    d_amount_button[disp_count].place(relx = 0.5, rely = 0.6, relwidth = 0.9, relheight = 0.2, anchor="n")

    d_amount_increase_button.append(tk.Button(d_amount_frames[disp_count], bg=colours["d_frame"], activebackground=colours["d_frame"],  borderwidth=0, relief="sunken", text="+", font=("Trebuchet MS",26), anchor="c", disabledforeground="black"))
    d_amount_increase_button[disp_count].place(relx = 0.5, rely = 0.4, relwidth = 0.9, relheight = 0.2, anchor="n")

    d_amount_decrease_button.append(tk.Button(d_amount_frames[disp_count], bg=colours["d_frame"], activebackground=colours["d_frame"],  borderwidth=0, relief="sunken", text="−", font=("Trebuchet MS",26), anchor="c", disabledforeground="black"))
    d_amount_decrease_button[disp_count].place(relx = 0.5, rely = 0.8, relwidth = 0.9, relheight = 0.2, anchor="n")

d_amount_increase_button[0].configure(command=lambda:dispense_page_increase_button(0))
d_amount_increase_button[1].configure(command=lambda:dispense_page_increase_button(1))
d_amount_increase_button[2].configure(command=lambda:dispense_page_increase_button(2))
d_amount_increase_button[3].configure(command=lambda:dispense_page_increase_button(3))
d_amount_increase_button[4].configure(command=lambda:dispense_page_increase_button(4))
d_amount_increase_button[5].configure(command=lambda:dispense_page_increase_button(5))
d_amount_decrease_button[0].configure(command=lambda:dispense_page_decrease_button(0))
d_amount_decrease_button[1].configure(command=lambda:dispense_page_decrease_button(1))
d_amount_decrease_button[2].configure(command=lambda:dispense_page_decrease_button(2))
d_amount_decrease_button[3].configure(command=lambda:dispense_page_decrease_button(3))
d_amount_decrease_button[4].configure(command=lambda:dispense_page_decrease_button(4))
d_amount_decrease_button[5].configure(command=lambda:dispense_page_decrease_button(5))

d_dispense_button = tk.Button(dispense_page, text="Dispense", font=("Trebuchet MS", 18), bg=colours["d_bn_u"], relief="solid", borderwidth=2, activebackground=colours["d_bn_p"], command=dispense_dipense_button)
d_dispense_button.place(relx=0.5, rely=0.85, relwidth=5/32, relheight=0.08, anchor="n")


#Pill Page

pill_page = Page(window, bg=colours["pn_bg"])
pill_page.place(relx=0, rely=0, relwidth=1, relheight=1)

p_pill_name_label = tk.Label(pill_page, text="", font=("Trebuchet MS", 24), bg=colours["pn_bg"])
p_pill_name_label.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2, anchor="n")

p_left_button = tk.Button(pill_page, image=left_arrow_image, bg=colours["pn_bg"], activebackground=colours["pn_bg"], relief="sunken", borderwidth=0, command = pill_left_nav_button)
p_left_button.place(relx=0.04, rely=0.5, anchor="w")

p_right_button = tk.Button(pill_page, image=right_arrow_image, bg=colours["pn_bg"], activebackground=colours["pn_bg"], relief="sunken", borderwidth=0, command = pill_right_nav_button)
p_right_button.place(relx=0.96, rely=0.5, anchor="e")

p_back_button = tk.Button(pill_page, image=back_icon_image, bg=colours["pn_menu_bn_u"], activebackground=colours["pn_menu_bn_p"], relief="sunken", borderwidth=0, command = goto_main_page_button)
p_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

p_pill_button = tk.Button(pill_page, image = pill_images[0], bg=colours["pn_bg"], activebackground=colours["pn_bg"], relief="sunken", borderwidth=0, command = lambda:goto_pill_detail_page_button(current_pill))
p_pill_button.place(relx=0.5, rely=0.5, relwidth=0.3, relheight=0.5, anchor ="c")

p_message_label = tk.Label(pill_page, text="", font=("Trebuchet MS", 18), fg="red", bg=colours["pn_bg"])
p_message_label.place(relx=0.5, rely=0.88, relwidth=0.5, relheight=0.08, anchor="s")

#Pill Details Page

pill_detail_page = Page(window, bg=colours["pd_bg"])
pill_detail_page.place(relx=0, rely=0, relwidth=1, relheight=1)

pd_back_button = tk.Button(pill_detail_page, image=back_icon_image, bg=colours["pd_menu_bn_u"], activebackground=colours["pd_menu_bn_p"], relief="sunken", borderwidth=0, command = goto_pill_page_button)
pd_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

pd_pill_name_button = tk.Label(pill_detail_page, text="Medicine Name", font=("Trebuchet MS", 24), bg=colours["pd_bg"])
pd_pill_name_button.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2, anchor="n")

pd_pill_button = tk.Label(pill_detail_page, image = pill_images_small[1], bg=colours["pd_bg"])
pd_pill_button.place(relx=0.9, rely=0, relwidth=0.12, relheight=0.2, anchor ="ne")

pd_open_button = tk.Button(pill_detail_page, text="Open", font=("Trebuchet MS", 18), bg=colours["pd_bn_u"], relief="solid", borderwidth=2, activebackground=colours["pd_bn_p"], command=lambda:pill_dispenser_open(current_pill))
pd_open_button.place(relx=0.35, rely=0.85, relwidth=5/32, relheight=0.08, anchor="n")

pd_edit_button = tk.Button(pill_detail_page, text="Details", font=("Trebuchet MS", 18), bg=colours["pd_bn_u"], relief="solid", borderwidth=2, activebackground=colours["pd_bn_p"], command=goto_pill_edit_page_button)
pd_edit_button.place(relx=0.65, rely=0.85, relwidth=5/32, relheight=0.08, anchor="n")

pd_chart_frame = tk.Frame(pill_detail_page, bg=colours["pd_bg"])
pd_chart_frame.place(relx=0.05, rely=0.2, relwidth=0.35, relheight=0.6)

pd_chart_bar = tk.Frame(pd_chart_frame, bg=colours["pd_bc"], highlightbackground=colours["pd_ln"], highlightthickness=3)
pd_chart_bar.place(relx=0.65, rely=0.9, relwidth=0.2, relheight=0.5, anchor="sw")

pd_chart_labels = []
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="Empty", anchor="e"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="1 Month", anchor="e"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="2 Months", anchor="e"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="3 Months", anchor="e"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="4 Months", anchor="e"))

pd_chart_labels[0].place(relx=0.1, rely=0.9, relwidth=0.34, relheight=0.2, anchor="w")
pd_chart_labels[1].place(relx=0.1, rely=0.7, relwidth=0.34, relheight=0.2, anchor="w")
pd_chart_labels[2].place(relx=0.1, rely=0.5, relwidth=0.34, relheight=0.2, anchor="w")
pd_chart_labels[3].place(relx=0.1, rely=0.3, relwidth=0.34, relheight=0.2, anchor="w")
pd_chart_labels[4].place(relx=0.1, rely=0.1, relwidth=0.34, relheight=0.2, anchor="w")

pd_chart_lines = []
for chart_count in range(7):
    pd_chart_lines.append(tk.Frame(pd_chart_frame, bg=colours["pd_ln"]))

pd_chart_lines[0].place(relx=0.5, rely=0.9, width=3, relheight=0.84, anchor="sw")
pd_chart_lines[1].place(relx=0.5, rely=0.9, relwidth=0.5, height=3, anchor="sw")
pd_chart_lines[2].place(relx=0.48, rely=0.9, relwidth=0.02, height=3, anchor="sw")
pd_chart_lines[3].place(relx=0.48, rely=0.7, relwidth=0.02, height=3, anchor="sw")
pd_chart_lines[4].place(relx=0.48, rely=0.5, relwidth=0.02, height=3, anchor="sw")
pd_chart_lines[5].place(relx=0.48, rely=0.3, relwidth=0.02, height=3, anchor="sw")
pd_chart_lines[6].place(relx=0.48, rely=0.1, relwidth=0.02, height=3, anchor="sw")

pd_data_frame = tk.Frame(pill_detail_page, bg=colours["pd_bg"])
pd_data_frame.place(relx=0.45, rely=0.2, relwidth=0.45, relheight=0.6)
pd_quantity_frame = tk.Frame(pd_data_frame, bg=colours["pd_bg"])
pd_quantity_frame.place(relx=0, rely=6/30, relwidth=1, relheight=4/30)
pd_quantity_label = tk.Label(pd_quantity_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 18), text = "Pills Remaining: ", anchor="w")
pd_quantity_label.place(relx=0, rely=0, relwidth=0.5, relheight=1)

pd_container_label = tk.Label(pd_data_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 18), text = "Stored in Container", anchor="w")
pd_container_label.place(relx=0, rely=0, relwidth=1, relheight=4/30)

pd_qty_button = tk.Button(pd_quantity_frame, text="100", font=("Trebuchet MS", 18), bg=colours["pd_bn_u"], relief="solid", borderwidth=2, activebackground=colours["pd_bn_p"], command=lambda:open_numpad_button(pill_detail_page, "Pill Quantity", pd_qty_button, 1))
pd_qty_button.place(relx=0.5, rely=0, relwidth=0.2, relheight=1)

pd_empty_label = tk.Label(pd_data_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 18), text = "Empty On ", anchor="w")
pd_empty_label.place(relx=0, rely=12/30, relwidth=0.8, relheight=4/30)

pd_message_label = tk.Label(pd_data_frame, bg=colours["pd_bg"], fg="red", font=("Trebuchet MS", 18), text = "", anchor="w")
pd_message_label.place(relx=0, rely=18/30, relwidth=1, relheight=4/30)

#Pill Edit Page

pill_edit_page = Page(window, bg=colours["pe_menu_bn_u"])
pill_edit_page.place(relx=0, rely=0, relwidth=1, relheight=1)

pe_menu_frame = tk.Frame(pill_edit_page, bg=colours["pe_menu_bn_u"])
pe_menu_frame.place(relx = 0, rely = 0, relwidth = 0.12, relheight = 1)

pe_back_button = tk.Button(pe_menu_frame, image=back_icon_image, bg=colours["pe_menu_bn_u"], activebackground=colours["pe_menu_bn_p"], relief="sunken", borderwidth=0, command=pill_edit_back_button, anchor = "c")
pe_back_button.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=1, anchor="n")

pe_pill_button = tk.Button(pe_menu_frame, image=pill_icon_simple_image, bg=colours["pe_menu_bn_u"], activebackground=colours["pe_menu_bn_p"], relief="sunken", borderwidth=0, anchor = "c", command=pill_edit_pill_button)
pe_pill_button.place(relx=0.5, rely=0.2, relheight=0.2, relwidth=1, anchor="n")

pe_schedule_button = tk.Button(pe_menu_frame, image=calendar_image, bg=colours["pe_menu_bn_u"], activebackground=colours["pe_menu_bn_p"], relief="sunken", borderwidth=0, anchor = "c", command=pill_edit_schedule_button)
pe_schedule_button.place(relx=0.5, rely=0.4, relheight=0.2, relwidth=1, anchor="n")

pe_delete_button = tk.Button(pe_menu_frame, image=delete_image, bg=colours["pe_menu_bn_u"], activebackground=colours["pe_menu_bn_p"], relief="sunken", borderwidth=0, anchor = "c", command=pill_edit_delete_button)
pe_delete_button.place(relx=0.5, rely=0.6, relheight=0.2, relwidth=1, anchor="n")


pe_pill_frame = tk.Frame(pill_edit_page, bg=colours["pe_content_bg"])
pe_pill_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

pe_pill_title = tk.Label(pe_pill_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",24,"underline"), text="Medicine Information", padx=10, pady=10, anchor="w")
pe_pill_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

pe_pill_name_frame = tk.Frame(pe_pill_frame, bg=colours["pe_content_bg"])
pe_pill_name_label = tk.Label(pe_pill_name_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Pill Name: ", padx=10, pady=10, anchor="w")
pe_pill_name_button = tk.Button(pe_pill_name_frame, bg=colours["pe_content_entry"], activebackground=colours["pe_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(pill_edit_page, pe_pill_name_label, pe_pill_name_button))
pe_pill_name_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
pe_pill_name_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
pe_pill_name_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

pe_icon_frame = tk.Frame(pe_pill_frame, bg=colours["pe_content_bg"])
pe_icon_label = tk.Label(pe_icon_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Pill Icon: ", padx=10, pady=10, anchor="w")
pe_icon_button = tk.Label(pe_icon_frame, bg=colours["pe_content_bg"], image=pill_images_small[1], anchor="w")
pe_icon_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.12)
pe_icon_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
pe_icon_button.place(relx = 0.3, rely = 0, relwidth = 0.2, relheight = 1)

pe_icon_shape_frame = tk.Frame(pe_pill_frame, bg=colours["pe_content_bg"])
pe_icon_shape_label = tk.Label(pe_icon_shape_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Pill Shape: ", padx=10, pady=10, anchor="w")
pe_icon_shape_frame.place(relx = 0.05, rely = 0.48, relwidth = 0.9, relheight = 0.08)
pe_icon_shape_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
pe_icon_shape_buttons = []
for pe_count in range (7):
    pe_icon_shape_buttons.append(tk.Button(pe_icon_shape_frame, bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], image=pill_images_tiny[6*(pe_count + 1)], borderwidth=2, relief="flat", padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666"))
    pe_icon_shape_buttons[pe_count].place(relx = 0.3 + (pe_count * 0.1), rely = 0, relwidth = 0.1, relheight = 1)

pe_icon_colour_frame = tk.Frame(pe_pill_frame, bg=colours["pe_content_bg"])
pe_icon_colour_label = tk.Label(pe_icon_colour_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Pill Colour: ", padx=10, pady=10, anchor="w")

pe_icon_colour_frame.place(relx = 0.05, rely = 0.60, relwidth = 0.9, relheight = 0.08)
pe_icon_colour_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
pe_icon_colour_buttons = []

for pe_count in range (6):
    pe_icon_colour_buttons.append(tk.Button(pe_icon_colour_frame, bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"], image=colour_images[pe_count],  borderwidth=2, relief="flat", padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666"))
    pe_icon_colour_buttons[pe_count].place(relx = 0.3 + (pe_count * 0.1), rely = 0, relwidth = 0.1, relheight = 1)

pe_pill_message_frame = tk.Frame(pe_pill_frame, bg=colours["pe_content_bg"])
pe_pill_message_label = tk.Label(pe_pill_message_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="", fg="red", padx=10, pady=10, anchor="w")

pe_pill_message_frame.place(relx = 0.05, rely = 0.72, relwidth = 0.9, relheight = 0.08)
pe_pill_message_label.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

pe_pill_button_frame = tk.Frame(pe_pill_frame, bg=colours["pe_content_bg"])
pe_pill_edit_button = tk.Button(pe_pill_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Edit", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=pill_edit_pill_edit_button)
pe_pill_save_button = tk.Button(pe_pill_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Save", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=pill_edit_pill_save_button)
pe_pill_cancel_button = tk.Button(pe_pill_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=pill_edit_pill_cancel_button)
pe_pill_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
pe_pill_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
pe_pill_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
pe_pill_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)



pe_schedule_frame = tk.Frame(pill_edit_page, bg=colours["pe_content_bg"])
pe_schedule_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

pe_schedule_title = tk.Label(pe_schedule_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",24,"underline"), text="Dosage Information", padx=10, pady=10, anchor="w")
pe_schedule_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

pe_schedule_pill_icon = tk.Label(pe_schedule_frame, bg=colours["pe_content_bg"], image=pill_images_small[1], anchor="c")
pe_schedule_pill_icon.place(relx = 0.95, rely = 0.06, relwidth = 0.2, relheight = 0.12, anchor="ne")

pe_schedule_days_frame = tk.Frame(pe_schedule_frame, bg=colours["pe_content_bg"])
pe_schedule_days_label = tk.Label(pe_schedule_days_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Days: ", padx=10, pady=10, anchor="w")
pe_schedule_days_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
pe_schedule_days_label.place(relx = 0, rely = 0, relwidth = 0.15, relheight = 1)
pe_schedule_days_list = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
pe_schedule_days_buttons = []
for pe_count in range (7):
    pe_schedule_days_buttons.append(tk.Button(pe_schedule_days_frame, bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"],  borderwidth=2, relief="solid", text=pe_schedule_days_list[pe_count], padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666"))
    pe_schedule_days_buttons[pe_count].place(relx = 0.2 + (pe_count * 0.1), rely = 0, relwidth = 0.1, relheight = 1)

pe_schedule_times_frame = tk.Frame(pe_schedule_frame, bg=colours["pe_content_bg"])
pe_schedule_times_label = tk.Label(pe_schedule_times_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Time: ", padx=10, pady=10, anchor="w")
pe_schedule_times_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
pe_schedule_times_label.place(relx = 0, rely = 0, relwidth = 0.2, relheight = 1)
pe_schedule_times_list = ["Morning", "Afternoon", "Evening", "Night"]
pe_schedule_times_buttons = []
for pe_count in range (4):
    pe_schedule_times_buttons.append(tk.Button(pe_schedule_times_frame, bg=colours["pe_content_bg"], activebackground=colours["pe_content_entry"],  borderwidth=2, relief="solid", text=pe_schedule_times_list[pe_count], padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666"))
    pe_schedule_times_buttons[pe_count].place(relx = 0.2 + (pe_count * 0.2), rely = 0, relwidth = 0.2, relheight = 1)

pe_schedule_amount_frame = tk.Frame(pe_schedule_frame, bg=colours["pe_content_bg"])
pe_schedule_amount_label = tk.Label(pe_schedule_amount_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Quantity: ", padx=10, pady=10, anchor="w")
pe_schedule_amount_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
pe_schedule_amount_label.place(relx = 0, rely = 0, relwidth = 0.25, relheight = 1)
pe_schedule_amount_decrease_button = tk.Button(pe_schedule_amount_frame, bg=colours["pe_content_bg"], activebackground=colours["pe_content_bg"], borderwidth=0, relief="sunken", text="−", padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666")
pe_schedule_amount_increase_button = tk.Button(pe_schedule_amount_frame, bg=colours["pe_content_bg"], activebackground=colours["pe_content_bg"], borderwidth=0, relief="sunken", text="+", padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666")
pe_schedule_amount_button = tk.Button(pe_schedule_amount_frame, bg=colours["pe_content_entry"], activebackground=colours["pe_content_entry"],  borderwidth=2, relief="solid", text="1", padx=5, pady=10, font=("Trebuchet MS",18), anchor="c", disabledforeground="black", state ="disabled")
pe_schedule_amount_decrease_button.place(relx = 0.25, rely = 0, relwidth = 0.1, relheight = 1)
pe_schedule_amount_button.place(relx = 0.35, rely = 0, relwidth = 0.1, relheight = 1)
pe_schedule_amount_increase_button.place(relx = 0.45, rely = 0, relwidth = 0.1, relheight = 1)

pe_schedule_message_frame = tk.Frame(pe_schedule_frame, bg=colours["pe_content_bg"])
pe_schedule_message_label = tk.Label(pe_schedule_message_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="", fg="red", padx=10, pady=10, anchor="w")
pe_schedule_message_frame.place(relx = 0.05, rely = 0.72, relwidth = 0.9, relheight = 0.08)
pe_schedule_message_label.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

pe_schedule_button_frame = tk.Frame(pe_schedule_frame, bg=colours["pe_content_bg"])
pe_schedule_edit_button = tk.Button(pe_schedule_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Edit", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=pill_edit_schedule_edit_button)
pe_schedule_save_button = tk.Button(pe_schedule_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Save", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=pill_edit_schedule_save_button)
pe_schedule_cancel_button = tk.Button(pe_schedule_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=pill_edit_schedule_cancel_button)
pe_schedule_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
pe_schedule_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
pe_schedule_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
pe_schedule_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)



pe_delete_frame = tk.Frame(pill_edit_page, bg=colours["pe_content_bg"])
pe_delete_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

pe_delete_title = tk.Label(pe_delete_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",24,"underline"), text="Delete Medicine", padx=10, pady=10, anchor="w")
pe_delete_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

pe_delete_pill_icon = tk.Label(pe_delete_frame, bg=colours["pe_content_bg"], image=pill_images_small[1], anchor="c")
pe_delete_pill_icon.place(relx = 0.95, rely = 0.06, relwidth = 0.2, relheight = 0.12, anchor="ne")

pe_delete_label = tk.Label(pe_delete_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="Delete Medicine? This can not be undone.", padx=10, pady=10, anchor="w")
pe_delete_label.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)

pe_delete_message_frame = tk.Frame(pe_delete_frame, bg=colours["pe_content_bg"])
pe_delete_message_label = tk.Label(pe_delete_message_frame, bg=colours["pe_content_bg"], font=("Trebuchet MS",18), text="", fg="red", padx=10, pady=10, anchor="c")
pe_delete_message_frame.place(relx = 0.05, rely = 0.64, relwidth = 0.9, relheight = 0.16)
pe_delete_message_label.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

pe_delete_button_frame = tk.Frame(pe_delete_frame, bg=colours["pe_content_bg"])
pe_delete_delete_button = tk.Button(pe_delete_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Delete", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=pill_edit_delete_delete_button)
pe_delete_confirm_button = tk.Button(pe_delete_button_frame, bg=colours["pe_content_bn_u"], activebackground=colours["pe_content_bn_p"], font=("Trebuchet MS",18), text="Confirm", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=pill_edit_delete_confirm_button)
pe_delete_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
pe_delete_delete_button.place(relx = 0.2, rely = 0, relwidth = 0.2, relheight = 1)
pe_delete_confirm_button.place(relx = 0.6, rely = 0, relwidth = 0.2, relheight = 1)


pe_lines = []
for line_count in range(5):
    pe_lines.append(tk.Frame(pe_menu_frame, bg=colours["pe_menu_ln"]))
pe_lines[0].place(width=2, relheight=1, relx=1, rely=0, anchor="ne")
pe_lines[1].place(relwidth=1, height=2, relx=0, rely=0.2, anchor="w")
pe_lines[2].place(relwidth=1, height=2, relx=0, rely=0.4, anchor="w")
pe_lines[3].place(relwidth=1, height=2, relx=0, rely=0.6, anchor="w")
pe_lines[4].place(relwidth=1, height=2, relx=0, rely=0.8, anchor="w")

#Quantity Page

quantity_page = Page(window, bg=colours["q_bg"])
quantity_page.place(x=0, y=0, relwidth=1, relheight=1)

q_back_button = tk.Button(quantity_page, image=back_icon_image, bg=colours["q_menu_bn_u"], activebackground=colours["q_menu_bn_p"], relief="sunken", borderwidth=0, command=goto_main_page_button)
q_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

q_page_label = tk.Label(quantity_page, text="Quantity", font=("Trebuchet MS", 24, "underline"), bg=colours["q_bg"])
q_page_label.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2, anchor="n")

q_chart_frame = tk.Frame(quantity_page, bg=colours["q_bg"])
q_chart_frame.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.7)

q_chart_bars = []
for chart_count in range(6):
    q_chart_bars.append(tk.Frame(q_chart_frame, bg=colours["q_bc"], highlightbackground=colours["q_ln"], highlightthickness=3))

q_chart_bars[0].place(relx=0.23, rely=0.7, relwidth=0.08, relheight=0.5, anchor="sw")
q_chart_bars[1].place(relx=0.36, rely=0.7, relwidth=0.08, relheight=0.5, anchor="sw")
q_chart_bars[2].place(relx=0.49, rely=0.7, relwidth=0.08, relheight=0.5, anchor="sw")
q_chart_bars[3].place(relx=0.62, rely=0.7, relwidth=0.08, relheight=0.5, anchor="sw")
q_chart_bars[4].place(relx=0.75, rely=0.7, relwidth=0.08, relheight=0.5, anchor="sw")
q_chart_bars[5].place(relx=0.88, rely=0.7, relwidth=0.08, relheight=0.5, anchor="sw")

q_chart_labels = []
q_chart_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="Empty", anchor="e"))
q_chart_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="1 Month", anchor="e"))
q_chart_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="2 Months", anchor="e"))
q_chart_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="3 Months", anchor="e"))
q_chart_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="4 Months", anchor="e"))
q_chart_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="Quantity", anchor="e"))

q_chart_labels[0].place(relx=0, rely=0.69, relwidth=0.16, relheight=0.15, anchor="w")
q_chart_labels[1].place(relx=0, rely=0.54, relwidth=0.16, relheight=0.15, anchor="w")
q_chart_labels[2].place(relx=0, rely=0.39, relwidth=0.16, relheight=0.15, anchor="w")
q_chart_labels[3].place(relx=0, rely=0.24, relwidth=0.16, relheight=0.15, anchor="w")
q_chart_labels[4].place(relx=0, rely=0.09, relwidth=0.16, relheight=0.15, anchor="w")
q_chart_labels[5].place(relx=0, rely=0.92, relwidth=0.16, relheight=0.15, anchor="w")

q_chart_lines = []
for chart_count in range(7):
    q_chart_lines.append(tk.Frame(q_chart_frame, bg=colours["pd_ln"]))

q_chart_lines[0].place(relx=0.18, rely=0.7, width=3, relheight=0.85, anchor="sw")
q_chart_lines[1].place(relx=0.18, rely=0.7, relwidth=0.82, height=3, anchor="sw")
q_chart_lines[2].place(relx=0.17, rely=0.7, relwidth=0.01, height=3, anchor="sw")
q_chart_lines[3].place(relx=0.17, rely=0.55, relwidth=0.01, height=3, anchor="sw")
q_chart_lines[4].place(relx=0.17, rely=0.4, relwidth=0.01, height=3, anchor="sw")
q_chart_lines[5].place(relx=0.17, rely=0.25, relwidth=0.01, height=3, anchor="sw")
q_chart_lines[6].place(relx=0.17, rely=0.1, relwidth=0.01, height=3, anchor="sw")

q_chart_icons = []
for chart_count in range(6):
    q_chart_icons.append(tk.Label(q_chart_frame, bg=colours["q_bg"], anchor="c"))

q_chart_icons[0].place(relx = 0.27, rely = 0.72, relwidth = 0.08, relheight = 0.12, anchor="n")
q_chart_icons[1].place(relx = 0.40, rely = 0.72, relwidth = 0.08, relheight = 0.12, anchor="n")
q_chart_icons[2].place(relx = 0.53, rely = 0.72, relwidth = 0.08, relheight = 0.12, anchor="n")
q_chart_icons[3].place(relx = 0.66, rely = 0.72, relwidth = 0.08, relheight = 0.12, anchor="n")
q_chart_icons[4].place(relx = 0.79, rely = 0.72, relwidth = 0.08, relheight = 0.12, anchor="n")
q_chart_icons[5].place(relx = 0.92, rely = 0.72, relwidth = 0.08, relheight = 0.12, anchor="n")

q_chart_qty_labels = []
for chart_count in range(6):
    q_chart_qty_labels.append(tk.Label(q_chart_frame, bg=colours["q_bg"], font=("Trebuchet MS", 16), text="", anchor="c"))

q_chart_qty_labels[0].place(relx = 0.27, rely = 0.84, relwidth = 0.08, relheight = 0.16, anchor="n")
q_chart_qty_labels[1].place(relx = 0.40, rely = 0.84, relwidth = 0.08, relheight = 0.16, anchor="n")
q_chart_qty_labels[2].place(relx = 0.53, rely = 0.84, relwidth = 0.08, relheight = 0.16, anchor="n")
q_chart_qty_labels[3].place(relx = 0.66, rely = 0.84, relwidth = 0.08, relheight = 0.16, anchor="n")
q_chart_qty_labels[4].place(relx = 0.79, rely = 0.84, relwidth = 0.08, relheight = 0.16, anchor="n")
q_chart_qty_labels[5].place(relx = 0.92, rely = 0.84, relwidth = 0.08, relheight = 0.16, anchor="n")

#History Page

history_page = Page(window, bg=colours["h_bg"])
history_page.place(x=0, y=0, relwidth=1, relheight=1)

h_back_button = tk.Button(history_page, image=back_icon_image, bg=colours["h_menu_bn_u"], activebackground=colours["h_menu_bn_p"], relief="sunken", borderwidth=0, command=goto_main_page_button)
h_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.2, anchor="nw")

h_page_label = tk.Label(history_page, text="Missed Doses", font=("Trebuchet MS", 24, "underline"), bg=colours["h_bg"])
h_page_label.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2, anchor="n")

h_list_frame = tk.Frame(history_page, bg=colours["h_content_bg"])
h_list_frame.place(rely=0.2,relx=0.5,relwidth=0.9,relheight=0.75,anchor="n")

h_list_entry_frames = []
h_list_entry_day_labels = []
h_list_entry_time_labels = []
h_list_entry_pill_labels = []
for hist_count in range(5):
    h_list_entry_frames.append(tk.Frame(h_list_frame, bg=colours["h_content_bg"]))
    h_list_entry_frames[hist_count].place(relx=0,rely=hist_count*0.2,relwidth=1,relheight=0.2)
    h_list_entry_day_labels.append(tk.Label(h_list_entry_frames[hist_count], font=("Trebuchet MS", 20), bg=colours["h_content_bg"], anchor="w"))
    h_list_entry_day_labels[hist_count].place(relx=0,rely=0.04,relheight=0.46,relwidth=0.52)
    h_list_entry_time_labels.append(tk.Label(h_list_entry_frames[hist_count], font=("Trebuchet MS", 16), bg=colours["h_content_bg"], anchor="w"))
    h_list_entry_time_labels[hist_count].place(relx=0,rely=0.5,relheight=0.46,relwidth=0.52)
    temp_entry_pill_labels = []
    for pill_count in range(3):
        temp_entry_pill_labels.append(tk.Label(h_list_entry_frames[hist_count], font=("Trebuchet MS", 18), bg=colours["h_content_bg"], anchor="w", compound="right"))
        temp_entry_pill_labels[pill_count].place(relx=0.52+0.16*pill_count,rely=0.04,relwidth=0.16,relheight=0.46)
    for pill_count in range(3):
        temp_entry_pill_labels.append(tk.Label(h_list_entry_frames[hist_count], font=("Trebuchet MS", 18), bg=colours["h_content_bg"], anchor="w", compound="right"))
        temp_entry_pill_labels[pill_count+3].place(relx=0.52+0.16*pill_count,rely=0.5,relwidth=0.16,relheight=0.46)
    h_list_entry_pill_labels.append(temp_entry_pill_labels)

h_lines = []
for hist_count in range(8):
    h_lines.append(tk.Frame(h_list_frame, bg=colours["h_ln"]))
#Horizontal lines
h_lines[0].place(relx=0,rely=0,relwidth=1,height=2)
for hist_count in range(4):
    h_lines[hist_count + 1].place(x=0,rely=0.2+0.2*hist_count,relwidth=1,height=2,anchor="w")
h_lines[5].place(relx=0,rely=1,relwidth=1,height=2,anchor="sw")
#Vertical lines
h_lines[6].place(relx=0,rely=0,width=2,relheight=1)
h_lines[7].place(relx=1,rely=0,width=2,relheight=1,anchor="ne")

#Account Page
account_page = Page(window, bg=colours["a_content_bg"])
account_page.place(x=0, y=0, relwidth=1, relheight=1)

a_menu_frame = tk.Frame(account_page, bg=colours["a_menu_bn_u"])
a_menu_frame.place(relx = 0, rely = 0, relwidth = 0.12, relheight = 1)

a_back_button = tk.Button(a_menu_frame, image=back_icon_image, bg=colours["a_menu_bn_u"], activebackground=colours["a_menu_bn_p"], relief="sunken", borderwidth=0, command=account_back_button, anchor = "c")
a_back_button.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=1, anchor="n")

a_general_button = tk.Button(a_menu_frame, image=person_small_image, bg=colours["a_menu_bn_u"], activebackground=colours["a_menu_bn_p"], relief="sunken", borderwidth=0, command=account_general_button, anchor = "c")
a_general_button.place(relx=0.5, rely=0.2, relheight=0.2, relwidth=1, anchor="n")

a_sharing_button = tk.Button(a_menu_frame, image=group_image, bg=colours["a_menu_bn_u"], activebackground=colours["a_menu_bn_p"], relief="sunken", borderwidth=0, command=account_sharing_button, anchor = "c")
a_sharing_button.place(relx=0.5, rely=0.4, relheight=0.2, relwidth=1, anchor="n")

a_password_button = tk.Button(a_menu_frame, image=lock_image, bg=colours["a_menu_bn_u"], activebackground=colours["a_menu_bn_p"], relief="sunken", borderwidth=0, command=account_password_button, anchor = "c")
a_password_button.place(relx=0.5, rely=0.6, relheight=0.2, relwidth=1, anchor="n")

a_logout_button = tk.Button(a_menu_frame, image=logout_image, bg=colours["a_menu_bn_u"], activebackground=colours["a_menu_bn_p"], relief="sunken", borderwidth=0, command=account_logout_button, anchor = "c")
a_logout_button.place(relx=0.5, rely=0.8, relheight=0.2, relwidth=1, anchor="n")

a_lines = []
for line_count in range(5):
    a_lines.append(tk.Frame(a_menu_frame, bg=colours["a_menu_ln"]))
a_lines[0].place(width=2, relheight=1, relx=1, rely=0, anchor="ne")
a_lines[1].place(relwidth=1, height=2, relx=0, rely=0.2, anchor="w")
a_lines[2].place(relwidth=1, height=2, relx=0, rely=0.4, anchor="w")
a_lines[3].place(relwidth=1, height=2, relx=0, rely=0.6, anchor="w")
a_lines[4].place(relwidth=1, height=2, relx=0, rely=0.8, anchor="w")

a_general_frame = tk.Frame(account_page, bg=colours["a_content_bg"])
a_general_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_general_title = tk.Label(a_general_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",24,"underline"), text="General Account Settings", padx=10, pady=10, anchor="w")
a_general_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_email_frame = tk.Frame(a_general_frame, bg=colours["a_content_bg"])
a_email_label = tk.Label(a_email_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="Email: ", padx=10, pady=10, anchor="w")
a_email_button = tk.Label(a_email_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=10, pady=10, font=("Trebuchet MS",18), anchor="w")
a_email_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_email_label.place(relx = 0, rely = 0, relwidth = 0.2, relheight = 1)
a_email_button.place(relx = 0.2, rely = 0, relwidth = 0.8, relheight = 1)

a_userID_frame = tk.Frame(a_general_frame, bg=colours["a_content_bg"])
a_userID_label = tk.Label(a_userID_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User ID: ", padx=10, pady=10, anchor="w")
a_userID_button = tk.Label(a_userID_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w")
a_userID_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_userID_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_userID_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_first_name_frame = tk.Frame(a_general_frame, bg=colours["a_content_bg"])
a_first_name_label = tk.Label(a_first_name_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="First Name: ", padx=10, pady=10, anchor="w")
a_first_name_button = tk.Button(a_first_name_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_first_name_label, a_first_name_button))
a_first_name_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
a_first_name_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_first_name_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_last_name_frame = tk.Frame(a_general_frame, bg=colours["a_content_bg"])
a_last_name_label = tk.Label(a_last_name_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="Last Name: ", padx=10, pady=10, anchor="w")
a_last_name_button = tk.Button(a_last_name_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_last_name_label, a_last_name_button))
a_last_name_frame.place(relx = 0.05, rely = 0.56, relwidth = 0.9, relheight = 0.08)
a_last_name_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_last_name_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_general_message = tk.Label(a_general_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
a_general_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

a_general_button_frame = tk.Frame(a_general_frame, bg=colours["a_content_bg"])
a_general_edit_button = tk.Button(a_general_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Edit", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_general_edit_button)
a_general_save_button = tk.Button(a_general_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Save", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_general_save_button)
a_general_cancel_button = tk.Button(a_general_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_general_cancel_button)
a_general_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_general_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
a_general_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
a_general_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)


a_sharing_frame = tk.Frame(account_page, bg=colours["a_content_bg"])
a_sharing_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_sharing_title = tk.Label(a_sharing_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",24,"underline"), text="Data Sharing Settings", padx=10, pady=10, anchor="w")
a_sharing_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_sharing_user1_frame = tk.Frame(a_sharing_frame, bg=colours["a_content_bg"])
a_sharing_user1_label = tk.Label(a_sharing_user1_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User 1 User ID: ", padx=10, pady=10, anchor="w")
a_sharing_user1_button = tk.Button(a_sharing_user1_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user1_label, a_sharing_user1_button))
a_sharing_user1_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_sharing_user1_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user1_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_user2_frame = tk.Frame(a_sharing_frame, bg=colours["a_content_bg"])
a_sharing_user2_label = tk.Label(a_sharing_user2_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User 2 User ID: ", padx=10, pady=10, anchor="w")
a_sharing_user2_button = tk.Button(a_sharing_user2_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user2_label, a_sharing_user2_button))
a_sharing_user2_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_sharing_user2_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user2_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_user3_frame = tk.Frame(a_sharing_frame, bg=colours["a_content_bg"])
a_sharing_user3_label = tk.Label(a_sharing_user3_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User 3 User ID: ", padx=10, pady=10, anchor="w")
a_sharing_user3_button = tk.Button(a_sharing_user3_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user3_label, a_sharing_user3_button))
a_sharing_user3_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
a_sharing_user3_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user3_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_message = tk.Label(a_sharing_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
a_sharing_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

a_sharing_button_frame = tk.Frame(a_sharing_frame, bg=colours["a_content_bg"])
a_sharing_edit_button = tk.Button(a_sharing_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Edit", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_sharing_edit_button)
a_sharing_save_button = tk.Button(a_sharing_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Save", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_sharing_save_button)
a_sharing_cancel_button = tk.Button(a_sharing_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_sharing_cancel_button)
a_sharing_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_sharing_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
a_sharing_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
a_sharing_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)


a_password_frame = tk.Frame(account_page, bg=colours["a_content_bg"])
a_password_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_password_title = tk.Label(a_password_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",24,"underline"), text="Change Password", padx=10, pady=10, anchor="w")
a_password_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_password_current_frame = tk.Frame(a_password_frame, bg=colours["a_content_bg"])
a_password_current_label = tk.Label(a_password_current_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="Current Password: ", padx=10, pady=10, anchor="w")
a_password_current_button = tk.Button(a_password_current_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_password_current_label, a_password_current_button))
a_password_current_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_password_current_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
a_password_current_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

a_password_new_frame = tk.Frame(a_password_frame, bg=colours["a_content_bg"])
a_password_new_label = tk.Label(a_password_new_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="New Password: ", padx=10, pady=10, anchor="w")
a_password_new_button = tk.Button(a_password_new_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_password_new_label, a_password_new_button))
a_password_new_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_password_new_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
a_password_new_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

a_password_confirm_frame = tk.Frame(a_password_frame, bg=colours["a_content_bg"])
a_password_confirm_label = tk.Label(a_password_confirm_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="Confirm New Password: ", padx=10, pady=10, anchor="w")
a_password_confirm_button = tk.Button(a_password_confirm_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_password_confirm_label, a_password_confirm_button))
a_password_confirm_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
a_password_confirm_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
a_password_confirm_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

a_password_button_frame = tk.Frame(a_password_frame, bg=colours["a_content_bg"])
a_password_change_button = tk.Button(a_password_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Change Password", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_password_change_button)
a_password_cancel_button = tk.Button(a_password_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_password_cancel_button)
a_password_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_password_change_button.place(relx = 0.1, rely = 0, relwidth = 0.4, relheight = 1)
a_password_cancel_button.place(relx = 0.6, rely = 0, relwidth = 0.3, relheight = 1)

a_password_message = tk.Label(a_password_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
a_password_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)


a_logout_frame = tk.Frame(account_page, bg=colours["a_content_bg"])
a_logout_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_logout_title = tk.Label(a_logout_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",24,"underline"), text="Logout", padx=10, pady=10, anchor="w")
a_logout_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_logout_description = tk.Label(a_logout_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="Logout from account? Application will be set to offline\nmode.", padx=10, pady=10, anchor="w", justify="left")
a_logout_description.place(relx = 0.05, rely = 0.2, relwidth = 0.9, relheight = 0.16)

a_logout_message = tk.Label(a_logout_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
a_logout_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

a_logout_button_frame = tk.Frame(a_logout_frame, bg=colours["a_content_bg"])
a_logout_logout_button = tk.Button(a_logout_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Logout", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_logout_logout_button)
a_logout_confirm_button = tk.Button(a_logout_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Confirm", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_logout_confirm_button)
a_logout_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_logout_logout_button.place(relx = 0.2, rely = 0, relwidth = 0.2, relheight = 1)
a_logout_confirm_button.place(relx = 0.6, rely = 0, relwidth = 0.2, relheight = 1)


#Settings page
settings_page = Page(window, bg=colours["s_menu_bn_u"])
settings_page.place(x=0, y=0, relwidth=1, relheight=1)

s_menu_frame = tk.Frame(settings_page, bg=colours["s_menu_bn_u"])
s_menu_frame.place(relx = 0, rely = 0, relwidth = 0.12, relheight = 1)

s_back_button = tk.Button(s_menu_frame, image=back_icon_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_back_button, anchor = "c")
s_back_button.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=1, anchor="n")

s_time_button = tk.Button(s_menu_frame, image=clock_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_time_button, anchor = "c")
s_time_button.place(relx=0.5, rely=0.2, relheight=0.2, relwidth=1, anchor="n")

s_notification_button = tk.Button(s_menu_frame, image=notification_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_notification_button, anchor = "c")
s_notification_button.place(relx=0.5, rely=0.4, relheight=0.2, relwidth=1, anchor="n")

s_wifi_button = tk.Button(s_menu_frame, image=wifi_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_wifi_button, anchor = "c")
s_wifi_button.place(relx=0.5, rely=0.6, relheight=0.2, relwidth=1, anchor="n")

s_mode_button = tk.Button(s_menu_frame, image=cloud_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_mode_button, anchor = "c")
s_mode_button.place(relx=0.5, rely=0.6, relheight=0.2, relwidth=1, anchor="n")

s_lines = []
for line_count in range(5):
    s_lines.append(tk.Frame(s_menu_frame, bg=colours["s_menu_ln"]))
s_lines[0].place(width=2, relheight=1, relx=1, rely=0, anchor="ne")
s_lines[1].place(relwidth=1, height=2, relx=0, rely=0.2, anchor="w")
s_lines[2].place(relwidth=1, height=2, relx=0, rely=0.4, anchor="w")
s_lines[3].place(relwidth=1, height=2, relx=0, rely=0.6, anchor="w")
s_lines[4].place(relwidth=1, height=2, relx=0, rely=0.8, anchor="w")


s_time_frame = tk.Frame(settings_page, bg=colours["s_content_bg"])
s_time_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

s_time_title = tk.Label(s_time_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",24,"underline"), text="Time Settings", padx=10, pady=10, anchor="w")
s_time_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

s_time_morning_frame = tk.Frame(s_time_frame, bg=colours["s_content_bg"])
s_time_morning_label = tk.Label(s_time_morning_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="Morning: ", padx=10, pady=10, anchor="w")
s_time_morning_button = tk.Button(s_time_morning_frame, bg=colours["s_content_entry"], activebackground=colours["s_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, state="disabled", font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_numpad_button(settings_page, "Morning Time", s_time_morning_button, 2))
s_time_morning_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
s_time_morning_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
s_time_morning_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

s_time_afternoon_frame = tk.Frame(s_time_frame, bg=colours["s_content_bg"])
s_time_afternoon_label = tk.Label(s_time_afternoon_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="Afternoon: ", padx=10, pady=10, anchor="w")
s_time_afternoon_button = tk.Button(s_time_afternoon_frame, bg=colours["s_content_entry"], activebackground=colours["s_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, state="disabled", font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_numpad_button(settings_page, "Afternoon Time", s_time_afternoon_button, 2))
s_time_afternoon_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
s_time_afternoon_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
s_time_afternoon_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

s_time_evening_frame = tk.Frame(s_time_frame, bg=colours["s_content_bg"])
s_time_evening_label = tk.Label(s_time_evening_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="Evening: ", padx=10, pady=10, anchor="w")
s_time_evening_button = tk.Button(s_time_evening_frame, bg=colours["s_content_entry"], activebackground=colours["s_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, state="disabled", font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_numpad_button(settings_page, "Evening Time", s_time_evening_button, 2))
s_time_evening_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
s_time_evening_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
s_time_evening_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

s_time_night_frame = tk.Frame(s_time_frame, bg=colours["s_content_bg"])
s_time_night_label = tk.Label(s_time_night_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="Night: ", padx=10, pady=10, anchor="w")
s_time_night_button = tk.Button(s_time_night_frame, bg=colours["s_content_entry"], activebackground=colours["s_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, state="disabled", font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666", command = lambda: open_numpad_button(settings_page, "Night Time", s_time_night_button, 2))
s_time_night_frame.place(relx = 0.05, rely = 0.56, relwidth = 0.9, relheight = 0.08)
s_time_night_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
s_time_night_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

s_time_message = tk.Label(s_time_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
s_time_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

s_time_button_frame = tk.Frame(s_time_frame, bg=colours["s_content_bg"])
s_time_edit_button = tk.Button(s_time_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Edit", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=setting_time_edit_button)
s_time_save_button = tk.Button(s_time_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Save", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=setting_time_save_button)
s_time_cancel_button = tk.Button(s_time_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=setting_time_cancel_button)
s_time_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
s_time_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
s_time_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
s_time_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)


s_notification_frame = tk.Frame(settings_page, bg=colours["s_content_bg"])
s_notification_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

s_notification_title = tk.Label(s_notification_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",24,"underline"), text="Notification Settings", padx=10, pady=10, anchor="w")
s_notification_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)


s_exhaust_weeks = tk.IntVar()
s_exhaust_weeks.set(4)
s_exhaust_weeks_options = [1,2,3,4,8]

s_notification_exhaust_frame = tk.Frame(s_notification_frame, bg=colours["s_content_bg"])
s_notification_exhaust_label = tk.Label(s_notification_exhaust_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="Alert me when pills less than ", padx=10, pady=10, anchor="w")
s_notification_exhaust_button = tk.OptionMenu(s_notification_exhaust_frame, s_exhaust_weeks, *s_exhaust_weeks_options)
s_notification_exhaust_label_end = tk.Label(s_notification_exhaust_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="weeks.", padx=10, pady=10, anchor="w")
s_notification_exhaust_button.configure(bg=colours["s_content_entry"], activebackground=colours["s_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, state="disabled", font=("Trebuchet MS",18), anchor="c", disabledforeground="#666666")
s_notification_exhaust_button["menu"].configure(bg=colours["s_content_entry"], activebackground=colours["s_content_entry_p"], activeforeground="black", font=("Trebuchet MS",16))
s_notification_exhaust_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
s_notification_exhaust_label.place(relx = 0, rely = 0, relwidth = 0.55, relheight = 1)
s_notification_exhaust_button.place(relx = 0.55, rely = 0, relwidth = 0.15, relheight = 1)
s_notification_exhaust_label_end.place(relx = 0.70, rely = 0, relwidth = 0.30, relheight = 1)

s_notificaton_message = tk.Label(s_notification_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
s_notificaton_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

s_notificaton_button_frame = tk.Frame(s_notification_frame, bg=colours["s_content_bg"])
s_notificaton_edit_button = tk.Button(s_notificaton_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Edit", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=setting_notification_edit_button)
s_notificaton_save_button = tk.Button(s_notificaton_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Save", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=setting_notification_save_button)
s_notificaton_cancel_button = tk.Button(s_notificaton_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Cancel", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=setting_notification_cancel_button)
s_notificaton_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
s_notificaton_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
s_notificaton_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
s_notificaton_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)


s_wifi_frame = tk.Frame(settings_page, bg=colours["s_content_bg"])
s_wifi_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

s_wifi_title = tk.Label(s_wifi_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",24,"underline"), text="Wifi Settings", padx=10, pady=10, anchor="w")
s_wifi_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

s_wifi_wifi_frame = tk.Frame(s_wifi_frame, bg=colours["s_content_bg"])
s_wifi_wifi_label = tk.Label(s_wifi_wifi_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text="Wifi: ", padx=10, pady=10, anchor="w")
s_wifi_wifi_button = tk.Button(s_wifi_wifi_frame, bg=colours["s_content_entry"], activebackground=colours["s_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, state="disabled", font=("Trebuchet MS",18), anchor="w", disabledforeground="#666666")
s_wifi_wifi_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
s_wifi_wifi_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
s_wifi_wifi_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

s_wifi_button_frame = tk.Frame(s_wifi_frame, bg=colours["s_content_bg"])
s_wifi_configure_button = tk.Button(s_wifi_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Configure", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=lambda:goto_wifi_page_button(False))
s_wifi_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
s_wifi_configure_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)


s_mode_frame = tk.Frame(settings_page, bg=colours["s_content_bg"])
s_mode_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

s_mode_title = tk.Label(s_mode_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",24,"underline"), text="Switch to Online Mode", padx=10, pady=10, anchor="w")
s_mode_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

s_mode_info_frame = tk.Frame(s_mode_frame, bg=colours["s_content_bg"])
s_mode_info_label = tk.Label(s_mode_info_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), text=f"Switch to Online Mode?\nRequires WiFi Connection and enables data sharing.", padx=10, pady=10, anchor="w", justify="left")
s_mode_info_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.2)
s_mode_info_label.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

s_mode_message = tk.Label(s_mode_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",18), fg="red", padx=10, pady=10, anchor="w")
s_mode_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

s_mode_button_frame = tk.Frame(s_mode_frame, bg=colours["s_content_bg"])
s_mode_configure_button = tk.Button(s_mode_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Change Mode", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=setting_mode_configure_button)
s_mode_confirm_button = tk.Button(s_mode_button_frame, bg=colours["s_content_bn_u"], activebackground=colours["s_content_bn_p"], font=("Trebuchet MS",18), text="Confirm", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=setup_online_button_command)
s_mode_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
s_mode_configure_button.place(relx = 0.10, rely = 0, relwidth = 0.3, relheight = 1)
s_mode_confirm_button.place(relx = 0.6, rely = 0, relwidth = 0.3, relheight = 1)





numpad_page = Page(window, bg=colours["n_bg"])
numpad_page.place(x=0, y=0, relwidth=1, relheight=1)

n_content = tk.Frame(numpad_page, bg=colours["n_content"])
n_content.place(relx=0, y=0, relwidth=0.5, relheight=1)
n_numpad = tk.Frame(numpad_page, bg=colours["n_bg"])
n_numpad.place(relx=0.5, y=0, relwidth=0.5, relheight=1)

n_title = tk.Label(n_content, bg=colours["n_content"], font=("Trebuchet MS",24), anchor = "w")
n_entry = tk.Entry(n_content, bg=colours["n_entry"], borderwidth=2, relief="sunken", font=("Trebuchet MS",18))
n_message = tk.Label(n_content, bg=colours["n_content"], font=("Trebuchet MS",18), fg="red", anchor = "w")

n_title.place(relx=0.05, rely=0.08, relwidth=0.9, relheight=0.08)
n_entry.place(relx=0.05, rely=0.20, relwidth=0.9, relheight=0.08)
n_message.place(relx=0.05, rely=0.32, relwidth=0.9, relheight=0.08)

n_row_1 = tk.Frame(n_numpad, bg=colours["n_bg"])
n_row_2 = tk.Frame(n_numpad, bg=colours["n_bg"])
n_row_3 = tk.Frame(n_numpad, bg=colours["n_bg"])
n_row_4 = tk.Frame(n_numpad, bg=colours["n_bg"])
n_row_1.place(relx=0.05, rely=0.1, relwidth=0.9, relheight=0.2)
n_row_2.place(relx=0.05, rely=0.3, relwidth=0.9, relheight=0.2)
n_row_3.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.2)
n_row_4.place(relx=0.05, rely=0.7, relwidth=0.9, relheight=0.2)

#Row 1
n_button_7 = tk.Button(n_row_1, text = "7", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(7))
n_button_8 = tk.Button(n_row_1, text = "8", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(8))
n_button_9 = tk.Button(n_row_1, text = "9", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(9))
n_button_backspace = tk.Button(n_row_1, text = "⌫", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = numpad_backspace_button)
n_button_7.place(relx=0, rely=0, relwidth=0.25, relheight=1)
n_button_8.place(relx=0.25, rely=0, relwidth=0.25, relheight=1)
n_button_9.place(relx=0.5, rely=0, relwidth=0.25, relheight=1)
n_button_backspace.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

#Row 2
n_button_4 = tk.Button(n_row_2, text = "4", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(4))
n_button_5 = tk.Button(n_row_2, text = "5", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(5))
n_button_6 = tk.Button(n_row_2, text = "6", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(6))
n_button_special_1 = tk.Button(n_row_2, text = "−", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_math_button(1))
n_button_4.place(relx=0, rely=0, relwidth=0.25, relheight=1)
n_button_5.place(relx=0.25, rely=0, relwidth=0.25, relheight=1)
n_button_6.place(relx=0.5, rely=0, relwidth=0.25, relheight=1)
n_button_special_1.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

#Row 3
n_button_1 = tk.Button(n_row_3, text = "1", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(1))
n_button_2 = tk.Button(n_row_3, text = "2", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(2))
n_button_3 = tk.Button(n_row_3, text = "3", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(3))
n_button_special_2 = tk.Button(n_row_3, text = "−", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_math_button(-1))
n_button_1.place(relx=0, rely=0, relwidth=0.25, relheight=1)
n_button_2.place(relx=0.25, rely=0, relwidth=0.25, relheight=1)
n_button_3.place(relx=0.5, rely=0, relwidth=0.25, relheight=1)
n_button_special_2.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

#Row 4
n_button_0 = tk.Button(n_row_4, text = "0", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",18), command = lambda: numpad_type_button(0))
n_button_cancel = tk.Button(n_row_4, text = "Cancel", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",16), command = numpad_cancel_button)
n_button_enter = tk.Button(n_row_4, text = "Save", padx = 20, pady = 20, bg=colours["n_bn_u"], activebackground=colours["n_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",16), command = numpad_enter_button)
n_button_0.place(relx=0, rely=0, relwidth=0.5, relheight=1)
n_button_cancel.place(relx=0.5, rely=0, relwidth=0.25, relheight=1)
n_button_enter.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

keyboard_page = Page(window, bg=colours["k_bg"])
keyboard_page.place(x=0, y=0, relwidth=1, relheight=1)


k_header = tk.Frame(keyboard_page, bg=colours["k_content"])
k_keyboard = tk.Frame(keyboard_page, bg=colours["k_bg"], highlightbackground=colours["k_ln"], highlightthickness=1)
k_row_1 = tk.Frame(k_keyboard, bg=colours["k_bg"])
k_row_2 = tk.Frame(k_keyboard, bg=colours["k_bg"])
k_row_3 = tk.Frame(k_keyboard, bg=colours["k_bg"])
k_row_4 = tk.Frame(k_keyboard, bg=colours["k_bg"])
k_row_5 = tk.Frame(k_keyboard, bg=colours["k_bg"])

k_header.place(relx=0, rely=0, relwidth=1, relheight=0.32)
k_keyboard.place(relx=0, rely=0.32, relwidth=1, relheight=0.68)
k_row_1.place(relx=0, rely=1/17, relwidth=1, relheight=3/17)
k_row_2.place(relx=0, rely=4/17, relwidth=1, relheight=3/17)
k_row_3.place(relx=0, rely=7/17, relwidth=1, relheight=3/17)
k_row_4.place(relx=0, rely=10/17, relwidth=1, relheight=3/17)
k_row_5.place(relx=0, rely=13/17, relwidth=1, relheight=3/17)

k_title = tk.Label(k_header, bg=colours["k_content"], font=("Trebuchet MS",24), anchor = "w")
k_entry = tk.Entry(k_header, bg=colours["k_entry"], borderwidth=2, relief="sunken", font=("Trebuchet MS",18))

k_title.place(relx=1/32, rely=1/8, relwidth=30/32, relheight=1/4)
k_entry.place(relx = 1/32, rely = 4/8, relwidth = 30/32, relheight = 1/4)


#Row 1
k_button_tilde = tk.Button(k_row_1, text = "~\n`", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('`')))
k_button_1 = tk.Button(k_row_1, text = "!\n1", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('1')))
k_button_2 = tk.Button(k_row_1, text = "@\n2", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('2')))
k_button_3 = tk.Button(k_row_1, text = "#\n3", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('3')))
k_button_4 = tk.Button(k_row_1, text = "$\n4", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('4')))
k_button_5 = tk.Button(k_row_1, text = "%\n5", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('5')))
k_button_6 = tk.Button(k_row_1, text = "^\n6", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('6')))
k_button_7 = tk.Button(k_row_1, text = "&\n7", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('7')))
k_button_8 = tk.Button(k_row_1, text = "*\n8", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('8')))
k_button_9 = tk.Button(k_row_1, text = "(\n9", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('9')))
k_button_0 = tk.Button(k_row_1, text = ")\n0", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('0')))
k_button_minus = tk.Button(k_row_1, text = "_\n-", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('-')))
k_button_equal = tk.Button(k_row_1, text = "+\n=", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('=')))
k_button_backspace = tk.Button(k_row_1, text = "←\nBackspace", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_backspace_button)

k_button_tilde.place(relx = 1/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_1.place(relx = 3/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_2.place(relx = 5/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_3.place(relx = 7/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_4.place(relx = 9/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_5.place(relx = 11/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_6.place(relx = 13/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_7.place(relx = 15/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_8.place(relx = 17/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_9.place(relx = 19/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_0.place(relx = 21/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_minus.place(relx = 23/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_equal.place(relx = 25/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_backspace.place(relx = 27/32, rely = 0, relwidth = 4/32, relheight=1)


#Row 2
k_button_clear = tk.Button(k_row_2, text = "Clear", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_clear_button)
k_button_q = tk.Button(k_row_2, text = "Q", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('q')))
k_button_w = tk.Button(k_row_2, text = "W", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('w')))
k_button_e = tk.Button(k_row_2, text = "E", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('e')))
k_button_r = tk.Button(k_row_2, text = "R", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('r')))
k_button_t = tk.Button(k_row_2, text = "T", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('t')))
k_button_y = tk.Button(k_row_2, text = "Y", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('y')))
k_button_u = tk.Button(k_row_2, text = "U", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('u')))
k_button_i = tk.Button(k_row_2, text = "I", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('i')))
k_button_o = tk.Button(k_row_2, text = "O", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('o')))
k_button_p = tk.Button(k_row_2, text = "P", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('p')))
k_button_square_open = tk.Button(k_row_2, text = "{\n[", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('[')))
k_button_square_close = tk.Button(k_row_2, text = "}\n]", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(']')))
k_button_backslash = tk.Button(k_row_2, text = "|\n\\", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('\\')))

k_button_clear.place(relx = 1/32, rely = 0, relwidth = 3/32, relheight=1)
k_button_q.place(relx = 4/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_w.place(relx = 6/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_e.place(relx = 8/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_r.place(relx = 10/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_t.place(relx = 12/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_y.place(relx = 14/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_u.place(relx = 16/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_i.place(relx = 18/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_o.place(relx = 20/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_p.place(relx = 22/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_square_open.place(relx = 24/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_square_close.place(relx = 26/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_backslash.place(relx = 28/32, rely = 0, relwidth = 3/32, relheight=1)


#Row 3
k_button_caps = tk.Button(k_row_3, text = "Caps", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_capslock_button)
k_button_a = tk.Button(k_row_3, text = "A", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('a')))
k_button_s = tk.Button(k_row_3, text = "S", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('s')))
k_button_d = tk.Button(k_row_3, text = "D", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('d')))
k_button_f = tk.Button(k_row_3, text = "F", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('f')))
k_button_g = tk.Button(k_row_3, text = "G", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('g')))
k_button_h = tk.Button(k_row_3, text = "H", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('h')))
k_button_j = tk.Button(k_row_3, text = "J", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('j')))
k_button_k = tk.Button(k_row_3, text = "K", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('k')))
k_button_l = tk.Button(k_row_3, text = "L", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('l')))
k_button_semicolon = tk.Button(k_row_3, text = ":\n;", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(';')))
k_button_aprostrophe = tk.Button(k_row_3, text = "\"\n'", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('\'')))
k_button_delete = tk.Button(k_row_3, text = "Delete", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_delete_button)

k_button_caps.place(relx = 1/32, rely = 0, relwidth = 4/32, relheight=1)
k_button_a.place(relx = 5/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_s.place(relx = 7/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_d.place(relx = 9/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_f.place(relx = 11/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_g.place(relx = 13/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_h.place(relx = 15/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_j.place(relx = 17/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_k.place(relx = 19/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_l.place(relx = 21/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_semicolon.place(relx = 23/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_aprostrophe.place(relx = 25/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_delete.place(relx = 27/32, rely = 0, relwidth = 4/32, relheight=1)


#Row 4
k_button_shift = tk.Button(k_row_4, text = "Shift", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_shift_button)
k_button_z = tk.Button(k_row_4, text = "Z", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('z')))
k_button_x = tk.Button(k_row_4, text = "X", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('x')))
k_button_c = tk.Button(k_row_4, text = "C", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('c')))
k_button_v = tk.Button(k_row_4, text = "V", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('v')))
k_button_b = tk.Button(k_row_4, text = "B", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('b')))
k_button_n = tk.Button(k_row_4, text = "N", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('n')))
k_button_m = tk.Button(k_row_4, text = "M", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('m')))
k_button_comma = tk.Button(k_row_4, text = "<\n,", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(',')))
k_button_period = tk.Button(k_row_4, text = ">\n.", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('.')))
k_button_slash = tk.Button(k_row_4, text = "?\n/", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('/')))
k_button_cancel = tk.Button(k_row_4, text = "Cancel", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_cancel_button)

k_button_shift.place(relx = 1/32, rely = 0, relwidth = 5/32, relheight=1)
k_button_z.place(relx = 6/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_x.place(relx = 8/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_c.place(relx = 10/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_v.place(relx = 12/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_b.place(relx = 14/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_n.place(relx = 16/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_m.place(relx = 18/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_comma.place(relx = 20/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_period.place(relx = 22/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_slash.place(relx = 24/32, rely = 0, relwidth = 2/32, relheight=1)
k_button_cancel.place(relx = 26/32, rely = 0, relwidth = 5/32, relheight=1)


#Row 5
k_button_space =tk.Button(k_row_5, text = "Space", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(' ')))
k_button_enter =tk.Button(k_row_5, text = "⮠\nEnter", padx = 20, pady = 20, bg=colours["k_bn_u"], activebackground=colours["k_bn_p"], borderwidth=1, relief="solid", font=("Trebuchet MS",12), command = keyboard_enter_button)

k_button_space.place(relx = 1/32, rely = 0, relwidth=25/32, relheight=1)
k_button_enter.place(relx = 26/32, rely = 0, relwidth=5/32, relheight=1)

#window.attributes("-fullscreen", True)

start_page.lift()
#keyboard_page.lift()

window.mainloop()