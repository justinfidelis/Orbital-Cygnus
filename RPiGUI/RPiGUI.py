import tkinter as tk
from PIL import ImageTk,Image
import math

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
        return

class pill:
    def __init__(self, name, icon_id, qty):
        self.name = name
        self.icon_id = icon_id
        self.qty = qty

def start_button():
    if app_mode == 0:
        setup_page.lift()
    else:
        main_page.lift()
    return

def goto_pill_page_button():
    pill_page.lift()
    pill_update_pill_icons()
    return

def goto_quantity_page_button():
    quantity_page.lift()
    return

def goto_setting_page_button():
    settings_page.lift()
    s_wifi_frame.lift()
    s_wifi_button.configure(background="#F28E6D")
    return

def goto_account_page_button():
    account_page.lift()
    a_general_frame.lift()
    a_general_button.configure(background="#EFB85F")
    a_sharing_button.configure(background="#F4D297")
    a_password_button.configure(background="#F4D297")
    a_logout_button.configure(background="#F4D297")
    return

def goto_main_page_button():
    main_page.lift()
    return

def open_keyboard_button(page, label, button):
    global current_entry_button, current_page
    keyboard_page.lift()
    k_entry.delete(0,"end")
    k_entry.insert(0,button.cget("text"))
    k_entry.icursor("end")
    k_header.configure(bg=label.cget("bg"))
    k_title.configure(bg=label.cget("bg"))
    k_entry.configure(bg=button.cget("bg"))
    k_title.configure(text=label.cget("text"))
    current_entry_button = button
    current_page = page


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


def keyboard_type_button(asc):
    global shift, capslock
    if shift or capslock:
        asc = capitalise(asc, capslock, shift)
    k_entry.insert("insert", chr(asc))

    if shift:
        shift = False
        k_button_shift.configure(relief="groove")
    return

def keyboard_backspace_button():
    index = k_entry.index("insert")
    k_entry.delete(index-1, index) 
    return

def keyboard_delete_button():
    index = k_entry.index("insert")
    k_entry.delete(index)
    return

def keyboard_clear_button():
    k_entry.delete(0, "end")
    return

def keyboard_capslock_button():
    global capslock
    if capslock:
        k_button_caps.configure(relief="groove")
    else:
        k_button_caps.configure(relief="sunken")
    capslock = not capslock
    return

def keyboard_shift_button():
    global shift
    shift = not shift
    if shift:
        k_button_shift.configure(relief="sunken")
    else:
        k_button_shift.configure(relief="groove")
    return

def keyboard_enter_button():
    current_entry_button.configure(text=k_entry.get())
    current_page.lift()
    return

def keyboard_cancel_button():
    current_page.lift()
    return

def pill_left_nav_button():
    global current_pill, pills
    current_pill = (current_pill - 1) % len(pills)
    pill_update_pill_icons()
    return

def pill_right_nav_button():
    global current_pill
    current_pill = (current_pill + 1) % len(pills)
    pill_update_pill_icons()
    return

def pill_update_pill_icons():
    p_pill_name_label.configure(text=pills[current_pill].name)
    p_pill_button.configure(image=pill_images[pills[current_pill].icon_id])
    return

def pill_detail_update_page(index):
    pd_pill_name_button.configure(text=pills[index].name)
    pd_pill_button.configure(image=pill_images_small[pills[index].icon_id])
    return

def pill_select_button(index):
    pill_detail_update_page(index)
    pill_detail_page.lift()
    return

def pill_detail_edit_button(index):
    return

def pill_dispenser_open(index):
    return

def account_general_button():
    a_general_button.configure(background="#EFB85F")
    a_sharing_button.configure(background="#F4D297")
    a_password_button.configure(background="#F4D297")
    a_logout_button.configure(background="#F4D297")
    a_general_frame.lift()
    return

def account_sharing_button():
    a_general_button.configure(background="#F4D297")
    a_sharing_button.configure(background="#EFB85F")
    a_password_button.configure(background="#F4D297")
    a_logout_button.configure(background="#F4D297")
    a_sharing_frame.lift()
    return

def account_password_button():
    a_general_button.configure(background="#F4D297")
    a_sharing_button.configure(background="#F4D297")
    a_password_button.configure(background="#EFB85F")
    a_logout_button.configure(background="#F4D297")
    a_password_frame.lift()
    return

def account_logout_button():
    a_general_button.configure(background="#F4D297")
    a_sharing_button.configure(background="#F4D297")
    a_password_button.configure(background="#F4D297")
    a_logout_button.configure(background="#EFB85F")
    a_logout_frame.lift()
    a_logout_confirm_button.configure(state="disabled")
    a_logout_logout_button.configure(state="normal")
    return

def account_general_edit_button():
    global temp_first_name, temp_last_name, temp_username
    a_general_edit_button.configure(state="disabled")
    a_general_save_button.configure(state="normal")
    a_general_cancel_button.configure(state="normal")
    a_first_name_button.configure(state="normal", cursor="xterm")
    a_last_name_button.configure(state="normal", cursor="xterm")
    a_username_button.configure(state="normal", cursor="xterm")
    temp_first_name = a_first_name_button.cget("text")
    temp_last_name = a_last_name_button.cget("text")
    temp_username = a_username_button.cget("text")
    return

