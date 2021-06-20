import tkinter as tk
from PIL import ImageTk,Image
import math
import time
import pickle

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
        return

class pill:
    def __init__(self, name, icon_shape, icon_colour, qty, dosage_days, dosage_times, dosage_amount):
        self.name = name
        self.icon_shape = icon_shape
        self.icon_colour = icon_colour
        self.qty = qty
        self.dosage_days = dosage_days
        self.dosage_times = dosage_times
        self.dosage_amount = dosage_amount
        return
    def get_icon_id(self):
        if self.icon_shape == -1:
            return 0
        return 6 * self.icon_shape + self.icon_colour + 1

class user:
    def __init__(self, email, username, first_name, last_name, share_user1, share_user2, share_user3):
        self.email = email
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.share_user1 = share_user1
        self.share_user2 = share_user2
        self.share_user3 = share_user3
        return

class day_time:
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

class storage:
    def __init__(self, pills, times, mode):
        self.pills = pills
        self.times = times
        self.mode = mode
        return

def save_offline_data():
    temp_storage = storage(pills, times, app_mode)
    with open("user_data.p", "wb") as file:
        pickle.dump(temp_storage, file)
    return

def load_offline_data():
    global pills, times, app_mode
    try:
        with open("user_data.p", "rb") as file:
            temp_storage = pickle.load(open("user_data.p", "rb"))
            pills = temp_storage.pills
            times = temp_storage.times
            app_mode = temp_storage.mode
    except FileNotFoundError:
        pill_1 = pill("Aspirin", 1, 2, 100, [True, True, True, True, True, True, True],[True, False, False, True], 1) #For testing only
        pill_2 = pill("Omeprazole", 2, 4, 100, [False, True, True, True, True, True, False],[True, True, True, False], 2) #For testing only
        pills = [pill_1, pill_2, add_pill]
        times = [day_time(8,0), day_time(12,30), day_time(17,0), day_time(21,0)]
        app_mode = 0
    return

#Initial startup button
def start_button(): 
    global at_main
    load_offline_data()
    if app_mode == 0:
        setup_page.lift()
    else:
        #if app_mode == 1:

        #if app_mode == 2:
        goto_main_page_button()
    return

def setup_offline_button_command():
    global app_mode
    app_mode = 1
    goto_main_page_button()
    return

def setup_online_button_command():
    global app_mode
    app_mode = 2
    #goto login page
    return

def main_time_update():
    if at_main == True:
        m_time_label.configure(text=time.strftime(" %H:%M"))
        m_date_label.configure(text=time.strftime("%a, %d %B"))
        m_time_label.after(1000, main_time_update)
    return

#Dispense pills into pill container
def dispense_button():
    global at_main
    #hardware dispense function
    return

#Dispense pills into tray
def refill_button():
    global at_main
    #hardware refill function
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
    quantity_page.lift()
    at_main = False
    return

#Go to settings page
def goto_setting_page_button():
    global at_main
    settings_page.lift()
    setting_wifi_button()
    at_main = False
    return

#Go to account page
def goto_account_page_button():
    global at_main
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

def numpad_colon_button():
    n_entry.icursor("end")
    n_entry_length = len(n_entry.get())
    if ":" not in n_entry.get() and n_entry_length < 6 and n_entry_length > 0:
        n_entry.insert("end", ":")
    return

def numpad_backspace_button():
    global numpad_operator
    n_entry.icursor("end")
    index = n_entry.index("end")
    if index > 0 and (n_entry.get()[index-1] == "+" or n_entry.get()[index-1] == "−"):
        numpad_operator = 0
    n_entry.delete(index-1, index) 
    return

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
            temp_string = n_entry.get()
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
            #update charts
            #update database
        #<\especially bad code>
        current_page.lift()
    return

def numpad_cancel_button():
    current_page.lift()
    return

#Open keyboard; page: Page to return to after closing keyboard, label: Label that contains input title, button: Button that stores input text
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

#Pill Page: Update current pill
def pill_update_pill_icons():
    p_pill_name_label.configure(text=pills[current_pill].name)
    p_pill_button.configure(image=pill_images[pills[current_pill].get_icon_id()])
    p_message_label.configure(text="")
    return

