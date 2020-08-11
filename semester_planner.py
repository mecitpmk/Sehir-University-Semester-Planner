from bs4 import BeautifulSoup
import requests,re
from tkinter import *


class Course:
    all_courses=[]
    def __init__(self,course_code,lesson_day,lesson_hour):
        """

        Arguments:
            course_code {str} -- ex. UNI 112
            lesson_day {list} -- ['Monday' ,'Wednesday']
            lesson_hour {list} -- ['13:00-15:00','11:00-13:00']
        Notes:
            When Courses created Python will automatically append it to Course.all_coures list.
        """
        self.code=course_code
        self.days=lesson_day
        self.clocks=lesson_hour
        Course.all_courses.append(self)

    def __repr__(self):
        return f'{self.code} {self.days} {self.clocks}'

class FetchData:
    def fetch_profile(self,given_link):
        """

        Arguments:
            given_link {str} -- website link

        Returns:
            {dict} -- return a dictionary which sorted by name.

        Notes:
            Some lessons have two days but one clocks like: Monday Wednesday 13:00-15:00
            That means Monday and Wednesday 13:00-15:00 and 13:00-15:00
            Python will understand with given condition.
            By the way if day or clocks blocks empty python will skip it.

        """
        req=requests.get(given_link)
        self.soup=BeautifulSoup(req.content,"html.parser")
        other_counter,ct=0,0
        lessons_dict={}
        my_list=[]
        for tr in self.soup.find_all('tr'):
            for get_span in tr.find_all('span'):
                if ct != 6:
                    ct+=1
                    continue
                my_list.append(get_span.text)
        for info_count in range(0,len(my_list),6):
            lesson_code=my_list[info_count]
            # lesson_name=my_list[info_count+1]
            lesson_day=my_list[info_count+2]
            lesson_day=re.sub('[^A-Za-z0-9]+', ' ', lesson_day) 
            lesson_hour=my_list[info_count+3]
            lesson_hour=re.sub('[^A-Za-z0-9-:]+', ' ', lesson_hour)

            if lesson_hour == ' ' or lesson_day == ' ':
                continue
            
            check_lesson_day=lesson_day.split()
            check_lesson_hours=lesson_hour.split()
            if len(check_lesson_day) == 2 and len(check_lesson_hours) == 1:
                lesson_hour=f'{lesson_hour} {lesson_hour}'
            Course(course_code=lesson_code,lesson_day=lesson_day,lesson_hour=lesson_hour)
            lessons_dict[lesson_code]={'Lesson Days':lesson_day,'Lesson Hours':lesson_hour}

        return self.sort_dictionary(given_dict=lessons_dict)
    def sort_dictionary(self,given_dict):
        new_dict={}
        for key in sorted(given_dict):
            new_dict[key]=given_dict[key]
        return new_dict
    