def account_general_save_button():
    a_general_edit_button.configure(state="normal")
    a_general_save_button.configure(state="disabled")
    a_general_cancel_button.configure(state="disabled")
    a_first_name_button.configure(state="disabled", cursor="left_ptr")
    a_last_name_button.configure(state="disabled", cursor="left_ptr")
    a_username_button.configure(state="disabled", cursor="left_ptr")
    #Update database
    return

def account_general_cancel_button():
    a_general_edit_button.configure(state="normal")
    a_general_save_button.configure(state="disabled")
    a_general_cancel_button.configure(state="disabled")
    a_first_name_button.configure(state="disabled", cursor="left_ptr", text=temp_first_name)
    a_last_name_button.configure(state="disabled", cursor="left_ptr", text=temp_last_name)
    a_username_button.configure(state="disabled", cursor="left_ptr", text=temp_username)
    return

def account_sharing_edit_button():
    global temp_sharing_user1, temp_sharing_user2, temp_sharing_user3
    a_sharing_edit_button.configure(state="disabled")
    a_sharing_save_button.configure(state="normal")
    a_sharing_cancel_button.configure(state="normal")
    a_sharing_user1_button.configure(state="normal", cursor="xterm")
    a_sharing_user2_button.configure(state="normal", cursor="xterm")
    a_sharing_user3_button.configure(state="normal", cursor="xterm")
    temp_sharing_user1 = a_sharing_user1_button.cget("text")
    temp_sharing_user2 = a_sharing_user2_button.cget("text")
    temp_sharing_user3 = a_sharing_user3_button.cget("text")
    return

def account_sharing_save_button():
    a_sharing_edit_button.configure(state="normal")
    a_sharing_save_button.configure(state="disabled")
    a_sharing_cancel_button.configure(state="disabled")
    a_sharing_user1_button.configure(state="disabled", cursor="left_ptr")
    a_sharing_user2_button.configure(state="disabled", cursor="left_ptr")
    a_sharing_user3_button.configure(state="disabled", cursor="left_ptr")
    #Update database
    return

def account_sharing_cancel_button():
    a_sharing_edit_button.configure(state="normal")
    a_sharing_save_button.configure(state="disabled")
    a_sharing_cancel_button.configure(state="disabled")
    a_sharing_user1_button.configure(state="disabled", cursor="left_ptr", text=temp_sharing_user1)
    a_sharing_user2_button.configure(state="disabled", cursor="left_ptr", text=temp_sharing_user2)
    a_sharing_user3_button.configure(state="disabled", cursor="left_ptr", text=temp_sharing_user3)
    return

def account_password_change_button():
    #Update database code
    a_password_message.configure(text="Password changed successfully")
    a_password_current_button.configure(text="")
    a_password_new_button.configure(text="")
    a_password_confirm_button.configure(text="")
    return

def account_password_cancel_button():
    a_password_current_button.configure(text="")
    a_password_new_button.configure(text="")
    a_password_confirm_button.configure(text="")
    return

def account_logout_logout_button():
    a_logout_confirm_button.configure(state="normal")
    a_logout_logout_button.configure(state="disabled")
    return

def account_logout_confirm_button():
    #Logout code here
    return

def setting_wifi_button():
    s_wifi_frame.lift()
    return


keyboard_colour="#D8D8D8"
keyboard_colour_active="#C1C1C1"
#Pastel colours used: Blue "#98F3F9"; Green "#98F9CF"; Yellow "#F7EF99"; Orange "#F4D297"; Red "#F7B299"; Purple "#D9B1EF"
#Lighter colours used: Blue "#98F3F9"; Green "#B7F4DA"; Yellow "#F7EF99"; Orange "#F4E3CD"; Red "#F2D1C6"; Purple "#D9B1EF"
#Darker colours used: Blue "#98F3F9"; Green "#60F2B0"; Yellow "#F2E14B"; Orange "#EFB85F"; Red "#F28E6D"; Purple "#D9B1EF"


shift = False
capslock = False
app_mode = 1

#Initial set up = 0
#Offline mode = 1
#Online mode = 2

current_entry_button = None
current_page = None

temp_first_name = None
temp_last_name = None
temp_username = None

temp_sharing_user1 = None
temp_sharing_user2 = None
temp_sharing_user3 = None

add_pill = pill("Add Medicine", 0, 1)
pill_1 = pill("Aspirin", 5, 100)
pill_2 = pill("Omeprazole", 4, 100)

pills = [pill_1, pill_2, add_pill]

current_pill = 0

window = tk.Tk()
window.title("Cygnus App")
window.geometry("800x600")

start_image = ImageTk.PhotoImage(Image.open("Resources/start.png"))
pill_image = ImageTk.PhotoImage(Image.open("Resources/pill_icon.png"))
quantity_image = ImageTk.PhotoImage(Image.open("Resources/bar_chart_icon.png"))
person_image = ImageTk.PhotoImage(Image.open("Resources/person_icon.png"))
setting_image = ImageTk.PhotoImage(Image.open("Resources/setting_icon.png"))
left_arrow_image = ImageTk.PhotoImage(Image.open("Resources/left_arrow.png"))
right_arrow_image = ImageTk.PhotoImage(Image.open("Resources/right_arrow.png"))
back_icon_image = ImageTk.PhotoImage(Image.open("Resources/back_arrow.png"))
person_small_image = ImageTk.PhotoImage(Image.open("Resources/person_small_icon.png"))
group_image = ImageTk.PhotoImage(Image.open("Resources/group_icon.png"))
lock_image = ImageTk.PhotoImage(Image.open("Resources/lock_icon.png"))
logout_image = ImageTk.PhotoImage(Image.open("Resources/logout_icon.png"))
wifi_image = ImageTk.PhotoImage(Image.open("Resources/wifi_icon.png"))
pill_images = []
pill_images_small = []
pill_images.append(ImageTk.PhotoImage(Image.open("Resources/Pill_Icons/Add_Pill.png")))
pill_images_small.append(ImageTk.PhotoImage(Image.open("Resources/Pill_Icons/Add_Pill.png")))
for pill_counter in range(12):
    with Image.open(f"Resources/Pill_Icons/Pill{math.floor(pill_counter/6)}{pill_counter % 6}.png") as temp_image:
        pill_images.append(ImageTk.PhotoImage(temp_image))
        temp_image_small = temp_image.copy()
        temp_image.thumbnail((80,80))
        pill_images_small.append(ImageTk.PhotoImage(temp_image))

