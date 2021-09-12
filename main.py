import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import readxml
from PIL import ImageTk, Image
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
import matplotlib.colors as colors
import matplotlib.cm as cmx


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


# Hover help function
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text:
            return
        # calculate where the tip should be shown
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 37
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def createtooltip(widget, text):
    tool_tip = ToolTip(widget)

    def enter(event):
        tool_tip.showtip(text)

    def leave(event):
        tool_tip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class Mainprogramme:
    def __init__(self):
        # variables
        self.datadic = {}
        self.lenseq = {}
        self.seqlenlist = []
        self.counter = {}
        self.window = tk.Tk()
        self.window.title("Plothap")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.quit_me)
        self.coordinate = []
        self.edges = []
        self.group = []
        self.nodesize = []
        self.group_num = 0
        self.color = []
        self.theme = []
        self.group_kind = []
        self.legend_size = 10
        self.nodemax = 7
        self.nodemin = 2
        self.queryready = False

        # menu
        menubar = tk.Menu(self.window)

        filemenu = tk.Menu(menubar, tearoff=0)
        toolsmenu = tk.Menu(menubar, tearoff=0)
        plotmenu = tk.Menu(menubar, tearoff=0)
        helpmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label='File', menu=filemenu)
        menubar.add_cascade(label='Tools', menu=toolsmenu)
        menubar.add_cascade(label='Network', menu=plotmenu)
        menubar.add_cascade(label='Help', menu=helpmenu)

        filemenu.add_command(label='New', command=self.newproject)
        filemenu.add_command(label='Search', command=self.searchwindow)
        filemenu.add_command(label='Save', command=lambda: self.savefasta(True, "F"))
        filemenu.add_command(label='Load', command=self.loadwindow)
        filemenu.add_command(label='Add', command=self.adddata)
        filemenu.add_command(label='Export graphics', command=self.saveeps)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quitplothap)

        toolsmenu.add_command(label='Filter', command=self.filterwindow)
        toolsmenu.add_command(label='Alignment', command=self.alignmentwindow)
        toolsmenu.add_command(label='Summary plot', command=self.summaryplotwindow)

        plotmenu.add_command(label='TCS Network', command=lambda: self.generate_net("tcs"))
        plotmenu.add_command(label='MSN Network', command=lambda: self.generate_net("msn"))

        helpmenu.add_command(label='Help content', command=print(1))
        helpmenu.add_command(label='About', command=print(2))

        # tool frame
        # flat, groove, raised, ridge, solid, or sunken
        frametool = tk.Frame(self.window, relief='groove', bd=2, padx=2, pady=2)
        frametool.pack(fill="x", side="top")

        searchimgpath = Image.open("./icon/isearch.png")
        searchimgpath = searchimgpath.resize((30, 30))
        searchimg = ImageTk.PhotoImage(searchimgpath)
        botsearch = tk.Button(frametool, text='Search and download',
                              command=self.searchwindow, image=searchimg, bd=2, relief='flat')
        botsearch.grid(row=0, column=0)

        createtooltip(botsearch, text='Search through BOLDsystems\nDatasets can be downloaded from here.')

        loadimgpath = Image.open("./icon/iload.png")
        loadimgpath = loadimgpath.resize((30, 30))
        loadimg = ImageTk.PhotoImage(loadimgpath)
        botload = tk.Button(frametool, text='Load', command=self.loadwindow, image=loadimg,
                            bd=2, relief='flat')
        botload.grid(row=0, column=1)

        createtooltip(botload, text='Load file')

        filterimgpath = Image.open("./icon/ifilter.png")
        filterimgpath = filterimgpath.resize((30, 30))
        filterimg = ImageTk.PhotoImage(filterimgpath)
        botfilter = tk.Button(frametool, text='Filter',
                              command=self.filterwindow, image=filterimg, bd=2, relief='flat')
        botfilter.grid(row=0, column=3)

        createtooltip(botfilter, text='Filter')

        aliimgpath = Image.open("./icon/ialignment.png")
        aliimgpath = aliimgpath.resize((30, 30))
        aliimg = ImageTk.PhotoImage(aliimgpath)
        botali = tk.Button(frametool, text='Alignment', command=self.alignmentwindow, image=aliimg, bd=2, relief='flat')
        botali.grid(row=0, column=4)

        createtooltip(botali, text='Sequence alignment through MUSCLE.')

        sumimgpath = Image.open("./icon/iplotsum.png")
        sumimgpath = sumimgpath.resize((30, 30))
        sumimg = ImageTk.PhotoImage(sumimgpath)
        botsum = tk.Button(frametool, text='Summary plot', command=self.summaryplotwindow, image=sumimg, bd=2, relief='flat')
        botsum.grid(row=0, column=5)

        createtooltip(botsum, text='Summary plot for Trimming')

        zoominimgpath = Image.open("./icon/izoomi.png")
        zoominimgpath = zoominimgpath.resize((30, 30))
        zoominimg = ImageTk.PhotoImage(zoominimgpath)
        botzin = tk.Button(frametool, text='Zoom in', command=self.zoom_in, image=zoominimg, bd=2, relief='flat')
        botzin.grid(row=0, column=7)

        createtooltip(botzin, text='Zoom in')

        zoomoutimgpath = Image.open("./icon/izoomo.png")
        zoomoutimgpath = zoomoutimgpath.resize((30, 30))
        zoomoutimg = ImageTk.PhotoImage(zoomoutimgpath)
        botzout = tk.Button(frametool, text='Zoom out', command=self.zoom_out, image=zoomoutimg, bd=2, relief='flat')
        botzout.grid(row=0, column=8)

        createtooltip(botzout, text='Zoom out')

        plotoptionimgpath = Image.open("./icon/ioptions.png")
        plotoptionimgpath = plotoptionimgpath.resize((30, 30))
        plotoptionimg = ImageTk.PhotoImage(plotoptionimgpath)
        botpoption = tk.Button(frametool, text='Options', command=self.plotoption, image=plotoptionimg, bd=2, relief='flat')
        botpoption.grid(row=0, column=9)

        createtooltip(botpoption, text='Option for plotting')

        toolframe_sep = tk.ttk.Separator(frametool, orient='vertical')
        toolframe_sep.grid(row=0, column=2, sticky='ns', padx=2)

        toolframe_sep2 = tk.ttk.Separator(frametool, orient='vertical')
        toolframe_sep2.grid(row=0, column=6, sticky='ns', padx=2)

        # console
        frameconsole = tk.LabelFrame(self.window, text="Console", labelanchor="nw", bd=2, height=8)
        frameconsole.pack(side='bottom', fill="x")

        frameconsolebot = tk.Frame(frameconsole)
        frameconsolebot.pack(side='left', padx=2)
        consoleclear = tk.Button(frameconsolebot, text="Clear", bd=2, command=self.clearconsole)
        consoleclear.grid(row=0, column=0, sticky="ew", pady=2)
        consoletop = tk.Button(frameconsolebot, text="Top", bd=2, command=self.topconsole)
        consoletop.grid(row=1, column=0, sticky="ew", pady=2)
        consolebot = tk.Button(frameconsolebot, text="Bot", bd=2, command=self.botconsole)
        consolebot.grid(row=2, column=0, sticky="ew", pady=2)

        self.console = tk.Text(frameconsole, bd=1, height=8)
        consolescroll = tk.Scrollbar(frameconsole)
        consolescroll.pack(side=tk.RIGHT, fill=tk.Y)
        consolescroll.configure(command=self.console.yview)
        self.console.config(yscrollcommand=consolescroll.set, state="disabled")
        self.console.pack(side='right', expand=1, fill='both', padx=3)

        # Data description frame
        framedes = tk.LabelFrame(self.window, text="Data description", labelanchor="n", bd=2, width=20)
        framedes.pack(side='left', fill="y")
        self.descrip = tk.Text(framedes, bd=1, width=30)
        desscroll = tk.Scrollbar(framedes)
        desscroll.pack(side=tk.RIGHT, fill=tk.Y)
        desscroll.configure(command=self.descrip.yview)
        self.descrip.config(yscrollcommand=desscroll.set, state="disabled")
        self.descrip.pack(expand=1, fill="both")
        self.descrip.tag_config("tag_filename", font=('Arial', 13, "bold"))
        self.descrip.tag_config("tag_title", font=('Arial', 11, "bold"))
        self.descrip.tag_config("tag_content", font=('Arial', 10))

        plotarea = tk.LabelFrame(self.window, bd=2, width=500, height=480)
        plotarea.pack(fill="both", expand=1)
        self.canvas = tk.Canvas(plotarea, width=500, height=480, bg='white')
        self.canvas.pack(fill="both", expand=1)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_move)
        self.canvas.bind("<B1-ButtonRelease>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<B3-Motion>", self.on_canvas_right_move)

        self.dragging_node = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.stop = 1
        self.zoom = 1
        self.ready = False
        self.node = {}
        self.centre = [250, 240]
        self.textsize = 2.3
        self.dotsize = 2.3

        self.window.config(menu=menubar)

        self.window.mainloop()

    def quit_me(self):
        self.window.quit()
        self.window.destroy()

    def newproject(self):
        # when "new" function is performed, all dataset will be cleaned.
        self.datadic = {}
        self.lenseq = {}
        self.seqlenlist = []
        self.counter = {}
        self.coordinate = []
        self.edges = []
        self.group = []
        self.nodesize = []
        self.group_num = 0
        self.color = []
        self.theme = []
        self.group_kind = []
        self.legend_size = 10
        self.nodemax = 7
        self.nodemin = 2
        self.dragging_node = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.stop = 1
        self.zoom = 1
        self.ready = False
        self.node = {}
        self.centre = [250, 240]
        self.textsize = 2.3
        self.dotsize = 2.3
        self.descrip.configure(state="normal")
        self.descrip.delete("1.0", "end")
        self.descrip.configure(state="disable")
        self.canvas.delete("all")
        self.clearconsole()

    # data description function
    # id:[seq, spe_name_out, countryin, sexin, iden_provider, iden_method]
    def datadescription(self, dic, filename, status):
        sexdic = {}
        countrydic = {}
        taxondic = {}
        geodic = {}
        worlddic = {}
        providerdic = {}

        # if data hasn't been aligned
        if status == "na":
            # read dic
            # dic structure: id:[seq, spe_name_out, countryin, sexin, iden_provider, georegion, world]
            count = str(len(dic)) + "\n"
            for key, value in dic.items():
                species = value[1]
                country = value[2]
                sex = value[3]
                provider = value[4]
                geo = value[5]
                world = value[6]
                # count species
                if species not in taxondic.keys():
                    taxondic.setdefault(species, 1)
                else:
                    taxondic[species] += 1
                # count country
                if country not in countrydic.keys():
                    countrydic.setdefault(country, 1)
                else:
                    countrydic[country] += 1
                # count sex
                if sex not in sexdic.keys():
                    sexdic.setdefault(sex, 1)
                else:
                    sexdic[sex] += 1
                # count provider
                if provider not in providerdic.keys():
                    providerdic.setdefault(provider, 1)
                else:
                    providerdic[provider] += 1
                # count geo
                if geo not in geodic.keys():
                    geodic.setdefault(geo, 1)
                else:
                    geodic[geo] += 1
                # count world
                if world not in worlddic.keys():
                    worlddic.setdefault(world, 1)
                else:
                    worlddic[world] += 1
        else:
            # read dic
            # dic structure: length:[seq1, header1],[seq2, header2]. header: ID|Taxon|Country|Sex|Provider|geo|world
            count = 0
            for length, items in dic.items():
                for item in items:
                    count += 1
                    header = item[1]
                    headers = header.split("|")
                    species = headers[1]
                    country = headers[2]
                    sex = headers[3]
                    provider = headers[4]
                    geo = headers[5]
                    world = headers[6]
                    # count species
                    if species not in taxondic.keys():
                        taxondic.setdefault(species, 1)
                    else:
                        taxondic[species] += 1
                    # count country
                    if country not in countrydic.keys():
                        countrydic.setdefault(country, 1)
                    else:
                        countrydic[country] += 1
                    # count sex
                    if sex not in sexdic.keys():
                        sexdic.setdefault(sex, 1)
                    else:
                        sexdic[sex] += 1
                    # count provider
                    if provider not in providerdic.keys():
                        providerdic.setdefault(provider, 1)
                    else:
                        providerdic[provider] += 1
                    # count geo
                    if geo not in geodic.keys():
                        geodic.setdefault(geo, 1)
                    else:
                        geodic[geo] += 1
                    # count world
                    if world not in worlddic.keys():
                        worlddic.setdefault(world, 1)
                    else:
                        worlddic[world] += 1
            count = str(count) + "\n"

        # assemble text
        nametext = "File: " + filename + "\n"
        sextext = ""
        countrytext = ""
        taxontext = ""
        providertext = ""
        geotext = ""
        worldtext = ""
        # sex
        sexunknown = ""
        for s, sn in sexdic.items():
            if s == "M":
                sextext = sextext + "Male: " + str(sn) + "\n"
            elif s == "F":
                sextext = sextext + "Female: " + str(sn) + "\n"
            else:
                sexunknown = "Unknown: " + str(sn) + "\n"
        sextext = sextext + sexunknown
        # country
        cuntryunknown = ""
        for c, cn in countrydic.items():
            if c != "Unknown":
                countrytext = countrytext + c + ": " + str(cn) + "\n"
            else:
                cuntryunknown = c + ": " + str(cn) + "\n"
        countrytext = countrytext + cuntryunknown
        # taxon
        taxonunknown = ""
        for t, tn in taxondic.items():
            if t != "Unknown":
                taxontext = taxontext + t + ": " + str(tn) + "\n"
            else:
                taxonunknown = t + ": " + str(tn) + "\n"
        taxontext = taxontext + taxonunknown
        # provider
        providerunknown = ""
        for p, pn in providerdic.items():
            if p != "Unknown":
                providertext = providertext + p + ": " + str(pn) + "\n"
            else:
                providerunknown = p + ": " + str(pn) + "\n"
        providertext = providertext + providerunknown
        # geo
        geounknown = ""
        for g, gn in geodic.items():
            if g != "Unknown":
                geotext = geotext + g + ": " + str(gn) + "\n"
            else:
                geounknown = g + ": " + str(gn) + "\n"
        geotext = geotext + geounknown
        # world
        worldunknown = ""
        for w, wn in worlddic.items():
            if w != "Unknown":
                worldtext = worldtext + w + ": " + str(wn) + "\n"
            else:
                worldunknown = w + ": " + str(wn) + "\n"
        worldtext = worldtext + worldunknown

        # show information on window
        self.descrip.configure(state="normal")
        self.descrip.delete("1.0", "end")
        self.descrip.insert("end", nametext, "tag_filename")
        self.descrip.insert("end", "Sample number:\n", "tag_title")
        self.descrip.insert("end", count, "tag_content")
        self.descrip.insert("end", "Taxon:\n", "tag_title")
        self.descrip.insert("end", taxontext, "tag_content")
        self.descrip.insert("end", "Region:\n", "tag_title")
        self.descrip.insert("end", geotext, "tag_content")
        self.descrip.insert("end", "World:\n", "tag_title")
        self.descrip.insert("end", worldtext, "tag_content")
        self.descrip.insert("end", "Country:\n", "tag_title")
        self.descrip.insert("end", countrytext, "tag_content")
        self.descrip.insert("end", "Sex:\n", "tag_title")
        self.descrip.insert("end", sextext, "tag_content")
        self.descrip.insert("end", "Identification provided by:\n", "tag_title")
        self.descrip.insert("end", providertext, "tag_content")
        self.descrip.configure(state="disable")

    @staticmethod
    def updatelength(seqdic):
        lenlist = []
        count = {}
        for length, values in seqdic.items():
            nseq = len(values)
            content = [length] * nseq
            lenlist.extend(content)
            count[length] = nseq
        return lenlist, count

    # search window (file-search)
    def searchwindow(self):
        import urllib.request

        # function of add button
        def addfun():
            userentry = en1.get()
            kind = com.get()
            bind = "|"
            addtext = ""
            if len(userentry) != 0:
                querydic[kind].append(userentry)
                self.queryready = True

                for querykind, querycontent in querydic.items():
                    if len(querycontent) != 0:
                        each = bind.join(querycontent)
                        each = each + "[{0}]".format(querykind)
                        if len(addtext) > 1:
                            addtext = addtext + " & " + each
                        else:
                            addtext = each

                searchbox.configure(state='normal')
                searchbox.delete("1.0", "end")
                searchbox.insert("end", addtext)
                searchbox.configure(state='disabled')
                en1.delete(0, "end")

        # function of search button
        def searchfun():
            self.lenseq = {}

            if self.queryready:
                queryurl = "http://www.boldsystems.org/index.php/API_Public/combined?"
                if len(querydic["Taxon"]) != 0:
                    queryurl = queryurl + "taxon=" + "|".join(querydic["Taxon"])
                    queryurl = queryurl + "&"
                if len(querydic["BIN ID"]) != 0:
                    queryurl = queryurl + "bin=" + "|".join(querydic["BIN ID"])
                    queryurl = queryurl + "&"
                if len(querydic["Institution"]) != 0:
                    queryurl = queryurl + "institutions=" + "|".join(querydic["Institution"])
                    queryurl = queryurl + "&"
                if len(querydic["Researcher"]) != 0:
                    queryurl = queryurl + "researchers=" + "|".join(querydic["Researcher"])
                    queryurl = queryurl + "&"
                queryurl = queryurl + "format=xml"
                queryurl = queryurl.replace(" ", "%20")
                xmlpath = filedialog.asksaveasfilename(title='Save data at', defaultextension=".xml",
                                                       filetypes=[('XML', '*.xml')], parent=window_search)

                if len(xmlpath) > 0:
                    window_search.destroy()

                    self.console.config(state="normal")
                    self.console.insert("end", ">Data downloading, please wait....\n")
                    self.console.config(state="disable")
                    self.console.update()

                    urllib.request.urlretrieve(queryurl, xmlpath)
                    if os.path.getsize(xmlpath) > 0:
                        self.datadic = readxml.readxml(xmlpath)
                        messagebox.showinfo(title="Message", message="Download completed!")
                        # update console and data description
                        filename = xmlpath.rsplit("/", 1)[1]
                        self.datadescription(self.datadic, filename, "na")
                        self.console.config(state="normal")
                        self.console.insert("end", ">File loaded in\n")
                        self.console.see(tk.END)
                        self.console.update()
                        self.console.config(state="disable")
                    else:
                        messagebox.showwarning(title="Warning", message="No sample was found.")

        def clearbox():
            searchbox.configure(state='normal')
            searchbox.delete("1.0", "end")
            searchbox.configure(state='disabled')
            querydic.clear()
            querydic.setdefault("Taxon", [])
            querydic.setdefault("BIN ID", [])
            querydic.setdefault("Institution", [])
            querydic.setdefault("Researcher", [])
            self.queryready = False

        window_search = tk.Toplevel(self.window)
        window_search.geometry('370x230')
        window_search.minsize(370, 230)
        window_search.maxsize(370, 230)
        window_search.title('Search through BOLDsystem')

        querydic = {"Taxon": [], "BIN ID": [], "Institution": [], "Researcher": []}

        frame1 = tk.Frame(window_search)
        frame1.grid(row=0, column=0, sticky='w', padx=3)

        tk.Label(frame1, text="Search builder", font=('Arial', 11, "bold")).pack(side='left')

        frame2 = tk.Frame(window_search)
        frame2.grid(row=1, column=0, sticky='w', padx=3)

        tk.Label(frame2, text="Add terms to the query box", font=('Arial', 10)).pack(side='left')

        frame3 = tk.Frame(window_search, height=2, bd=3)
        frame3.grid(row=2, column=0, sticky='w', padx=3)

        xcom = window_search.var = tk.StringVar(value='Taxon')
        com = ttk.Combobox(frame3, width=10, textvariable=xcom)
        com.grid(row=0, column=0, sticky='w' + 's' + 'n' + 'e')
        com["value"] = ("Taxon", "BIN ID", "Institution", "Researcher")
        com['state'] = 'readonly'
        com.current(0)

        en1 = tk.Entry(frame3, width=20, show=None, font=('Arial', 10))
        en1.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e')

        botadd = tk.Button(frame3, text='Add', width=5, command=lambda: addfun())
        botadd.grid(row=0, column=2, padx=3, sticky='w' + 's' + 'n' + 'e')

        frame4 = tk.Frame(window_search, height=2, bd=3)
        frame4.grid(row=3, column=0, sticky='w', pady=10, padx=3)

        tk.Label(frame4, text="Query box", font=('Arial', 10)).grid(row=0, column=0, sticky='w')

        searchbox = tk.Text(frame4, height=5, bd=2, width=50)
        searchbox.grid(row=1, column=0, sticky='w')
        searchbox.configure(state='disabled')
        botclear = tk.Button(frame4, text='Clear', width=5, command=lambda: clearbox())
        botclear.grid(row=2, column=0, sticky='e', pady=3)
        botsear = tk.Button(frame4, text='Search and download', width=20, command=lambda: searchfun())
        botsear.grid(row=2, column=0, sticky='w', pady=3)

    def adddata(self):
        def addfile():
            xmlpath = filedialog.askopenfilename(title='Choose a file',
                                                 filetypes=[('XML', '*.xml'), ('FASTA', '*.fas'),
                                                            ('Aligned FASTA', '*.afas'), ('All Files', '*')],
                                                 multiple=True)
            if len(xmlpath) != 0:
                for path in xmlpath:
                    add_datadic = {}
                    if os.path.getsize(path) > 0:
                        filetype = path.split(".")[1]
                        if filetype == "xml":
                            add_datadic = readxml.readxml(path)
                        elif filetype == "fas":
                            add_datadic = readxml.readfasta(path)
                        elif filetype == "afas":
                            add_datadic = readxml.readfasta(path)
                        # combine datadic
                        self.datadic = {**self.datadic, **add_datadic}
                    else:
                        messagebox.showwarning(title="Warning", message="Empty file: {0}".format(path))

                # update console and data description
                filename = "merged_data"
                self.datadescription(self.datadic, filename, "na")
                self.console.config(state="normal")
                self.console.insert("end", ">Add datasets completed\n")
                self.console.see(tk.END)
                self.console.update()
                self.console.config(state="disable")
                self.zoom = 1

        # dic structure: length:[seq1, header1],[seq2, header2]. header: ID|Taxon|Country|Sex|Provider|geo|world
        # datadic: id:[seq, spe_name_out, countryin, sexin, iden_provider, iden_method]
        if len(self.lenseq) != 0:
            self.datadic = {}
            for seqlen, datasets in self.lenseq.items():
                for data in datasets:
                    seq = data[0]
                    header = data[1]
                    header_split = header.split("|")
                    header_id = header_split[0]
                    header_taxon = header_split[1]
                    header_country = header_split[2]
                    header_sex = header_split[3]
                    header_provider = header_split[4]
                    header_geo = header_split[5]
                    header_world = header_split[6]
                    self.datadic[header_id] = [seq, header_taxon, header_country, header_sex, header_provider, header_geo, header_world]

            addfile()

        else:
            addfile()

    def loadwindow(self):
        xmlpath = filedialog.askopenfilename(title='Choose a XML file', filetypes=[('XML', '*.xml'), ('FASTA', '*.fas'),
                                                                                   ('Aligned FASTA', '*.afas')])
        if len(xmlpath) != 0:
            if os.path.getsize(xmlpath) > 0:
                filetype = xmlpath.split(".")[1]
                if filetype == "xml":
                    self.datadic = readxml.readxml(xmlpath)
                    self.lenseq = {}
                elif filetype == "fas":
                    self.datadic = readxml.readfasta(xmlpath)
                    self.lenseq = {}
                elif filetype == "afas":
                    self.lenseq = readxml.readaligned(xmlpath)
                    # update counter
                    (self.seqlenlist, self.counter) = self.updatelength(self.lenseq)

                # update console and data description
                filename = xmlpath.rsplit("/", 1)[1]
                if filetype != "afas":
                    self.datadescription(self.datadic, filename, "na")
                else:
                    self.datadescription(self.lenseq, filename, "a")
                self.console.config(state="normal")
                self.console.insert("end", ">Load in completed\n")
                self.console.see(tk.END)
                self.console.update()
                self.console.config(state="disable")
                self.zoom = 1
            else:
                messagebox.showwarning(title="Warning", message="Empty file.")

    def savefasta(self, readin, align):
        def saveasfas(doc):
            ifile = open(doc, "w")
            for iiid, icontent in self.datadic.items():
                iseq = self.datadic[iiid][0] + "\n"
                ispices = self.datadic[iiid][1]
                icountry = self.datadic[iiid][2]
                isex = self.datadic[iiid][3]
                iprovider = self.datadic[iiid][4]
                igeo = self.datadic[iiid][5]
                iworld = self.datadic[iiid][6]
                iheader = ">{0}|{1}|{2}|{3}|{4}|{5}|{6}\n".format(iiid, ispices, icountry, isex, iprovider, igeo, iworld)
                ifile.write(iheader)
                ifile.write(iseq)

            ifile.close()

        def saveasaligned(doc):
            sfile = open(doc, "w")
            for length, contents in self.lenseq.items():
                for content in contents:
                    sseq = content[0] + "\n"
                    sheader = content[1].split("|")
                    sspices = sheader[1]
                    scountry = sheader[2]
                    ssex = sheader[3]
                    sprovider = sheader[4]
                    sgeo = sheader[5]
                    sworld = sheader[6]
                    siid = sheader[0]
                    southeader = ">{0}|{1}|{2}|{3}|{4}|{5}|{6}\n".format(siid, sspices, scountry, ssex,
                                                                         sprovider, sgeo, sworld)
                    sfile.write(southeader)
                    sfile.write(sseq)

            sfile.close()

        if len(self.descrip.get("0.0", "2.0")) > 1:
            if readin:
                if len(self.lenseq) != 0:
                    # dic structure: length1:[[seq1, header1],[seq2, header2]]. header: ID|Taxon|Country|Sex|Provider|geo|world
                    docname = filedialog.asksaveasfilename(title='Save data at', defaultextension=".afas",
                                                           filetypes=[('Aligned FASTA', '*.afas')])
                    if len(docname) != 0:
                        saveasaligned(docname)
                        self.console.config(state="normal")
                        self.console.insert("end", ">Save completed\n")
                        self.console.see(tk.END)
                        self.console.update()
                        self.console.config(state="disable")
                else:
                    docname = filedialog.asksaveasfilename(title='Save data at', defaultextension=".fas",
                                                           filetypes=[('FASTA', '*.fas')])
                    if len(docname) != 0:
                        saveasfas(docname)
                        self.console.config(state="normal")
                        self.console.insert("end", ">Save completed\n")
                        self.console.see(tk.END)
                        self.console.update()
                        self.console.config(state="disable")

            else:
                if align == "T":
                    docname = "./datafile/fornet.fas"
                    saveasaligned(docname)
                elif align == "F":
                    docname = "./datafile/alifas.fas"
                    saveasfas(docname)
                elif align == "S":
                    docname = "./datafile/aliedfas.fas"
                    file = open(docname, "w")
                    maxlen = max(self.seqlenlist)
                    for le, cs in self.lenseq.items():
                        for c in cs:
                            seq = c[0]
                            mylen = len(seq)
                            if mylen < maxlen:
                                fill = (maxlen - mylen) * "-"
                                seq = seq + fill
                            seq = seq + "\n"
                            header = c[1].split("|")
                            spices = header[1]
                            country = header[2]
                            sex = header[3]
                            provider = header[4]
                            geo = header[5]
                            world = header[6]
                            iid = header[0]
                            outheader = ">{0}|{1}|{2}|{3}|{4}|{5}|{6}\n".format(iid, spices, country, sex, provider,
                                                                                geo, world)
                            file.write(outheader)
                            file.write(seq)

                    file.close()
        else:
            messagebox.showwarning(title="Warning", message="Empty data.")

    def saveeps(self):
        if self.ready:
            docname = filedialog.asksaveasfilename(title='Save data at', defaultextension=".eps",
                                                   filetypes=[('EPS', '*.eps')])
            if len(docname) != 0:
                self.canvas.postscript(file=docname, colormode='color')
        else:
            messagebox.showwarning(title="Warning", message="Empty plot.")

    def filterwindow(self):
        window_filter = tk.Toplevel(self.window)
        window_filter.geometry('455x505')
        window_filter.minsize(455, 505)
        window_filter.maxsize(455, 505)
        window_filter.title('Filter')
        window_filter.wm_attributes("-topmost", 1)

        # Title
        frame1 = tk.Frame(window_filter)
        frame1.grid(row=0, column=0, sticky='w', padx=3)

        tk.Label(frame1, text="Filter", font=('Arial', 11, "bold")).pack(side='left')

        # Gender
        frame2 = tk.Frame(window_filter)
        frame2.grid(row=1, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame2, text="Gender:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        varsex = frame2.var = tk.StringVar(value="A")
        sexr1 = tk.Radiobutton(frame2, text='All', variable=varsex, value="A")
        sexr1.grid(row=0, column=1, sticky='w')

        sexr2 = tk.Radiobutton(frame2, text='No ambiguities', variable=varsex, value="T")
        sexr2.grid(row=0, column=2, sticky='w')

        sexr3 = tk.Radiobutton(frame2, text='Male', variable=varsex, value="M")
        sexr3.grid(row=0, column=3, sticky='w')

        sexr4 = tk.Radiobutton(frame2, text='Female', variable=varsex, value="F")
        sexr4.grid(row=0, column=4, sticky='w')

        # Zoogeographic Regions
        def regiondeselectall():
            regionc1.deselect()
            regionc2.deselect()
            regionc3.deselect()
            regionc4.deselect()
            regionc5.deselect()
            regionc6.deselect()
            regionc7.deselect()
            regionc8.deselect()
            regionc1.update()
            regionc2.update()
            regionc3.update()
            regionc4.update()
            regionc5.update()
            regionc6.update()
            regionc7.update()
            regionc8.update()

        def regionselectall():
            regionc1.select()
            regionc2.select()
            regionc3.select()
            regionc4.select()
            regionc5.select()
            regionc6.select()
            regionc7.select()
            regionc8.select()
            regionc1.update()
            regionc2.update()
            regionc3.update()
            regionc4.update()
            regionc5.update()
            regionc6.update()
            regionc7.update()
            regionc8.update()

        def isall():
            total = varregionc1.get() + varregionc2.get() + varregionc3.get() + varregionc4.get() + \
                    varregionc5.get() + varregionc6.get() + varregionc7.get() + varregionc8.get()

            if total == 8:
                regionr1.select()
            elif total == 0:
                messagebox.showwarning(title="Warning", message="Please select at least one region.",
                                       parent=window_filter)
                regionr2.select()
            else:
                regionrx.select()

        frame6 = tk.Frame(window_filter)
        frame6.grid(row=2, column=0, sticky='w', pady=4, padx=3, rowspan=4)

        tk.Label(frame6, text="Region:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')

        frame6i1 = tk.Frame(frame6)
        frame6i1.grid(row=0, column=1, sticky='w')
        varregion = frame6i1.var = tk.StringVar(value="A")
        regionr1 = tk.Radiobutton(frame6i1, text='All', variable=varregion, value="A", command=regionselectall)
        regionr1.grid(row=0, column=0, sticky='w')

        regionr2 = tk.Radiobutton(frame6i1, text='No ambiguities', variable=varregion,
                                  value="T", command=regiondeselectall)
        regionr2.grid(row=0, column=1, sticky='w')

        regionrx = tk.Radiobutton(frame6i1, text='x', variable=varregion, value="X")

        varregionc1 = frame6.var = tk.IntVar(value=1)
        regionc1 = tk.Checkbutton(frame6, text='Western Palaearctic', variable=varregionc1, onvalue=1, offvalue=0, command=isall)
        regionc1.grid(row=1, column=1, sticky='w')

        varregionc2 = frame6.var = tk.IntVar(value=1)
        regionc2 = tk.Checkbutton(frame6, text='Eastern Palaearctic', variable=varregionc2, onvalue=1, offvalue=0, command=isall)
        regionc2.grid(row=1, column=2, sticky='w')

        varregionc3 = frame6.var = tk.IntVar(value=1)
        regionc3 = tk.Checkbutton(frame6, text='Oriental', variable=varregionc3, onvalue=1, offvalue=0, command=isall)
        regionc3.grid(row=2, column=1, sticky='w')

        varregionc4 = frame6.var = tk.IntVar(value=1)
        regionc4 = tk.Checkbutton(frame6, text='Australian', variable=varregionc4, onvalue=1, offvalue=0, command=isall)
        regionc4.grid(row=2, column=2, sticky='w')

        varregionc5 = frame6.var = tk.IntVar(value=1)
        regionc5 = tk.Checkbutton(frame6, text='Ethiopian', variable=varregionc5, onvalue=1, offvalue=0, command=isall)
        regionc5.grid(row=2, column=3, sticky='w')

        varregionc6 = frame6.var = tk.IntVar(value=1)
        regionc6 = tk.Checkbutton(frame6, text='Nearctic ', variable=varregionc6, onvalue=1, offvalue=0, command=isall)
        regionc6.grid(row=3, column=1, sticky='w')

        varregionc7 = frame6.var = tk.IntVar(value=1)
        regionc7 = tk.Checkbutton(frame6, text='Neotropical', variable=varregionc7, onvalue=1, offvalue=0, command=isall)
        regionc7.grid(row=3, column=2, sticky='w')

        varregionc8 = frame6.var = tk.IntVar(value=1)
        regionc8 = tk.Checkbutton(frame6, text='Others', variable=varregionc8, onvalue=1, offvalue=0, command=isall)
        regionc8.grid(row=3, column=3, sticky='w')

        # World
        frame7 = tk.Frame(window_filter)
        frame7.grid(row=6, column=0, sticky='w', pady=4, padx=3, rowspan=1)

        tk.Label(frame7, text="World:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')

        varworld = frame7.var = tk.StringVar(value="A")
        worldr1 = tk.Radiobutton(frame7, text='All', variable=varworld, value="A")
        worldr1.grid(row=0, column=1, sticky='w')

        worldr2 = tk.Radiobutton(frame7, text='No ambiguities', variable=varworld, value="T")
        worldr2.grid(row=0, column=2, sticky='w')

        worldr3 = tk.Radiobutton(frame7, text='New world', variable=varworld, value="N")
        worldr3.grid(row=0, column=3, sticky='w')

        worldr4 = tk.Radiobutton(frame7, text='Old world', variable=varworld, value="O")
        worldr4.grid(row=0, column=4, sticky='w')

        # Country
        def countrydisableall():
            iengeo.delete(0, "end")
            eengeo.delete(0, "end")
            geocheck1.deselect()
            geocheck2.deselect()
            iengeo.configure(state="disable")
            eengeo.configure(state="disable")
            geocheck1.configure(state="disable")
            geocheck2.configure(state="disable")
            iengeo.update()
            eengeo.update()
            geocheck1.update()
            geocheck2.update()

        def countryincludeenable():
            eengeo.delete(0, "end")
            geocheck2.deselect()
            eengeo.configure(state="disable")
            geocheck2.configure(state="disable")
            iengeo.configure(state="normal")
            geocheck1.configure(state="normal")
            iengeo.update()
            eengeo.update()
            geocheck1.update()
            geocheck2.update()

        def countryexcludeenable():
            iengeo.delete(0, "end")
            geocheck1.deselect()
            iengeo.configure(state="disable")
            geocheck1.configure(state="disable")
            eengeo.configure(state="normal")
            geocheck2.configure(state="normal")
            iengeo.update()
            eengeo.update()
            geocheck1.update()
            geocheck2.update()

        frame3 = tk.Frame(window_filter)
        frame3.grid(row=7, column=0, sticky='w', pady=4, padx=3, rowspan=3)

        tk.Label(frame3, text="Country:   ", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        vargeo = frame3.var = tk.StringVar(value="A")

        frame3i1 = tk.Frame(frame3)
        frame3i1.grid(row=0, column=1, sticky='w')
        geor1 = tk.Radiobutton(frame3i1, text='All', variable=vargeo, value="A", command=countrydisableall)
        geor1.grid(row=0, column=1, sticky='w')

        geor2 = tk.Radiobutton(frame3i1, text='No ambiguities', variable=vargeo, value="T", command=countrydisableall)
        geor2.grid(row=0, column=2, sticky='w', padx=15)

        frame3i2 = tk.Frame(frame3)
        frame3i2.grid(row=1, column=1, sticky='w')
        geor3 = tk.Radiobutton(frame3i2, text='Include:', variable=vargeo, value="I", command=countryincludeenable)
        geor3.grid(row=0, column=0, sticky='w')
        iengeo = tk.Entry(frame3i2, width=20, show=None, font=('Arial', 10), bd=2)
        iengeo.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        vargeoc1 = frame3i2.var = tk.IntVar(value=0)
        geocheck1 = tk.Checkbutton(frame3i2, text='Include ambiguities', variable=vargeoc1, onvalue=1, offvalue=0)
        geocheck1.grid(row=0, column=2, sticky='w')

        frame3i3 = tk.Frame(frame3)
        frame3i3.grid(row=2, column=1, sticky='w')
        geor4 = tk.Radiobutton(frame3i3, text='Exclude:', variable=vargeo, value="E", command=countryexcludeenable)
        geor4.grid(row=0, column=0, sticky='w')
        eengeo = tk.Entry(frame3i3, width=20, show=None, font=('Arial', 10), bd=2)
        eengeo.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        vargeoc2 = frame3i3.var = tk.IntVar(value=0)
        geocheck2 = tk.Checkbutton(frame3i3, text='Exclude ambiguities', variable=vargeoc2, onvalue=1, offvalue=0)
        geocheck2.grid(row=0, column=2, sticky='w')

        iengeo.configure(state="disable")
        eengeo.configure(state="disable")
        geocheck1.configure(state="disable")
        geocheck2.configure(state="disable")

        # Taxon
        def taxdisableall():
            ientax.delete(0, "end")
            eentax.delete(0, "end")
            taxcheck1.deselect()
            taxcheck2.deselect()
            ientax.configure(state="disable")
            eentax.configure(state="disable")
            taxcheck1.configure(state="disable")
            taxcheck2.configure(state="disable")
            ientax.update()
            eentax.update()
            taxcheck1.update()
            taxcheck2.update()

        def taxincludeenable():
            eentax.delete(0, "end")
            taxcheck2.deselect()
            eentax.configure(state="disable")
            taxcheck2.configure(state="disable")
            ientax.configure(state="normal")
            taxcheck1.configure(state="normal")
            ientax.update()
            eentax.update()
            taxcheck1.update()
            taxcheck2.update()

        def taxexcludeenable():
            ientax.delete(0, "end")
            taxcheck1.deselect()
            ientax.configure(state="disable")
            taxcheck1.configure(state="disable")
            eentax.configure(state="normal")
            taxcheck2.configure(state="normal")
            ientax.update()
            eentax.update()
            taxcheck1.update()
            taxcheck2.update()

        frame4 = tk.Frame(window_filter)
        frame4.grid(row=12, column=0, sticky='w', pady=4, padx=3, rowspan=3)

        tk.Label(frame4, text="Taxon: ", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        vartax = frame4.var = tk.StringVar(value="A")

        frame4i1 = tk.Frame(frame4)
        frame4i1.grid(row=0, column=1, sticky='w')
        taxr1 = tk.Radiobutton(frame4i1, text='All', variable=vartax, value="A", command=taxdisableall)
        taxr1.grid(row=0, column=0, sticky='w')
        taxr2 = tk.Radiobutton(frame4i1, text='No ambiguities', variable=vartax, value="T", command=taxdisableall)
        taxr2.grid(row=0, column=1, sticky='w', padx=15)

        frame4i2 = tk.Frame(frame4)
        frame4i2.grid(row=1, column=1, sticky='w')
        taxr3 = tk.Radiobutton(frame4i2, text='Include:', variable=vartax, value="I", command=taxincludeenable)
        taxr3.grid(row=0, column=0, sticky='w')
        ientax = tk.Entry(frame4i2, width=20, show=None, font=('Arial', 10), bd=2)
        ientax.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        vartaxc1 = frame4i2.var = tk.IntVar(value=0)
        taxcheck1 = tk.Checkbutton(frame4i2, text='Include ambiguities', variable=vartaxc1, onvalue=1, offvalue=0)
        taxcheck1.grid(row=0, column=2, sticky='w')

        frame4i3 = tk.Frame(frame4)
        frame4i3.grid(row=2, column=1, sticky='w')
        taxr4 = tk.Radiobutton(frame4i3, text='Exclude:', variable=vartax, value="E", command=taxexcludeenable)
        taxr4.grid(row=0, column=0, sticky='w')
        eentax = tk.Entry(frame4i3, width=20, show=None, font=('Arial', 10), bd=2)
        eentax.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        vartaxc2 = frame4i3.var = tk.IntVar(value=0)
        taxcheck2 = tk.Checkbutton(frame4i3, text='Exclude ambiguities', variable=vartaxc2, onvalue=1, offvalue=0)
        taxcheck2.grid(row=0, column=2, sticky='w')

        ientax.configure(state="disable")
        eentax.configure(state="disable")
        taxcheck1.configure(state="disable")
        taxcheck2.configure(state="disable")

        # Specimen Identification
        frame5 = tk.Frame(window_filter)
        frame5.grid(row=15, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame5, text="Specimen Identification:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        varsi = frame5.var = tk.StringVar(value="A")
        frame5i = tk.Frame(frame5)
        frame5i.grid(row=0, column=1, sticky='w')
        sir1 = tk.Radiobutton(frame5i, text='All', variable=varsi, value="A")
        sir1.grid(row=0, column=0, sticky='w')

        sir2 = tk.Radiobutton(frame5i, text='No ambiguities', variable=varsi, value="T")
        sir2.grid(row=0, column=1, sticky='w')

        sir3 = tk.Radiobutton(frame5, text='Only by researchers', variable=varsi, value="R")
        sir3.grid(row=1, column=1, sticky='w')

        # filter button
        def seqfilter():
            if len(self.descrip.get("0.0", "2.0")) > 1:
                if len(self.lenseq) == 0:
                    # data structure: id:[seq, spe_name_out, countryin, sexin, iden_provider, geo, world]

                    # filter by sex:
                    if varsex.get() == "T":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[3] != "Unknown"}
                    elif varsex.get() == "F":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[3] == "F"}
                    elif varsex.get() == "M":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[3] == "M"}

                    # filter by country:
                    if vargeo.get() == "T":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[2] != "Unknown"}
                    elif vargeo.get() == "I":
                        cond = iengeo.get()
                        cff = cond.split("+")
                        filtered_dic = {}
                        for ii in cff:
                            dic = {k: v for k, v in self.datadic.items() if v[2] == ii}
                            filtered_dic = {**filtered_dic, **dic}
                        if vargeoc1.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[2] == "Unknown"}
                            filtered_dic = {**filtered_dic, **dic}
                        self.datadic = filtered_dic
                    elif vargeo.get() == "E":
                        cond = eengeo.get()
                        cff = cond.split("+")
                        for ii in cff:
                            self.datadic = {k: v for k, v in self.datadic.items() if v[2] != ii}
                        if vargeoc2 == 1:
                            self.datadic = {k: v for k, v in self.datadic.items() if v[2] != "Unknown"}

                    # filter by region:
                    if varregion.get() == "T":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[5] != "Unknown"}
                    elif varregion.get() == "X":
                        filtered_dic = {}
                        if varregionc1.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Western Palaearctic"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc2.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Eastern Palaearctic"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc3.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Oriental"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc4.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Australian"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc5.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Ethiopian"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc6.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Nearctic"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc7.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Neotropical"}
                            filtered_dic = {**filtered_dic, **dic}
                        if varregionc8.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[5] == "Others"}
                            filtered_dic = {**filtered_dic, **dic}
                        self.datadic = filtered_dic

                    # filter by world:
                    if varworld.get() == "T":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[6] != "Unknown"}
                    elif varworld.get() == "N":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[6] == "New world"}
                    elif varworld.get() == "O":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[6] == "Old world"}

                    # filter by taxon:
                    if vartax.get() == "T":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[1] != "Unknown"}
                    elif vartax.get() == "I":
                        cond = ientax.get()
                        cff = cond.split("+")
                        filtered_dic = {}
                        for ii in cff:
                            dic = {k: v for k, v in self.datadic.items() if v[1] == ii}
                            filtered_dic = {**filtered_dic, **dic}
                        if vartaxc1.get() == 1:
                            dic = {k: v for k, v in self.datadic.items() if v[1] == "Unknown"}
                            filtered_dic = {**filtered_dic, **dic}
                        self.datadic = filtered_dic
                    elif vartax.get() == "E":
                        cond = eentax.get()
                        cff = cond.split("+")
                        for ii in cff:
                            self.datadic = {k: v for k, v in self.datadic.items() if v[1] != ii}
                        if vartaxc2 == 1:
                            self.datadic = {k: v for k, v in self.datadic.items() if v[1] != "Unknown"}

                    # filter by identification
                    if varsi.get() == "T":
                        self.datadic = {k: v for k, v in self.datadic.items() if v[4] != "Unknown"}
                    elif varsi.get() == "R":
                        self.datadic = {k: v for k, v in self.datadic.items() if (v[4] != "Unknown") & (v[4] != "BOLD ID Engine")}

                    window_filter.destroy()
                    messagebox.showinfo(title="Message", message="Filter finished!")
                    filtername = self.descrip.get("0.0", "2.0")
                    filtername = filtername.rstrip('\n')
                    filtername = filtername.split(": ")[1]
                    self.datadescription(self.datadic, filtername, "na")
                    self.console.config(state="normal")
                    self.console.insert("end", ">Filter completed\n")
                    self.console.see(tk.END)
                    self.console.update()
                    self.console.config(state="disable")
                else:
                    messagebox.showwarning(title="Warning", message="Filter should be performed before alignment.",
                                           parent=window_filter)
            else:
                messagebox.showwarning(title="Warning", message="Please load in data before filter!",
                                       parent=window_filter)

        botfil = tk.Button(window_filter, text='Filter', width=8, bd=2, command=lambda: seqfilter())
        botfil.grid(row=17, column=0, sticky='e', pady=3)

    def alignmentwindow(self):
        import alignment_R

        def aligngo():
            gapopen = engap.get()
            maxiter = eniter.get()
            if len(self.descrip.get("0.0", "2.0")) > 1:
                if is_number(gapopen) and is_number(maxiter):
                    if int(gapopen) < 0:
                        # save dic as fas file then do alignment
                        window_align.destroy()

                        self.console.config(state="normal")
                        self.console.insert("end", ">Alignment processing, please wait....\n")
                        self.console.config(state="disable")
                        self.console.update()

                        self.savefasta(False, "F")
                        segsites = alignment_R.seqalignment(gapopen, maxiter)
                        # osegpath = "./datafile/segsites.txt"
                        # osegfile = open(osegpath, "w")
                        # segsites = list(map(str, segsites))
                        # strn = "\n"
                        # osegfile.write(strn.join(segsites))
                        # osegfile.close()

                        # Read in aligned data
                        alignedpath = "./datafile/aliedfas.fas"
                        self.lenseq = readxml.readaligned(alignedpath)
                        # update counter
                        (self.seqlenlist, self.counter) = self.updatelength(self.lenseq)

                        # Handle outliers
                        df = pd.DataFrame(self.seqlenlist)
                        q = df.describe()

                        # find outliers base on John Tukey's method
                        q3 = q.loc["75%"][0]
                        q1 = q.loc["25%"][0]
                        iqr = q3 - q1
                        upperlimit = q3 + (1.5 * iqr)
                        lowerlimit = q1 - (1.5 * iqr)

                        alllength = np.array(list(self.lenseq.keys()))
                        uok = alllength[alllength > upperlimit]
                        lok = alllength[alllength < lowerlimit]

                        if len(uok) > 0:
                            ntrim = 0
                            uol = []
                            # trim upper outliers to the length of the longest sequences(not outlier)
                            noo = max(alllength[alllength <= upperlimit])
                            for i in uok:
                                # trim sequences
                                for j in self.lenseq[i]:
                                    uoheader = j[1]
                                    uoseq = j[0]
                                    trimmedseq = uoseq[0: noo]
                                    self.lenseq[noo].append([trimmedseq, uoheader])
                                    uol.append(uoheader)
                                    ntrim += 1
                                del self.lenseq[i]

                            self.console.config(state="normal")
                            self.console.insert("end", ">{0} sequences have been trimmed since they are longer outliers. "
                                                  "They are:\n".format(ntrim))
                            for i in uol:
                                self.console.insert("end", "\t{0}\n".format(i))
                            self.console.config(state="disable")

                        if varhandle.get() == 1:
                            if len(lok) > 0:
                                ndiscard = 0
                                lol = []
                                # discard lower outliers (need user confirm)
                                for i in lok:
                                    for j in self.lenseq[i]:
                                        lol.append(j[1])
                                        ndiscard += 1
                                    del self.lenseq[i]

                                self.console.config(state="normal")
                                self.console.insert("end",
                                               ">{0} sequences have been discarded since they are lower outliers. "
                                               "They are:\n".format(ndiscard))
                                for i in lol:
                                    self.console.insert("end", "\t{0}\n".format(i))
                                self.console.config(state="disable")

                        # update sequence length list
                        (self.seqlenlist, self.counter) = self.updatelength(self.lenseq)

                        # find out the seg sites
                        self.savefasta(False, "S")
                        alignment_R.segsites()

                        # update data description
                        alignedname = self.descrip.get("0.0", "2.0")
                        alignedname = alignedname.rstrip('\n')
                        alignedname = alignedname.split(": ")[1]
                        alignedname = "aligned_" + alignedname
                        self.datadescription(self.lenseq, alignedname, "a")

                        self.console.config(state="normal")
                        self.console.insert("end", ">Alignment completed\n")
                        self.console.see(tk.END)
                        self.console.config(state="disable")
                        self.console.update()

                        messagebox.showinfo(title="Message", message="Alignment finished!")

                    else:
                        messagebox.showwarning(title="Warning", message="Gap open must be negative!",
                                               parent=window_align)
                else:
                    messagebox.showwarning(title="Warning", message="Gap open or max iterations is not numeric!",
                                           parent=window_align)
            else:
                messagebox.showwarning(title="Warning", message="Please load in data before alignment!",
                                       parent=window_align)

        window_align = tk.Toplevel(self.window)
        window_align.geometry('180x220')
        window_align.minsize(180, 220)
        window_align.maxsize(180, 220)
        window_align.title('Alignment')
        window_align.wm_attributes("-topmost", 1)

        # Title1
        frame1 = tk.Frame(window_align)
        frame1.grid(row=0, column=0, sticky='w', padx=3)

        tk.Label(frame1, text="Alignment by MUSCLE", font=('Arial', 11, "bold")).pack(side='left')

        # Option 1
        frame2 = tk.Frame(window_align)
        frame2.grid(row=1, column=0, sticky='w', padx=3, pady=5)

        tk.Label(frame2, text="Gap penalties", font=('Arial', 10), bg="silver").grid(row=0, column=0, sticky="nw")

        frame2i = tk.Frame(frame2)
        frame2i.grid(row=1, column=0, sticky='w', padx=3, pady=3)
        tk.Label(frame2i, text="Gap Open:", font=('Arial', 10)).grid(row=0, column=0)
        engap = tk.Entry(frame2i, width=10, show=None, font=('Arial', 10), bd=2)
        engap.insert("end", '-400')
        engap.grid(row=0, column=1)

        # Option 2
        tk.Label(frame2, text="Iteration", font=('Arial', 10), bg="silver").grid(row=2, column=0, sticky="nw")

        frame2i2 = tk.Frame(frame2)
        frame2i2.grid(row=3, column=0, sticky='w', padx=3, pady=3)
        tk.Label(frame2i2, text="Max Iterations:", font=('Arial', 10)).grid(row=0, column=0)
        eniter = tk.Entry(frame2i2, width=7, show=None, font=('Arial', 10), bd=2)
        eniter.insert("end", '16')
        eniter.grid(row=0, column=1)

        # Option 3
        option_sep = tk.ttk.Separator(window_align, orient='horizontal')
        option_sep.grid(row=3, column=0, sticky='we', padx=2)

        frame3 = tk.Frame(window_align)
        frame3.grid(row=4, column=0, sticky='w', padx=3, pady=5)
        varhandle = window_align.var = tk.IntVar(value=1)
        handlecheck = tk.Checkbutton(frame3, text='Discard shorter outliers', variable=varhandle, onvalue=1,
                                     offvalue=0)
        handlecheck.grid(row=0, column=0, sticky='w')

        # Button Ok
        botaliok = tk.Button(window_align, text='OK', width=8, bd=2, command=lambda: aligngo())
        botaliok.grid(row=5, column=0, sticky='e', pady=3)

    def summaryplotwindow(self):
        def summaryplot(lenlist, count):
            seqnum = len(lenlist)  # count how many sequences we have in total
            minlen = min(lenlist)
            maxlen = max(lenlist)
            catlen = np.array(list(count.keys()))  # count how many kinds of sequences we have

            # calculate the density
            xforden = sorted(count.keys())
            sumcount = 0
            denlist = []
            for ii in xforden:
                sumcount += count[ii]
                denlist.append(sumcount / seqnum)

            sumplot = plt.figure()

            ax1 = plt.subplot()
            plt.title("Summary plot")
            plt.xticks(rotation=45)

            # bar chart
            # chart 1: number of segsites that may be trimmed
            segpath = "./datafile/segsites.txt"
            segfile = pd.read_table(segpath, header=None)
            seglist = np.array(segfile[0])
            numofseg = []
            segtotal = len(seglist)
            for ii in xforden:
                # total - selected length
                numofseg.append(segtotal - np.sum(seglist <= ii))

            l1 = ax1.plot(xforden, numofseg, label="Polymorphic site (number)", color="green", linewidth=1)

            # chart 2: Overall quality score & find the best length
            # calculate the score for each length
            min_ts = float('inf')
            scorelist = []
            lengthopt = []
            for ii in range(minlen, maxlen + 1):
                shorter = catlen[catlen < ii]
                longer = catlen[catlen > ii]
                s_score = 0
                l_score = 0

                # calculate the s_score
                for ji in shorter:
                    scores = (ii - ji) * count[ji]  # can multiply a weight if want
                    s_score += scores
                # print(s_score)

                # calculate the l_score
                for ji in longer:
                    # find how many segsites exist between this length and the setting length
                    numseg = len(seglist[(seglist > ii) & (seglist <= ji)])

                    scorel = numseg * count[ji]  # can multiply a weight if want
                    l_score += scorel
                # print(l_score, "_")
                t_score = l_score + s_score
                scorelist.append(t_score)
                if t_score <= min_ts:
                    if t_score < min_ts:
                        min_ts = t_score
                        # min_l = l_score
                        # min_s = s_score
                        lengthopt = [ii]
                    else:
                        lengthopt.append(ii)

            if len(lengthopt) == 0:
                messagebox.showwarning(parent=window_sumplot, title="Warning", message="Can't find the optimal length.")

            nscorelist = [ii / ((min_ts + 1) / 10) for ii in scorelist]
            l2 = ax1.plot(np.arange(minlen, maxlen + 1, 1), nscorelist, label="OPS", color="firebrick", linewidth=1)

            # chart 3: number of sequence in each length
            l3 = ax1.bar(list(count.keys()),
                    height=list(count.values()),
                    width=1,
                    bottom=0,
                    align='center',
                    color='pink',
                    edgecolor='black',
                    linewidth=0.5,
                    log=False,
                    label="Sequences (number)")

            ax1.set_xlabel("Length")
            ax1.set_ylabel("Number")
            x_major_locator = MultipleLocator(4)
            ax1.xaxis.set_major_locator(x_major_locator)
            plt.xticks(size=8)
            y1_major_locator = MultipleLocator(10)
            ax1.yaxis.set_major_locator(y1_major_locator)
            plt.grid(axis="y")

            # chart 4: Density plot
            ax2 = ax1.twinx()
            l4 = ax2.plot(xforden, denlist, label="Cumulative distribution", color="blue", linewidth=1)
            ax2.set_ylabel("Density")
            ax2.set_ylim(bottom=0)
            y2_major_locator = MultipleLocator(0.1)
            ax2.yaxis.set_major_locator(y2_major_locator)

            # legend
            ax_list = (l1[0], l2[0], l4[0], l3)
            lables = [name.get_label() for name in ax_list]
            ax1.legend(ax_list, lables, loc="upper left", bbox_to_anchor=(0, 1))

            return sumplot, lengthopt

        def discardseq():
            def discard(seqdic, length):
                catlen = np.array(list(seqdic.keys()))
                dislen = catlen[catlen < length]
                for ii in dislen:
                    del seqdic[ii]

                return seqdic

            discardlen = endiscard.get()
            if discardlen.isdigit():
                if int(discardlen) <= max(self.counter.keys()):
                    # discard sequences
                    self.lenseq = discard(self.lenseq, int(discardlen))

                    # update data description
                    alignedname = self.descrip.get("0.0", "2.0")
                    alignedname = alignedname.rstrip('\n')
                    alignedname = alignedname.split(": ")[1]
                    self.datadescription(self.lenseq, alignedname, "a")

                    # update sequence length list
                    countbefore = len(self.seqlenlist)
                    (self.seqlenlist, self.counter) = self.updatelength(self.lenseq)

                    messagebox.showinfo(parent=window_sumplot, title="Message",
                                        message="{0} sequences are discarded.".format(countbefore- len(self.seqlenlist)))

                    # do summary plot again
                    window_sumplot.destroy()
                    self.summaryplotwindow()
                else:
                    messagebox.showwarning(title="Warning", message="input is larger than the longest length!",
                                           parent=window_sumplot)
            else:
                messagebox.showwarning(title="Warning", message="Length must be a positive integer!",
                                       parent=window_sumplot)

        def trim():
            def trim_with_length(seqdic, trlength):
                dicout = {}
                dicout.setdefault(int(trlength), [])
                if int(trlength) in seqdic:
                    dicout[int(trlength)] = seqdic[int(trlength)]
                for length, seqlist in seqdic.items():
                    if int(length) > int(trlength):
                        for data in seqlist:
                            sequence = data[0][0:int(trlength)]
                            dicout[int(trlength)].append([sequence, data[1]])
                    elif int(length) < int(trlength):
                        nfill = int(trlength) - int(length)
                        for data in seqlist:
                            sequence = data[0] + nfill * "-"
                            dicout[int(trlength)].append([sequence, data[1]])

                return dicout

            def fintrim():
                window_sumplot.destroy()
                messagebox.showinfo(title="Message", message="Trimming completed!")
                self.console.config(state="normal")
                self.console.insert("end", ">Trimming completed\n")
                self.console.see(tk.END)
                self.console.update()
                self.console.config(state="disable")

            # get the option and trim
            trimoption = vartrim.get()
            # "I" input length, "L" longest length, "S" shortest length
            if trimoption == "I":
                inlen = en.get()
                if inlen.isdigit():
                    seq_trimmed = trim_with_length(self.lenseq, inlen)
                    self.lenseq = seq_trimmed
                    fintrim()
                else:
                    messagebox.showwarning(title="Warning", message="Length must be a positive integer!",
                                           parent=window_sumplot)
            elif trimoption == "L":
                length_l = max(self.seqlenlist)
                seq_trimmed = trim_with_length(self.lenseq, length_l)
                self.lenseq = seq_trimmed
                fintrim()
            else:
                length_s = min(self.seqlenlist)
                seq_trimmed = trim_with_length(self.lenseq, length_s)
                self.lenseq = seq_trimmed
                fintrim()

        if len(self.descrip.get("0.0", "2.0")) > 1:
            if len(self.lenseq) > 1:
                window_sumplot = tk.Toplevel(self.window)
                window_sumplot.geometry('800x600')
                window_sumplot.minsize(440, 360)
                window_sumplot.title('Summary plot')

                (plot_sum, optlen) = summaryplot(self.seqlenlist, self.counter)

                framebar = tk.Frame(window_sumplot)
                framebar.pack(side="right", fill="y")

                framelen = tk.Frame(framebar)
                framelen.pack(side="top", fill="y")
                lentext = "Recommended length:\n{0}\n".format(optlen)
                tk.Label(framelen, text=lentext, font=('Arial', 10)).pack()

                frameoption = tk.LabelFrame(framebar, text="Option", labelanchor="n", bd=2)
                frameoption.pack(side="top", fill="y")

                frame1 = tk.Frame(frameoption)
                frame1.pack(side="top", fill="x")
                tk.Label(frame1, text="Discard Sequences", font=('Arial', 11)).grid(row=0, column=0, sticky='w')

                frame1i1 = tk.Frame(frame1)
                frame1i1.grid(row=1, column=0, sticky="w")
                tk.Label(frame1i1, text="Length under:", font=('Arial', 10)).grid(row=0, column=0, sticky='w',
                                                                                  pady=3, padx=5)
                endiscard = tk.Entry(frame1i1, width=12, show=None, font=('Arial', 10), bd=2)
                endiscard.grid(row=0, column=1, padx=5, pady=3)

                botdiscard = tk.Button(frame1, text='Discard', width=8, bd=2, command=discardseq)
                botdiscard.grid(row=2, column=0, sticky='e', pady=5, padx=3)

                option_sep = tk.ttk.Separator(frameoption, orient='horizontal')
                option_sep.pack(side="top", fill="x")

                def enableinput():
                    en.configure(state="normal")

                def disableinput():
                    en.delete(0, "end")
                    en.configure(state="disable")

                frame2 = tk.Frame(frameoption)
                frame2.pack(side="top", fill="x", expand="yes")
                tk.Label(frame2, text="Trim data", font=('Arial', 11)).grid(row=0, column=0, sticky='w')

                vartrim = frame2.var = tk.StringVar(value="I")

                frame1i2 = tk.Frame(frame2)
                frame1i2.grid(row=1, column=0, sticky='w')
                trimr1 = tk.Radiobutton(frame1i2, text='Trim by length:', variable=vartrim, value="I",
                                        command=enableinput)
                trimr1.grid(row=0, column=0, sticky='w', padx=3)
                en = tk.Entry(frame1i2, width=9, show=None, font=('Arial', 10), bd=2)
                en.insert(0, optlen[0])
                en.grid(row=0, column=1, padx=3, sticky='w', pady=4)

                trimr2 = tk.Radiobutton(frame2, text='Keep all sequences the\nsame length as the longest',
                                        variable=vartrim, value="L", command=disableinput)
                trimr2.grid(row=2, column=0, sticky='w', padx=3)

                trimr3 = tk.Radiobutton(frame2, text='Keep all sequences the\nsame length as the shortest',
                                        variable=vartrim, value="S", command=disableinput)
                trimr3.grid(row=3, column=0, sticky='w', padx=3)

                botdiscard = tk.Button(frame2, text='Trim', width=5, bd=2, command=trim)
                botdiscard.grid(row=4, column=0, sticky='e', pady=5, padx=3)

                frameplot = tk.LabelFrame(window_sumplot)
                frameplot.pack(side="left", fill="both", expand="yes")

                canvas = FigureCanvasTkAgg(plot_sum, master=frameplot)
                canvas.draw()
                canvas.get_tk_widget().pack(side="top", fill="both", expand="yes")

                toolbar = NavigationToolbar2Tk(canvas, frameplot)
                toolbar.update()
                canvas.tkcanvas.pack(side="top", fill="both", expand="yes")

            elif len(self.lenseq) == 0:
                messagebox.showwarning(title="Warning",
                                       message="Sequences should be aligned before doing summary plot.")
            else:
                messagebox.showwarning(title="Warning", message="Sequences are already in the "
                                                                "same length of {0}.".format(list(self.lenseq.keys())[0]))
        else:
            messagebox.showwarning(title="Warning", message="Empty data.")

    def plotnetwork(self, easy):
        import copy

        def lerp(a, b, t):
            return [a[0] * t + b[0] * (1 - t), a[1] * t + b[1] * (1 - t)]

        def legend():
            legend_x = 15
            legend_y = 15
            for ii in range(0, len(self.color)):
                self.canvas.create_rectangle([legend_x, legend_y, legend_x + 20 + self.legend_size, legend_y + 5 + self.legend_size], fill=self.color[ii])
                self.canvas.create_text([legend_x + 25 + self.legend_size, legend_y + self.legend_size], fill="black", text=self.group_kind[ii],
                                        font=("Times", str(3 + self.legend_size), 'bold'), anchor=tk.W)
                legend_y += 10 + self.legend_size
            legend_y += self.legend_size
            self.canvas.create_line([legend_x, legend_y, legend_x + 20 + self.legend_size, legend_y], fill="black")
            self.canvas.create_rectangle([legend_x + (20 + self.legend_size)/2 - self.legend_size, legend_y - self.legend_size, legend_x + (20 + self.legend_size)/2 + self.legend_size, legend_y + self.legend_size], fill="white", outline="black")
            self.canvas.create_text([legend_x + (20 + self.legend_size)/2, legend_y], text="5", fill="black", font=("Times", str(2 + self.legend_size), 'bold'))
            self.canvas.create_text([legend_x + 25 + self.legend_size, legend_y], fill="black", text="Number of step",
                                    font=("Times", str(3 + self.legend_size), 'bold'), anchor=tk.W)

        self.canvas.delete("all")
        legend()
        mynodesize = copy.copy(self.nodesize)

        # edit node size
        maxsize = max(mynodesize)
        for i in range(0, len(mynodesize)):
            mynodesize[i] = (self.nodemin + (mynodesize[i] / maxsize * self.nodemax))
        nodesize_zoomed = [i * self.zoom for i in mynodesize]

        if not easy:
            n = 0
            for irow in self.coordinate:
                n += 1
                x = float(irow.split("\t")[0]) * 10 + self.centre[0]
                y = float(irow.split("\t")[1]) * 10 + self.centre[1]
                self.node[str(n)] = [x, y]
        for irow in self.edges:
            edge = irow.split("\t")
            start = copy.copy(self.node[edge[0]])
            start[0] = self.centre[0] + (start[0] - self.centre[0]) * self.zoom
            start[1] = self.centre[1] + (start[1] - self.centre[1]) * self.zoom
            end = copy.copy(self.node[edge[1]])
            end[0] = self.centre[0] + (end[0] - self.centre[0]) * self.zoom
            end[1] = self.centre[1] + (end[1] - self.centre[1]) * self.zoom
            self.canvas.create_line([start[0], start[1], end[0], end[1]], fill="Black")
            mytextsize = self.textsize * self.zoom / 2
            mydotsize = self.dotsize * self.zoom / 2
            if int(edge[2]) < 5:
                for i in range(0, int(edge[2])):
                    p = lerp(start, end, i / int(edge[2]))
                    self.canvas.create_oval([p[0] - mydotsize, p[1] - mydotsize, p[0] + mydotsize, p[1] + mydotsize], fill="black")
            else:
                p = lerp(start, end, 1 / 2)
                self.canvas.create_rectangle([p[0] - 3 * mytextsize, p[1] - 3 * mytextsize, p[0] + 3 * mytextsize, p[1] + 3 * mytextsize], fill="white", outline="black")
                self.canvas.create_text([p[0], p[1] + 2 * mytextsize], fill="black", text=edge[2],
                                        font=("Times", str(int(mytextsize * 3)), 'bold'))

        for irow, coo in self.node.items():
            x = copy.copy(coo[0])
            y = copy.copy(coo[1])
            x = self.centre[0] + (x - self.centre[0]) * self.zoom
            y = self.centre[1] + (y - self.centre[1]) * self.zoom
            group_nonezero = 0
            for i in self.group[int(irow) - 1]:
                if i != "0":
                    group_nonezero += 1
            if group_nonezero > 1:
                part = sum(map(eval, self.group[int(irow) - 1]))
                npart = 360 / part
                piestart = 0
                for i in range(0, self.group_num):
                    extent = int(self.group[int(irow) - 1][i]) * npart
                    pie = self.canvas.create_arc(
                        [x - nodesize_zoomed[int(irow) - 1], y - nodesize_zoomed[int(irow) - 1], x + nodesize_zoomed[int(irow) - 1],
                         y + nodesize_zoomed[int(irow) - 1]], start=piestart, extent=extent, fill=self.color[i], tags="tag"+str(irow))
                    self.canvas.tag_bind(pie, '<ButtonPress-1>', self.on_click)
                    self.canvas.tag_bind(pie, '<B1-Motion>', self.on_drag)
                    piestart = piestart + extent
            else:
                for i in range(0, self.group_num):
                    if self.group[int(irow) - 1][i] != "0":
                        pie = self.canvas.create_oval([x - nodesize_zoomed[int(irow) - 1], y - nodesize_zoomed[int(irow) - 1],
                                                       x + nodesize_zoomed[int(irow) - 1], y + nodesize_zoomed[int(irow) - 1]],
                                                      fill=self.color[i], tags="tag"+str(irow))
                        self.canvas.tag_bind(pie, '<ButtonPress-1>', self.on_click)
                        self.canvas.tag_bind(pie, '<B1-Motion>', self.on_drag)
        self.ready = True
        self.mouse_x = 0
        self.mouse_x = 0

    def generate_net(self, net_type):
        import network
        from itertools import islice

        if len(self.descrip.get("0.0", "2.0")) > 1:
            if len(self.lenseq) == 1:
                self.savefasta(False, "T")
                file = open("./datafile/group.txt", "w", encoding="utf-8")
                for ilen, seqs in self.lenseq.items():
                    for iseq in seqs:
                        header = iseq[1].split("|")
                        spices = header[1]
                        country = header[2]
                        # sex = header[3]
                        # provider = header[4]
                        region = header[5]
                        world = header[6]
                        file.write("{0}\t{1}\t{2}\t{3}\n".format(country, region, world, spices))
                file.close()

                if net_type == "tcs":
                    network.tcs()
                elif net_type == "msn":
                    network.msn()

                self.coordinate = []
                coordinatefile = open("./datafile/network/xy.txt", "r")
                for irow in islice(coordinatefile, 1, None):
                    self.coordinate.append(irow)
                coordinatefile.close()

                self.edges = []
                edgesfile = open("./datafile/network/edge.txt", "r")
                for irow in islice(edgesfile, 1, None):
                    self.edges.append(irow)
                edgesfile.close()

                with open("./datafile/network/size.txt", "r") as sizefile:
                    self.nodesize = list(map(int, [line.strip() for line in sizefile.readlines()]))
                # maxsize = max(self.nodesize)
                # for i in range(0, len(self.nodesize)):
                #     self.nodesize[i] = (2 + (self.nodesize[i] / maxsize * 7))
                sizefile.close()

                groupfile = open("./datafile/network/pie_country.txt", "r")

                self.group = []
                group_header = groupfile.readline()
                group_header = group_header.rstrip('\n')
                self.group_kind = group_header.split("\t")
                self.group_num = len(self.group_kind)

                values = range(self.group_num)
                cm = plt.get_cmap("rainbow")
                cnorm = colors.Normalize(vmin=0, vmax=values[-1])
                scalarmap = cmx.ScalarMappable(norm=cnorm, cmap=cm)
                self.theme = []
                for i in range(self.group_num):
                    colorval = scalarmap.to_rgba(values[i])
                    colorhex = colors.rgb2hex(colorval)
                    self.theme.append(colorhex)

                self.color = self.theme[0:self.group_num]

                for i in groupfile:
                    line = i.rstrip('\n')
                    group_split = line.split("\t")
                    self.group.append(group_split)
                # print(sum(map(eval, group[0])))
                groupfile.close()

                self.plotnetwork(False)

                self.mouse_x = 0
                self.mouse_x = 0

            elif len(self.lenseq) == 0:
                messagebox.showwarning(title="Warning", message="Alignment is needed before drawing network!")
            elif len(self.lenseq) > 1:
                messagebox.showwarning(title="Warning", message="Sequences are not in the same length.\n"
                                                                "Please use the 'Summary plot' function for trimming.")
        else:
            messagebox.showwarning(title="Warning", message="Empty data.")

    def plotoption(self):
        window_option = tk.Toplevel(self.window)
        window_option.geometry('445x250')
        window_option.minsize(445, 250)
        window_option.maxsize(445, 250)
        window_option.title('Plot options')
        window_option.wm_attributes("-topmost", 1)

        # Title
        frame1 = tk.Frame(window_option)
        frame1.grid(row=0, column=0, sticky='w', padx=3)

        tk.Label(frame1, text="Plot options", font=('Arial', 11, "bold")).pack(side='left')

        # Group by
        frame2 = tk.Frame(window_option)
        frame2.grid(row=1, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame2, text="Group by:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        var_group = frame2.var = tk.StringVar(value="C")
        groupr1 = tk.Radiobutton(frame2, text='Country', variable=var_group, value="C")
        groupr1.grid(row=0, column=1, sticky='w')

        groupr2 = tk.Radiobutton(frame2, text='Taxon', variable=var_group, value="T")
        groupr2.grid(row=0, column=2, sticky='w')

        groupr3 = tk.Radiobutton(frame2, text='Zoogeographic Region', variable=var_group, value="Z")
        groupr3.grid(row=0, column=3, sticky='w')

        groupr4 = tk.Radiobutton(frame2, text='World', variable=var_group, value="W")
        groupr4.grid(row=0, column=4, sticky='w')

        # theme
        frame3 = tk.Frame(window_option)
        frame3.grid(row=2, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame3, text="Theme:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        var_theme = frame3.var = tk.StringVar(value="R")
        themer1 = tk.Radiobutton(frame3, text='Gist', variable=var_theme, value="G")
        themer1.grid(row=0, column=2, sticky='w')

        themer2 = tk.Radiobutton(frame3, text='Rainbow', variable=var_theme, value="R")
        themer2.grid(row=0, column=1, sticky='w')

        themer3 = tk.Radiobutton(frame3, text='Tab20', variable=var_theme, value="T")
        themer3.grid(row=0, column=3, sticky='w')

        themer4 = tk.Radiobutton(frame3, text='Set3', variable=var_theme, value="S")
        themer4.grid(row=0, column=4, sticky='w')


        # node size (max min)
        frame4 = tk.Frame(window_option)
        frame4.grid(row=3, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame4, text="Node size:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')

        frame4i1 = tk.Frame(frame4)
        frame4i1.grid(row=0, column=1, sticky='w', padx=8)
        tk.Label(frame4i1, text="Max", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        enmax = tk.Entry(frame4i1, width=8, show=None, font=('Arial', 10), bd=2)
        enmax.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        enmax.insert(0, self.nodemax)

        frame4i2 = tk.Frame(frame4)
        frame4i2.grid(row=0, column=2, sticky='w', padx=8)
        tk.Label(frame4i2, text="Min", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        enmin = tk.Entry(frame4i2, width=8, show=None, font=('Arial', 10), bd=2)
        enmin.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        enmin.insert(0, self.nodemin)

        # legend size
        frame5 = tk.Frame(window_option)
        frame5.grid(row=4, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame5, text="Legend size:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')

        enlegend = tk.Entry(frame5, width=8, show=None, font=('Arial', 10), bd=2)
        enlegend.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        enlegend.insert(0, self.legend_size)

        # Mutation step ([text], point size)
        frame6 = tk.Frame(window_option)
        frame6.grid(row=5, column=0, sticky='w', pady=4, padx=3)

        tk.Label(frame6, text="Mutation display:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')

        frame6i1 = tk.Frame(frame6)
        frame6i1.grid(row=0, column=1, sticky='w', padx=8)
        tk.Label(frame6i1, text="Text size ", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        entext = tk.Entry(frame6i1, width=8, show=None, font=('Arial', 10), bd=2)
        entext.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        entext.insert(0, self.textsize)

        frame6i2 = tk.Frame(frame6)
        frame6i2.grid(row=0, column=2, sticky='w', padx=8)
        tk.Label(frame6i2, text="Dot size ", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        endot = tk.Entry(frame6i2, width=8, show=None, font=('Arial', 10), bd=2)
        endot.grid(row=0, column=1, padx=3, sticky='w' + 's' + 'n' + 'e', pady=4)
        endot.insert(0, self.dotsize)

        def editplot():
            def changegroup(which):
                groupfile = open("./datafile/network/pie_{0}.txt".format(which), "r")

                self.group = []
                group_header = groupfile.readline()
                group_header = group_header.rstrip('\n')
                self.group_kind = group_header.split("\t")
                self.group_num = len(self.group_kind)
                for i in groupfile:
                    line = i.rstrip('\n')
                    group_split = line.split("\t")
                    self.group.append(group_split)
                # print(sum(map(eval, group[0])))
                groupfile.close()

            def changetheme(which):
                values = range(self.group_num)
                cm = plt.get_cmap(which)
                cnorm = colors.Normalize(vmin=0, vmax=values[-1])
                scalarmap = cmx.ScalarMappable(norm=cnorm, cmap=cm)
                self.theme = []
                for i in range(self.group_num):
                    colorval = scalarmap.to_rgba(values[i])
                    colorhex = colors.rgb2hex(colorval)
                    self.theme.append(colorhex)
                self.color = self.theme[0:self.group_num]

            if self.ready:
                # group change
                if var_group.get() == "C":
                    changegroup("country")
                elif var_group.get() == "T":
                    changegroup("taxon")
                elif var_group.get() == "Z":
                    changegroup("region")
                elif var_group.get() == "W":
                    changegroup("world")

                # theme change
                if var_theme.get() == "G":
                    changetheme("gist_rainbow")
                elif var_theme.get() == "R":
                    changetheme("rainbow")
                elif var_theme.get() == "T":
                    if self.group_num <= 20:
                        changetheme("tab20")
                    else:
                        messagebox.showwarning(parent=window_option, title="Warning",
                                               message="Tab20 is only available for group under 20.")
                elif var_theme.get() == "S":
                    if self.group_num <= 12:
                        changetheme("Set3")
                    else:
                        messagebox.showwarning(parent=window_option, title="Warning",
                                               message="Set3 is only available for group under 12.")

                if is_number(enmax.get()) and is_number(enmin.get()):
                    self.nodemax = float(enmax.get())
                    self.nodemin = float(enmin.get())
                else:
                    messagebox.showwarning(parent=window_option, title="Warning",
                                           message="Node sizes should be numeric.")

                if enlegend.get().isdigit():
                    self.legend_size = int(enlegend.get())
                else:
                    messagebox.showwarning(parent=window_option, title="Warning",
                                           message="Legend size should be numeric.")

                if is_number(entext.get()) and is_number(endot.get()):
                    self.dotsize = float(endot.get())
                    self.textsize = float(entext.get())
                else:
                    messagebox.showwarning(parent=window_option, title="Warning",
                                           message="Text size and dot size should be numeric.")
                self.plotnetwork(True)

            else:
                messagebox.showwarning(parent=window_option, title="Warning", message="Empty plot")

        botedit = tk.Button(window_option, text='Edit', width=8, bd=2, command=editplot)
        botedit.grid(row=6, column=0, sticky='e', pady=3)

    def zoom_in(self):
        self.zoom = self.zoom * 1.05
        if self.ready:
            self.plotnetwork(True)

    def zoom_out(self):
        self.zoom = self.zoom * 0.95
        if self.ready:
            self.plotnetwork(True)

    def on_canvas_click(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def on_canvas_move(self, event):
        if not self.dragging_node and self.ready:
            mouse_x = event.x
            mouse_y = event.y
            dx = (self.mouse_x - mouse_x)/self.zoom
            dy = (self.mouse_y - mouse_y)/self.zoom
            for name, nd in self.node.items():
                nd[0] -= dx
                nd[1] -= dy

            self.plotnetwork(True)

            self.mouse_x = mouse_x
            self.mouse_y = mouse_y

    def on_canvas_right_click(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def on_canvas_right_move(self, event):
        if self.ready:
            mouse_x = event.x
            mouse_y = event.y
            dy = (self.mouse_y - mouse_y)
            self.zoom += dy * 0.01

            if self.zoom < 0.1: self.zoom = 0.1

            self.plotnetwork(True)

            self.mouse_x = mouse_x
            self.mouse_y = mouse_y

    def on_click(self, event):
        self.dragging_node = True
        self.curr_x = event.x
        self.curr_y = event.y

    def on_drag(self, event):
        dx = (self.curr_x - event.x)
        dy = (self.curr_y - event.y)
        vertex = self.canvas.gettags("current")[0][3:]
        self.node[vertex][0] -= dx/self.zoom
        self.node[vertex][1] -= dy/self.zoom
        items = self.canvas.find_withtag("tag" + vertex)
        for item in items:
            self.canvas.move(item, -dx, -dy)
        self.curr_x = event.x
        self.curr_y = event.y

    def on_release(self, event):
        if self.ready:
            self.dragging_node = False
            self.plotnetwork(True)

    def quitplothap(self):
        exitchoice = messagebox.askyesno(title="Message", message="Want to exit?")
        if exitchoice:
            self.window.quit()

    def clearconsole(self):
        self.console.config(state="normal")
        self.console.delete(0.0, "end")
        self.console.config(state="disable")

    def topconsole(self):
        self.console.config(state="normal")
        self.console.see("0.0")
        self.console.update()
        self.console.config(state="disable")

    def botconsole(self):
        self.console.config(state="normal")
        self.console.see(tk.END)
        self.console.update()
        self.console.config(state="disable")


Mainprogramme()
