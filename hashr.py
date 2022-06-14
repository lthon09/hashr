from sys import platform
from json import load, dump
from os import getenv
from os.path import getsize, isfile, expanduser
from hashlib import md5, sha1, sha224, sha256, sha384, sha512
from threading import Thread
from pyperclip import copy
from webbrowser import open_new_tab
from ttkbootstrap import Window, IntVar, Menu, Frame, Notebook, Label, Button, Menubutton, Checkbutton, Radiobutton, Entry, Progressbar
from ttkbootstrap.toast import ToastNotification
from tkinter.filedialog import askopenfilename

def get_os() -> int:
    if platform in ["win32", "cygwin", "msys"]:
        return 1
    elif platform == "linux":
        return 2
    elif platform == "darwin":
        return 3
    else:
        return 4

def get_settings_path() -> str:
    if _os == 1:
        directory = getenv("appdata")
    elif _os == 2:
        directory = expanduser("~")
    elif _os == 3:
        directory = f"{expanduser('~')}/Library/Application Support"
    elif _os == 4:
        directory = ""

    return f"{directory}/hashr.json" if _os != 2 else f"{directory}/.hashr.json"

def get_settings() -> None:
    if not isfile(settings_path):
        create_settings()

    with open(settings_path, "r") as file:
        settings_data = load(file)

    return settings_data

def create_settings() -> None:
    with open(settings_path, "w") as file:
        dump(SETTINGS, file)

def save_settings() -> None:
    with open(settings_path, "w") as file:
        dump(settings_data, file)

def open_repository() -> None:
    open_new_tab("https://github.com/lthon09/hashr")

def change_window_geometry() -> None:
    window.geometry(TABS_GEOMETRIES[menu.index(menu.select())])

def check_tab_1() -> None:
    file_location = file_location_1.get()
    algorithm = algorithm_var_1.get()

    if file_location == "The File's Location" or algorithm == 0:
        return

    get_hash_button.config(state="normal")

def check_tab_2() -> None:
    file_location = file_location_2.get()
    hash_value = hash_value_2.get()
    algorithm = algorithm_var_2.get()

    if file_location == "The File's Location" or hash_value == "The Hash to Be Matched Against The File's Hash" or hash_value.strip() == "" or algorithm == 0:
        return

    match_hash_button.config(state="normal")

def check_tab_3() -> None:
    if chunk_size_var.get() != settings_data["chunk_size"] or completion_alert_var.get() != settings_data["completion_alert"] or theme_var.get() != settings_data["theme"]:
        save.config(state="normal")
    else:
        save.config(state="disabled")

def _save_settings() -> None:
    global close

    close = False

    if theme_var.get() != settings_data["theme"]:
        close = True

    settings_data["chunk_size"] = chunk_size_var.get()
    settings_data["completion_alert"] = completion_alert_var.get()
    settings_data["theme"] = theme_var.get()

    save_settings()

    if close:
        exit()

def select_file(tab : int) -> None:
    path = askopenfilename()

    if not path:
        return

    if _os == 1:
        path = path.replace("/", "\\")

    if tab == 1:
        file_location_1.config(state="normal")

        file_location_1.delete(0, "end")
        file_location_1.insert(0, path)

        file_location_1.config(state="readonly")

        select_file_button_1.config(bootstyle="primary")

        check_tab_1()
    elif tab == 2:
        file_location_2.config(state="normal")

        file_location_2.delete(0, "end")
        file_location_2.insert(0, path)

        file_location_2.config(state="readonly")

        select_file_button_2.config(bootstyle="primary")

        check_tab_2()

def select_algorithm(tab : int) -> None:
    algorithm_1.config(bootstyle="primary") if tab == 1 else algorithm_2.config(bootstyle="primary")

    check_tab_1() if tab == 1 else check_tab_2()

def get_hash(path : str, algorithm : int, progress : list[Progressbar, Label] | None, tab : int) -> str:
    global cancelled_1, hash_1
    global cancelled_2, hash_2

    menu.tab(2, state="disabled")

    _hash = ALGORITHMS[algorithm][1]()
    chunk_size = CHUNK_SIZES[settings_data["chunk_size"]]

    with open(path, "rb") as file:
        while True:
            if not isfile(path):
                file.close()

                if tab == 1:
                    hash_1 = "File Not Found, cancelled"

                    cancelled_1 = True
                elif tab == 2:
                    hash_2 = "File Not Found, cancelled"

                    cancelled_2 = True

                return ToastNotification(
                    title="File Not Found - Hashr",
                    message="The selected file doesn't exist anymore, the process is cancelled.",
                    duration=5000,
                    alert=True
                ).show_toast()

            if tab == 1:
                if cancelled_1:
                    file.close()

                    hash_1 = "Cancelled"

                    return
            elif tab == 2:
                if cancelled_2:
                    file.close()

                    hash_2 = "Cancelled"

                    return

            chunk = file.read(chunk_size)

            if not chunk:
                break

            _hash.update(chunk)

            if progress:
                progress[0].config(value=file.tell() / getsize(path) * 100)
                progress[1].config(text=f"{int(progress[0]['value'])}%")

    if tab == 1:
        hash_1 = _hash.hexdigest()
    elif tab == 2:
        hash_2 = _hash.hexdigest()