#Pill Detail Page: Update page with current pill information 
def pill_detail_page_update(pill_index):
    pd_pill_name_button.configure(text=pills[pill_index].name)
    pd_pill_button.configure(image=pill_images_small[pills[pill_index].get_icon_id()])
    pd_qty_button.configure(text=pills[pill_index].qty)
    return

#Go to pill detail page
def goto_pill_detail_page_button(pill_index):
    if pill_index != len(pills) - 1:
        pill_detail_page_update(pill_index)
        pill_detail_page.lift()
    else:
        pills.insert(len(pills)-1,pill("New Pill",0,0,0,[True,True,True,True,True,True,True],[False,False,False,False],1))
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

def pill_edit_page_update():
    pe_pill_name_button.configure(text=pills[current_pill].name)
    pe_icon_button.configure(image=pill_images_small[pills[current_pill].get_icon_id()])
    return

def goto_pill_edit_page_button():
    pill_edit_page_update()
    pill_edit_page_icons_disable(pills[current_pill].icon_shape, pills[current_pill].icon_colour)
    pill_edit_page.lift()
    pill_edit_pill_button()
    return

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
    #Update database
    return

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

def pill_edit_pill_shape_button(shape_id):
    global temp_pill
    pe_icon_shape_buttons[temp_pill.icon_shape].configure(relief="flat", bg=colours["pe_content_bg"])
    temp_pill.icon_shape = shape_id
    pe_icon_shape_buttons[shape_id].configure(relief="sunken", bg=colours["pe_content_entry"])
    pe_icon_button.configure(image=pill_images_small[temp_pill.get_icon_id()])
    return

def pill_edit_pill_colour_button(colour_id):
    global temp_pill
    pe_icon_colour_buttons[temp_pill.icon_colour].configure(relief="flat", bg=colours["pe_content_bg"])
    temp_pill.icon_colour = colour_id
    pe_icon_colour_buttons[colour_id].configure(relief="sunken", bg=colours["pe_content_entry"])
    pe_icon_button.configure(image=pill_images_small[temp_pill.get_icon_id()])
    return

def pill_edit_schedule_day_buttons_update(day, dosage_days):
    if dosage_days[day]:
        pe_schedule_days_buttons[day].configure(relief="sunken", bg=colours["pe_content_entry"], borderwidth=2)
    else:
        pe_schedule_days_buttons[day].configure(relief="ridge", bg=colours["pe_content_bg"], borderwidth=2)
    return

def pill_edit_schedule_time_buttons_update(time, dosage_times):
    if dosage_times[time]:
        pe_schedule_times_buttons[time].configure(relief="sunken", bg=colours["pe_content_entry"], borderwidth=2)
    else:
        pe_schedule_times_buttons[time].configure(relief="ridge", bg=colours["pe_content_bg"], borderwidth=2)
    return

def pill_edit_schedule_days_button(day):
    global temp_pill
    temp_pill.dosage_days[day] = not temp_pill.dosage_days[day]
    pill_edit_schedule_day_buttons_update(day, temp_pill.dosage_days)
    return

def pill_edit_schedule_times_button(time):
    global temp_pill
    temp_pill.dosage_times[time] = not temp_pill.dosage_times[time]
    pill_edit_schedule_time_buttons_update(time, temp_pill.dosage_times)
    return

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

def pill_edit_schedule_buttons_disable():
    for count in range(7):
        pe_schedule_days_buttons[count].configure(command="")
    for count in range(4):
        pe_schedule_times_buttons[count].configure(command="")
    pe_schedule_amount_decrease_button.configure(command="")
    pe_schedule_amount_increase_button.configure(command="")
    return

def pill_edit_schedule_amount_decrease():
    global temp_pill
    if temp_pill.dosage_amount > 1:
        temp_pill.dosage_amount -= 1
    pe_schedule_amount_button.configure(text=temp_pill.dosage_amount)
    return

