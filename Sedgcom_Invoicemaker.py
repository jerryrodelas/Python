from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tmsg
import os
import time
from fpdf import FPDF
from PIL import Image
import csv


#===================Python Variables=======================

menu_category = ["Alarm Systems","CCTV","Access Control","Network","Data Cabling","Audio Visual","Satellite & Terrestial"]
menu_category_dict = {"Alarm Systems":"1 Alarm Systems.csv","CCTV":"2 CCTV.csv",
                "Access Control":"3 Access Control.csv","Network":"4 Network.csv",
                "Data Cabling":"5 Data Cabling.csv","Audio Visual":"6 Audio Visual.csv",
                "Satellite & Terrestial":"7 Satellite & Terrestial.csv"}

order_dict = {}
for i in menu_category:
    order_dict[i] = {}

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#====================Backend Functions===========================
def load_menu():
    menuCategory.set("")
    menu_table.delete(*menu_table.get_children())
    menu_file_list = os.listdir("Menu")
    for file in menu_file_list:
        f = open("Menu\\" + file , "r")
        category=""
        while True:
            line = f.readline()
            if(line==""):
                menu_table.insert('',END,values=["","",""])
                break
            elif (line=="\n"):
                continue
            elif(line[0]=='#'):
                category = line[1:-1]
                name = "\t\t"+line[:-1]
                price = ""
            elif(line[0]=='*'):
                name = line[:-1]
                price = ""
            else:
                name = line[:line.rfind(" ")]
                price = line[line.rfind(" ")+1:-3]
            
            menu_table.insert('',END,values=[name,price,category])


def load_order():
    order_table.delete(*order_table.get_children())
    for category in order_dict.keys():
        if order_dict[category]:
            for lis in order_dict[category].values():
                order_table.insert('',END,values=lis)
    update_total_price()

def add_button_operation():
    name = itemName.get()
    rate = itemRate.get()
    category = itemCategory.get()
    quantity = itemQuantity.get()


    if name in order_dict[category].keys():
        tmsg.showinfo("Error", "Item already exist in your order")
        return
    if not quantity.isdigit():
        tmsg.showinfo("Error", "Please Enter Valid Quantity")
        return

    lis = [name,rate,quantity,str(int(rate)*int(quantity)),category]
    order_dict[category][name] = lis
    load_order()
    
def load_item_from_menu(event):
    cursor_row = menu_table.focus()
    contents = menu_table.item(cursor_row)
    row = contents["values"]

    itemName.set(row[0])
    itemRate.set(row[1])
    itemCategory.set(row[2])
    itemQuantity.set("1")

def load_item_from_order(event):
    cursor_row = order_table.focus()
    contents = order_table.item(cursor_row)
    row = contents["values"]

    itemName.set(row[0])
    itemRate.set(row[1])
    itemQuantity.set(row[2])
    itemCategory.set(row[4])

def show_button_operation():
    category = menuCategory.get()
    if category not in menu_category:
        tmsg.showinfo("Error", "Please select valid Choice")
    else:
        menu_table.delete(*menu_table.get_children())
        f = open("Menu\\" + menu_category_dict[category] , "r")
        while True:
            line = f.readline()
            if(line==""):
                break
            if (line[0]=='#' or line=="\n"):
                continue
            if(line[0]=='*'):
                name = "\t"+line[:-1]
                menu_table.insert('',END,values=[name,"",""])
            else:
                name = line[:line.rfind(" ")]
                price = line[line.rfind(" ")+1:-3]
                menu_table.insert('',END,values=[name,price,category])

def clear_button_operation():
    itemName.set("")
    itemRate.set("")
    itemQuantity.set("")
    itemCategory.set("")
    itemHours.set("")
def cancel_button_operation():
    names = []
    for i in menu_category:
        names.extend(list(order_dict[i].keys()))
    if len(names)==0:
        tmsg.showinfo("Error", "Your order list is Empty")
        return
    ans = tmsg.askquestion("Cancel Order", "Are You Sure to Cancel Order?")
    if ans=="no":
        return
    order_table.delete(*order_table.get_children())
    for i in menu_category:
        order_dict[i] = {}
    clear_button_operation()
    update_total_price()