def _get_hash() -> None:
    global hashing_1, cancelled_1

    if not isfile(file_location_1.get()):
        return ToastNotification(
            title="File Not Found - Hashr",
            message="The selected file doesn't exist anymore.",
            duration=5000,
            alert=True
        ).show_toast()

    hashing_1 = True

    file_location_1.config(state="disabled")
    select_file_button_1.config(state="disabled")
    algorithm_1.config(state="disabled")

    hash_value_1.config(state="normal")

    hash_value_1.delete(0, "end")
    hash_value_1.insert(0, "Calculating...")

    hash_value_1.config(state="readonly")

    get_hash_button.config(state="disabled")
    cancel_1.config(state="normal")

    thread = Thread(target=get_hash, args=(
        file_location_1.get(),
        algorithm_var_1.get(),
        [progress_bar, progress_percentage],
        1,
    ), daemon=True)

    thread.start()
    thread.join()

    menu.tab(2, state="normal")

    file_location_1.config(state="readonly")

    hash_value_1.config(state="normal")

    hash_value_1.delete(0, "end")
    hash_value_1.insert(0, hash_1)

    hash_value_1.config(state="readonly")

    clear_1.config(state="normal")

    if not cancelled_1:
        _copy.config(state="normal")

    algorithm_1.config(bootstyle="secondary")
    cancel_1.config(state="disabled")

    ToastNotification(
        title="Completed - Hashr",
        message="Hash calculation has completed.",
        duration=5000,
        alert=True
    ).show_toast() if settings_data["completion_alert"] and not cancelled_1 else None

    cancelled_1 = False

def match_hash() -> None:
    global hashing_2, cancelled_2

    if not isfile(file_location_2.get()):
        return ToastNotification(
            title="File Not Found - Hashr",
            message="The selected file doesn't exist anymore.",
            duration=5000,
            alert=True
        ).show_toast()

    hashing_2 = True

    file_location_2.config(state="disabled")
    select_file_button_2.config(state="disabled")
    hash_value_2.config(state="disabled")
    algorithm_2.config(state="disabled")

    result.config(state="normal")

    result.insert(0, "Matching...")

    result.config(state="readonly")

    match_hash_button.config(state="disabled")

    thread = Thread(target=get_hash, args=(
        file_location_2.get(),
        algorithm_var_2.get(),
        None,
        2,
    ), daemon=True)

    thread.start()
    thread.join()

    menu.tab(2, state="normal")

    file_location_2.config(state="readonly")
    hash_value_2.config(state="readonly")

    result.config(state="normal")

    result.delete(0, "end")
    result.insert(0, "Matched" if hash_value_2.get() == hash_2 else "Not Matched")

    result.config(state="readonly")

    clear_2.config(state="normal")

    algorithm_2.config(bootstyle="secondary")
    cancel_2.config(state="disabled")

    ToastNotification(
        title="Completed - Hashr",
        message="Hash matching has completed.",
        duration=5000,
        alert=True
    ).show_toast() if settings_data["completion_alert"] and not cancelled_2 else None

def cancel_hashing(tab : int) -> None:
    global cancelled_1, cancelled_2

    if tab == 1:
        cancelled_1 = True
    elif tab == 2:
        cancelled_2 = True

def clear_results_1() -> None:
    global hashing_1

    file_location_1.config(state="normal")
    hash_value_1.config(state="normal")

    file_location_1.delete(0, "end")
    hash_value_1.delete(0, "end")

    file_location_1.insert(0, "The File's Location")
    hash_value_1.insert(0, "The File's Hash will Be Displayed Here")

    file_location_1.config(state="readonly")
    hash_value_1.config(state="readonly")

    select_file_button_1.config(state="normal", bootstyle="secondary")

    clear_1.config(state="disabled")
    _copy.config(state="disabled")

    algorithm_1.config(state="normal")

    algorithm_var_1.set(0)

    progress_bar.config(value=0)
    progress_percentage.config(text="0%")

    hashing_1 = False

