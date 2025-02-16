#dependency imports
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import cv2,dlib,numpy as np,json
import os,threading
from tkinter import filedialog
import encodingSupport as es
import time
import pandas as pd
import tksheet as sheet
#Variables and the Initiallizations 
folder_name = 'MyProtechFolder'
folder_dict={}
encoding_list = []
displaydata=[]
imgindx=[] 
cam_flag =[False,0]
save_path = None
facedata=[]

title_font = ("Arial", 16, "bold")
label_font = ("Arial", 12, "bold")
entry_font = ("Arial", 11)
button_font = ("Arial", 10, "bold")
message_font = ("Arial", 10, "italic")
pinkishred='#FF4B2B'
blackbg='#000000'
metalblack='#2c2c2b'
bg_color = '#1c1c1c'
menu_bg_color = '#2e2e2e'
button_bg_color = '#0f52ba'
button_fg_color = '#f0f0f0'
section_bg_color = '#333333'
highlight_color = '#00ff00'
scrollbar_bg_color = '#555555'
canvas_bg_color = '#444444'
label_font = '#00e5ee'
border_color = '#29a3a3'

futuristic_blue = "#0A84FF"
futuristic_green = "#00FF85",'#31ccad'
futuristic_purple = "#A020F0"
white_text = "#FFFFFF"
gray_bg = "#333333"

def create_workspace_folder_on_desktop(folder_name):
        folder_structure = ['Staff Folder','Student Folder','Guest Folder']
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        folder_path = os.path.join(desktop_path, folder_name)
        r = folder_path
        # folder_dict[folder_name]=folder_path
        try:
            if not os.path.exists(folder_path):
                if messagebox.askokcancel('Folder Not Found','WorkSpace folder not found. Creating New WorkSpace Folder on Desktop....'):
                    os.mkdir(folder_path)
                else:
                    messagebox.showerror("Wrok Space Error","Permission denaied to Create Working Repository for storing data...\n!Closing Application. ")
                    exit()
        except FileNotFoundError as e:
            messagebox.showinfo('Error',e)

        for filename in folder_structure:
            file_path = os.path.join(folder_path, filename)
            try:
                if not os.path.exists(file_path):
                    os.mkdir(file_path)
                    folder_dict[filename]=file_path
            except PermissionError:
                messagebox.showwarning("Warning","You don't have permission to create this file.")
            except OSError as e:
                messagebox.showerror("Error","An error occurred:", e)

        if os.path.isdir(folder_path):
            folder_list = os.listdir(folder_path)
            for i in folder_list:
                folder_dict[i]=os.path.join(folder_path,i)

#Function change color of selected files  
def toggle_color(button ,var,file,folder_path):   
        global encoding_list      
        with open(os.path.join(folder_path,file),"r") as d:
                data = json.load(d)
        if var.get():
            button.config(bg='lightgreen',activebackground='green')
            encoding_list.extend([np.array(ad) for ad in data])
        else:
            button.config(bg='black',activebackground='black')
            to_remove = [np.array(ad) for ad in data]
            encoding_list= [enc for enc in encoding_list if not any(np.array_equal(enc, rm) for rm in to_remove)]

def compare_faces(known_encodings, face_encoding_to_check, tolerance=0.6):
            try:
                distances = np.linalg.norm(np.array(known_encodings) - face_encoding_to_check, axis=1)
                return distances <= tolerance 
            except ValueError:
                return [False]
            
def stop_cam():
    global cam_flag
    cam_flag[0] = False
    