def update_button_operation():
    name = itemName.get()
    rate = itemRate.get()
    category = itemCategory.get()
    quantity = itemQuantity.get()

    if category=="":
        return
    if name not in order_dict[category].keys():
        tmsg.showinfo("Error", "Item is not in your order list")
        return
    if order_dict[category][name][2]==quantity:
        tmsg.showinfo("Error", "No changes in Quantity")
        return
    order_dict[category][name][2] = quantity
    order_dict[category][name][3] = str(int(rate)*int(quantity))
    load_order()

def remove_button_operation():
    name = itemName.get()
    category = itemCategory.get()

    if category=="":
        return
    if name not in order_dict[category].keys():
        tmsg.showinfo("Error", "Item is not in your order list")
        return
    del order_dict[category][name]
    load_order()

def update_total_price():
    price = 0
    for i in menu_category:
        for j in order_dict[i].keys():
            price += int(order_dict[i][j][3])
    if price == 0:
        totalPrice.set("")
    else:
        totalPrice.set(int(price))


def bill_button_operation():
    customer_name = customerName.get()
    customer_contact = customerContact.get()
    item_hours = itemHours.get()
    names = []

    for i in menu_category:
        names.extend(list(order_dict[i].keys()))
    if len(names)==0:
        tmsg.showinfo("Error", "Your order list is Empty")
        return
    if customer_name=="" or customer_contact=="":
        tmsg.showinfo("Error", "Customer Details Required")
        return

    if not item_hours.isdigit():
        tmsg.showinfo("Error", "Please Enter Valid Labour Hours")
        return

    if not customerContact.get().isdigit():
        tmsg.showinfo("Error", "Invalid Customer Contact")
        return   
    ans = tmsg.askquestion("Generate Bill", "Are You Sure to Generate Bill?")
    ans = "yes"
    if ans=="yes":
        bill = Toplevel()
        bill.title("Invoice")
        bill.geometry("670x500+300+100")
        bill.wm_iconbitmap("cctv.ico")

        bill_text_area = Text(bill, font=("verdana", 12))
        st = "\t\t\t\tSedgcom Pty Ltd\n"
        st += "\t\t\tABN: 81 612 022 769\n"
        st += "-"*61 + "Invoice" + "-"*61 + "\nDate:- "

        #Date and time
        t = time.localtime(time.time())
        week_day_dict = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",
                            6:"Sunday"}
        st += f"{t.tm_mday} / {t.tm_mon} / {t.tm_year} ({week_day_dict[t.tm_wday]})"
        st += " "*10 + f"\t\t\t\t\t\tTime:- {t.tm_hour} : {t.tm_min} : {t.tm_sec}"

        #Customer Name & Contact
        st += f"\nCustomer Name:- {customer_name}\nCustomer Contact:- {customer_contact}\n"
        st += "-"*130 + "\n" + " "*4 + "DESCRIPTION\t\t\t\t\t\t\t\t\t\t\t\t\t\tRATE\t\t\t\tQUANTITY\t\t\t\tAMOUNT\n"
        st += "-"*130 + "\n"
        csv_tab = "Description,Rate,Qty,Amount\n"
        #List of Items
        for i in menu_category:
            for j in order_dict[i].keys():
                lis = order_dict[i][j]
                name = lis[0]
                rate = lis[1]
                quantity = lis[2]
                price = lis[3]
                csv_tab += name + "," + rate + "," + quantity +","+ price +"\n"  # only takes the list of materials data
                st += name + "," + rate + "," +quantity +","+ price+ "\n\n"

        st += "-"*130