def pill_edit_schedule_amount_increase():
    global temp_pill
    if temp_pill.dosage_amount < 10:
        temp_pill.dosage_amount += 1
    pe_schedule_amount_button.configure(text=temp_pill.dosage_amount)
    return

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

def pill_edit_schedule_save_button():
    global pe_editing
    pe_schedule_edit_button.configure(state="normal")
    pe_schedule_save_button.configure(state="disabled")
    pe_schedule_cancel_button.configure(state="disabled")
    for count in range(7):
        pills[current_pill].dosage_days[count] = temp_pill.dosage_days[count]
    for count in range(4):
        pills[current_pill].dosage_times[count] = temp_pill.dosage_times[count]
    pills[current_pill].dosage_amount = temp_pill.dosage_amount
    save_offline_data()
    pill_edit_schedule_buttons_disable()
    pe_schedule_message_label.configure(text="")
    pe_editing = False
    #Update database
    return

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

def pill_edit_delete_delete_button():
    pe_delete_delete_button.configure(state="disabled")
    pe_delete_confirm_button.configure(state="normal")
    pe_delete_message_label.configure(text=f"Confirm deletion of {pills[current_pill].name}?\nThis cannot be undone.")
    return
    
def pill_edit_delete_confirm_button():
    text = pills[current_pill].name
    pills.pop(current_pill)
    save_offline_data()
    goto_pill_page_button()
    p_message_label.configure(text=f"{text} deleted sucessfully.")
    return

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

def pill_edit_pill_button():
    global current_pe_page
    if pe_editing == False:
        pe_pill_button.configure(bg=colours["pe_menu_bn_p"])
        pe_schedule_button.configure(bg=colours["pe_menu_bn_u"])
        pe_delete_button.configure(bg=colours["pe_menu_bn_u"])
        current_pe_page = 0
        pe_pill_frame.lift()
        return
    if current_pe_page == 1:
        pe_schedule_message_label.configure(text="Would you like to save recent changes?")
    return

def pill_edit_schedule_button():
    global current_pe_page
    if pe_editing == False:
        pe_pill_button.configure(bg=colours["pe_menu_bn_u"])
        pe_schedule_button.configure(bg=colours["pe_menu_bn_p"])
        pe_delete_button.configure(bg=colours["pe_menu_bn_u"])
        for count in range(7):
            pill_edit_schedule_day_buttons_update(count, pills[current_pill].dosage_days)
        for count in range(4):
            pill_edit_schedule_time_buttons_update(count, pills[current_pill].dosage_times)
        current_pe_page = 1
        pe_schedule_pill_icon.configure(image=pill_images_small[pills[current_pill].get_icon_id()])
        pe_schedule_frame.lift()
        return
    if current_pe_page == 0:
        pe_pill_message_label.configure(text="Would you like to save recent changes?")
    return

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

def pill_dispenser_open(index):
    #TODO hardware
    return

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
        return
    if current_a_page == 0:
        a_general_message.configure(text="Would you like to save recent changes?")
        return
    if current_a_page == 1:
        a_sharing_message.configure(text="Would you like to save recent changes?")
    return


def account_general_edit_button():
    global temp_user, a_editing
    a_general_edit_button.configure(state="disabled")
    a_general_save_button.configure(state="normal")
    a_general_cancel_button.configure(state="normal")
    a_first_name_button.configure(state="normal", cursor="xterm")
    a_last_name_button.configure(state="normal", cursor="xterm")
    a_username_button.configure(state="normal", cursor="xterm")
    temp_user.first_name = a_first_name_button.cget("text")
    temp_user.last_name = a_last_name_button.cget("text")
    temp_user.username = a_username_button.cget("text")
    a_editing = True
    return

def account_general_save_button():
    global a_editing
    a_general_edit_button.configure(state="normal")
    a_general_save_button.configure(state="disabled")
    a_general_cancel_button.configure(state="disabled")
    a_first_name_button.configure(state="disabled", cursor="left_ptr")
    a_last_name_button.configure(state="disabled", cursor="left_ptr")
    a_username_button.configure(state="disabled", cursor="left_ptr")
    a_editing = False
    a_general_message.configure(text="")
    #Update database
    return