class GUI(Frame):
    def __init__(self,parent):
        self.parent=parent
        Frame.__init__(self,parent)
        self.fetch=FetchData()
        self.grid()
        self.initGUI()
    def initGUI(self):
        # https://www.sehir.edu.tr/tr/duyurular/2019_2020_akademik_yili_bahar_donemi_ders_programi
        self.BIG_TEXT=Label(self,text="SEHIR COURSE PLANNER",bg="black",fg="aqua",font=("Helvetica",14,"bold"),anchor=CENTER)
        self.BIG_TEXT.grid(row=0,column=0,sticky=E+W+S+N,columnspan=5)

        Label(self,text="Course Offering Url:").grid(row=1,column=0,padx=10,pady=10)
        self.link_entry=Entry(self,width=100)
        self.link_entry.grid(row=1,column=1,padx=10,pady=10)

        self.fetch_button=Button(self,text="Fetch Courses",command=self.fetch_data_buttons)
        self.fetch_button.grid(row=1,column=2,padx=10,pady=10)

        self.filter_Frame=Frame(self,relief=GROOVE,borderwidth=4)
        self.filter_Frame.grid(row=2,column=0,padx=10,pady=10,columnspan=3)

        Label(self.filter_Frame,text="Filter:").grid(row=0,column=0,padx=10,pady=10,sticky=E)


        self.filter_Entry=Entry(self.filter_Frame)
        self.filter_Entry.grid(row=0,column=1,sticky=W)
        self.filter_Entry.bind("<Key>",self.filtered_keys)

        self.courses_listbox=Listbox(self.filter_Frame,height=5)
        self.courses_listbox.grid(row=1,column=0,padx=10,pady=10,columnspan=2,ipadx=100)
        self.courses_listbox.bind("<<ListboxSelect>>",self.courses_listbox_selected)

        self.scrool_first=Scrollbar(self.filter_Frame)
        self.scrool_first.grid(row=1,column=0,sticky=E,columnspan=2,padx=10,ipady=15)
        self.courses_listbox.configure(yscrollcommand=self.scrool_first.set)
        self.scrool_first.config(command=self.courses_listbox.yview)




        self.add_button=Button(self.filter_Frame,text="Add to \nSelected Courses",command=self.add_clicked)
        self.add_button.grid(row=1,column=2,padx=10,pady=10)
        
        self.remove_button=Button(self.filter_Frame,text="Remove from\nSelected Courses",command=self.delete_buttons)
        self.remove_button.grid(row=1,column=3,padx=10,pady=10)

        self.error_labels=Label(self.filter_Frame,anchor=CENTER)
        self.error_labels.grid(row=0,column=2,sticky=E)


        Label(self.filter_Frame,text="Selected Courses").grid(row=0,column=4,padx=10,pady=10)
        self.selected_courses_listbox=Listbox(self.filter_Frame,height=5)
        self.selected_courses_listbox.grid(row=1,column=4,padx=10,pady=10,ipadx=100)
        self.selected_courses_listbox.bind("<<ListboxSelect>>",self.added_courses_select)

        self.scrool_second=Scrollbar(self.filter_Frame)
        self.scrool_second.grid(row=1,column=4,sticky=E,padx=10,ipady=15)
        self.selected_courses_listbox.configure(yscrollcommand=self.scrool_second.set)
        self.scrool_second.config(command=self.selected_courses_listbox.yview)



        self.schedule_Frame=Frame(self,relief=GROOVE,borderwidth=4)
        self.schedule_Frame.grid(row=3,column=0,padx=10,pady=3,columnspan=3)

 

        self.days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        self.clock_lists=[]
        for i in range(9,22,1):
            y=i
            if i == 9:
                i=f'0{i}'
            self.clock_lists.append(f'{i}:00-{i}:30')
            self.clock_lists.append(f'{i}:30-{y+1}:00')

        self.colors=['medium aquamarine', 'aquamarine',  'LemonChiffon4', 'cornsilk2', 'turquoise', 
                        'cyan', 'dark violet', 'blue violet', 'purple' ,'dodger blue',
                                'pale turquoise','honeydew2','cadet blue']

        self.taken_colors={}
        self.days_and_clocks={}
        
        
        """
        Notes at the below, python create an time table ex:
                            {etc....    Tuesday:{09:00-09:30 : [] , 09:30-10:00 : []  .....etc}}
        """
        
        for day in self.days:
            for clock in self.clock_lists:
                self.days_and_clocks.setdefault(day,{})
                self.days_and_clocks[day][clock]=[]
        
        self.before_selected=[]
        self.make_clock_labels()
        
    def add_clicked(self):
        """
        Notes:
            if Add to Selected Courses button clicked This function will work and this function
            will triggers to self.course_selected_check,So as you can see parameeter of add=True
            other parameeter is self.selected_course So, python will recognize easily which course selected and
            send it to other function.
        """
        self.course_selected_check(self.selected_course,add=True)

    def added_courses_select(self,event):
        """

        Notes:
            In that function, if in the selected courses listbox triggers (Clicked any lessons) this function will
            work thanks to tkinter event. Python will recognize which lesson clicked thanks to for loop.
        """
        capture_event=event.widget
        self.capture_event_index=capture_event.curselection()
        selected_course=self.selected_courses_listbox.get(self.capture_event_index)
        for c in Course.all_courses:
            if c.__repr__() == selected_course:
                self.will_delete=c
    
    def delete_buttons(self):
        """
        Notes:
            In that function if Remove from Selected courses button clicked, this function will work.
            In that part if self.will_delete is attribute to object itself, condition will be provided.
            Every label turn in to green again, and lessons will remove from clocks dictionary
            Ex-> Before ->  {Monday: { 09:00-09:30:["MATH 103"]}}
                 After  ->  {Monday: { 09:00-09:30:[           ]}} -> removed..
        """
        if hasattr(self,"will_delete"):
            self.selected_courses_listbox.delete(self.capture_event_index)
            course_code=self.will_delete.code
            
            for day in self.days_and_clocks:
                clocks_dict=self.days_and_clocks[day]
                check_bool=True
                for date in clocks_dict:
                    if course_code in clocks_dict[date]:
                        clocks_dict[date].remove(course_code)
                        self.days_clocks_labels[day][date].configure(bg="green",text="")
            for color in self.taken_colors:
                if course_code == self.taken_colors[color]:
                    deleted_color=color
                    break
            del self.taken_colors[deleted_color]

            self.before_selected.clear()
    def filtered_keys(self,event):
        """
        Notes:
            If the any keyword will entered to Entry, python will understand easily thakns to tkinter event.
            and filters to listbox. Pyton will filters lessons according to LESSON NAME!
        """
        wid=event.widget
        word=self.filter_Entry.get()
        # print(word)
        if word != '':
            capitalized_word=word.upper()
            my_list=[]
            for courses in Course.all_courses:
                c_name_only=courses.code.split()[0]
                c_code=courses.code.split()[1]
                concanate=f'{c_name_only} {c_code}'
                full_name=courses.code
                # if capitalized_word == courses.code.split()[0] or capitalized_word == concanate \
                #                                  or capitalized_word == full_name:
                if capitalized_word == courses.code[:len(capitalized_word)]:
                    my_list.append(courses)
            self.courses_listbox.delete(0,END)
            for c in my_list:
                self.courses_listbox.insert(END,c)
        else:
            self.courses_listbox.delete(0,END)
            for c in Course.all_courses:
                self.courses_listbox.insert(END,c)

    def courses_listbox_selected(self,event):
        """
        Notes:
            This function provide python to which lesson will selected.
            and python gain an attribute which is self.selected_course
        """
        if hasattr(self,"before_selected"):
            for label,color in self.before_selected:
                label.configure(bg=color)
                self.update()
            self.before_selected.clear()
        
        self.capture_event=event.widget
        try:
            self.x=self.capture_event.curselection()
            self.x=self.courses_listbox.get(self.x)
            for course in Course.all_courses:
                if course.__repr__() == self.x:
                    self.selected_course=course
                    break
            self.course_selected_check(chosen_course=self.selected_course,add=False)
        except:
            pass
        # print(self.selected_course.course_code)
        # print(type(self.x.course_code))

    def check_color(self,given_course_code):
        """

        Arguments:
            given_course_code {str} - Ex. UNI 112

        Returns:
            str -- color name
        """
        for color in self.taken_colors:
            if given_course_code == self.taken_colors[color]:
                return color

    def course_selected_check(self,chosen_course,add=False):
        """

        Arguments:
            chosen_course {object} -- chosen_course is an object of Course

        Notes:
            If add=True but, condition is not provided (example: 09:00-09:30 is not empty block.) python give an an error label 
                    to user to inform .
                
            Besides that, this function also triggers when listbox clicked.            
            Python show corresponding courses clocks as yellow.
            If corresponding courses clocks already fulled, it show that cell as red!
        
        Keyword Arguments:
            add {bool} -- if add True python will try to add this course
                                    to time table. (default: {False})
        """
        # self.before_selected=[]
        self.added_lists=[]
        self.currently_added={}
        chosen_course_days=chosen_course.days.split()

        for day in range(len(chosen_course_days)):
            day_first=chosen_course_days[day]
            
            clocks_chosen_course=chosen_course.clocks.split()
            day_first_clocks=clocks_chosen_course[day]
            day_first_clocks=day_first_clocks.split("-")
            
            day_first_start=day_first_clocks[0]
            day_first_end=day_first_clocks[1]
            
            check_bool=False
            for days_clocks in self.days_and_clocks[day_first]:
                clock=days_clocks.split("-")
                start=clock[0]
                end=clock[1]
                if day_first_start == start:
                    check_bool=True
                if check_bool:
                    if day_first_end != end:
                        if len(self.days_and_clocks[day_first][days_clocks]) == 0:
                            self.currently_added[f'{day_first} {days_clocks}']=len(self.days_and_clocks[day_first][days_clocks]) == 0
                        else:self.currently_added[f'{day_first} {days_clocks}']=len(self.days_and_clocks[day_first][days_clocks]) == 0
                    else:
                        if len(self.days_and_clocks[day_first][days_clocks]) == 0:
                            self.currently_added[f'{day_first} {days_clocks}']=len(self.days_and_clocks[day_first][days_clocks]) == 0
                        else:self.currently_added[f'{day_first} {days_clocks}']=len(self.days_and_clocks[day_first][days_clocks]) == 0
                        check_bool=False
        # print(self.currently_added)
        not_add=True
        if add:
            if False in self.currently_added.values():
                print("Can' be added.")
                self.error_labels.configure(text="Could'nt Be Added ! " , bg="red")
                self.original_settings(self.error_labels)
                # print(self.before_selected)
                not_add=True
            else:
                for day_time in self.currently_added:
                    day_times=day_time.split()
                    day=day_times[0]
                    times=day_times[1]
                    self.before_selected.clear()
                    if self.check_color(self.selected_course.code) is None:
                        for color in self.colors:
                            if color not in self.taken_colors:
                                self.taken_colors[color]=self.selected_course.code
                                self.my_color=color
                                break
                    else:
                        self.my_color=self.check_color(self.selected_course.code)
                    self.days_clocks_labels[day][times].configure(bg=self.my_color)
                    self.days_and_clocks[day][times].append(self.selected_course.code)
                    self.days_clocks_labels[day][times].configure(text=self.selected_course.code)
                    if self.selected_course not in self.added_lists:
                        self.added_lists.append(self.selected_course)
                        for c in self.added_lists:self.selected_courses_listbox.insert(END,c)
                    
        elif not_add:
            for day_time in self.currently_added:
                day_times=day_time.split()
                day=day_times[0]
                times=day_times[1]
                if self.currently_added[day_time] == False:
                    prev=self.days_clocks_labels[day][times]['bg']
                    self.before_selected.append((self.days_clocks_labels[day][times],prev))
                    self.days_clocks_labels[day][times].configure(bg="red")
                else:
                    prev=self.days_clocks_labels[day][times]['bg']
                    self.before_selected.append((self.days_clocks_labels[day][times],prev))
                    self.days_clocks_labels[day][times].configure(bg="yellow")
                
    def fetch_data_buttons(self):
        """
        Notes:
            This function provide to fetch profiles from given link. 
            Given link comes from entry.
            Collected links inserting to self.courses_listbox.
        """
        link=self.link_entry.get()
        if link != '':
            self.fetch.fetch_profile(link)
            for course in Course.all_courses:
                self.update()
                self.courses_listbox.insert(END,course)
                self.update()
        else:
            self.error_labels.config(text="ENTER LINK!!!!",bg="yellow")
            self.original_settings(self.error_labels)
    def make_clock_labels(self):
        """
        Notes:
            This function carries important role in terms of which time has which label
            Ex. {Monday: {09:00-09:39 : label_object , 09:30-10:00 : label_object2}}
        """
        self.days_clocks_labels={}
        Label(self.schedule_Frame,text="Clocks",bg="black",fg="white").grid(row=0,column=0,ipadx=10)
        # row,column=0,1
        row,column=1,0
        for clock in self.clock_lists:
            Label(self.schedule_Frame,text=clock,bg="aquamarine",width=10,font=("Helvetica",9,"bold")).grid(row=row,column=column)
            row+=1
        row,column=0,1
        for day in self.days:
            row=0
            day_label=Label(self.schedule_Frame,text=day,bg="aquamarine",width=9,font=("Helvetica",10,"bold")).grid(row=row,column=column,
                                                                                                                            padx=3,pady=3,ipadx=10)
            for clock in self.clock_lists:
                label=Label(self.schedule_Frame,text="",bg="green",width=13)
                label.grid(row=row+1,column=column,padx=3,pady=3)
                self.days_clocks_labels.setdefault(day,{})
                self.days_clocks_labels[day][clock]=label
                row+=1
            column+=1
    def original_settings(self,given_label):
        """
        Notes:
            This function for temporary error labels.
            Adjusted 1500 ms . After 1500 ms label will return default settings.
        """
        self.after(1500,lambda: given_label.configure(text="",bg="SystemButtonFace"))



if __name__ == "__main__":
    root=Tk()
    gui=GUI(root)
    root.mainloop()