#Total Price

        total_hours = int(itemHours.get())*50
        total_cost_of_material = totalPrice.get()
        result = int(total_cost_of_material) + total_hours
        gst = result*0.1
        result_with_gst = result + gst

        st += f"\nTotal Labour Cost :A$ {total_hours} \t Cost of Materials:A$ {total_cost_of_material} \t GST:{str('%.2f'%(gst))} \tTotal price :A$ {result_with_gst}\n"
        st += "-"*130

        #display bill in new window
        bill_text_area.insert(1.0, st)

        #write into file
        folder = f"{t.tm_mday},{t.tm_mon},{t.tm_year}"
        if not os.path.exists(f"Invoice Records\\{folder}"):
            os.makedirs(f"Invoice Records\\{folder}")
        file = open(f"Invoice Records\\{folder}\\{customer_name+customer_contact}.txt", "w")
        file2 = open(f"Invoice Records\\{folder}\\{customer_name+customer_contact}.csv", "w")
        file.write(st)
        file2.write(csv_tab)
        file.close()
        file2.close()


        #Clear operations
        order_table.delete(*order_table.get_children())
        for i in menu_category:
            order_dict[i] = {}
            clear_button_operation()
            update_total_price()
            customerName.set("")
            customerContact.set("")

        bill_text_area.pack(expand=True, fill=BOTH)
        bill.focus_set()
        bill.protocol("WM_DELETE_WINDOW", close_window)

        with open(f"Invoice Records\\{folder}\\{customer_name+customer_contact}.csv", newline='') as f:
            reader = csv.reader(f)
            pdf = FPDF()
            pdf.add_page()

            im = Image.open('sedgcom.jpg')
            width_img, height_img = im.size

            #mm = (pixels * 25.4) / dpi
            # - 25.4 millimeters in an inch
            w = (width_img*25.4)/280
            h = (height_img*25.4)/300
            pdf.image('sedgcom.jpg',155,1,w,h)

            pdf.set_font("Courier",'B',size=15)
            pdf.cell(200,5,txt="sedgcomptyltd@gmail.com",ln=2,align='L')
            pdf.cell(200,5,txt="ABN: 81 612 022 769",ln=3,align='L')
            pdf.cell(200,5,txt="Tax Invoice",ln=4,align='L')

            pdf.set_font("Courier",'B',size=12)
            pdf.cell(200,10,txt="_"*130,ln=19,align='C')
            pdf.cell(200,5,txt="Date:-"+ f"{t.tm_mday} / {t.tm_mon} / {t.tm_year} ({week_day_dict[t.tm_wday]})",ln=20,align='L')
            pdf.cell(200,5,txt="Customer Name:-"+(customer_name),ln=21,align='L')
            pdf.cell(200,5,txt="Customer Contact:-"+(customer_contact),ln=22,align='L')
            pdf.cell(200,5,txt="_"*130,ln=23,align='C')
            pdf.cell(200,5,txt="",ln=24,align='C')


            pdf.set_font('Courier', 'B', 12)

            pdf.ln(1)

            th = pdf.font_size

            for row in reader:
                pdf.cell(130, th, str(row[0]), border=1)
                pdf.cell(20, th, row[1], border=1)
                pdf.cell(20, th, row[2], border=1)
                pdf.cell(20, th, row[3], border=1)
                pdf.ln(th)
            pdf.set_font('Courier', 'B', 7)
            pdf.cell(100,th, '- end of report -',align='C')

            pdf.ln(10)

            pdf.set_font('Courier', 'B', 12)
            pdf.cell(200,5,txt="Total Labour Cost :A$"+ str(total_hours) + "\tCost of Materials :A$\t"+str(total_cost_of_material),ln=29,align='L')
            pdf.cell(200,5,txt="GST  :A$\t" + str('%.2f'%(gst)) + "\tTotal price :A$\t" + str(result_with_gst),ln=30,align='L')



            pdf.output(f"Invoice Records\\{folder}\\{customer_name+customer_contact}.pdf")


def close_window():
    tmsg.showinfo("Close Window", "Thanks for using our service!")
    root.destroy()

#==================Backend Code Ends===============

#================Frontend Code Start==============
root = Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.title("Security and Communications Order Form")
root.wm_iconbitmap("Secure.ico")
#root.attributes('-fullscreen', True)
#root.resizable(0, 0)

#================Title==============
style_button = ttk.Style()
style_button.configure("TButton",font = ("verdana",10,"bold"),
   background="black")

title_frame = Frame(root, bd=8, bg="#dce0de", relief=GROOVE)
title_frame.pack(side=TOP, fill="x")

title_label = Label(title_frame, text="Sedgcom Pty Ltd  ABN: 81 612 022 769",
                    font=("verdana", 20, "bold"),bg = "#dce0de", fg="black", pady=5)
title_label.pack()

#==============Customer=============
customer_frame = LabelFrame(root,text="Customer Details",font=("verdana", 15, "bold"),
                            bd=8, bg="#dce0de", relief=GROOVE)
customer_frame.pack(side=TOP, fill="x")

customer_name_label = Label(customer_frame, text="Name", 
                    font=("verdana", 15, "bold"),bg = "#dce0de", fg="black")
customer_name_label.grid(row = 0, column = 0)

customerName = StringVar()
customerName.set("")
customer_name_entry = Entry(customer_frame,width=30,font="verdana 15",bd=5,
                                textvariable=customerName)