def main(base):
    #Main Functions and methods Starts from Here
    create_workspace_folder_on_desktop(folder_name)

    def update_files(path,frame):
                var =tk.BooleanVar()
                staff_file_list = os.listdir(path)
                for widget in frame.winfo_children():
                    widget.destroy()

                if len(staff_file_list)!=0:
                    for file in staff_file_list:
                        button = tk.Checkbutton(frame,text=file,variable=var,font=button_font ,bg="black",fg='white',cursor='target')
                        button.pack(side='top',anchor='w',fill='x',pady=2,padx=2)
                        button.config(command=lambda b=button,v=var,f=file:toggle_color(b,v,f,path))
                else:
                    tk.Label(frame,text="No Encoding Data in the Repository...",font=label_font,height=2).pack(side='top',fill='both',padx=2,pady=2)

    def open_file():
        messagebox.showinfo("Open File","Open an existing file.")

    def save_file():
        messagebox.showinfo("Save File", "Save the current file.")

    def exit_app():
        root.quit()

    def copy():
        messagebox.showinfo("Copy", "Copy selected text.")

    def paste():
        messagebox.showinfo("Paste", "Paste copied text.")

    def about():
        messagebox.showinfo("About", "This is a sample application.")

    def close_window():
        root.quit()
        root.destroy()

    def minimize_window():
        root.iconify()

    def toggle_fullscreen(event = None):
        root.attributes('-fullscreen',True)

    def end_fullscreen(event = None):
        root.attributes('-fullscreen',False)


    def display_image_cv2(*args,frame,encoding):
        global displaydata,imgindx

        def deleteimg(frame):
            find=imgindx.index(frame)

            displaydata.pop(find)
            imgindx.pop(find)
            frame.destroy()

        result = compare_faces(known_encodings=displaydata,face_encoding_to_check=encoding,tolerance=0.5)
        result = any(result)
        if result:
            return
        else:
            displaydata.append(encoding)
            image_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_cv2)
            image_pil = image_pil.resize((370, 200), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(image_pil)
            imgframe = tk.Frame(status_scrollbar)
            imgframe.pack(pady=10, padx=10)
            imgindx.append(imgframe)
            label = tk.Label(imgframe, image=tk_image)
            label.image = tk_image  # Keep a reference to avoid garbage collection
            label.pack()
            deletebutton = tk.Button(imgframe, text="Delete", command=lambda l=imgframe: deleteimg(l) )
            deletebutton.pack(side='right')
            add_data = tk.Button(imgframe,text='Add face Data')
            add_data.pack(side='left')

    def start_video(*args,camera_number=None, url_link=None):
        cam = cv2.VideoCapture(camera_number) if camera_number is not None else cv2.VideoCapture(url_link)

        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("dependencey/shape_predictor_68_face_landmarks.dat")
        facerec = dlib.face_recognition_model_v1("dependencey/dlib_face_recognition_resnet_model_v1.dat")

        def get_face_encodings(image):
            detected_faces = detector(image, 1)
            face_encodings = []
            for face in detected_faces:
                shape = predictor(image, face)
                face_encoding = np.array(facerec.compute_face_descriptor(image, shape))
                face_encodings.append(face_encoding)
            return face_encodings, detected_faces

        def update_frame():
            global encoding_list,cam_flag

            face_label.config(text=f'Faces Permitted:{len(encoding_list)}')
            

            if not cam_flag[0]:
                fallback_img = Image.open('image/Untitled_design-removebg-preview.png')
                fallback_img = fallback_img.resize((400,260),Image.Resampling.LANCZOS)
                fallback_imgtk = ImageTk.PhotoImage(image=fallback_img)
                video_label.imgtk = fallback_imgtk
                video_label.configure(image=fallback_imgtk)
                camdetail.config(text='Feed From Camera: Disconnected')
                cam.release()
                return  # Exit if cam_flag is False

            ret, frame = cam.read()
            if ret:
                frame = cv2.resize(frame, (400, 260))
                face_encodings, faces = get_face_encodings(frame)

                # Annotate faces
                for face_encoding, face in zip(face_encodings, faces):
                    x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
                    result = compare_faces(encoding_list, face_encoding)
                    match = np.any(result)
                    if not match:
                        label = "Unknown"
                        #displayes imges in the alert section
                        display_image_cv2(frame=frame, encoding=face_encoding)
                    else:
                        label = "Recognized"


                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255) if not match else (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255) if not match else (0, 255, 0), 2)

                # Update the Tkinter label
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                # img = img.resize((400,260),Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)
                video_label.after(30, update_frame)
            else:
                messagebox.showerror("Camera Error", "Failed to open camera.")
                # Display fallback image if the camera feed fails
                fallback_img = Image.open('image/Untitled_design-removebg-preview.png')
                fallback_img = fallback_img.resize((400,260),Image.Resampling.LANCZOS)
                fallback_imgtk = ImageTk.PhotoImage(image=fallback_img)
                video_label.imgtk = fallback_imgtk
                video_label.configure(image=fallback_imgtk)
        # print(len(encoding_list),'\n',encoding_list[1])
        update_frame()

    def select_cam():
        global cam_flag
        cam_flag[0] = False
        cam = tk.Toplevel()
        cam.title('Select Camera')
        cam.geometry('490x300')
        cam.config(bg="#474747")
        cam.transient(root)
        camera_number_var = tk.StringVar()
        def validate_int_input(newvalue):
            return newvalue.isdigit() or newvalue=='' 

        validateCommand = cam.register(validate_int_input)
        tk.Label(cam,text='Select Camera',fg='white', bg="#474747",font=label_font,height=2).pack(pady=10)

        camframe = tk.Frame(cam,bg='#474747')
        camframe.pack(pady=10,fill='x')

        tk.Label(camframe, text='Enter the Camera number\n (default value will be 0):', font=label_font, fg='white', bg="#474747").pack(side='left',padx=5)
        camera_number = tk.Entry(camframe, font=entry_font,textvariable=camera_number_var,validate='key',validatecommand=(validateCommand,'%P'))
        camera_number.pack(side='left',padx=5)

        def combined():
            global cam_flag
            cam.destroy()
            cam_flag[0] = True
            cam_input= cam_flag[1] =camera_number_var.get().strip()
            camdetail.config(text=f'Feed from Camera:{cam_input}')
            camThread = threading.Thread(
            target=start_video,
            kwargs={
                'camera_number': int(cam_input) if cam_input.isdigit() else None,
                'url_link': cam_input if not cam_input.isdigit() else None},name="camThread")
            camThread.start()


        connect = tk.Button(camframe,text='Connect',fg='Blue',bg='Red',font=button_font,command= lambda:combined(),relief='raised')
        connect.pack(side='left',padx=5)

        tk.Label(cam,text='OR',fg='white',bg='#474747',font=label_font).pack(pady=10)

        urlframe = tk.Frame(cam,bg='#474747')
        urlframe.pack(pady=5,fill='x')

        tk.Label(urlframe,text='Enter URL to connect the\nremote camera:',font=label_font,fg='white',bg='#474747').pack(side='left',padx=5)
        url_address = tk.Entry(urlframe,font=entry_font)
        url_address.pack(side='left',padx=5)
        connect1 = tk.Button(urlframe,text="Connect",fg='blue',bg='red',font=button_font,command=lambda:combined(variable=url_address.get()),relief='raised')
        connect1.pack(side='left',padx=5)

    def Create_Encoding_File(*args):
        stop_cam()
        create_encod = tk.Toplevel(root)
        create_encod.geometry('700x600')
        create_encod.title("Encodings")
        create_encod.overrideredirect(True)
        screen_width = create_encod.winfo_screenwidth()
        screen_height = create_encod.winfo_screenheight()
        x = (screen_width // 2) - (700 // 2)  # Center horizontally
        y = (screen_height // 2) - (600 // 2)  # Center vertically
        create_encod.geometry(f"+{x}+{y}")
        main_options = tk.Frame(create_encod,bg='gray')
        workbench =tk.Frame(create_encod,bg='gray')
        main_options.pack(side='left',fill='y',pady=5,padx=5,anchor='nw')
        workbench.pack(side='left',fill='both',expand=True,padx=5,pady=5,anchor='ne')

        def clear_frame(buttons):
            for widget in workbench.winfo_children():
                widget.destroy()
            for button in buttons:
                button.config(state="normal",fg='gray')
            create_encod.focus_force()


        def close_window(*args):
            setup_activity_frame()
            global cam_flag
            cam_flag[0] = True
            create_encod.destroy()
            

        exit_button = tk.Button(main_options,text="←",bg='black',fg='red',font=button_font,command=close_window,height=1,width=10)
        exit_button.pack( side='top',anchor='nw',padx=5,pady=5)

        def create_encodingFolder(*args,**kargs):
        
            buttons = [add_facestoFolder,delete_facedata_file,delete_single_face]
            folder_path =None
            clear_frame(buttons)
            create_encoding_folder.config(state="disabled",fg='blue')

            encodingframe = tk.Frame(workbench,bg='Black')
            encodingframe.pack( side='left', expand=True, fill='both', anchor='nw')
            tk.Label(encodingframe,text='New File',font=title_font,height=1,fg='white',bg='black').pack(side='top',padx=10,pady=10)

            filenameframe = tk.Frame(encodingframe,bg='black')
            filenameframe.pack(side='top',fill='x')
            tk.Label(filenameframe,text='Enter the Name of the File :',font=label_font,fg='white',bg='black',padx=5).pack(side='left',pady=5)
            filename = tk.Entry(filenameframe,width=30)
            filename.pack(side='left',pady=5)

            designationframe =tk.Frame(encodingframe,bg='black')
            designationframe.pack(side='top',fill='x')
            option =tk.StringVar()
            file = ['Staff Folder','Student Folder','Guest Folder']
            option.set("select")
            tk.Label(designationframe,text='Select the Designation:',fg='white',bg='black',padx=5,font=label_font).pack(side='left',anchor='nw',pady=10)
            designationoption =tk.OptionMenu(designationframe,option,*file)
            designationoption.pack(side='left',pady=10)

            rawfaceframe=tk.Frame(encodingframe,bg='black')
            rawfaceframe.pack(side='top',padx=5,pady=10,fill='x')
            tk.Label(rawfaceframe,text="Select the Folder of Rawface Data:",fg='white',bg='black',font=label_font).pack(side='left')

            def select_folder():
                nonlocal folder_path
                create_encod.overrideredirect(False)
                folder_path = filedialog.askdirectory(title="Select folder")
                create_encod.focus_force()
                create_encod.overrideredirect(True)
                if folder_path:
                    rawfacebutton.config(text=f'{folder_path}')


            rawfacebutton = tk.Button(rawfaceframe,text="Select Folder",command=select_folder,font=button_font)
            rawfacebutton.pack(side='left')

            def create_file(*args):
                # Validate user inputs
                selected_option = option.get()
                file_name = filename.get()
                if not file_name or selected_option == "select" or not folder_path:
                    tk.messagebox.showerror("Error", "All fields must be filled!")
                    create_encodingFolder()


                # Construct the path dynamically
                designation = os.path.join(
                    os.path.expanduser("~"),
                    "Desktop",
                    "MyProtechFolder",
                    selected_option,
                    f"{file_name}.json"
                )

                try:
                    es.generatefacedata(imgpath=folder_path, encodingPath=designation)
                    tk.messagebox.showinfo("Success", f"File created at {designation}")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"An error occurred: {e}")
                create_encod.focus_force()
               
            createbutton =tk.Button(encodingframe,text="Create",font=button_font,command=create_file)
            createbutton.pack(side='top',padx=5,pady=5)
        create_encoding_folder = tk.Button(main_options,text="New faceses folder",fg='gray',font=button_font,bg='black',command= create_encodingFolder,height=1)
        create_encoding_folder.pack(side='top',padx=5,pady=5)


        def addfacesFolder():
            def adding_face_data(*args):
                encod_path =os.path.join(os.path.expanduser("~"),"Desktop","MyProtechFolder",option.get(),file_option.get())
                img_path = imgselected.get()
                es.generatefacedata(imgpath=img_path,encodingPath=encod_path)
                messagebox.showinfo("Status",f"Face data Add Successfully to {file_option.get()}")
                option.set("Select")
                file_option.set("Select")
                selecetedfileframe.config(text="No Image Selected",image=None)
                create_encod.focus_force()


            def update_file_list(*args):
                file_list=[]
                selected_folder =option.get()

                if selected_folder !='Select':
                    folder_path = os.path.join(os.path.expanduser("~"),"Desktop","MyProtechFolder",selected_folder)
                    if os.path.exists(folder_path):
                        file_list =os.listdir(folder_path)

                file_option_menu['menu'].delete(0,'end')
                if file_list:
                    for file in file_list:
                        file_option_menu['menu'].add_command(label=file,command =lambda value =file:file_option.set(value))
                    file_option.set("Select")
                    file_option_menu.config(state="normal")
                else:
                    file_option.set("NO file available")
                    file_option_menu.config(state ="disabled")

            def select_file(*args):

                file_path=filedialog.askopenfilename(title="Select a Image to add",filetypes=[
                        ("All Files", "*.jped *.jpg *.png")
                    ])
                create_encod.focus_force()
                imgselected.set(file_path)
                if file_path:
                    img = cv2.imread(file_path)
                    img = cv2.resize(img,(350,350))
                    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    img_tk =ImageTk.PhotoImage(img)

                    selecetedfileframe.config(image=img_tk)
                    selecetedfileframe.image = img_tk
                    addbutton.config(state='normal')
                else:
                    selecetedfileframe.config(text="No Image Selected")

            buttons = [create_encoding_folder,delete_facedata_file,delete_single_face]
            clear_frame(buttons)
            add_facestoFolder.config(state="disabled",fg='blue')
            encodingFolder = tk.Frame(workbench,bg='black')
            encodingFolder.pack(side='left',expand=True,fill='both')

            tk.Label(encodingFolder,text='Add Face Data',fg='white',bg='black',font=label_font).pack(side='top',fill='x',padx=5,pady=5)

            designationframe =tk.Frame(encodingFolder,bg='black')
            designationframe.pack(side='top',padx=5,pady=5,fill='x')
            tk.Label(designationframe,text='Select the Designation:',fg='white',bg='black',font=label_font).pack(side='left',padx=5,anchor='nw')
            file = ['Staff Folder','Student Folder','Guest Folder']
            option =tk.StringVar()
            option.set("Select")
            designation = tk.OptionMenu(designationframe,option,*file)
            designation.pack(side='left',anchor='nw')
            option.trace('w',update_file_list)

            file_option =tk.StringVar()
            file_option.set("No file available")
            fileframe= tk.Frame(encodingFolder,bg='black')
            fileframe.pack(side='top',fill='x',padx=5,pady=5)
            tk.Label(fileframe,text="Select the file to Add face data:",fg='white',bg='black',font=label_font).pack(side='left',anchor='nw')
            file_option_menu = tk.OptionMenu(fileframe,file_option,[])
            file_option_menu.config(state='disabled')
            file_option_menu.pack(side='left',anchor='nw')
            imgselected = tk.StringVar()
            imgselectframe = tk.Frame(encodingFolder,bg='black')
            imgselectframe.pack(side='top',fill='x')
            tk.Label(imgselectframe,text='Select the Image to add face data:',fg='white',bg='black',font=label_font).pack(side='left',anchor='nw')
            selectimg =tk.Button(imgselectframe,text="Select",command=lambda:select_file(imgselected),font=button_font,justify='left')
            selectimg.pack(side='left',anchor='nw')

            selecetedfileframe = tk.Label(encodingFolder,text='No image Selected',bg='darkgray',fg="white",font=label_font)
            selecetedfileframe.pack(side='top',padx=5,pady=5)

            addbutton = tk.Button(encodingFolder,text="Add",font=button_font,bg='lightblue',command=adding_face_data)
            addbutton.config(state='disabled')
            addbutton.pack(side='top',padx=5,pady=5)
            
        add_facestoFolder =tk.Button(main_options,text="Add New Face",font=button_font,fg='gray',bg='black',command=addfacesFolder,height=1,width=15)
        add_facestoFolder.pack(side='top',padx=5,pady=5,)


        def delete_faceDatafile():

            buttons = [create_encoding_folder,add_facestoFolder,delete_single_face]
            file = ['Staff Folder','Student Folder','Guest Folder']
            clear_frame(buttons)

            delete_facedata_file.config(state="disabled",fg='blue')
            delete_faces = tk.Frame(workbench,bg='Black')
            delete_faces.pack(side='top',expand=True,fill='both')

            def update_file_list(*args):
                    file_list=[]
                    selected_folder =folder_name.get()

                    if selected_folder !='Select':
                        folder_path = os.path.join(os.path.expanduser("~"),"Desktop","MyProtechFolder",selected_folder)
                        if os.path.exists(folder_path):
                            file_list =os.listdir(folder_path)

                    selectfile['menu'].delete(0,'end')

                    if file_name.get()!="NO file available":
                        warningcheck.config(state='normal')
                        filename.config(text=f'Selected File:{file_name.get()}')
                    if file_list:
                        for file in file_list:
                            selectfile['menu'].add_command(label=file,command =lambda value =file:file_name.set(value))


                        selectfile.config(state="normal")

                    else:
                        file_name.set("NO file available")
                        selectfile.config(state ="disabled")


            def checkwarinig(*args):
                bol = waringvari.get()
                if bol:
                    deletefilebutton.config(state='normal')
                    warningcheck.config(bg='red',activebackground='red')
                else:
                    deletefilebutton.config(state='disabled')
                    warningcheck.config(bg='black',activebackground='black')

            def reset_ui(*args):
                """Reset variables and frame."""
                # Reset variables
                folder_name.set("Select")
                waringvari.set(False)
                file_name.set("No file available")

                # Clear and reinitialize frame
                buttons.extend(delete_facedata_file)
                clear_frame(buttons)
                delete_faceDatafile()

            def deleteencodingfile(*args):
                folder =folder_name.get()
                file = file_name.get()
                file_path = os.path.join(os.path.expanduser("~"),"Desktop","MyProtechFolder",folder,file)
            
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        messagebox.showinfo('Status',f"{file} is successffully deleted.")
                        reset_ui()


                    except Exception as e:
                        messagebox.showerror("Error",f"Error message:\n{e}")
                else:
                    messagebox.showinfo("Status",f"{file} not found!")
                create_encod.focus_force()

            tk.Label(delete_faces,text="Delete Face Data File",fg='white',bg='black',font=label_font).pack(side="top",fill='x',padx=5,pady=5)
            folder_name = tk.StringVar()
            folder_name.set("Select")
            selcetfolderframe = tk.Frame(delete_faces,bg='black')
            selcetfolderframe.pack(side='top',fill='x',padx=5,pady=5)
            tk.Label(selcetfolderframe,text='Select the folder:',font=label_font,fg='white',bg='black').pack(side='left')
            selectfolder = tk.OptionMenu(selcetfolderframe,folder_name,*file)
            selectfolder.pack(side='left',anchor='nw')

            folder_name.trace('w',update_file_list)

            file_name =tk.StringVar()
            file_name.set('No file available')
            selectfileframe = tk.Frame(delete_faces,bg='black')
            selectfileframe.pack(side='top',fill='x',padx=5,pady=5)
            tk.Label(selectfileframe,text="Select the File wish to Delete :",font=label_font,fg='white',bg='black').pack(side='left')
            selectfile = tk.OptionMenu(selectfileframe,file_name,[])
            selectfile.config(state='disabled')
            selectfile.pack(side='left',anchor='nw')

            displayframe = tk.Frame(delete_faces,bg='black')
            displayframe.pack(side='top',fill='x',padx=5,pady=10)
            filename=tk.Label(displayframe,font=label_font)
            filename.config(text=file_name.get() )
            file_name.trace('w',update_file_list)
            filename.pack(side='left',anchor='nw')

            waringvari = tk.BooleanVar()
            waringframe = tk.Frame(delete_faces,bg='white')
            waringframe.pack(side='top',fill='x',padx=10,pady=10)
            warningcheck = tk.Checkbutton(waringframe,font=label_font,text="Click on the Check box to achknoledge it.",variable=waringvari,command=lambda:checkwarinig(waringvari))
            warningcheck.pack(side='left',fill='x',expand=True)
            warningcheck.config(state='disabled',fg='white',bg='black')

            deletefilebutton = tk.Button(delete_faces,text='Delete',font=button_font,height=2,state='disabled',command=deleteencodingfile)
            deletefilebutton.pack(side='top',padx=10,pady=10)
            
        delete_facedata_file = tk.Button(main_options,command=delete_faceDatafile,fg='gray',bg='black',font=button_font,text="Delete data File",height=1, width=15)
        delete_facedata_file.pack(side='top',padx=5,pady=5)


        def delete_singleFace():
            buttons = [create_encoding_folder,add_facestoFolder,delete_facedata_file]
            clear_frame(buttons)
            delete_single_face.config(state='disabled')
            deleteSingle = tk.Frame(workbench,bg='black')
            deleteSingle.pack(side='top',expand=True,fill='both')
        delete_single_face = tk.Button(main_options,text="Delete Faces",fg='gray',font=button_font,bg='black',command=delete_singleFace,height=1, width=15)
        delete_single_face.pack(side='top',padx=5,pady=5)

    def show_file_menu(*args,event = None):
        # Create a menu
        file_menu = tk.Menu(root,bg='black',fg='white', tearoff=0)
        file_menu.add_command(label='Create Encodings File',command=Create_Encoding_File,font=mennu_bar_font)
        file_menu.add_command(label='Open Encodings File',command=open_file,font=mennu_bar_font)
        file_menu.add_command(label="Open", command=open_file,font=mennu_bar_font)
        file_menu.add_command(label="Save", command=save_file,font= mennu_bar_font)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=close_window,font=mennu_bar_font)

        # Display the menu at the button's position
        x = main_menu.winfo_rootx()
        y = main_menu.winfo_rooty()+ main_menu.winfo_height()
        file_menu.tk_popup(x, y)

    def add_face_encoding(path):
    
        add_face_frame = tk.Toplevel(root,bg="gray")
        add_face_frame.overrideredirect(True)
        add_face_frame.pack()

    def add_face(event = None):
        add_face_menu = tk.Menu(root,bg='black',fg='white',font=mennu_bar_font,tearoff=0)
        add_face_menu.add_command(label='Add Staff Details',command=lambda p=folder_dict['Staff Folder']:add_face_encoding(path=p))
        add_face_menu.add_command(label='Add Student Details',command=lambda:print('Hi'))
        add_face_menu.add_command(label='Add Guest',command=lambda:print("Hey"))

        x= add_encoding.winfo_rootx()
        y= add_encoding.winfo_rooty()+add_encoding.winfo_height()
        add_face_menu.tk_popup(x,y)



    # Main code
    root = base
    # root = tk.Tk()
    root.title('Dashboard')
    root.iconbitmap('image/Untitled_design-removebg-preview.ico')
    root.configure(bg=bg_color)
    root.state('zoomed')
    #Menu Bar
    menu_bar = tk.Frame(root, bg=menu_bg_color,  height=40)
    menu_bar.pack(side='top',fill='x')
    mennu_bar_font = ("Helvetica",10,'bold')


    #Menu button
    main_menu = tk.Button(menu_bar,text='Main Menu',command=lambda:show_file_menu,bg=menu_bg_color,font=mennu_bar_font,fg='white',height=2,relief='flat')
    main_menu.pack(side='left',padx=7)
    add_encoding = tk.Button(menu_bar,text='Add Face',command=lambda:add_face,bg=menu_bg_color, font=mennu_bar_font,fg='white',height=2,relief='flat')
    add_encoding.pack(side='left',padx=7)
    help_button = tk.Button(menu_bar,text='Help',command=lambda:print("help"),font=mennu_bar_font,fg='white',bg=menu_bg_color,height=2,relief='flat')
    help_button.pack(side='left',padx=7)
    about_button = tk.Button(menu_bar,text='About',command=lambda:print("About"),font=mennu_bar_font,fg='white',bg=menu_bg_color,relief='flat',height=2)
    about_button.pack(side='left',padx=7)


    #Alert Section
    status_section = tk.Frame(root,bg='Black',width=420)
    status_section.pack(side='right',fill='both',padx=0,pady=7,expand=True)
    tk.Label(status_section,text='Status',font=label_font,fg='white',bg=menu_bg_color).pack(side='top',fill='x')
    status_canva = tk.Canvas(status_section,bg='gray')
    scrollbar = tk.Scrollbar(status_section,orient='vertical',command=status_canva.yview)
    status_scrollbar = tk.Frame(status_canva,bg='gray')
    status_scrollbar.bind("<Configure>",lambda e:status_canva.configure(scrollregion=status_canva.bbox('all')))
    status_canva.create_window((0,0),window=status_scrollbar,anchor='nw')
    status_canva.configure(yscrollcommand=scrollbar.set)
    status_canva.pack(side='left',fill='both',expand=True)
    scrollbar.pack(side='right',fill='y')


    #Camera Feed Section
    live_feed = tk.Frame(root,bg='black',width=420)
    live_feed.pack(side='left',pady=7,fill='both',)
    live_feed.propagate(False)
    cam_action = tk.Frame(live_feed,bg=menu_bg_color,height=40)
    cam_action.pack(side='top',fill='x')
    cam_action.propagate(False)
    cam_button = tk.Button(cam_action,text='Connect Camera',command=select_cam,font=mennu_bar_font,fg='black',bg=pinkishred,height=1,relief='raised')
    cam_button.pack(side='left',padx=5)
    cam_stop_button =tk.Button(cam_action,text='Stop',bg=pinkishred,command=stop_cam,font=mennu_bar_font,fg=blackbg,relief='raised')
    cam_stop_button.pack(side='right',padx=5)
    
    video_frame = tk.Label(live_feed,width=410,height=210,bg='#3b3b3b')
    video_frame.pack(side='top')
    video_label = tk.Label(video_frame)
    video_label.pack()
    face_label = tk.Label(live_feed,text='Faces Permitted: 0',bg=bg_color,fg=white_text,font=label_font)
    face_label.pack(side='top',anchor='nw',pady=5)
    camdetail =tk.Label(live_feed,text='Feed from Camera:Not connected',bg=bg_color,fg=white_text,font=label_font)
    camdetail.pack(side='top',anchor='nw',pady=5)
    guestlist =tk.Label(live_feed,text='Active Guest: 0',bg=bg_color,fg=white_text,font=label_font)
    guestlist.pack(side='top',anchor='nw',pady=5)
    fallback_img = Image.open('image/Untitled_design-removebg-preview.png')
    fallback_img = fallback_img.resize((400,260),Image.Resampling.LANCZOS)
    fallback_imgtk = ImageTk.PhotoImage(image=fallback_img)
    video_label.imgtk = fallback_imgtk
    video_label.configure(image=fallback_imgtk)
   


    #Activity Sections
    activity_frame =tk.Frame(root,bg='black',width=690)
    activity_frame.pack(side='left',fill='y',padx=5,pady=7)

    def handle_guest(baseframe,table_frame):
        stname = tk.StringVar()
        dept =tk.StringVar()

        def delete_frame(frame, facedata):
            global encoding_list
            frame.destroy()
            to_remove = [np.array(ad) for ad in facedata]
            encoding_list[:] = [enc for enc in encoding_list if not any(np.array_equal(enc,rm) for rm in to_remove)]

        def get_face_data():
            name = name_entry.get()
            global save_path,facedata,frame,make_entry
            cam =cv2.VideoCapture(0)
            if cam.isOpened():
                _,frame =cam.read()
                if _:
                    os.makedirs('C:/Users/ASUS/Desktop/MyProtechFolder/Guest Folder/data', exist_ok=True)
                    save_path = f'C:/Users/ASUS/Desktop/MyProtechFolder/Guest Folder/data/{name}_{time.strftime("%d-%m-%Y_%H_%M")}.jpg'
                    cv2.imwrite(save_path, frame)
                    facedata = es.get_face_encodings(frame)
                    frame = cv2.resize(frame, (250, 190))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    frame = ImageTk.PhotoImage(image=frame)
                    entry_button.config(state='normal')
                    img.imgtk = frame
                    img.config(image=frame)
                    

                cam.release()
                

            def make_entry(name, purpose, contact, audience, student, dept, exit_time='Not Exited'):
                date = time.strftime('%d_%m_%Y')
                t = time.strftime('%H:%M')
                # cv2.imwrite(save_path,frame)
                encoding_list.extend(facedata)

                img.imgtk = frame
                img.config(image=frame)
                imgframe =tk.Frame(table_frame,bd=2,relief='ridge')
                imgframe.pack(side='left')
                # Create a label for the image
                result_label = tk.Label(imgframe, image=frame)
                result_label.pack(pady=5, side='top')
                result_label.imgtk = frame  # Reference to avoid garbage collection
                delete = tk.Button(imgframe,text='Delete',command=lambda frame=imgframe,fd=facedata,igpath=save_path,n=name :delete_frame(frame=frame,facedata=fd))
                delete.pack()

                data = pd.DataFrame({
                    'Date': [date],
                    'Time': [t],
                    'Name': [name],
                    'Purpose': [purpose],
                    'Audience': [audience],
                    'Contact': [contact],
                    'Student': [student],
                    'Dept': [dept],
                    'Exited at': [exit_time],
                    'Image Path': [save_path]
                })

                file_name = f'{date}.xlsx'
                folder ='C:/Users/ASUS/Desktop/MyProtechFolder/Guest Folder'


                if file_name in os.listdir(folder):
                    with pd.ExcelWriter(f'{folder}/{file_name}', mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                        data.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
                else:
                    data.to_excel(f'{folder}/{file_name}', index=False)

        def send_data():
            n = name_entry.get()
            p = purpose_entry.get()
            c = contact_entry.get()
            a = audience_var.get()
            s = stname.get()
            d = dept.get()

            if not n or not p or not c or a == "Select":
                messagebox.showerror('Warning',"Please fill in all required fields.")
                return

            make_entry(name=n, purpose=p, contact=c, audience=a, student=s, dept=d)
            messagebox.showinfo('Status','Data Registered Successfully')
            guest_window.destroy()
        
        def get_student_detail(*args):
            for widget in student_frame.winfo_children():
                widget.destroy()

            if audience_var.get() == 'Student':
                tk.Label(student_frame, text='Student Details:', bg='lightgray').pack(anchor='w', pady=2)
                tk.Label(student_frame, text='Name:', bg='lightgray').pack(anchor='w')
                tk.Entry(student_frame, textvariable=stname).pack(fill='x', pady=2)
                tk.Label(student_frame, text='Dept:', bg='lightgray').pack(anchor='w')
                tk.Entry(student_frame, textvariable=dept).pack(fill='x', pady=2)

        guest_window = tk.Toplevel(baseframe)
        guest_window.transient(baseframe)
        guest_window.title("Guest Entry")
        guest_window.geometry('600x500')
        guest_window.config(bg='black')

        tk.Label(guest_window, text='Guest Entry', fg='white', bg='gray', font=('Helvetica', 16, 'bold')).pack(fill='x', pady=5)

        image_frame = tk.Frame(guest_window, bg='black')
        image_frame.pack(side='right', padx=10, pady=10, fill='y')

        global img
        ref = cv2.imread('image\images.png')
        ref = cv2.resize(ref,(250,190))
        ref  = cv2.cvtColor(ref,cv2.COLOR_BGR2RGB)
        ref = Image.fromarray(ref)
        reftk= ImageTk.PhotoImage(ref)
        img = tk.Label(image_frame,image=reftk)
        img.imgtk =reftk
        img.pack()
        tk.Button(image_frame, text='Take Photo', command=get_face_data, bg='gray', fg='black').pack(pady=10)

        details_frame = tk.Frame(guest_window, bg='lightgray')
        details_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        tk.Label(details_frame, text='Name:', bg='lightgray').pack(anchor='w')
        name_entry = tk.Entry(details_frame)
        name_entry.pack(fill='x', pady=5)

        tk.Label(details_frame, text='Contact:', bg='lightgray').pack(anchor='w')
        contact_entry = tk.Entry(details_frame)
        contact_entry.pack(fill='x', pady=5)

        tk.Label(details_frame, text='Purpose:', bg='lightgray').pack(anchor='w')
        purpose_entry = tk.Entry(details_frame)
        purpose_entry.pack(fill='x', pady=5)

        tk.Label(details_frame, text=f'Date & Time: {time.strftime("%A, %d %B %Y at %H:%M")}', bg='lightgray').pack(anchor='w', pady=5)

        tk.Label(details_frame, text='Audience:', bg='lightgray').pack(anchor='w')
        audience_var = tk.StringVar(value='Select')
        audience_menu = tk.OptionMenu(details_frame, audience_var, 'Principal', 'MR', 'HOD', 'Staff', 'Student', command=get_student_detail)
        audience_menu.pack(fill='x', pady=5)

        student_frame = tk.Frame(details_frame, bg='lightgray')
        student_frame.pack(fill='x', pady=5)

        global entry_button
        entry_button = tk.Button(details_frame, text='Register', state='disabled', command=send_data, bg='gray', fg='black')
        entry_button.pack(pady=20)

        return facedata


    
    
    def setup_activity_frame():
        global encoding_list
        x = activity_frame.winfo_width()
        y = activity_frame.winfo_height()
        activity_frame.grid_rowconfigure(0,weight=1)
        activity_frame.grid_rowconfigure(1,weight=1)
        activity_frame.grid_columnconfigure(0,weight=1)
        activity_frame.grid_columnconfigure(1,weight=1)
        def staff_frame():
            #variables
            staff_path = folder_dict['Staff Folder']
            #staff details frame
            staff_frame = tk.Frame(activity_frame,bg='blue',width=(x//2)-5,height=(y//2)-5)
            staff_frame.grid(row=0,column=0,padx=4,pady=3,sticky='nsew')
            tk.Label(staff_frame,text="Staff Details",font=label_font,fg='black',height=1,relief='flat').pack(side='top',pady=5,padx=5,fill='x')
            staff_frame.propagate(False)
            #staff details Folder and file handleing
            staff_scrollbar = tk.Scrollbar(staff_frame,cursor="cross")
            staff_scrollbar.pack(side='right',fill='y')
            staff_canva = tk.Canvas(staff_frame,bg='black',yscrollcommand=staff_scrollbar.set)
            staff_canva.pack(side='top',fill='both',expand=True,padx=5,pady=5)
            staff_button_frame = tk.Frame(staff_canva,bg='Black',padx=5,pady=5)
            staff_button_frame.pack(side='left',padx=2,pady=2,fill='both',expand=True)
            staff_canva.create_window((0,0),window=staff_button_frame,anchor='n')
            update_files(path=staff_path,frame=staff_button_frame)
            staff_scrollbar.config(command=staff_canva.yview)
            def on_frame_configure(event):
                staff_canva.configure(scrollregion=staff_canva.bbox('all'))
            def on_mouse_wheel(event):
                staff_canva.yview_scroll(-1 * int(event.delta / 120), "units")
            def bind_to_mousewheel(event):
                staff_canva.bind_all("<MouseWheel>",on_mouse_wheel)
            def unbind_to_mousewheel(event):
                staff_canva.unbind_all('<MouseWheel>')
            root.bind_all("<MouseWheel>", on_mouse_wheel)
            staff_button_frame.bind("<Configure>",on_frame_configure)
            staff_canva.bind("<Enter>",bind_to_mousewheel)
            staff_canva.bind("<Leave>",unbind_to_mousewheel)


        def student_detail():
            #variables 
            var = tk.BooleanVar()
            student_path = folder_dict['Student Folder']
            # student_file_list = os.listdir(student_path)
            #student details frame
            student_frame = tk.Frame(activity_frame,bg='blue',width=(x//2)-5,height=(y//2)-5)
            student_frame.grid(row=0,column=1,padx=4,pady=3,sticky='nsew')
            tk.Label(student_frame,text="Student details",fg='black',font=label_font,height=1,relief='flat').pack(side='top',padx=5,pady=5,fill='x')
            student_frame.propagate(False)
            #Student details Folder and File handling
            student_scrollbar =tk.Scrollbar(student_frame,cursor='cross')
            student_scrollbar.pack(side='right',fill='y')
            student_canva = tk.Canvas(student_frame,bg='black',yscrollcommand=student_scrollbar.set)
            student_canva.pack(side='top',fill='both',expand=True,pady=5,padx=5)
            student_button_frame = tk.Frame(student_canva,bg='Black')
            student_button_frame.pack(side='top',padx=5,pady=5,expand=True,fill='both')
            student_canva.create_window((0,0),window=student_button_frame,anchor='n')
            update_files(student_path,student_button_frame)
            def on_frame_configure(event):
                student_canva.configure(scrollregion=student_canva.bbox('all'))
            def on_frame_configure(event):
                student_canva.configure(scrollregion=student_canva.bbox('all'))
            def on_mouse_wheel(event):
                student_canva.yview_scroll(-1 * int(event.delta / 120), "units")
            def bind_to_mousewheel(event):
                student_canva.bind_all("<MouseWheel>",on_mouse_wheel)
            def unbind_to_mousewheel(event):
                student_canva.unbind_all('<MouseWheel>')
            student_button_frame.bind("<Configure>",on_frame_configure)
            student_canva.bind("<Enter>",bind_to_mousewheel)
            student_canva.bind("<Leave>",unbind_to_mousewheel)



        def canva_list_guest():
            # Variables
            guest_path = folder_dict['Guest Folder']

            def add_guest():
                global encoding_list
                data = handle_guest(baseframe=root,table_frame = displayframe)
                
                


            def on_frame_configure(event):
                """Update canvas scroll region."""
                guest_canva.configure(scrollregion=guest_canva.bbox('all'))

            # Create guest frame
            guest_frame = tk.Frame(activity_frame, bg='blue', width=x-10, height=(y//2)-10)
            guest_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky='nsew')

            tk.Label(guest_frame, text='Guest Details', fg='black', font=label_font, relief='flat').pack(
                side='top', padx=5, pady=5, fill='x')
            guest_frame.propagate(False)

            # Buttons Frame
            guest_buttons = tk.Frame(guest_frame)
            guest_buttons.pack(side='top', fill='x', padx=5)

            addguestbutton = tk.Button(guest_buttons, text='Add Guest', command=add_guest,font=button_font,fg=button_fg_color, bg=button_bg_color)
            addguestbutton.pack(side='left', padx=5, pady=2)

            # Canvas and Scrollbar
            guest_canva = tk.Canvas(guest_frame, bg='black')
            guest_canva.pack(side='top', expand=True, padx=5, pady=5, fill='both')

            guest_scrollbar_x = tk.Scrollbar(guest_frame, orient='horizontal', command=guest_canva.xview)
            guest_scrollbar_x.pack(side='bottom', fill='x')
            guest_canva.configure(xscrollcommand=guest_scrollbar_x.set)

            # Display Frame
            displayframe = tk.Frame(guest_canva,padx=5,pady=5,bg=blackbg)
            guest_canva.create_window((0, 0), window=displayframe, anchor='nw')
           

            # Bind configure event
            displayframe.bind("<Configure>", on_frame_configure)

           
        staff_frame()
        student_detail()
        canva_list_guest()
    root.after(10,setup_activity_frame)
    root.bind('<Escape>',end_fullscreen)
    root.bind('<F11>',toggle_fullscreen)
    main_menu.bind('<Button-1>',show_file_menu)
    add_encoding.bind('<Button-1>',add_face)

    root.mainloop()