def account_general_cancel_button():
    global a_editing
    a_general_edit_button.configure(state="normal")
    a_general_save_button.configure(state="disabled")
    a_general_cancel_button.configure(state="disabled")
    a_first_name_button.configure(state="disabled", cursor="left_ptr", text=temp_user.first_name)
    a_last_name_button.configure(state="disabled", cursor="left_ptr", text=temp_user.last_name)
    a_username_button.configure(state="disabled", cursor="left_ptr", text=temp_user.username)
    a_editing = False
    a_general_message.configure(text="")
    return

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

def setting_back_button():
    if s_editing == False:
        goto_main_page_button()
        return
    if current_s_page == 1:
        s_time_message.configure(text="Would you like to save recent changes?")
    return


def setting_wifi_button():
    global current_s_page
    if s_editing == False:
        s_wifi_frame.lift()
        current_s_page = 0
        s_wifi_button.configure(bg=colours["s_menu_bn_p"])
        s_time_button.configure(bg=colours["s_menu_bn_u"])
        return
    if current_s_page == 1:
        s_time_message.configure(text="Would you like to save recent changes?")
    return

def setting_time_button():
    global current_s_page
    if s_editing == False:
        s_time_morning_button.configure(text=times[0].to_string())
        s_time_afternoon_button.configure(text=times[1].to_string())
        s_time_evening_button.configure(text=times[2].to_string())
        s_time_night_button.configure(text=times[3].to_string())
        s_time_frame.lift()
        current_s_page = 1
        s_wifi_button.configure(bg=colours["s_menu_bn_u"])
        s_time_button.configure(bg=colours["s_menu_bn_p"])
    return

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

def setting_time_save_button():
    global s_editing, times
    s_time_edit_button.configure(state="normal")
    s_time_save_button.configure(state="disabled")
    s_time_cancel_button.configure(state="disabled")
    s_time_morning_button.configure(state="disabled", cursor="left_ptr")
    s_time_afternoon_button.configure(state="disabled", cursor="left_ptr")
    s_time_evening_button.configure(state="disabled", cursor="left_ptr")
    s_time_night_button.configure(state="disabled", cursor="left_ptr")
    times[0].from_string(s_time_morning_button.cget("text"))
    times[1].from_string(s_time_afternoon_button.cget("text"))
    times[2].from_string(s_time_evening_button.cget("text"))
    times[3].from_string(s_time_night_button.cget("text"))
    save_offline_data()
    s_editing = False
    s_time_message.configure(text="")
    #Update database
    return

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




#Pastel colours used: Blue "#98F3F9"; Green "#98F9CF"; Yellow "#F7EF99"; Orange "#F4D297"; Red "#F7B299"; Purple "#D9B1EF"
#Lighter colours used: Blue "#98F3F9"; Green "#B7F4DA"; Yellow "#F7EF99"; Orange "#F4E3CD"; Red "#F2D1C6"; Purple "#D9B1EF"
#Darker colours used: Blue "#98F3F9"; Green "#60F2B0"; Yellow "#F2E14B"; Orange "#EFB85F"; Red "#F28E6D"; Purple "#D9B1EF"

numpad_mode = 0
numpad_operator = 0

shift = False
capslock = False
app_mode = 1 #0: Initial set up; 1: Offline mode; 2: Online mode



current_entry_button = None
current_page = None

temp_user = user("","","","","","","")
temp_pill = pill("",0,0,0,[False, False, False, False, False, False, False],[False, False, False, False], 0)
temp_times = ["","","",""]

add_pill = pill("Add Medicine", -1, 0, 1, [False, False, False, False, False, False, False],[False, False, False, False], 1)

pills = []
times = []


current_time = time.localtime(time.time())

at_main = False

current_pill = 0

current_pe_page = 0 #0: Pill; 1: Calendar; 2: Delete
pe_editing = False

current_a_page = 0 #0: General; 1: Sharing; 2: Password; 3: Logout
a_editing = False

current_s_page = 0
s_editing = False