def clear_results_2() -> None:
    global hashing_2

    file_location_2.config(state="normal")

    file_location_2.delete(0, "end")
    file_location_2.insert(0, "The File's Location")

    select_file_button_2.config(state="normal", bootstyle="secondary")

    hash_value_2.config(state="normal")
    result.config(state="normal")

    hash_value_2.delete(0, "end")
    result.delete(0, "end")

    hash_value_2.insert(0, "The Hash to Be Matched Against The File's Hash")
    result.insert(0, "The Result will Be Displayed Here")

    result.config(state="readonly")

    clear_2.config(state="disabled")

    algorithm_2.config(state="normal")

    algorithm_var_2.set(0)

    hashing_2 = False

def copy_hash() -> None:
    copy(hash_value_1.get())

SETTINGS = {
    "chunk_size": 4,
    "completion_alert": True,
    "theme": 1
}

ALGORITHMS = {
    1: ["MD5", md5],
    2: ["SHA1", sha1],
    3: ["SHA224", sha224],
    4: ["SHA256", sha256],
    5: ["SHA384", sha384],
    6: ["SHA512", sha512]
}

CHUNK_SIZES = {
    1: 1024,
    2: 2048,
    3: 4096,
    4: 8192,
    5: 16384,
    6: 32768,
    7: 65536
}

TABS_GEOMETRIES = {
    0: "500x200",
    1: "500x250",
    2: "500x430",
    3: "300x200"
}

_os = get_os()

settings_path = get_settings_path()

settings_data = get_settings()

hash_1 = None
hash_2 = None

hashing_1 = False
hashing_2 = False

cancelled_1 = False
cancelled_2 = False

window = Window(
    title="Hashr",
    themename="cosmo" if settings_data["theme"] == 1 else "darkly",
    resizable=(False, False),
    hdpi=False
)

menu = Notebook(window)

calculator = Frame(menu)

file_label_1 = Label(calculator, text="File:", font=("", 11))

file_label_1.place(x=6, y=13)

file_location_1 = Entry(calculator, width=57)

file_location_1.insert(0, "The File's Location")

file_location_1.config(state="readonly")

file_location_1.place(x=43, y=10)

select_file_button_1 = Button(calculator, text="Select File", command=lambda : select_file(1), bootstyle="secondary")

select_file_button_1.place(x=410, y=10)

hash_label_1 = Label(calculator, text="Hash:", font=("", 11))

hash_label_1.place(x=6, y=55)

hash_value_1 = Entry(calculator, width=50)

hash_value_1.insert(0, "The File's Hash will Be Displayed Here")

hash_value_1.config(state="readonly")

hash_value_1.place(x=54, y=52)

clear_1 = Button(calculator, text="Clear", command=clear_results_1, state="disabled", bootstyle="secondary")

clear_1.place(x=379, y=52)

_copy = Button(calculator, text="Copy", command=copy_hash, state="disabled", bootstyle="success")

_copy.place(x=434, y=52)

algorithm_var_1 = IntVar(value=0)

algorithm_1 = Menubutton(calculator, text="Algorithm", bootstyle="secondary")

algorithm_1.menu = Menu(algorithm_1, tearoff=False)

algorithm_1["menu"] = algorithm_1.menu

for _algorithm in ALGORITHMS:
    algorithm_1.menu.add_radiobutton(label=ALGORITHMS[_algorithm][0], variable=algorithm_var_1, value=_algorithm, command=lambda : select_algorithm(1))

algorithm_1.place(x=9, y=110)

progress_bar = Progressbar(calculator, length=228, orient="horizontal", mode="determinate")

progress_bar.place(x=118, y=118)

progress_percentage = Label(calculator, text="0%", font=("", 9))

progress_percentage.place(x=220, y=135)

get_hash_button = Button(calculator, text="Get Hash", command=lambda : Thread(target=_get_hash).start(), state="disabled")

get_hash_button.place(x=351, y=110)

cancel_1 = Button(calculator, text="Cancel", command=lambda : cancel_hashing(1), state="disabled", bootstyle="secondary")

cancel_1.place(x=427, y=110)

matcher = Frame(menu)

file_label_2 = Label(matcher, text="File:", font=("", 11))

file_label_2.place(x=6, y=13)

file_location_2 = Entry(matcher, width=57)

file_location_2.insert(0, "The File's Location")

file_location_2.config(state="readonly")

file_location_2.place(x=43, y=10)

select_file_button_2 = Button(matcher, text="Select File", command=lambda : select_file(2), bootstyle="secondary")

select_file_button_2.place(x=410, y=10)

hash_label_2 = Label(matcher, text="Hash:", font=("", 11))

hash_label_2.place(x=6, y=55)

hash_value_2 = Entry(matcher, width=70)

hash_value_2.insert(0, "The Hash to Be Matched Against The File's Hash")

