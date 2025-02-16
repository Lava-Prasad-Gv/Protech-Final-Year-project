import tkinter as tk
import time
import os
import cv2
import pandas as pd 
import encodingSupport as es
from PIL import Image, ImageTk
from tkinter import messagebox as mb
import numpy as np

save_path = None
facedata=[]
def handle_guest(baseframe,table_frame, encoding_list):
    stname = tk.StringVar()
    dept = tk.StringVar()

    def delete_frame(frame, facedata):
        # Destroy the frame
        global encoding_list
        frame.destroy()

        # Create the list of data to remove
        to_remove = [np.array(ad) for ad in facedata]

        # Update the encoding list
        encoding_list[:] = [enc for enc in encoding_list if not any(np.array_equal(enc, rm) for rm in to_remove)]
    
    def get_face_data():
        name= name_entry.get()
        global save_path,facedata
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            ret, frame = cam.read()
            if ret:
                os.makedirs('C:/Users/ASUS/Desktop/MyProtechFolder/Guest Folder/data', exist_ok=True)
                save_path = f'C:/Users/ASUS/Desktop/MyProtechFolder/Guest Folder/data/{name}_{time.strftime("%d-%m-%Y_%H_%M")}.jpg'
                cv2.imwrite(save_path, frame)
                facedata = es.get_face_encodings(frame)
                print('Inside guestfunction:',type(facedata))
                frame = cv2.resize(frame, (250, 190))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                frame = ImageTk.PhotoImage(image=frame)
                encoding_list.extend(facedata)

                img.imgtk = frame
                img.config(image=frame)
                entry_button.config(state='normal')

                imgframe =tk.Frame(table_frame,bd=2,relief='ridge')
                imgframe.pack(side='left')
                # Create a label for the image
                result_label = tk.Label(imgframe, image=frame)
                result_label.pack(pady=5, side='top')
                result_label.imgtk = frame  # Reference to avoid garbage collection
                
                delete = tk.Button(imgframe,text='Delete',command=lambda frame=imgframe,fd=facedata,igpath=save_path,n=name :delete_frame(frame=frame,facedata=fd))
                delete.pack()
        
                
            cam.release()
    
        

    def make_entry(name, purpose, contact, audience, student, dept, exit_time='Not Exited'):
        date = time.strftime('%d_%m_%Y')
        t = time.strftime('%H:%M')
        data = pd.DataFrame({
            'Date': [date],
            'Time': [t],
            'Name': [name],
            'Purpose': [purpose],
            'Audience': [audience],
            'Contact': [contact],
            'Student': [student],
            'Dept': [dept],
            'Exited at': [exit_time]
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
            mb.showerror('Warning',"Please fill in all required fields.")
            return

        make_entry(name=n, purpose=p, contact=c, audience=a, student=s, dept=d)
        mb.showinfo('Status','Data Registered Successfully')
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