colours = {
    "start_bg": "#98F3F9",
    "setup_bg": "#98F3F9",
    "setup_ln": "#FFFFFF",
    "main_dispense_bg": "#98F3F9",
    "main_status_bg": "#F2F2F2",
    "main_pill_bg": "#98F9CF",
    "main_quantity_bg": "#F7EF99",
    "main_history_bg": "#F4D297",
    "main_account_bg": "#F7B299",
    "main_settings_bg": "#D9B1EF",
    "main_ln": "#FFFFFF",
    "pn_bg": "#98F3F9",
    "pn_menu_bn_u": "#98F3F9",
    "pn_menu_bn_p": "#74F0F7",
    "pd_bg": "#98F3F9",
    "pd_menu_bn_u": "#98F3F9",
    "pd_menu_bn_p": "#74F0F7",
    "pd_bn_u": "#F7EF99",
    "pd_bn_p": "#F2E14B",
    "pd_ln": "#FFFFFF",
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
dispense_image = ImageTk.PhotoImage(Image.open("Resources/dispense_icon.png"))
refill_image = ImageTk.PhotoImage(Image.open("Resources/refill_icon.png"))
pill_image = ImageTk.PhotoImage(Image.open("Resources/pill_icon.png"))
quantity_image = ImageTk.PhotoImage(Image.open("Resources/bar_chart_icon.png"))
history_image = ImageTk.PhotoImage(Image.open("Resources/history_icon.png"))
person_image = ImageTk.PhotoImage(Image.open("Resources/person_icon.png"))
setting_image = ImageTk.PhotoImage(Image.open("Resources/setting_icon.png"))
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
clock_image = ImageTk.PhotoImage(Image.open("Resources/clock_icon.png"))
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
        temp_image.thumbnail((35,35))
        pill_images_tiny.append(ImageTk.PhotoImage(temp_image))
colour_images = []
for image_counter in range(6):
    with Image.open(f"Resources/Pill_Icons/Colour{image_counter}.png") as temp_image:
        temp_image.thumbnail((30,30))
        colour_images.append(ImageTk.PhotoImage(temp_image))

start_page = Page(window)
start_page.place(x=0, y=0, relwidth=1, relheight=1)
start_button = tk.Button(start_page, image=start_image, command = start_button, relief="sunken", borderwidth=0, bg=colours["start_bg"], activebackground=colours["start_bg"])
start_button.place(x=0, y=0, relwidth=1, relheight=1)

setup_page = Page(window, bg=colours["setup_bg"])
setup_page.place(x=0, y=0, relwidth=1, relheight=1)
setup_offline_button = tk.Button(setup_page, text="Offline Mode", relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], font=("Trebuchet MS",24,"underline"), command=setup_offline_button_command)
setup_offline_button.place(relwidth=0.5, relheight=1, relx=0, rely=0, anchor="nw")
setup_online_button = tk.Button(setup_page, text="Online Mode", relief="sunken", borderwidth=0, bg=colours["setup_bg"], activebackground=colours["setup_bg"], font=("Trebuchet MS",24,"underline"), command=setup_online_button_command)
setup_online_button.place(relwidth=0.5, relheight=1, relx=1, rely=0, anchor="ne")

setup_line = tk.Frame(setup_page, bg=colours["setup_ln"])
setup_line.place(width=2, relheight=1, relx=0.5, rely=0, anchor="n")


main_page = Page(window, bg=colours["main_dispense_bg"])
main_page.place(relx=0, rely=0, relwidth=1, relheight=1)