start_page = Page(window)
start_page.place(x=0, y=0, relwidth=1, relheight=1)
start_button = tk.Button(start_page, image=start_image, command = start_button, relief="sunken", borderwidth=0, bg="#98F3F9", activebackground="#98F3F9")
start_button.place(x=0, y=0, relwidth=1, relheight=1)

setup_page = Page(window, bg="#98F9CF")
setup_page.place(x=0, y=0, relwidth=1, relheight=1)
setup_offline_button = tk.Button(setup_page, text="Offline Mode", relief="sunken", borderwidth=0, bg="#98F3F9", activebackground="#98F3F9", font=("Trebuchet MS",24))
setup_offline_button.place(relwidth=0.5, relheight=1, relx=0, rely=0, anchor="nw")
setup_online_button = tk.Button(setup_page, text="Online Mode", relief="sunken", borderwidth=0, bg="#98F9CF", activebackground="#98F9CF", font=("Trebuchet MS",24))
setup_online_button.place(relwidth=0.5, relheight=1, relx=1, rely=0, anchor="ne")



main_page = Page(window, bg="#98F3F9")
main_page.place(relx=0, rely=0, relwidth=1, relheight=1)

m_dispense_frame = tk.Frame(main_page, bg="#98F3F9")
m_dispense_frame.place(relwidth=0.6, relheight=0.5, relx=0, rely=0, anchor="nw")


m_refill_frame = tk.Frame(main_page, bg="#98F3F9")
m_refill_frame.place(relwidth=0.6, relheight=0.5, relx=0, rely=0.5, anchor="nw")


m_status_frame = tk.Frame(main_page, bg="#F2F2F2")
m_status_frame.place(relwidth=0.4, relheight=0.1, relx=1, rely=0, anchor="ne")

m_pill_frame = tk.Frame(main_page, bg="#98F9CF")
m_pill_frame.place(relwidth=0.4, relheight=0.225, relx=1, rely=0.1, anchor="ne")
m_pill_button = tk.Button(m_pill_frame, bg="#98F9CF", image=pill_image, text=" Medicine", compound="left", activebackground="#98F9CF", relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_pill_page_button)
m_pill_button.place(relwidth = 1, relheight=1, relx=0, rely=0.5, anchor="w")

m_quantity_frame = tk.Frame(main_page, bg="#F7EF99")
m_quantity_frame.place(relwidth=0.4, relheight=0.225, relx=1, rely=0.325, anchor="ne")
m_quantity_button = tk.Button(m_quantity_frame, bg="#F7EF99", image=quantity_image, text=" Quantity", compound="left", activebackground="#F7EF99", relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_quantity_page_button)
m_quantity_button.place(relwidth = 1, relheight=1, relx=0, rely=0.5, anchor="w")

m_account_frame = tk.Frame(main_page, bg="#F4D297")
m_account_frame.place(relwidth=0.4, relheight=0.225, relx=1, rely=0.55, anchor="ne")
m_account_button = tk.Button(m_account_frame, bg="#F4D297", image=person_image, text=" Account", compound="left", activebackground="#F4D297", relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_account_page_button)
m_account_button.place(relwidth = 1, relheight=1, relx=0, rely=0.5, anchor="w")

m_settings_frame = tk.Frame(main_page, bg="#F4A497")
m_settings_frame.place(relwidth=0.4, relheight=0.225, relx=1, rely=0.775, anchor="ne")
m_setting_button = tk.Button(m_settings_frame, bg="#F7B299", image=setting_image, text=" Settings", compound="left", activebackground="#F7B299", relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_setting_page_button)
m_setting_button.place(relwidth = 1, relheight=1, relx=0, rely=0.5, anchor="w")

main_lines = []
for line_count in range(6):
    main_lines.append(tk.Frame(main_page, bg="white"))
main_lines[0].place(relwidth=0.4, height=2, relx=1, rely=0.1, anchor="e")
main_lines[1].place(relwidth=0.4, height=2, relx=1, rely=0.325, anchor="e")
main_lines[2].place(relwidth=0.4, height=2, relx=1, rely=0.55, anchor="e")
main_lines[3].place(relwidth=0.4, height=2, relx=1, rely=0.775, anchor="e")
main_lines[4].place(relwidth=0.6, height=2, relx=0, rely=0.5, anchor="w")
main_lines[5].place(width=2, relheight=1, relx=0.6, rely=0, anchor="n")

#Pill Page