hash_value_2.bind("<Button-1>", lambda _ : hash_value_2.delete(0, "end"))
hash_value_2.bind("<KeyRelease>", lambda _ : check_tab_2())

hash_value_2.place(x=54, y=52)

result_label = Label(matcher, text="Result:", font=("", 11))

result_label.place(x=6, y=100)

result = Entry(matcher, width=58)

result.insert(0, "The Result will Be Displayed Here")

result.config(state="readonly")

result.place(x=62, y=97)

clear_2 = Button(matcher, text="Clear", command=clear_results_2, state="disabled", bootstyle="secondary")

clear_2.place(x=435, y=97)

algorithm_var_2 = IntVar(value=0)

algorithm_2 = Menubutton(matcher, text="Algorithm", bootstyle="secondary")

algorithm_2.menu = Menu(algorithm_2, tearoff=False)

algorithm_2["menu"] = algorithm_2.menu

for _algorithm in ALGORITHMS:
    algorithm_2.menu.add_radiobutton(label=ALGORITHMS[_algorithm][0], variable=algorithm_var_2, value=_algorithm, command=lambda : select_algorithm(2))

algorithm_2.place(x=9, y=159)

match_hash_button = Button(matcher, text="Match Hash", command=lambda : Thread(target=match_hash).start(), state="disabled")

match_hash_button.place(x=117, y=159)

cancel_2 = Button(matcher, text="Cancel", command=lambda : cancel_hashing(2), state="disabled", bootstyle="secondary")

cancel_2.place(x=209, y=159)

settings = Frame(menu)

chunk_size_label = Label(settings, text="Chunk Size", font=("", 11))

chunk_size_label.place(x=6, y=13)

chunk_size_description = Label(settings, text="The size of each chunk of data to be iterated through in a file. The larger the chunk size, the faster the hash calculation is, but more resources are used.", wraplength=500)

chunk_size_description.place(x=6, y=35)

chunk_size_var = IntVar(value=settings_data["chunk_size"])

chunk_size_selector = Menubutton(settings, text="Chunk Size")

chunk_size_selector.menu = Menu(chunk_size_selector, tearoff=False)

chunk_size_selector["menu"] = chunk_size_selector.menu

for chunk_size in CHUNK_SIZES:
    chunk_size_selector.menu.add_radiobutton(label=f"{CHUNK_SIZES[chunk_size]:,} Bytes", variable=chunk_size_var, value=chunk_size, command=check_tab_3)

chunk_size_selector.place(x=8, y=80)

completion_alert_label = Label(settings, text="Completion Alert", font=("", 11))

completion_alert_label.place(x=6, y=130)

completion_alert_description = Label(settings, text="If enabled, you'll get a sound alert when the hash calculating/matching is completed.", wraplength=500)

completion_alert_description.place(x=6, y=152)

completion_alert_var = IntVar(value=settings_data["completion_alert"])

completion_alert_selector = Checkbutton(settings, text="Completion Alert", variable=completion_alert_var, command=check_tab_3)

completion_alert_selector.place(x=8, y=180)

theme_label = Label(settings, text="Theme", font=("", 11))

theme_label.place(x=6, y=220)

theme_description = Label(settings, text="The theme of the application.")

theme_description.place(x=6, y=242)

theme_var = IntVar(value=settings_data["theme"])

theme_selector_light = Radiobutton(settings, text="Light", variable=theme_var, value=1, command=check_tab_3)

theme_selector_light.place(x=8, y=270)

theme_selector_dark = Radiobutton(settings, text="Dark", variable=theme_var, value=2, command=check_tab_3)

theme_selector_dark.place(x=8, y=295)

save = Button(settings, text="Save", command=_save_settings, state="disabled", bootstyle="success")

save.place(x=8, y=340)

about = Frame(menu)

description_label = Label(about, text="Description:", font=("", 11))

description_label.pack(pady=(10, 0))

description = Label(about, text="A simple file hash checker.", font=("", 10), bootstyle="primary")

description.pack()

author_label = Label(about, text="Author:", font=("", 11))

author_label.pack(pady=(15, 0))

author = Label(about, text="lthon09", font=("", 10), bootstyle="primary")

author.pack()

repository = Label(about, text="Visit The GitHub Repository", cursor="hand2", font=("", 9), bootstyle="info")

repository.bind("<Button-1>", lambda _ : open_repository())

repository.pack(pady=(20, 0))

menu.add(calculator, text="Calculator")
menu.add(matcher, text="Matcher")
menu.add(settings, text="Settings")
menu.add(about, text="About")

menu.pack(fill="both", expand=True)

window.bind("<<NotebookTabChanged>>", lambda _ : change_window_geometry())

window.mainloop()