m_dispense_frame = tk.Frame(main_page, bg=colours["main_dispense_bg"])
m_dispense_frame.place(relwidth=0.6, relheight=0.5, relx=0, rely=0, anchor="nw")
m_dispense_button = tk.Button(m_dispense_frame, bg=colours["main_dispense_bg"], image=dispense_image, text=" Dispense", compound="left", activebackground=colours["main_dispense_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="c", padx=20, command=dispense_button)
m_dispense_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_refill_frame = tk.Frame(main_page, bg=colours["main_dispense_bg"])
m_refill_frame.place(relwidth=0.6, relheight=0.5, relx=0, rely=0.5, anchor="nw")
m_refill_button = tk.Button(m_refill_frame, bg=colours["main_dispense_bg"], image=refill_image, text=" Refill", compound="left", activebackground=colours["main_dispense_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="c", padx=20, command=refill_button)
m_refill_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_status_frame = tk.Frame(main_page, bg=colours["main_status_bg"])
m_status_frame.place(relwidth=0.4, relheight=0.05, relx=1, rely=0, anchor="ne")

m_pill_frame = tk.Frame(main_page, bg=colours["main_pill_bg"])
m_pill_frame.place(relwidth=0.4, relheight=0.19, relx=1, rely=0.05, anchor="ne")
m_pill_button = tk.Button(m_pill_frame, bg=colours["main_pill_bg"], image=pill_image, text=" Medicine", compound="left", activebackground=colours["main_pill_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_pill_page_button)
m_pill_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_quantity_frame = tk.Frame(main_page, bg=colours["main_quantity_bg"])
m_quantity_frame.place(relwidth=0.4, relheight=0.19, relx=1, rely=0.24, anchor="ne")
m_quantity_button = tk.Button(m_quantity_frame, bg=colours["main_quantity_bg"], image=quantity_image, text=" Quantity", compound="left", activebackground=colours["main_quantity_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_quantity_page_button)
m_quantity_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_history_frame = tk.Frame(main_page, bg=colours["main_history_bg"])
m_history_frame.place(relwidth=0.4, relheight=0.19, relx=1, rely=0.43, anchor="ne")
m_history_button = tk.Button(m_history_frame, bg=colours["main_history_bg"], image=history_image, text=" History", compound="left", activebackground=colours["main_history_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_quantity_page_button)
m_history_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_account_frame = tk.Frame(main_page, bg=colours["main_account_bg"])
m_account_frame.place(relwidth=0.4, relheight=0.19, relx=1, rely=0.62, anchor="ne")
m_account_button = tk.Button(m_account_frame, bg=colours["main_account_bg"], image=person_image, text=" Account", compound="left", activebackground=colours["main_account_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_account_page_button)
m_account_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

m_settings_frame = tk.Frame(main_page, bg=colours["main_settings_bg"])
m_settings_frame.place(relwidth=0.4, relheight=0.19, relx=1, rely=0.81, anchor="ne")
m_setting_button = tk.Button(m_settings_frame, bg=colours["main_settings_bg"], image=setting_image, text=" Settings", compound="left", activebackground=colours["main_settings_bg"], relief="sunken", borderwidth=0, font=("Trebuchet MS",24), anchor="w", padx=20, command=goto_setting_page_button)
m_setting_button.place(relwidth = 1, relheight=1, relx=0, rely=0, anchor="nw")

#Status Frame

m_time_label = tk.Label(m_status_frame, bg=colours["main_status_bg"], text="", font=("Trebuchet MS",12), anchor="w")
m_time_label.place(relx=0, rely=0, relwidth=0.3, relheight=1)
m_date_label = tk.Label(m_status_frame, bg=colours["main_status_bg"], text="", font=("Trebuchet MS",12), anchor="c")
m_date_label.place(relx=0.5, rely=0, relwidth=0.4, relheight=1, anchor="n")

main_lines = []
for line_count in range(7):
    main_lines.append(tk.Frame(main_page, bg=colours["main_ln"]))
main_lines[0].place(relwidth=0.4, height=2, relx=1, rely=0.05, anchor="e")
main_lines[1].place(relwidth=0.4, height=2, relx=1, rely=0.24, anchor="e")
main_lines[2].place(relwidth=0.4, height=2, relx=1, rely=0.43, anchor="e")
main_lines[3].place(relwidth=0.4, height=2, relx=1, rely=0.62, anchor="e")
main_lines[4].place(relwidth=0.4, height=2, relx=1, rely=0.81, anchor="e")
main_lines[5].place(relwidth=0.6, height=2, relx=0, rely=0.5, anchor="w")
main_lines[6].place(width=2, relheight=1, relx=0.6, rely=0, anchor="n")





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
p_message_label.place(relx=0.5, rely=0.92, relwidth=0.5, relheight=0.08, anchor="s")

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

pd_chart_labels = []
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="Empty"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="1 Month"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="2 Months"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="3 Months"))
pd_chart_labels.append(tk.Label(pd_chart_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 16), text="4 Months"))

pd_chart_labels[0].place(relx=0.1, rely=0.9, relwidth=0.4, relheight=0.2, anchor="w")
pd_chart_labels[1].place(relx=0.1, rely=0.7, relwidth=0.4, relheight=0.2, anchor="w")
pd_chart_labels[2].place(relx=0.1, rely=0.5, relwidth=0.4, relheight=0.2, anchor="w")
pd_chart_labels[3].place(relx=0.1, rely=0.3, relwidth=0.4, relheight=0.2, anchor="w")
pd_chart_labels[4].place(relx=0.1, rely=0.1, relwidth=0.4, relheight=0.2, anchor="w")

pd_chart_lines = []
for chart_count in range(7):
    pd_chart_lines.append(tk.Frame(pd_chart_frame, bg=colours["pd_ln"]))

pd_chart_lines[0].place(relx=0.5, rely=0.1, width=3, relheight=0.8)
pd_chart_lines[1].place(relx=0.5, rely=0.9, relwidth=0.5, height=3)
pd_chart_lines[2].place(relx=0.48, rely=0.9, relwidth=0.02, height=3)
pd_chart_lines[3].place(relx=0.48, rely=0.7, relwidth=0.02, height=3)
pd_chart_lines[4].place(relx=0.48, rely=0.5, relwidth=0.02, height=3)
pd_chart_lines[5].place(relx=0.48, rely=0.3, relwidth=0.02, height=3)
pd_chart_lines[6].place(relx=0.48, rely=0.1, relwidth=0.02, height=3)

pd_data_frame = tk.Frame(pill_detail_page, bg=colours["pd_bg"])
pd_data_frame.place(relx=0.45, rely=0.2, relwidth=0.45, relheight=0.6)
pd_quantity_frame = tk.Frame(pd_data_frame, bg=colours["pd_bg"])
pd_quantity_frame.place(relx=0, rely=0, relwidth=1, relheight=4/30)
pd_quantity_label = tk.Label(pd_quantity_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 18), text = "Pills remaining: ", anchor="w")
pd_quantity_label.place(relx=0, rely=0, relwidth=0.5, relheight=1)


pd_qty_button = tk.Button(pd_quantity_frame, text="100", font=("Trebuchet MS", 18), bg=colours["pd_bn_u"], relief="solid", borderwidth=2, activebackground=colours["pd_bn_p"], command=lambda:open_numpad_button(pill_detail_page, "Pill Quantity", pd_qty_button, 1))
pd_qty_button.place(relx=0.5, rely=0, relwidth=0.2, relheight=1)

pd_empty_label = tk.Label(pd_data_frame, bg=colours["pd_bg"], font=("Trebuchet MS", 18), text = "Empty on 5 Jan 20", anchor="w")
pd_empty_label.place(relx=0, rely=6/30, relwidth=0.8, relheight=4/30)

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
a_email_button = tk.Label(a_email_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=10, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666")
a_email_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_email_label.place(relx = 0, rely = 0, relwidth = 0.2, relheight = 1)
a_email_button.place(relx = 0.2, rely = 0, relwidth = 0.8, relheight = 1)

a_username_frame = tk.Frame(a_general_frame, bg=colours["a_content_bg"])
a_username_label = tk.Label(a_username_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="Username: ", padx=10, pady=10, anchor="w")
a_username_button = tk.Button(a_username_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_username_label, a_username_button))
a_username_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_username_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_username_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

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
a_sharing_user1_label = tk.Label(a_sharing_user1_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User 1: ", padx=10, pady=10, anchor="w")
a_sharing_user1_button = tk.Button(a_sharing_user1_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user1_label, a_sharing_user1_button))
a_sharing_user1_frame.place(relx = 0.05, rely = 0.20, relwidth = 0.9, relheight = 0.08)
a_sharing_user1_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user1_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_user2_frame = tk.Frame(a_sharing_frame, bg=colours["a_content_bg"])
a_sharing_user2_label = tk.Label(a_sharing_user2_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User 2: ", padx=10, pady=10, anchor="w")
a_sharing_user2_button = tk.Button(a_sharing_user2_frame, bg=colours["a_content_entry"], activebackground=colours["a_content_entry"], borderwidth=2, relief="solid", padx=5, pady=10, font=("Trebuchet MS",18), anchor="w", state="disabled", disabledforeground="#666666", command = lambda: open_keyboard_button(account_page, a_sharing_user2_label, a_sharing_user2_button))
a_sharing_user2_frame.place(relx = 0.05, rely = 0.32, relwidth = 0.9, relheight = 0.08)
a_sharing_user2_label.place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)
a_sharing_user2_button.place(relx = 0.3, rely = 0, relwidth = 0.7, relheight = 1)

a_sharing_user3_frame = tk.Frame(a_sharing_frame, bg=colours["a_content_bg"])
a_sharing_user3_label = tk.Label(a_sharing_user3_frame, bg=colours["a_content_bg"], font=("Trebuchet MS",18), text="User 3: ", padx=10, pady=10, anchor="w")
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

a_logout_button_frame = tk.Frame(a_logout_frame, bg=colours["a_content_bg"])
a_logout_logout_button = tk.Button(a_logout_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Logout", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_logout_logout_button)
a_logout_confirm_button = tk.Button(a_logout_button_frame, bg=colours["a_content_bn_u"], activebackground=colours["a_content_bn_p"], font=("Trebuchet MS",18), text="Confirm", borderwidth=2, relief="solid", padx=10, pady=10, anchor="c", disabledforeground="#666666", command=account_logout_confirm_button)
a_logout_button_frame.place(relx = 0.05, rely = 0.84, relwidth = 0.9, relheight = 0.08)
a_logout_logout_button.place(relx = 0.2, rely = 0, relwidth = 0.2, relheight = 1)
a_logout_confirm_button.place(relx = 0.6, rely = 0, relwidth = 0.2, relheight = 1)



settings_page = Page(window, bg=colours["s_menu_bn_u"])
settings_page.place(x=0, y=0, relwidth=1, relheight=1)

s_menu_frame = tk.Frame(settings_page, bg=colours["s_menu_bn_u"])
s_menu_frame.place(relx = 0, rely = 0, relwidth = 0.12, relheight = 1)

s_back_button = tk.Button(s_menu_frame, image=back_icon_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_back_button, anchor = "c")
s_back_button.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=1, anchor="n")

s_wifi_button = tk.Button(s_menu_frame, image=wifi_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_wifi_button, anchor = "c")
s_wifi_button.place(relx=0.5, rely=0.2, relheight=0.2, relwidth=1, anchor="n")

s_time_button = tk.Button(s_menu_frame, image=clock_image, bg=colours["s_menu_bn_u"], activebackground=colours["s_menu_bn_p"], relief="sunken", borderwidth=0, command=setting_time_button, anchor = "c")
s_time_button.place(relx=0.5, rely=0.4, relheight=0.2, relwidth=1, anchor="n")

s_lines = []
for line_count in range(4):
    s_lines.append(tk.Frame(s_menu_frame, bg=colours["s_menu_ln"]))
s_lines[0].place(width=2, relheight=1, relx=1, rely=0, anchor="ne")
s_lines[1].place(relwidth=1, height=2, relx=0, rely=0.2, anchor="w")
s_lines[2].place(relwidth=1, height=2, relx=0, rely=0.4, anchor="w")
s_lines[3].place(relwidth=1, height=2, relx=0, rely=0.6, anchor="w")

s_wifi_frame = tk.Frame(settings_page, bg=colours["s_content_bg"])
s_wifi_frame.place(relx=1, rely=0, anchor="ne", relwidth=0.88, relheight=1)

s_wifi_title = tk.Label(s_wifi_frame, bg=colours["s_content_bg"], font=("Trebuchet MS",24,"underline"), text="Wifi Settings", padx=10, pady=10, anchor="w")
s_wifi_title.place(relx = 0.05, rely = 0.08, relwidth = 0.9, relheight = 0.08)

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