pill_page = Page(window, bg="#98f9cf")
pill_page.place(relx=0, rely=0, relwidth=1, relheight=1)

p_pill_name_label = tk.Label(pill_page, text="", font=("Trebuchet MS", 24), bg="#98f9cf")
p_pill_name_label.place(relx=0.5, rely=0.08, relwidth=0.5, relheight=0.16, anchor="c")

p_left_button = tk.Button(pill_page, image=left_arrow_image, bg="#98f9cf", activebackground="#98f9cf", relief="sunken", borderwidth=0, command = pill_left_nav_button)
p_left_button.place(relx=0.04, rely=0.5, anchor="w")

p_right_button = tk.Button(pill_page, image=right_arrow_image, bg="#98f9cf", activebackground="#98f9cf", relief="sunken", borderwidth=0, command = pill_right_nav_button)
p_right_button.place(relx=0.96, rely=0.5, anchor="e")

p_back_button = tk.Button(pill_page, image=back_icon_image, bg="#98f9cf", activebackground="#60F2B0", relief="sunken", borderwidth=0, command = goto_main_page_button)
p_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.16, anchor="nw")

p_pill_button = tk.Button(pill_page, image = pill_images[0], bg="#98f9cf", activebackground="#98f9cf", relief="sunken", borderwidth=0, command = lambda:pill_select_button(current_pill))
p_pill_button.place(relx=0.5, rely=0.5, relwidth=0.3, relheight=0.4, anchor ="c")

#p_pill_left_label = tk.Label(pill_page, image = pill_images[0], bg="#98f9cf")


#Pill Details Page

pill_detail_page = Page(window, bg="#B7F4DA")
pill_detail_page.place(relx=0, rely=0, relwidth=1, relheight=1)

pd_back_button = tk.Button(pill_detail_page, image=back_icon_image, bg="#B7F4DA", activebackground="#60F2B0", relief="sunken", borderwidth=0, command = goto_pill_page_button)
pd_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.16, anchor="nw")

pd_pill_name_button = tk.Label(pill_detail_page, text="Medicine Name", font=("Trebuchet MS", 24), bg="#B7F4DA", activebackground="#B7F4DA", relief="sunken", borderwidth=0)
pd_pill_name_button.place(relx=0.5, rely=0.08, relwidth=0.5, relheight=0.16, anchor="c")

pd_pill_button = tk.Label(pill_detail_page, image = pill_images_small[1], bg="#B7F4DA", activebackground="#B7F4DA", relief="sunken", borderwidth=0)
pd_pill_button.place(relx=0.9, rely=0, relwidth=0.12, relheight=0.16, anchor ="ne")

pd_open_button = tk.Button(pill_detail_page, text="Open", font=("Trebuchet MS", 20), bg="#98f9cf", relief="groove", borderwidth=2, activebackground="#51F7AA", command=pill_dispenser_open(current_pill))
pd_open_button.place(relx=0.35, rely=0.85, relwidth=5/32, relheight=0.08, anchor="n")

pd_edit_button = tk.Button(pill_detail_page, text="Edit", font=("Trebuchet MS", 20), bg="#98f9cf", relief="groove", borderwidth=2, activebackground="#51F7AA")
pd_edit_button.place(relx=0.65, rely=0.85, relwidth=5/32, relheight=0.08, anchor="n")

pd_calendar_frame = tk.Frame(pill_detail_page, bg="#98f9cf", highlightbackground="white", highlightthickness=2)
pd_calendar_frame.place(relx=0.05, rely=0.5, relwidth=0.66, relheight=0.5, anchor ="w")

pd_cal_sunday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="S")
pd_cal_sunday.place(relx=5/12, rely=0, relwidth=1/12, relheight=0.2)
pd_cal_monday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="M")
pd_cal_monday.place(relx=6/12, rely=0, relwidth=1/12, relheight=0.2)
pd_cal_tuesday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="T")
pd_cal_tuesday.place(relx=7/12, rely=0, relwidth=1/12, relheight=0.2)
pd_cal_wednesday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="W")
pd_cal_wednesday.place(relx=8/12, rely=0, relwidth=1/12, relheight=0.2)
pd_cal_thursday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="T")
pd_cal_thursday.place(relx=9/12, rely=0, relwidth=1/12, relheight=0.2)
pd_cal_friday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="F")
pd_cal_friday.place(relx=10/12, rely=0, relwidth=1/12, relheight=0.2)
pd_cal_saturday = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="S")
pd_cal_saturday.place(relx=11/12, rely=0, relwidth=1/12, relheight=0.2)

pd_cal_time = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="Time", anchor="c")
pd_cal_time.place(relx=0, rely=0, relwidth=5/12, relheight=0.2)
pd_cal_morning = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="Morning", anchor="c")
pd_cal_morning.place(relx=0, rely=0.2, relwidth=3/12, relheight=0.2)
pd_cal_afternoon = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="Afternoon", anchor="c")
pd_cal_afternoon.place(relx=0, rely=0.4, relwidth=3/12, relheight=0.2)
pd_cal_evening = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="Evening", anchor="c")
pd_cal_evening.place(relx=0, rely=0.6, relwidth=3/12, relheight=0.2)
pd_cal_night = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="Night", anchor="c")
pd_cal_night.place(relx=0, rely=0.8, relwidth=3/12, relheight=0.2)