customer_name_entry.grid(row = 0, column=1,padx=50)

customer_contact_label = Label(customer_frame, text="Contact", 
                    font=("verdana", 15, "bold"),bg = "#dce0de", fg="black")
customer_contact_label.grid(row = 0, column = 2)

customerContact = StringVar()
customerContact.set("")
customer_contact_entry = Entry(customer_frame,width=30,font="verdana 15",bd=5,
                                textvariable=customerContact)
customer_contact_entry.grid(row = 0, column=3,padx=50)

#===============Menu===============
menu_frame = Frame(root,bd=8, bg="black", relief=GROOVE)
menu_frame.place(x=0,y=125,height=585,width=680)

menu_label = Label(menu_frame, text="Menu", 
                    font=("verdana", 15, "bold"),bg = "#dce0de", fg="black", pady=0)
menu_label.pack(side=TOP,fill="x")

menu_category_frame = Frame(menu_frame,bg="#dce0de",pady=10)
menu_category_frame.pack(fill="x")

combo_label = Label(menu_category_frame,text="Select Type", 
                    font=("verdana", 12, "bold"),bg = "#dce0de", fg="black")
combo_label.grid(row=0,column=0,padx=10)

menuCategory = StringVar()
combo_menu = ttk.Combobox(menu_category_frame,values=menu_category,
                            textvariable=menuCategory)
combo_menu.grid(row=0,column=1,padx=30)

show_button = ttk.Button(menu_category_frame, text="Show",width=10,
                        command=show_button_operation)
show_button.grid(row=0,column=2,padx=60)

show_all_button = ttk.Button(menu_category_frame, text="Show All",
                        width=10,command=load_menu)
show_all_button.grid(row=0,column=3)

############################# Menu table ##########################################
menu_table_frame = Frame(menu_frame)
menu_table_frame.pack(fill=BOTH,expand=1)

scrollbar_menu_x = Scrollbar(menu_table_frame,orient=HORIZONTAL)
scrollbar_menu_y = Scrollbar(menu_table_frame,orient=VERTICAL)

style = ttk.Style()
style.configure("Treeview.Heading",font=("verdana",12, "bold"))
style.configure("Treeview",font=("verdana",12),rowheight=25)

menu_table = ttk.Treeview(menu_table_frame,style = "Treeview",
            columns =("name","price","category"),xscrollcommand=scrollbar_menu_x.set,
            yscrollcommand=scrollbar_menu_y.set)

menu_table.heading("name",text="Description")
menu_table.heading("price",text="Price")
menu_table["displaycolumns"]=("name", "price")
menu_table["show"] = "headings"
menu_table.column("price",width=50,anchor='center')

scrollbar_menu_x.pack(side=BOTTOM,fill=X)
scrollbar_menu_y.pack(side=RIGHT,fill=Y)

scrollbar_menu_x.configure(command=menu_table.xview)
scrollbar_menu_y.configure(command=menu_table.yview)

menu_table.pack(fill=BOTH,expand=1)


load_menu()
menu_table.bind("<ButtonRelease-1>",load_item_from_menu)

###########################################################################################

#===============Item Frame=============
item_frame = Frame(root,bd=8, bg="black", relief=GROOVE)
item_frame.place(x=680,y=125,height=300,width=680)

item_title_label = Label(item_frame, text="Item",
                    font=("verdana", 15, "bold"),bg = "#dce0de", fg="black")
item_title_label.pack(side=TOP,fill="x")

item_frame2 = Frame(item_frame, bg="#dce0de")
item_frame2.pack(fill=X)

item_name_label = Label(item_frame2, text="Description",
                    font=("verdana", 12, "bold"),bg = "#dce0de", fg="black")
item_name_label.grid(row=0,column=0)

itemCategory = StringVar()
itemCategory.set("")

itemName = StringVar()
itemName.set("")
item_name = Entry(item_frame2, font="verdana 12",textvariable=itemName,state=DISABLED, width=25)
item_name.grid(row=0,column=1,padx=10)

item_rate_label = Label(item_frame2, text="Rate", 
                    font=("verdana", 12, "bold"),bg = "#dce0de", fg="black")
item_rate_label.grid(row=0,column=2,padx=40)

itemRate = StringVar()
itemRate.set("")
item_rate = Entry(item_frame2, font="verdana 12",textvariable=itemRate,state=DISABLED, width=10)
item_rate.grid(row=0,column=3,padx=10)

