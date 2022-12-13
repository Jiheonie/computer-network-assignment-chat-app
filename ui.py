import customtkinter

class MainUi(customtkinter.CTk):
    def __init__(self, node):
        super().__init__()
        self.geometry("450x800")
        self.title("Chat Application")
        self.node = node
        self.peer_list = ["No one chosen"]
        self.resizable(0, 0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.current_peer_name = customtkinter.StringVar()


        self.peer_chooser = customtkinter.CTkOptionMenu(master=self, corner_radius=0, values=self.peer_list, font=customtkinter.CTkFont(size=14))
        self.peer_chooser.grid(row=0, column=0, columnspan=1, padx=(20, 5), pady=(20, 10), sticky="ew")

        self.reload_button = customtkinter.CTkButton(master=self, command=self.reload_handler, text="Reload", corner_radius=0, font=customtkinter.CTkFont(size=14))
        self.reload_button.grid(row=0, column=1, padx=(10, 10), pady=(20, 10), sticky="e")

        self.connect_button = customtkinter.CTkButton(master=self, command=self.connect_handler, text="Connect", corner_radius=0, font=customtkinter.CTkFont(size=14))
        self.connect_button.grid(row=0, column=2, padx=(5, 20), pady=(20, 10), sticky="e")

        self.income_message = customtkinter.CTkTextbox(master=self, state="disabled" , height=580, width=410, font=customtkinter.CTkFont(size=16))
        self.income_message.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 0), sticky="nsew")

        self.input_message = customtkinter.CTkEntry(master=self, placeholder_text="Input message", width=400, corner_radius=0, font=customtkinter.CTkFont(size=16))
        self.input_message.grid(row=2, column=0, columnspan=2, padx=(20, 5), pady=(15, 5), sticky="w")

        self.send_button = customtkinter.CTkButton(master=self, command=self.send_handler, height=74, text="Send", corner_radius=0, font=customtkinter.CTkFont(size=16))
        self.send_button.grid(row=2, column=2, rowspan=2, padx=(5, 20), pady=(15, 10), sticky="e")

        self.file_label = customtkinter.CTkLabel(master=self, text="No file chosen", font=customtkinter.CTkFont(size=16))
        self.file_label.grid(row=3, column=0, padx=(5, 20), pady=(0, 20), sticky="e")

        self.browse_button = customtkinter.CTkButton(master=self, command=self.browse_file, text="Browse", corner_radius=0, font=customtkinter.CTkFont(size=14))
        self.browse_button.grid(row=3, column=1, padx=(5, 5), pady=(0, 20), sticky="e")

        self.filepath = ""


    def show_mesage(self):
        self.income_message.configure(state="normal")
        self.income_message.delete("0.0", "end")
        for message in self.node.messages:
            self.income_message.insert("end", message)
        self.income_message.configure(state="disabled")
        self.after(500, self.show_mesage)


    def reload_handler(self):
        self.node.request_server("!online")
        self.peer_list = []
        print(self.node.available_users)
        for name in self.node.available_users[1]:
            if name != self.node.name:
                self.peer_list.append(name)
        if self.peer_list == []:
            self.peer_list = ["No online user"]
        self.peer_chooser.configure(values=self.peer_list)


    def connect_handler(self):
        name = self.peer_chooser.get()
        if name != "No one chosen":
            self.node.connect_auto(name)


    def send_handler(self):
        name = self.peer_chooser.get()
        msg = self.input_message.get()
        filename = self.file_label.cget(attribute_name="text")
        if msg:
            msg_sent = self.node.send_by_name(name, msg)
            self.input_message.delete("0", "end")
            sent_report = f"[To {name}]  {msg}\n\n"
            if msg_sent:
                self.node.messages.append(sent_report)
        if filename:
            self.node.filename = self.filepath
            self.node.sending_file = True
            self.node.send_by_name(name, "!file")
            self.file_label.configure(text="No file chosen")
            self.filepath = ""


    def browse_file(self):
        browsed_file = customtkinter.filedialog.askopenfilename()
        file_name = browsed_file.split("/")[-1]
        if file_name:
            self.file_label.configure(text=file_name)
        self.filepath = browsed_file