pd_cal_time_m = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="08:00", anchor="c")
pd_cal_time_m.place(relx=3/12, rely=0.2, relwidth=2/12, relheight=0.2)
pd_cal_time_a = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="12:00", anchor="c")
pd_cal_time_a.place(relx=3/12, rely=0.4, relwidth=2/12, relheight=0.2)
pd_cal_time_e = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="16:00", anchor="c")
pd_cal_time_e.place(relx=3/12, rely=0.6, relwidth=2/12, relheight=0.2)
pd_cal_time_n = tk.Label(pd_calendar_frame, bg="#98f9cf", font=("Trebuchet MS", 16), text="20:00", anchor="c")
pd_cal_time_n.place(relx=3/12, rely=0.8, relwidth=2/12, relheight=0.2)

pd_cal_lines = []
for line_count in range(12):
    pd_cal_lines.append(tk.Frame(pd_calendar_frame, bg="white"))
pd_cal_lines[0].place(relwidth=1, height=2, relx=0, rely=0.2, anchor="w")
pd_cal_lines[1].place(relwidth=1, height=2, relx=0, rely=0.4, anchor="w")
pd_cal_lines[2].place(relwidth=1, height=2, relx=0, rely=0.6, anchor="w")
pd_cal_lines[3].place(relwidth=1, height=2, relx=0, rely=0.8, anchor="w")
pd_cal_lines[4].place(width=2, relheight=0.8, relx=3/12, rely=0.2, anchor="n")
pd_cal_lines[5].place(width=2, relheight=1, relx=5/12, rely=0, anchor="n")
pd_cal_lines[6].place(width=2, relheight=1, relx=6/12, rely=0, anchor="n")
pd_cal_lines[7].place(width=2, relheight=1, relx=7/12, rely=0, anchor="n")
pd_cal_lines[8].place(width=2, relheight=1, relx=8/12, rely=0, anchor="n")
pd_cal_lines[9].place(width=2, relheight=1, relx=9/12, rely=0, anchor="n")
pd_cal_lines[10].place(width=2, relheight=1, relx=10/12, rely=0, anchor="n")
pd_cal_lines[11].place(width=2, relheight=1, relx=11/12, rely=0, anchor="n")

#Quantity Page

quantity_page = Page(window, bg="#F7EF99")
quantity_page.place(x=0, y=0, relwidth=1, relheight=1)

q_back_button = tk.Button(quantity_page, image=back_icon_image, bg="#F7EF99", activebackground="#F2E14B", relief="sunken", borderwidth=0, command=goto_main_page_button)
q_back_button.place(relx=0, rely=0, relwidth=0.12, relheight=0.16, anchor="nw")



account_page = Page(window, bg="#F4D297")
account_page.place(x=0, y=0, relwidth=1, relheight=1)

a_menu_frame = tk.Frame(account_page, bg="#F4D297")
a_menu_frame.place(relx = 0, rely = 0, relwidth = 0.12, relheight = 1)

a_back_button = tk.Button(a_menu_frame, image=back_icon_image, bg="#F4D297", activebackground="#EFB85F", relief="sunken", borderwidth=0, command=goto_main_page_button, anchor = "c")
a_back_button.place(relx=0.5, rely=0.0, relheight=0.16, relwidth=1, anchor="n")

a_general_button = tk.Button(a_menu_frame, image=person_small_image, bg="#F4D297", activebackground="#EFB85F", relief="sunken", borderwidth=0, command=account_general_button, anchor = "c")
a_general_button.place(relx=0.5, rely=0.16, relheight=0.21, relwidth=1, anchor="n")

a_sharing_button = tk.Button(a_menu_frame, image=group_image, bg="#F4D297", activebackground="#EFB85F", relief="sunken", borderwidth=0, command=account_sharing_button, anchor = "c")
a_sharing_button.place(relx=0.5, rely=0.37, relheight=0.21, relwidth=1, anchor="n")

a_password_button = tk.Button(a_menu_frame, image=lock_image, bg="#F4D297", activebackground="#EFB85F", relief="sunken", borderwidth=0, command=account_password_button, anchor = "c")
a_password_button.place(relx=0.5, rely=0.58, relheight=0.21, relwidth=1, anchor="n")

a_logout_button = tk.Button(a_menu_frame, image=logout_image, bg="#F4D297", activebackground="#EFB85F", relief="sunken", borderwidth=0, command=account_logout_button, anchor = "c")
a_logout_button.place(relx=0.5, rely=0.79, relheight=0.21, relwidth=1, anchor="n")

a_lines = []
for line_count in range(5):
    a_lines.append(tk.Frame(a_menu_frame, bg="white"))
a_lines[0].place(width=2, relheight=1, relx=1, rely=0, anchor="ne")
a_lines[1].place(relwidth=1, height=2, relx=0, rely=0.16, anchor="w")
a_lines[2].place(relwidth=1, height=2, relx=0, rely=0.37, anchor="w")
a_lines[3].place(relwidth=1, height=2, relx=0, rely=0.58, anchor="w")
a_lines[4].place(relwidth=1, height=2, relx=0, rely=0.79, anchor="w")