item_quantity_label = Label(item_frame2, text="Quantity",
                    font=("verdana", 12, "bold"),bg = "#dce0de", fg="black")
item_quantity_label.grid(row=1,column=0,padx=30,pady=15)

itemQuantity = StringVar()
itemQuantity.set("")
item_quantity = Entry(item_frame2, font="verdana 12",textvariable=itemQuantity, width=10)
item_quantity.grid(row=1,column=1)

# labour hours
item_hours_label = Label(item_frame2, text="Labour Hours",
                            font=("verdana", 12, "bold"),bg = "#dce0de", fg="black")
item_hours_label.grid(row=1,column=2,padx=10,pady=15)

itemHours = StringVar()
itemHours.set("")
item_hours = Entry(item_frame2, font="verdana 12",textvariable=itemHours, width=10)
item_hours.grid(row=1,column=3)

item_frame3 = Frame(item_frame, bg="#c4cfc2")
item_frame3.pack(fill=X)

add_button = ttk.Button(item_frame3, text="Add Item"
                        ,command=add_button_operation)
add_button.grid(row=0,column=0,padx=40,pady=30)

remove_button = ttk.Button(item_frame3, text="Remove Item"
                        ,command=remove_button_operation)
remove_button.grid(row=0,column=1,padx=20,pady=10)

update_button = ttk.Button(item_frame3, text="Update Quantity"
                        ,command=update_button_operation)
update_button.grid(row=0,column=2,padx=20,pady=10)

clear_button = ttk.Button(item_frame3, text="Clear",
                        width=8,command=clear_button_operation)

clear_button.grid(row=0,column=3,padx=40,pady=30)

#==============Order Frame=====================
order_frame = Frame(root,bd=8, bg="#dce0de", relief=GROOVE)
order_frame.place(x=680,y=335,height=370,width=680)

order_title_label = Label(order_frame, text="Invoice",
                    font=("verdana", 15, "bold"),bg = "#dce0de", fg="black")
order_title_label.pack(side=TOP,fill="x")

############################## Order table ###################################
order_table_frame = Frame(order_frame)
order_table_frame.place(x=0,y=40,height=260,width=680)

scrollbar_order_x = Scrollbar(order_table_frame,orient=HORIZONTAL)
scrollbar_order_y = Scrollbar(order_table_frame,orient=VERTICAL)

order_table = ttk.Treeview(order_table_frame,
            columns =("name","rate","quantity","price","category"),xscrollcommand=scrollbar_order_x.set,
            yscrollcommand=scrollbar_order_y.set)

order_table.heading("name",text="Description")
order_table.heading("rate",text="Rate")
order_table.heading("quantity",text="Quantity")
order_table.heading("price",text="Price")
order_table["displaycolumns"]=("name", "rate","quantity","price")
order_table["show"] = "headings"
order_table.column("rate",width=100,anchor='center', stretch=NO)
order_table.column("quantity",width=100,anchor='center', stretch=NO)
order_table.column("price",width=100,anchor='center', stretch=NO)

order_table.bind("<ButtonRelease-1>",load_item_from_order)

scrollbar_order_x.pack(side=BOTTOM,fill=X)
scrollbar_order_y.pack(side=RIGHT,fill=Y)

scrollbar_order_x.configure(command=order_table.xview)
scrollbar_order_y.configure(command=order_table.yview)

order_table.pack(fill=BOTH,expand=1)


###########################################################################################

total_price_label = Label(order_frame, text="Total Material Cost",
                    font=("verdana", 12, "bold"),bg = "#dce0de", fg="black")
total_price_label.pack(side=LEFT,anchor=SW,padx=20,pady=10)


totalPrice = StringVar()
totalPrice.set("")

total_price_entry = Entry(order_frame, font="verdana 12",textvariable=totalPrice,state=DISABLED,
                            width=10)
total_price_entry.pack(side=LEFT,anchor=SW,padx=0,pady=10)

bill_button = ttk.Button(order_frame, text="Generate Invoice",width=15,
                        command=bill_button_operation)
bill_button.pack(side=LEFT,anchor=SW,padx=50,pady=10)

cancel_button = ttk.Button(order_frame, text="Cancel Order",command=cancel_button_operation)
cancel_button.pack(side=LEFT,anchor=SW,padx=0,pady=10)

root.mainloop()
#====================Frontend code ends=====================