a_general_frame = tk.Frame(account_page, bg="#F4E3CD")
a_general_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_general_title = tk.Label(a_general_frame, bg="#F4E3CD", font=("Trebuchet MS",24,"underline"), text="General Account Settings", padx=10, pady=10, anchor="w")
a_general_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_email_frame = tk.Frame(a_general_frame, bg="#F4E3CD")
a_email_label = tk.Label(a_email_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="Email: ", padx=10, pady=10, anchor="w")
a_email_button = tk.Label(a_email_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=10, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666")

a_email_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_email_label.place(relx = 0, rely = 0, relwidth = 0.2, relheight = 1)
a_email_button.place(relx = 0.2, rely = 0, relwidth = 0.8, relheight = 1)

a_username_frame = tk.Frame(a_general_frame, bg="#F4E3CD")
a_username_label = tk.Label(a_username_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="Username: ", padx=10, pady=10, anchor="w")
a_username_button = tk.Button(a_username_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_username_label, a_username_button))
a_username_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_username_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_username_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_first_name_frame = tk.Frame(a_general_frame, bg="#F4E3CD")
a_first_name_label = tk.Label(a_first_name_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="First Name: ", padx=10, pady=10, anchor="w")
a_first_name_button = tk.Button(a_first_name_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_first_name_label, a_first_name_button))
a_first_name_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
a_first_name_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_first_name_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_last_name_frame = tk.Frame(a_general_frame, bg="#F4E3CD")
a_last_name_label = tk.Label(a_last_name_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="Last Name: ", padx=10, pady=10, anchor="w")
a_last_name_button = tk.Button(a_last_name_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_last_name_label, a_last_name_button))
a_last_name_frame.place(relx = 0.05, rely = 0.56, relwidth = 0.9, relheight = 0.08)
a_last_name_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_last_name_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_general_message = tk.Label(a_general_frame, bg="#F4E3CD", font=("Trebuchet MS",20), padx=10, pady=10, anchor="w")
a_general_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

a_general_button_frame = tk.Frame(a_general_frame, bg="#F4E3CD")
a_general_edit_button = tk.Button(a_general_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Edit", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_general_edit_button)
a_general_save_button = tk.Button(a_general_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Save", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_general_save_button)
a_general_cancel_button = tk.Button(a_general_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Cancel", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_general_cancel_button)
a_general_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_general_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
a_general_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
a_general_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)


a_sharing_frame = tk.Frame(account_page, bg="#F4E3CD")
a_sharing_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_sharing_title = tk.Label(a_sharing_frame, bg="#F4E3CD", font=("Trebuchet MS",24,"underline"), text="Data Sharing Settings", padx=10, pady=10, anchor="w")
a_sharing_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_sharing_user1_frame = tk.Frame(a_sharing_frame, bg="#F4E3CD")
a_sharing_user1_label = tk.Label(a_sharing_user1_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="User 1: ", padx=10, pady=10, anchor="w")
a_sharing_user1_button = tk.Button(a_sharing_user1_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user1_label, a_sharing_user1_button))
a_sharing_user1_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_sharing_user1_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user1_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_user2_frame = tk.Frame(a_sharing_frame, bg="#F4E3CD")
a_sharing_user2_label = tk.Label(a_sharing_user2_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="User 2: ", padx=10, pady=10, anchor="w")
a_sharing_user2_button = tk.Button(a_sharing_user2_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user2_label, a_sharing_user2_button))
a_sharing_user2_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_sharing_user2_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user2_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_user3_frame = tk.Frame(a_sharing_frame, bg="#F4E3CD")
a_sharing_user3_label = tk.Label(a_sharing_user3_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="User 3: ", padx=10, pady=10, anchor="w")
a_sharing_user3_button = tk.Button(a_sharing_user3_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user3_label, a_sharing_user3_button))
a_sharing_user3_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
a_sharing_user3_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user3_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_message = tk.Label(a_sharing_frame, bg="#F4E3CD", font=("Trebuchet MS",20), padx=10, pady=10, anchor="w")
a_sharing_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)

a_sharing_button_frame = tk.Frame(a_sharing_frame, bg="#F4E3CD")
a_sharing_edit_button = tk.Button(a_sharing_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Edit", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_sharing_edit_button)
a_sharing_save_button = tk.Button(a_sharing_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Save", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_sharing_save_button)
a_sharing_cancel_button = tk.Button(a_sharing_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Cancel", padx=10, pady=10, anchor="c", state="disabled", disabledforeground="#666666", command=account_sharing_cancel_button)
a_sharing_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_sharing_edit_button.place(relx = 0.1, rely = 0, relwidth = 0.2, relheight = 1)
a_sharing_save_button.place(relx = 0.4, rely = 0, relwidth = 0.2, relheight = 1)
a_sharing_cancel_button.place(relx = 0.7, rely = 0, relwidth = 0.2, relheight = 1)


a_password_frame = tk.Frame(account_page, bg="#F4E3CD")
a_password_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_password_title = tk.Label(a_password_frame, bg="#F4E3CD", font=("Trebuchet MS",24,"underline"), text="Change Password", padx=10, pady=10, anchor="w")
a_password_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_password_current_frame = tk.Frame(a_password_frame, bg="#F4E3CD")
a_password_current_label = tk.Label(a_password_current_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="Current Password: ", padx=10, pady=10, anchor="w")
a_password_current_button = tk.Button(a_password_current_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_password_current_label, a_password_current_button))
a_password_current_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_password_current_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
a_password_current_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

a_password_new_frame = tk.Frame(a_password_frame, bg="#F4E3CD")
a_password_new_label = tk.Label(a_password_new_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="New Password: ", padx=10, pady=10, anchor="w")
a_password_new_button = tk.Button(a_password_new_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_password_new_label, a_password_new_button))
a_password_new_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_password_new_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
a_password_new_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

a_password_confirm_frame = tk.Frame(a_password_frame, bg="#F4E3CD")
a_password_confirm_label = tk.Label(a_password_confirm_frame, bg="#F4E3CD", font=("Trebuchet MS",20), text="Confirm New Password: ", padx=10, pady=10, anchor="w")
a_password_confirm_button = tk.Button(a_password_confirm_frame, bg="#F4D297", activebackground="#F4D297", borderwidth=2, relief="sunken", padx=5, pady=10, font=("Trebuchet MS",20), anchor="w", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_password_confirm_label, a_password_confirm_button))
a_password_confirm_frame.place(relx = 0.05, rely = 0.44, relwidth = 0.9, relheight = 0.08)
a_password_confirm_label.place(relx = 0, rely = 0, relwidth = 0.5, relheight = 1)
a_password_confirm_button.place(relx = 0.5, rely = 0, relwidth = 0.5, relheight = 1)

a_password_button_frame = tk.Frame(a_password_frame, bg="#F4E3CD")
a_password_change_button = tk.Button(a_password_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Change Password", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_password_change_button)
a_password_cancel_button = tk.Button(a_password_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Cancel", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_password_cancel_button)
a_password_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_password_change_button.place(relx = 0.1, rely = 0, relwidth = 0.4, relheight = 1)
a_password_cancel_button.place(relx = 0.6, rely = 0, relwidth = 0.3, relheight = 1)

a_password_message = tk.Label(a_password_frame, bg="#F4E3CD", font=("Trebuchet MS",20), padx=10, pady=10, anchor="w")
a_password_message.place(relx = 0.05, rely = 0.68, relwidth = 0.9, relheight = 0.08)


a_logout_frame = tk.Frame(account_page, bg="#F4E3CD")
a_logout_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

a_logout_title = tk.Label(a_logout_frame, bg="#F4E3CD", font=("Trebuchet MS",24,"underline"), text="Logout", padx=10, pady=10, anchor="w")
a_logout_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

a_logout_button_frame = tk.Frame(a_logout_frame, bg="#F4E3CD")
a_logout_logout_button = tk.Button(a_logout_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Logout", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_logout_logout_button)
a_logout_confirm_button = tk.Button(a_logout_button_frame, bg="#F4D297", activebackground="#EFB85F", font=("Trebuchet MS",20), text="Confirm", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_logout_confirm_button)
a_logout_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_logout_logout_button.place(relx = 0.2, rely = 0, relwidth = 0.2, relheight = 1)
a_logout_confirm_button.place(relx = 0.6, rely = 0, relwidth = 0.2, relheight = 1)



settings_page = Page(window, bg="#F2D1C6")
settings_page.place(x=0, y=0, relwidth=1, relheight=1)

s_menu_frame = tk.Frame(settings_page, bg="#F7B299")
s_menu_frame.place(relx = 0, rely = 0, relwidth = 0.12, relheight = 1)

s_back_button = tk.Button(s_menu_frame, image=back_icon_image, bg="#F7B299", activebackground="#F28E6D", relief="sunken", borderwidth=0, command=goto_main_page_button, anchor = "c")
s_back_button.place(relx=0.5, rely=0.0, relheight=0.16, relwidth=1, anchor="n")

s_wifi_button = tk.Button(s_menu_frame, image=wifi_image, bg="#F7B299", activebackground="#F28E6D", relief="sunken", borderwidth=0, command=goto_main_page_button, anchor = "c")
s_wifi_button.place(relx=0.5, rely=0.16, relheight=0.21, relwidth=1, anchor="n")

s_lines = []
for line_count in range(3):
    s_lines.append(tk.Frame(s_menu_frame, bg="white"))
s_lines[0].place(width=2, relheight=1, relx=1, rely=0, anchor="ne")
s_lines[1].place(relwidth=1, height=2, relx=0, rely=0.16, anchor="w")
s_lines[2].place(relwidth=1, height=2, relx=0, rely=0.37, anchor="w")

s_wifi_frame = tk.Frame(settings_page, bg="#F2D1C6")
s_wifi_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)


keyboard_page = Page(window, bg=keyboard_colour)
keyboard_page.place(x=0, y=0, relwidth=1, relheight=1)


k_header = tk.Frame(keyboard_page, bg=keyboard_colour)
k_keyboard = tk.Frame(keyboard_page, bg=keyboard_colour, highlightbackground="#000000", highlightthickness=1)
k_row_1 = tk.Frame(k_keyboard, bg=keyboard_colour)
k_row_2 = tk.Frame(k_keyboard, bg=keyboard_colour)
k_row_3 = tk.Frame(k_keyboard, bg=keyboard_colour)
k_row_4 = tk.Frame(k_keyboard, bg=keyboard_colour)
k_row_5 = tk.Frame(k_keyboard, bg=keyboard_colour)

k_header.place(relx=0, rely=0, relwidth=1, relheight=0.32)
k_keyboard.place(relx=0, rely=0.32, relwidth=1, relheight=0.68)
k_row_1.place(relx=0, rely=1/17, relwidth=1, relheight=3/17)
k_row_2.place(relx=0, rely=4/17, relwidth=1, relheight=3/17)
k_row_3.place(relx=0, rely=7/17, relwidth=1, relheight=3/17)
k_row_4.place(relx=0, rely=10/17, relwidth=1, relheight=3/17)
k_row_5.place(relx=0, rely=13/17, relwidth=1, relheight=3/17)

k_title = tk.Label(k_header, bg=keyboard_colour, font=("Trebuchet MS",24), anchor = "w")
k_entry = tk.Entry(k_header, bg=keyboard_colour, borderwidth=2, relief="sunken", font=("Trebuchet MS",20))

k_title.place(relx=1/32, rely=1/8, relwidth=30/32, relheight=1/4)
k_entry.place(relx = 1/32, rely = 4/8, relwidth = 30/32, relheight = 1/4)


#Row 1
k_button_tilde = tk.Button(k_row_1, text = "~\n`", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('`')))
k_button_1 = tk.Button(k_row_1, text = "!\n1", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('1')))
k_button_2 = tk.Button(k_row_1, text = "@\n2", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('2')))
k_button_3 = tk.Button(k_row_1, text = "#\n3", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('3')))
k_button_4 = tk.Button(k_row_1, text = "$\n4", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('4')))
k_button_5 = tk.Button(k_row_1, text = "%\n5", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('5')))
k_button_6 = tk.Button(k_row_1, text = "^\n6", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('6')))
k_button_7 = tk.Button(k_row_1, text = "&\n7", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('7')))
k_button_8 = tk.Button(k_row_1, text = "*\n8", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('8')))
k_button_9 = tk.Button(k_row_1, text = "(\n9", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('9')))
k_button_0 = tk.Button(k_row_1, text = ")\n0", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('0')))
k_button_minus = tk.Button(k_row_1, text = "_\n-", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('-')))
k_button_equal = tk.Button(k_row_1, text = "+\n=", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('=')))
k_button_backspace = tk.Button(k_row_1, text = "Backspace", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_backspace_button)

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
k_button_clear = tk.Button(k_row_2, text = "Clear", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_clear_button)
k_button_q = tk.Button(k_row_2, text = "Q", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('q')))
k_button_w = tk.Button(k_row_2, text = "W", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('w')))
k_button_e = tk.Button(k_row_2, text = "E", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('e')))
k_button_r = tk.Button(k_row_2, text = "R", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('r')))
k_button_t = tk.Button(k_row_2, text = "T", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('t')))
k_button_y = tk.Button(k_row_2, text = "Y", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('y')))
k_button_u = tk.Button(k_row_2, text = "U", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('u')))
k_button_i = tk.Button(k_row_2, text = "I", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('i')))
k_button_o = tk.Button(k_row_2, text = "O", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('o')))
k_button_p = tk.Button(k_row_2, text = "P", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('p')))
k_button_square_open = tk.Button(k_row_2, text = "{\n[", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('[')))
k_button_square_close = tk.Button(k_row_2, text = "}\n]", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(']')))
k_button_backslash = tk.Button(k_row_2, text = "|\n\\", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('\\')))

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
k_button_caps = tk.Button(k_row_3, text = "Caps", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_capslock_button)
k_button_a = tk.Button(k_row_3, text = "A", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('a')))
k_button_s = tk.Button(k_row_3, text = "S", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('s')))
k_button_d = tk.Button(k_row_3, text = "D", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('d')))
k_button_f = tk.Button(k_row_3, text = "F", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('f')))
k_button_g = tk.Button(k_row_3, text = "G", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('g')))
k_button_h = tk.Button(k_row_3, text = "H", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('h')))
k_button_j = tk.Button(k_row_3, text = "J", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('j')))
k_button_k = tk.Button(k_row_3, text = "K", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('k')))
k_button_l = tk.Button(k_row_3, text = "L", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('l')))
k_button_semicolon = tk.Button(k_row_3, text = ":\n;", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(';')))
k_button_aprostrophe = tk.Button(k_row_3, text = "\"\n'", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('\'')))
k_button_delete = tk.Button(k_row_3, text = "Delete", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_delete_button)

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
k_button_shift = tk.Button(k_row_4, text = "Shift", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_shift_button)
k_button_z = tk.Button(k_row_4, text = "Z", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('z')))
k_button_x = tk.Button(k_row_4, text = "X", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('x')))
k_button_c = tk.Button(k_row_4, text = "C", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('c')))
k_button_v = tk.Button(k_row_4, text = "V", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('v')))
k_button_b = tk.Button(k_row_4, text = "B", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('b')))
k_button_n = tk.Button(k_row_4, text = "N", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('n')))
k_button_m = tk.Button(k_row_4, text = "M", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('m')))
k_button_comma = tk.Button(k_row_4, text = "<\n,", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(',')))
k_button_period = tk.Button(k_row_4, text = ">\n.", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('.')))
k_button_slash = tk.Button(k_row_4, text = "?\n/", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord('/')))
k_button_cancel = tk.Button(k_row_4, text = "Cancel", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_cancel_button)

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
k_button_space =tk.Button(k_row_5, text = "Space", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = lambda: keyboard_type_button(ord(' ')))
k_button_enter =tk.Button(k_row_5, text = "Enter", padx = 20, pady = 20, bg=keyboard_colour, activebackground=keyboard_colour_active, relief="groove", font=("Trebuchet MS",12), command = keyboard_enter_button)

k_button_space.place(relx = 1/32, rely = 0, relwidth=25/32, relheight=1)
k_button_enter.place(relx = 26/32, rely = 0, relwidth=5/32, relheight=1)

#window.attributes("-fullscreen", True)

start_page.lift()
#keyboard_page.lift()

window.mainloop()