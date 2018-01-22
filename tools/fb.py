""" Facebook Lab for Social Dynamics package

This module is for the Social Dynamics Facebook lab (jonatwell.com/lab). It uses your Facebook data and helps
you augment those with your intimate knowledge about your relationships. You can then plot your network, color it
by a variety of attributes and do measurements on it.

It uses the Facebook.py SDK (copyright Facebook) to connect to the Facebook graph and lets you do the authentication
 to Facebook so as to make sure your password is not leaked.

It also uses the awesome open-source libraries that are IPython, Pandas, NetworkX and Matplotlib.

It is designed to be run using an IPython notebook (version 1.1.0 and greater) and therefore implements
the database using Pandas which has been integrated into the Notebooks platform.

Finally, development of this lab was supported with a curriculum development grant from the Department of Sociology
at the University of Michigan.

"""

import pandas as pd
import networkx as nx
import random
import math



def clear_screen():
        try:
            ip.core.display.clear_output(other=False) # This clears the Notebook input cell
        except:
            ip.core.display.clear_output()




class FBgraph(object):
    """ This is the only class unique to the module. It holds key variables and other objects (like
    the facebook connection and the pandas database. The name parameter is so that multiple databases
    and networks can be worked on simultaneously."""



    def __init__(self, name="data1"):
        """ This initializing function mostly creates fields to be filled in later. It could fill everything
        in but that is saved so that the Lab user can get a better feel for what it going on."""

        # Basic objects
        self.graph_name = name
        self.facebook_link = False
        self.friend_db = pd.DataFrame()
        self.my_ID = False
        self.mynet = nx.Graph()
        self.contexts_list = {}
        self.defined_colors = []
        self.me = False
        self.old_positions=[]



    def check_answer(self, q):
        """This function enforces meaningful yes/no answers from the user and interprets them. It is
        frequently called by other functions."""

        checking = True
        ask_count = 0
        while checking and ask_count <10 :
            if q=="y" or q=="Y" or q=="yes" or q=="Yes":
                checking = False
                return True
            elif q=="n" or q=="N" or q=="no" or q=="No":
                checking = False
                return False
            else:
                q = input("\nTry answering again please. (y/n)")
                ask_count += 1



    def get_access(self):

        """ This function uses the Python SDK (which is imported as fb) to get access to the
        User's graph. It does this by asking for the User to supply a valid token which they
        may choose to save. It does this rather than handling authentication via usernames and
        passwords to ensure password data aren't leaked by this program.
        It first looks for and tries any stored passwords.
        """

        # Looking for saved keys
        try:
            key_file = open("./key.txt", "r+")
            token = key_file.readline().strip()

            # Testing if the saved key is still valid
            try:
                mygraph = fb.GraphAPI(access_token=token)
                me = mygraph.get_object("me")
                need_key = False
                print("Accessing using saved key...")

            # We end up here if the old token doesn't work
            except:
                print("Your old key isn't valid anymore. Please get one from Facebook.")
                need_key = True

        # We end up here if there is no saved token
        except:
            need_key = True

        while need_key:

            # This loop gets the user to supply a token
            token = str(input("\nPlease enter access token: [Instructions are available at jonatwell.com/facebook_tokens.html]"))

            # Checking to see if the token is valid
            try:
                mygraph = fb.GraphAPI(access_token=token)
                me = mygraph.get_object("me")
                need_key = False

                # Querying to save a valid key
                q = input("\nWould you like to save your key? (y/n)")
                if self.check_answer(q):
                    key_file = open("./key.txt", "w+")
                    key_file.write(token+"\n")
                    key_file.close()
                    print("Key successfully saved")
                else:
                    print("Key not saved")

            # The token was invalid
            except:
                print("Sorry, your token didn't work. Please try again.")

        clear_screen()

        print("\n\nHi "+ me['name'] +"! Welcome to the Facebook Lab\n")

        # This sets this links as the active one for the rest of the run
        self.facebook_link = mygraph



    def get_me(self):
        """ This method uses an active Facebook connection to get the users information."""

        # Testing the facebook link
        try:
            me = self.facebook_link.get_object("me")

            # Letting the user see their data
            for i in list(me.items()):
                print(i)

            self.me = me

        except:
            print("You must first use the \"get_access( )\" command with a valid token before you can get your user data")



    def setup_db(self):
        """ This function gets the User's information and puts it into the database. It also asks the
        user to provide additional information about schools, jobs and places they have lived (and that's
        why it is so long!)"""


        # Creating a python dictionary that will be used as the index for the Pandas dataframe
        full_dictionary = {}

        full_dictionary["name"] = self.me["name"]
        full_dictionary["gender"] = self.me["gender"]
        full_dictionary["mutuals"] = "-1"
        full_dictionary["strong tie"] = "-1"
        full_dictionary["known from"] = "-1"
        full_dictionary["tie strength"] = "-1"


        # Setting up social contexts list

        # First is schools
        count = 0
        school_list =""

        # Testing to see if they had any listed on their profile
        try:
            schools = self.me['education']
            for item in schools:
                for key in list(item.keys()):
                    if key == "school":
                        count += 1
                        self.contexts_list[count] = str(item[key]["name"])+ " (school)"
                        school_list += item[key]["name"] + ", "

            print("\nYour profile has the following schools:")
            print(school_list[:-2])

        except:
            print("\nYour profile doesn't have any information about schools")

        # asking for additional schools
        asked = False
        while not asked:
            print("\nWould you like to add a school? (y/n)")
            q=input()
            if self.check_answer(q):
                count += 1
                print("\nPlease enter a name: ")
                q=input()
                self.contexts_list[count] = q + " (school)"
            else:
                asked = True

        # Clears the Notebook input screen for the next round of questions
        clear_screen()



        # Second is jobs
        work_list = ""

        # Testing to see if they have any listed on their profile
        try:
            work = self.me['work']
            for item in work:
                for key in list(item.keys()):
                    if key == "employer":
                        count += 1
                        self.contexts_list[count] = str(item[key]["name"]) + " (work)"
                        work_list += item[key]["name"] +", "

            print("\nYour profile has the following places of employment:")
            print(work_list[:-2])

        except:
            print("\nYour profile doesn't have any information about employment")

        asked = False
        while not asked:
            print("\nWould you like to add a workplace? (y/n)")
            q=input()
            if self.check_answer(q):
                count += 1
                print("\nPlease enter a name: ")
                q=input()
                self.contexts_list[count] = q + " (work)"

            else:
                asked = True

        clear_screen()


        # Third is current place of residence
        try:
            name = self.me["location"]["name"]
            count +=1
            self.contexts_list[count] = str(name.split(",")[0]) + " (residence)"
            print("\nAccording to your profile you currently live in " + name)

        except:
            print("\nYour profile doesn't list your current place of residence")
            print("\nWould you like to add your current place of residence? (y/n)")
            q= input()
            if self.check_answer(q):
                count +=1
                print("\nPlease enter your current place of residence.")
                self.contexts_list[count] = input() + " (residence)"


        clear_screen()


        # Four is the User's hometown
        try:
            info = self.me["hometown"]["name"]
            count +=1
            self.contexts_list[count] = str(info.split(",")[0]) + " (lived)"
            print("\nAccording to your profile your hometown is "+info.split(",")[0])

        except:
            print("\nYour profile doesn't list a hometown")

        clear_screen()


        asked = False
        while not asked:
            if self.check_answer(input("\nWould you like to add a place where you have lived? (y/n)")):
                clear_screen()
                count +=1
                self.contexts_list[count] = input("\nPlease enter a place you lived") + " (lived)"
            else:
                asked=True


        self.contexts_list[(count+1)] = "Family"


        # This puts your node in the network
        self.my_ID = int(self.me["id"])
        self.mynet.add_node(self.my_ID)

        full_dictionary["undefined1"] = "nan"
        full_dictionary["undefined2"] = "nan"
        full_dictionary["undefined3"] = "nan"

        # This converts the python dictionary to a Pandas series object with the name my_ID (user's facebook ID)
        series = pd.Series(full_dictionary, name=self.my_ID)

        # This creates a Pandas DataFrame object with series as the first entry.
        self.friend_db = pd.DataFrame(series)

        clear_screen()

        print("\nYour Database is now set up with your information")



    def extend_contexts_list(self):
        """ This method allows the user to add social contexts to the list first created using Facebook
        data. The method trim_contexts_lists() does the opposite."""

        my_list = {}
        count = 1

        if len(self.contexts_list) != 0:
            print("So far you have the following social contexts added:")
            for i in list(self.contexts_list.keys()):
                print(str(self.contexts_list[i]))
                count += 1


        adding = True
        while adding:
            clear_screen()

            q= input("\n\nWould you like to add another group/place you know people from? (y/n)")
            if self.check_answer(q):
                clear_screen()
                self.contexts_list[count] = input("Please enter a name:")
                count+=1
            else:
                adding = False

        self.contexts_list[count+1] = "Other"
        clear_screen()



    def trim_contexts_list(self):
        """ This method allows the User to remove social contexts from their list. """

        my_list = {}

        # Making sure there are elements to be removed
        if len(self.contexts_list) == 0:
            print("You don't have any listed currently")

        else:
            print("So far you have the following social contexts added:")
            for i in list(self.contexts_list.keys()):
                print(str(self.contexts_list[i]))

            count = 1
            for context in list(self.contexts_list.keys()):
                clear_screen()

                if not self.check_answer(input("\n\nWould you like to remove "+ str(self.contexts_list[context])+"? (y/n)")):
                    my_list[count] = self.contexts_list[context]
                    count+=1

            if len(my_list) == 0:
                print("You choose to delete all contexts so your changed will not be saved")
            else:
                self.contexts_list = my_list


    def get_friends(self):
        """ This function gets the friends of the ego (the user) using the Facebook.py SDK.
        It extracts as much information as possible."""


        try:
            # Checking to see if the database has friends loaded already
            cont=True
            if self.friend_db.shape[1] > 1:
                if self.check_answer(input("\nYou already have friends saved. Would you like to overwrite them? [y/n]")):
                    cont = True
                else:
                    print("OK, nothing has changed.")
                    cont = False

            if cont:
                if self.facebook_link != False:
                    friends = self.facebook_link.get_connections("me","friends")["data"]
                    count = 1
                    for person in friends:
                        their_id = person["id"]
                        info = self.facebook_link.get_object(str(their_id))
                        clear_screen()
                        print(count)
                        count +=1
                        # This loop removes non-ascii characters
                        for i in list(info.keys()):
                            try:
                                blank = str(info[i])
                            except:
                                try:
                                    info[i] = info[i].encode("utf-8")
                                except:
                                    info[i] = their_id[-10:] # trimming some leading zeros

                        self.friend_db[int(info["id"])] = pd.Series(info)

                        # adding the friend to the network
                        self.mynet.add_node(int(their_id))
                        self.mynet.add_edge(self.my_ID,int(their_id))

                    print("Your friend data are now loaded.")

                else:
                    print("Sorry, you must first get access to your graph using the get_access() function")
        except:
            print("Sorry. Please get a new Facebook connection and try again.")


    def get_mutual_friends(self):
        """ This method uses the Facebook.py SDK to get mutual friends for all of the ego's friends."""

        if self.facebook_link !=False:
            count = 1
            # Iterating over the list of all friends
            for i in list(self.friend_db.columns.values):
                if (i != self.my_ID):
                    mutuals = self.facebook_link.get_connections(str(i), "mutualfriends")["data"]
                    my_list = []
                    for mfrnd in mutuals:
                        my_list.append(int(mfrnd["id"]))

                        # adding to the network
                        self.mynet.add_edge(int(i),int(mfrnd["id"]))

                    # Adding the list of mutual friends to the database
                    self.friend_db[i]["mutuals"] = my_list
                    try:
                        ip.core.display.clear_output(other=False) # This clears the Notebook input cell
                    except:
                        ip.core.display.clear_output()
                    print(count)
                    count +=1

            print("Mutual friend data successfully retrieved.")
        else:
            print("You must first get a Facebook connection.")

    def random_sample(self,count=200):
        """ Creating a random sampling of the whole network to make adding personal knowledge more
        tractable. The only way this can be undone is to reload your data from Facebook. """

        total = len(list(self.friend_db.columns.values))
        for sap in random.sample(list(self.friend_db.columns.values),(total-count)):
            if sap != self.my_ID:
                del self.friend_db[int(sap)]
                self.mynet.remove_node(int(sap))

        print("Your network now has a random subset of "+str(count)+" nodes from your whole network")



    def define_strong_ties(self, overwrite=False):
        """ This method allows the user to define which ties are strong ties. The entries are saved
        periodically so the users can take a break without fear of losing the data already entered.
        If this categorization is too strict, the user can use define_tie_strength() to weight
        the ties strength as being between 0 and 1 instead. """

        print("\nThis loop lets you define which ties with your facebook friends are strong")
        count = 0
        clear_screen()
        for person in list(self.friend_db.columns.values):
            info = self.friend_db[int(person)]
            if (info["strong tie"] != info["strong tie"] or overwrite) and person !=self.my_ID: #funky NaN check

                if self.check_answer(input("\nIs you friendship with "+str(info["name"]) +" a strong tie? (y/n)")):
                    self.friend_db[person]["strong tie"] = 1
                    self.mynet[int(person)][self.my_ID]["strong"] = 1
                else:
                    self.friend_db[person]["strong tie"] = 0
                    self.mynet[int(person)][self.my_ID]["strong"] = 0
                clear_screen()

            count += 1
            if count == 10:
                self.save()
                count = 0

        for i in self.mynet.edges():
            if i[0]==i[1]:
                self.mynet[i[0]][i[1]]["strong"] = 0
            try:
                self.mynet[i[0]][i[1]]["strong"]
            except:
                self.mynet[i[0]][i[1]]["strong"] = 0
        return {1:"strong", 0:"weak"}



    def define_tie_strength(self, overwrite=False):
        """ This method allows the user to define a weight for ties. The entries are saved
        periodically so the users can take a break without fear of losing the data already entered.
        Weights must be between 0 and 1 inclusive and might be interpreted as more fine-grained tie strength or  """

        print("\nThis loop lets you define a weight (between 0 and 1, inclusive) for ties.")
        count = 0
        for person in self.mynet.nodes():
            info = self.friend_db[int(person)]
            if (info["tie strength"] != info["tie strength"] or overwrite) and person!=self.my_ID: #funky NaN check

                asking = True
                while asking:

                    q= input("\nWhat weight would you like for  "+str(info["name"]) +" ? [0 up to 1]")
                    try:
                        if (0.<=float(q)<=1.):
                            self.friend_db[person]["tie strength"] = q
                            self.mynet[int(person)][self.my_ID]["weight"] = (float(q)*20)+1 # times 20 for visualization
                            asking=False
                        else:
                            print("You entry +"+str(q)+" doesn't work. Please enter a valid number.")
                    except:
                        print("Invalid entry: Please enter a valid number.")

                clear_screen()
            count += 1
            if count == 10:
                self.save()
                count = 0

        for i in self.mynet.edges():
            if i[0]==i[1]:
                self.mynet[i[0]][i[1]]["weight"] = 1
            try:
                self.mynet[i[0]][i[1]]["weight"]
            except:
                self.mynet[i[0]][i[1]]["weight"] = 1




    def code_for_place_met(self, overwrite=False):
        """ This allows the user to code where they know each friend from. The entries are periodically
        saved in case the user needs to take a break! """

        count = 0
        for person in list(self.friend_db.columns.values):
            clear_screen()

            if (self.friend_db[int(person)]["known from"] != self.friend_db[int(person)]["known from"] or overwrite) and person != self.my_ID: # funky NaN check
                for i in list(self.contexts_list.keys()):
                    print(str(i) +" "+ str(self.contexts_list[i]))
                trying = True
                while trying:
                    q = input("Where do you know " + str(self.friend_db[int(person)]["name"]) + " from? (Enter a number)")
                    try:
                        input = int(q)
                        if int(q) in list(self.contexts_list.keys()):
                            self.friend_db[int(person)]["known from"] = int(q)
                            trying = False
                    except:
                        print("Please enter a number again")
            count +=1
            if count == 10:
                self.save()
                count = 0

        clear_screen()
        print("All friends coded for place met")


    def add_and_code_new_attribute(self, overwrite=False):
        """ This method allows the user to define an attribute and code friends according to it."""

        # Because adding can be slow, the dataframe is created with empty rows. This checks to see if one is available
        indices = list(self.friend_db.index.values)
        if 'undefined1' in indices or 'undefined2' in indices or 'undefined3' in indices:
            asking = True
            while asking:
                attribute = input("\nPlease name that attribute would you like to code for: (e.g. religious affiliation, ethnicity, race, sexuality, etc.):")
                clear_screen()
                if self.check_answer(input("Is "+attribute+ " correct? (y/n)")):
                    for name in indices:
                        if "undefined" in name and asking:
                            indices[indices.index(name)] = attribute
                            self.friend_db.index=indices
                            asking = False

            clear_screen()

            print("Now we'll define some possible values the attribute can take (e.g. Christian, Jewish, Muslim, etc):")


            count = 1
            asking = True
            my_dictionary = {}
            print("You current have "+str(0)+" attributes entered")
            while asking:

                if self.check_answer(input("\nWould you like to add a category? (y/n)")):
                    clear_screen()
                    my_dictionary[count] = input("Please name the new category:")
                    count +=1
                else:
                    asking=False




            count = 0
            clear_screen()
            print("Please code your friends using the following prompts.")
            for person in list(self.friend_db.columns.values):
                if (self.friend_db[int(person)][attribute] != self.friend_db[int(person)][attribute]) or overwrite and person!=self.my_ID: # funky NaN check
                    clear_screen()
                    print("What category is " + str(self.friend_db[int(person)]["name"]) + " in? (Enter a number)")
                    for i in list(my_dictionary.keys()):
                        print(str(i) +" "+ str(my_dictionary[i]))
                    trying = True
                    while trying:
                        q = input()
                        if int(q) in list(my_dictionary.keys()):
                            self.friend_db[int(person)][attribute] = int(q)
                            trying = False
                        else:
                            print("Please enter a number again")
                    count += 1
                    if count == 10:
                        self.save()
                        count = 0
                else:
                    print("Everything is filled in and you haven't changed the override argument to True")
            clear_screen()
            print("New attribute successfully added")
            return my_dictionary

        else:
            print("Sorry, space for extra attributes is gone")



    def create_gender_dictionary(self):
        return {"female":"female", "male":"male","no response":"nan"}



    ## Rendering the network visually

    def define_colors(self, attribute, dictionary):
        """ This method allows the user to color friends' nodes based on the given attribute"""

        self.defined_colors = []
        my_dict = {}

        # Letting the user pick the colors
        for i in list(dictionary.keys()):
            my_dict[i] = input("\nWhat color should nodes be for people with value " + str(dictionary[i])+"?")
            clear_screen()

        # creating a list with the appropriate colors
        for person in self.mynet.nodes():
            if person == self.my_ID:
                self.defined_colors.append("blue")
            else:
                key = self.friend_db[person][attribute]
                try:
                    self.defined_colors.append(my_dict[key])
                except:
                    self.defined_colors.append("white")






    def count_components(self, withme=True):
        """ This method returns the number of components in the network without the ego.
        It does this by removing the ego in a copy of the network."""

        if withme:
            print("If you're in the network, it has to have a single component!")
        else:
            bu = nx.Graph()
            bu.add_nodes_from(self.mynet.nodes())
            bu.add_edges_from(self.mynet.edges())
            bu.remove_node(self.my_ID)

            print("Your network has "+ str(nx.number_connected_components(bu)) +" components")





    def draw_network(self,colors=[], strong=False, weight=False, withme=True):
        """ This function writes the network to a .json file to be read using the
        the fb_net.html page so that users can explore the network move thoroughly.
        """
        my_file = open("./visualizations/fbgraph.json", "w+")
        my_file.write("{\"nodes\":[\n")

        if not withme:
            strong=False
            weight=False

            if colors == []:
                colors = self.defined_colors
                if colors != []:
                    backup_colors = {}
                    nodes = list(self.mynet.nodes())
                    for i in range(len(nodes)):
                        backup_colors[nodes[i]] = self.defined_colors[i]
                    index = list(self.mynet.nodes()).index(self.my_ID)
                    self.defined_colors.pop(index)
                else:
                    backup_colors = []
            else:
                backup_colors = {}
                nodes = list(self.mynet.nodes())
                for i in range(len(nodes)):
                    backup_colors[nodes[i]] = self.defined_colors[i]
                index = list(self.mynet.nodes()).index(self.my_ID)
                self.defined_colors.pop(index)


            backup_net = nx.Graph(self.mynet)
            self.mynet.remove_node(self.my_ID)


        # This defaults the coloring scheme to what the user has previously defined (if anything)
        # if no color argument is passed in
        if colors == []:
            colors = list(self.defined_colors)
            if colors == []:
                for i in self.mynet.nodes():
                    if i == self.my_ID:
                        colors.append("blue")
                    else:
                        colors.append("aqua")


        rewrite = {} # A dictionary for renumbering the node ids
        count = 0    # also for the renumbering operation.
        mutuals = {} # We use the count of mutual friends as data
        nodes = list(self.mynet.nodes()) # We use the member list from the network instead of the database
                                # because it colors nodes in the order of this list and the imported
                                # color list is in that order

        # In both the loop for nodes and links, we do n-1 first and the last one manually because of the
        # the need to insert the right characters for the .json format.

        for j in range(len(nodes)-1):
            i = nodes[j]            # i is the usual id number
            rewrite[i]=count        # renumbering business
            my_mutuals = [int(k) for k in self.friend_db["mutuals"][int(i)]] # A Pandas series object is just like a python dictionary, but isn't...Cast it!
            #print my_dct
            mutuals[i]=len(my_mutuals)
            # The next 3 lines create the bulk of the text
            newdct ="{\"color\":"+"\""+str(colors[count])+"\""
            newdct +=",\"id\":"+"\""+str(rewrite[i])+"\""
            newdct +=",\"name\":"+"\""+str(self.friend_db["name"][i])+"\", \"value\":"+str(mutuals[i])+"},\n" #\"x\":50, \"y\":50"+",\
            count +=1
            my_file.write(newdct)


        # The next 5 lines write the info for the last node and the end-list characters
        mutuals[nodes[count]] = len(self.friend_db["mutuals"][nodes[count]])
        rewrite[nodes[count]]=count
        my_dct = dict()
        st = "{\"color\":"+"\""+str(colors[count])+"\",\"id\":"+"\""+str(rewrite[nodes[-1]])+"\",\"name\":"
        st += "\""+str(self.friend_db["name"][int(nodes[-1])])+"\", \"value\":"+str(mutuals[nodes[-1]])+" }],\n\"links\":["       #\"x\":50, \"y\":50
        my_file.write(st)


        # Part 2: adding the nodes
        count = 0
        edges = list(self.mynet.edges()) #

        for i in range(len(edges)-1):
            j = edges[i] # this is a tuple of source and target pairs
            my_file.write("\n{\"source\":"+str(rewrite[j[0]])+", \"target\":"+str(rewrite[j[1]])+", \"n1\":\""
                              +str(self.friend_db["name"][j[0]])+"\", \"n2\":\""+str(self.friend_db["name"][j[1]])+"\"")

            end = ""
            if strong:
                try:
                    strg = self.mynet[j[0]][j[1]]["strong"]
                    if not (strg==strg) or strg==-1:
                        end +=",\"strong\":"+str(0)
                    else:
                        end +=",\"strong\":"+str(strg)
                except:
                    end +=",\"strong\":"+str(0)
            else:
                end +=",\"strong\":"+str(0)
            if weight:
                try:
                    strength = self.mynet[j[0]][j[1]]["weight"]
                    if not (strength==strength) or strength==-1:
                        end +=",\"weight\":"+str(0)
                    else:
                        end +=",\"weight\":"+str(strength)
                except:
                    end +=",\"weight\":"+str(0)
            else:
                end +=",\"weight\":"+str(0)
            end+="},"
            my_file.write(end)

            count +=1

        # The last edge and end-list characters again
        j = edges[-1]


        my_file.write("\n{\"source\":"+str(rewrite[j[0]])+", \"target\":"+str(rewrite[j[1]])+", \"n1\":\""
                          +str(self.friend_db["name"][j[0]])+"\", \"n2\":\""+str(self.friend_db["name"][j[1]])+"\"")
        end = ""
        if strong:
            try:
                strg = self.mynet[j[0]][j[1]]["strong"]
                if not (strg==strg) or strg==-1:
                    end +=",\"strong\":"+str(0)
                else:
                    end +=",\"strong\":"+str(strg)
            except:
                end +=",\"strong\":"+str(0)
        else:
            end +=",\"strong\":"+str(0)
        if weight:
            try:
                strength = self.mynet[j[0]][j[1]]["weight"]
                if not (strength==strength) or strength==-1:
                    end +=",\"weight\":"+str(0)
                else:
                    end +=",\"weight\":"+str(strength)
            except:
                end +=",\"weight\":"+str(0)
        else:
            end +=",\"weight\":"+str(0)
        end+="}]}"
        my_file.write(end)

        # OK, file is complete
        my_file.close()

        if not withme:
            self.mynet = nx.Graph(backup_net)
            if backup_colors == []:
                self.defined_colors = []
            else:
                clrs = []
                for i in self.mynet.nodes():
                    clrs.append(backup_colors[i])
                self.defined_colors = clrs

    ## I/O functions to save progress
    def save(self):
        """ This method outputs data to files to be loaded later. """

        self.friend_db.to_csv("./"+str(self.graph_name)+"_friend_data.csv")
        other_data = open("./"+str(self.graph_name)+"_general_data.csv", "w+")
        other_data.write("my_ID;"+str(self.my_ID)+"\n")
        other_data.write("contexts_list;")
        for item in list(self.contexts_list.items()):
            other_data.write(str(item[0])+":"+item[1]+",")
        other_data.write("\n")
        if self.defined_colors != []:
            other_data.write("defined_colors;")
            for item in self.defined_colors:
                other_data.write(item+",")
            other_data.write("\n")

        other_data.close()


    def change_friend_values(self, name):
        id = 0
        for i in list(self.friend_db.columns.values):
            if self.friend_db[i]["name"] == str(name):
                id = i
        if id == 0:
            print("Name not found. Please try again.")
        else:
            for attr in list(self.friend_db.index.values):
                val = self.friend_db[id][attr]
                if self.check_answer(input(str(name)+ " has value "+ str(val)+ " for attribute "+str(attr)+". Would you like to change it? (y/n)")):
                    asking = True
                    while asking:

                        if attr == "tie strength":
                            q = input("Please input the new value:")
                            try:
                                q = float(q)
                                if 0.<=q<=1.:
                                    self.friend_db[id][attr] = q
                                    asking = False
                                else:
                                    print("Invalid value. Enter again.")
                            except:
                                print("Invalid value. Enter again.")
                        if attr == "strong tie":
                            q = input("Please input the new value:")
                            try:
                                q = int(q)
                                if 0==q or 1==q:
                                    self.friend_db[id][attr] = q
                                    asking = False
                                else:
                                    print("Invalid value. Enter again.")
                            except:
                                print("Invalid value. Enter again.")
                        if attr == "known from":
                            q = input("Please input the new value:")
                            try:
                                q = int(q)
                                if q in list(self.contexts_list.keys()):
                                    self.friend_db[id][attr] = q
                                    asking = False
                                else:
                                    print("Invalid value. Enter again.")
                            except:
                                print("Invalid value. Enter again.")
                        else:
                            print("There are no input checks available for this attribute so be careful!")
                            try:
                                q = int(input("Please input the new value:"))
                                self.friend_db[id][attr] = q
                                asking = False
                            except:
                                print("Not an integer, try again.")

                clear_screen()

            print("Update complete.")


    def load_data(self,file_name="1"):
        """ This method loads existing data into a graph object. """

        cont = True
        if self.friend_db.empty == False:
            print("You already have data loaded. Would you like to delete it? (y/n)")
            q = input()
            if self.check_answer(q):
                print("Ok, data deleted.")
                self.friend_db = False
            else:
                "OK, data load aborted"
                cont = False

        if cont:
            self.contexts_list = {}

            # Loading in data other than the Database
            other = open("./"+str(file_name)+"_general_data.csv", "r+")
            for line in other:
                data = line.strip().split(";")
                if data[0] == "my_ID":
                    if data[1] == 'False':
                        self.my_ID = -1
                    else:
                        self.my_ID = int(data[1])
                        self.mynet.add_node(self.my_ID)
                if data[0] == "contexts_list":
                    self.contexts_list = {}
                    if data[1] != "":
                        new_data = data[1].split(",")
                        for i in new_data:
                            if i != "":
                                j = i.split(":")
                                self.contexts_list[int(j[0])] = j[1]
                if data[0] == "defined_colors":
                    self.defined_colors = [i for i in data[1].split(",")]


            # loading in the database
            self.friend_db = pd.read_csv("./"+str(file_name)+"_friend_data.csv", header=0, index_col=0)
            new_names = []
            for i in list(self.friend_db.columns.values):
                new_names.append(int(i))
                if self.my_ID != i:
                    # adding network ties
                    self.mynet.add_node(int(i))
                    self.mynet.add_edge(int(i), self.my_ID)

            self.friend_db.columns = new_names

            attrs=list(self.friend_db.index.values)
            # adding the mutual ties connections (and converting to ints from strings)
            for i in list(self.friend_db.columns.values):

                q = self.friend_db[int(i)]["known from"]
                if q==q:
                    self.friend_db[int(i)]["known from"] = int(q)

                """r = self.friend_db[int(i)][attrs[6]]
                if r==r:
                    self.friend_db[int(i)][attrs[6]] = int(r)

                p = self.friend_db[int(i)][attrs[7]]
                if p==p:
                    self.friend_db[int(i)][attrs[7]] = int(p)

                s = self.friend_db[int(i)][attrs[8]]
                if s==s:
                    self.friend_db[int(i)][attrs[8]] = int(s)"""

                if type(self.friend_db[int(i)]["mutuals"]) == str:
                    mut_str = self.friend_db[int(i)]["mutuals"][1:-1].split(",")
                    mutuals = []
                    for j in mut_str:
                        try:
                            mutuals.append(int(j))
                        except:
                            if j != "":
                                mutuals.append(int(j))
                            else:
                                pass

                self.friend_db[int(i)]["mutuals"] = mutuals
                for j in mutuals:
                    if int(j) in new_names:
                        try:
                            edge = self.mynet[int(j)][int(i)]
                        except:
                            self.mynet.add_edge(int(j), int(i))

                #val = self.friend_db[int(i)]["tie strength"]
                #if val != "" and (val==val):
                #    self.mynet[int(i)][self.my_ID]["weight"] = float(val)

                val2 = self.friend_db[int(i)]["strong tie"]
                if val2 != "" and (val2==val2):
                    self.mynet[int(i)][self.my_ID]["strong"] = int(val2)

            for edge in self.mynet.edges():
                try:
                    self.mynet[int(edge[0])][int(edge[1])]["strong"]
                except:
                    self.mynet[int(edge[0])][int(edge[1])]["strong"]=0
                try:
                    self.mynet[int(edge[0])][int(edge[1])]["weight"]
                except:
                    self.mynet[int(edge[0])][int(edge[1])]["weight"]=0.


            print("Data successfully loaded")

    def build_network(self):
        self.my_ID = 1
        new_names = []
        for i in list(self.friend_db.index.values):
            new_names.append(int(i))
            if self.my_ID != i:
                # adding network ties
                self.mynet.add_node(int(i))
                self.mynet.add_edge(int(i), self.my_ID)


        self.friend_db.index = new_names


        attrs=list(self.friend_db.columns.values)
        # adding the mutual ties connections (and converting to ints from strings)
        for i in list(self.friend_db.index.values):

            q = self.friend_db["known from"][int(i)]
            if q==q:
                self.friend_db["known from"][int(i)] = int(q)

            """r = self.friend_db[int(i)][attrs[6]]
            if r==r:
                self.friend_db[int(i)][attrs[6]] = int(r)

            p = self.friend_db[int(i)][attrs[7]]
            if p==p:
                self.friend_db[int(i)][attrs[7]] = int(p)

            s = self.friend_db[int(i)][attrs[8]]
            if s==s:
                self.friend_db[int(i)][attrs[8]] = int(s)"""

            if type(self.friend_db["mutuals"][int(i)]) == str:
                mut_str = self.friend_db["mutuals"][int(i)][1:-1].split(",")
                mutuals = []
                for j in mut_str:
                    try:
                        mutuals.append(int(j))
                    except:
                        if j != "":
                            mutuals.append(int(j))
                        else:
                            pass

            self.friend_db["mutuals"][int(i)] = mutuals
            for j in mutuals:
                if int(j) in new_names:
                    try:
                        edge = self.mynet[int(i)][int(j)]
                    except:
                        self.mynet.add_edge(int(j), int(i))

            #val = self.friend_db[int(i)]["tie strength"]
            #if val != "" and (val==val):
            #    self.mynet[int(i)][self.my_ID]["weight"] = float(val)




    def avg_path_length(self):
        return nx.average_shortest_path_length(self.mynet)

    def diameter(self, withme=True):

        if withme:
            print("If you're in the network, it has to be diameter 2")
        else:
            bu = nx.Graph()
            bu.add_nodes_from(self.mynet.nodes())
            bu.add_edges_from(self.mynet.edges())
            bu.remove_node(self.my_ID)
            to_remove = []
            for n in bu.nodes():
                if nx.is_isolate(bu, n):
                    to_remove.append(n)

            for n in to_remove:
                bu.remove_node(n)

            print("Your network has a diameter of "+ str(nx.diameter(bu)))

    def degree_centrality(self, withme=True, node=True):

        if node:
            if withme:
                my_dict = nx.degree_centrality(self.mynet)
                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]
                return new
            else:
                bu = nx.Graph()
                bu.add_nodes_from(self.mynet.nodes())
                bu.add_edges_from(self.mynet.edges())
                bu.remove_node(self.my_ID)
                my_dict = nx.degree_centrality(bu)

                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]

                return new

        else:
            try:
                my_dict = nx.degree_centrality(self.mynet)
                return my_dict[node]
            except:
                try:
                    return my_dict[self.name_to_id(node)]
                except:
                    print("Invalid node name")

    def betweenness_centrality(self, withme=True, node=True):
        if node:
            if withme:
                my_dict = nx.betweenness_centrality(self.mynet)
                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]
                return new
            else:
                bu = nx.Graph()
                bu.add_nodes_from(self.mynet.nodes())
                bu.add_edges_from(self.mynet.edges())
                bu.remove_node(self.my_ID)
                my_dict = nx.betweenness_centrality(bu)

                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]

                return new

        else:
            try:
                my_dict = nx.betweenness_centrality(self.mynet)
                return my_dict[node]
            except:
                try:
                    return my_dict[self.name_to_id(node)]
                except:
                    print("Invalid node name")

    def closeness_centrality(self, withme=True, node=True):
        if node:
            if withme:
                my_dict = nx.closeness_centrality(self.mynet)
                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]
                return new
            else:
                bu = nx.Graph()
                bu.add_nodes_from(self.mynet.nodes())
                bu.add_edges_from(self.mynet.edges())
                bu.remove_node(self.my_ID)
                my_dict = nx.closeness_centrality(bu)

                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]

                return new

        else:
            try:
                my_dict = nx.closeness_centrality(self.mynet)
                return my_dict[node]
            except:
                try:
                    return my_dict[self.name_to_id(node)]
                except:
                    print("Invalid node name")

    def eigenvector_centrality(self, iterations, withme=True, node=True):
        my_dict = nx.eigenvector_centrality(self.mynet,max_iter = iterations)

        if node:
            if withme:
                my_dict =nx.eigenvector_centrality(self.mynet,max_iter = iterations)
                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]
                return new
            else:
                bu = nx.Graph()
                bu.add_nodes_from(self.mynet.nodes())
                bu.add_edges_from(self.mynet.edges())
                bu.remove_node(self.my_ID)
                my_dict = nx.eigenvector_centrality(bu,max_iter = iterations)

                new = {}
                for i in my_dict:
                    new[self.id_to_name(i)] = my_dict[i]

                return new

        else:
            try:
                my_dict = nx.eigenvector_centrality(self.mynet,max_iter = iterations)
                return my_dict[node]
            except:
                try:
                    return my_dict[self.name_to_id(node)]
                except:
                    print("Invalid node name")


    def degree(self, node):
        try:
            return self.mynet.degree(node)
        except:
            print("Invalid node name.")

    def average_degree(self):
        vals = list(self.mynet.degree(mynet.nodes()).values())
        return sum(vals)/float(len(vals))



    def clustering(self, group=0):
        """ This method calculates the clustering coefficients for the specified group (context number). The default
        group is the whole network minus the ego because it skews everything so much."""

        node_list = []
        if group==-1:
            for i in self.mynet.nodes():
                if i != self.my_ID:
                    node_list.append(i)
        elif group==0:
            node_list = self.mynet.nodes()
        else:
            for i in self.mynet.nodes():
                if self.friend_db["known from"][int(i)] == group:
                    node_list.append(i)

        clustering = nx.clustering(self.mynet, node_list)

        try:
            g_name = self.contexts_list[group]
        except:
            if group == -1:
                g_name = "Whole Graph (without you)"
            if group == 0:
                g_name = "Whole Graph"

        print("Clustering coefficient for people in the group " + g_name)



        return clustering

    def clustering_by_attribute_summary(self, attribute):
        """ This allows the user to group people by an attribute and look at clustering within those
        categories. """
        if attribute == "mutuals" or attribute == "id":
            print("Sorry, "+attribute+ " is not a sortable attribute")
        else:
            node_dict = {}
            for i in list(self.friend_db.index.values):
                val  = self.friend_db[attribute][int(i)]
                try:
                    node_dict[val].append(int(i))
                except:
                    node_dict[val] = [int(i)]

            cluster_dict = {}
            for i in node_dict:
                nodes = node_dict[i]
                cluster_coef = nx.clustering(self.mynet, nodes)
                rewrite = {}
                for r in cluster_coef:
                    rewrite[self.id_to_name(r)] = cluster_coef[r]
                cluster_dict[i] = cluster_coef
                tot = sum(rewrite.values())/float(len(list(rewrite.values())))
                print("Average clustering coef. for friends with attribute value "+str(i)+" is: "+ str(tot))

            return cluster_dict

    def clustering_by_attribute(self, attribute):
        """ This allows the user to group people by an attribute and look at clustering within those
        categories. """
        if attribute == "mutuals" or attribute == "id":
            print("Sorry, "+attribute+ " is not a sortable attribute")
        else:
            node_dict = {}
            for i in list(self.friend_db.index.values):
                val  = self.friend_db[attribute][int(i)]
                try:
                    node_dict[val].append(int(i))
                except:
                    node_dict[val] = [int(i)]

            cluster_dict = {}
            for i in node_dict:
                nodes = node_dict[i]
                cluster_coef = nx.clustering(self.mynet, nodes)
                rewrite = {}
                for r in cluster_coef:
                    rewrite[self.id_to_name(r)] = cluster_coef[r]
                cluster_dict[i] = cluster_coef
                print("Clustering coef. for friends with attribute value "+str(i)+" is: "+ str(rewrite))

            return cluster_dict

    def associativity_by_attribute(self, attribute):
        """ This allows the user to see the probability of alters sharing at attribute."""

        if attribute =="id" or attribute =="mutuals":
            print("Sorry, "+ attribute+ " is not a sortable attribute.")

        else:
            trans_dict = {}
            for i in list(self.friend_db.index.values):
                val = self.friend_db[attribute][i]
                mutuals = list(self.friend_db["mutuals"][i])
                hit = 0
                total = 0
                for j in mutuals:
                    if self.friend_db[attribute][int(j)] == val:
                        hit +=1
                    total +=1
                if (i != self.my_ID):
                    if (self.friend_db[attribute][self.my_ID] == val):
                        hit +=1
                    total += 1

                if total != 0:
                    coef = hit/float(total)
                else:
                    coef = 0

                try:
                    trans_dict[val].append(coef)
                except:
                    trans_dict[val] = [coef]

            avg_dict = {}
            for i in trans_dict:
                val = trans_dict[i]
                avg = sum(val)/float(len(val))
                avg_dict[i] = avg
                print("Associativity avg for people with value "+str(i) + " is: " +str(avg))

            return avg_dict



    def get_average_clustering(self, a_dictionary):
        """ This method accepts a dictionary or a dictionary of dictionaries and finds the average values
        sorted by keys."""

        try:
            for i in a_dictionary:
                my_list = []
                sub_dict = a_dictionary[i]
                for j in sub_dict:
                    my_list.append(sub_dict[j])
                avg= sum(my_list)/float(len(my_list))
                print("Avg. clustering for attribute value "+str(i)+ " is " +str(avg))

        except:
            my_list = []
            for i in a_dictionary:
                my_list.append(a_dictionary[i])
            avg = sum(my_list)/float(len(my_list))
            print("Average clustering for group is "+str(avg))





    def attribute_by_attribute(self, attribute_one, group_number, attribute_two):
        """ This method allows the user to see the prevalences of a particular
        attribute within a group. This is no doubt a way to do this using Pandas functionality,
        but that is for a later iteration."""

        indices = list(self.friend_db.column.values)
        if (attribute_one not in indices or attribute_two not in indices):
            print("Invalid inputs. Make sure the dictionary and spelling are correct.")


        else:
            vals = {}
            count = 0
            for i in list(self.friend_db.index.values):
                if (self.friend_db[str(attribute_one)][i] == group_number):
                    which = self.friend_db[str(attribute_two)][i]
                    try:
                        vals[which] += 1
                        count +=1
                    except:
                        vals[which] = 1
                        count +=1

            print("For friends in group "+str(group_number)+" for attribute "+str(attribute_one)+",")
            print("they breakdown into the following percentages for attribute "+str(attribute_two))
            print("(Sample size = "+str(count)+")")

            for j in vals:
                try:
                    number = vals[j]/float(count)
                except:
                    number = 0

                print(str(j)+" : "+str(number))


    def attribute_breakdown(self, attribute):
            """ This method finds the percentage within categories of an attribute"""

            if attribute not in list(self.friend_db.columns.values):
                print("Not a valid attribute")

            vals = {}
            count = 0
            for i in list(self.friend_db.index.values):
                which = self.friend_db[str(attribute)][i]
                try:
                    vals[which] += 1
                    count +=1
                except:
                    vals[which] = 1
                    count +=1

            print("Your friend breakdown into the following percentages for attribute "+str(attribute))
            print("(Sample size = "+str(count)+")")

            for j in vals:
                try:
                    number = vals[j]/float(count)
                except:
                    number = 0

                print(str(j)+" : "+str(number))


    def ids_to_names(self):
        """ Returns a dictionary links IDs to names. """
        my_dict = {}
        for i in list(self.friend_db.index.values):
            my_dict[int(i)] = self.friend_db["name"][int(i)]

        return my_dict


    def name_to_id(self, name):
        """Returns the ID number associated with the name ."""

        for id in self.friend_db:
                    name1 = str(self.friend_db["name"][int(id)])
                    if name1 == name:
                        return id
        print("Not a valid name")


    def id_to_name(self, id):
        """Returns the name associated with the ID number."""
        try:
            name = str(self.friend_db["name"][int(id)])
            return name
        except:
            print("Not a valid ID")
            return id


    def view_mutual_friends(self, name):
        """ This allows the user to see mutual friends of the specified friend """
        id = 0
        for i in list(self.friend_db.index.values):
            if self.friend_db["name"][i] == str(name):
                id = i
        if id == 0:
            print("Name not found. Please try again.")
        else:
            print("You have the follow mutual friends:")
            mutuals = self.friend_db["mutuals"][id]
            for i in mutuals:
                print(self.friend_db["name"][i])



    def view_friend_info(self, name):
        """ This allows the user to see a friend's attributes """
        id = 0
        for i in list(self.friend_db.index.values):
            if self.friend_db["name"][i] == str(name):
                id = i
        if id == 0:
            print("Name not found. Please try again.")
        else:
            print("ID#: "+str(id))
            for attr in list(self.friend_db.columns.values):
                print(str(attr) + ": "+ str(self.friend_db[attr][id]))



    def view_people_from(self, group):
        """This method allows the user to see who the user knows from the various social contexts"""

        if group not in self.contexts_list:
            print("Incorrect group name")
        else:
            my_list = []
            for i in self.friend_db.index.values:
                if self.friend_db["known from"][i] == group:
                    my_list.append(self.friend_db["name"][i])
            print("You have included the following people in the group named "+str(self.contexts_list[group])+":")
            for i in my_list:
                print(i)


    def test_Strong_Triadic_Closure(self):
        """ This method has the user test the principle of strong triadic closure; there is a
        good chance that friends with whom the ego has strong ties are also friends. This
        algorithm will not work if the user hasn't already defined which ties are strong."""
        comps = []
        edges = nx.get_edge_attributes(self.mynet, "strong")
        if edges != {}:
            for e in edges:
                if edges[e] == 1:
                    comps.append(e)
            hit = []
            for i in comps:
                for j in comps:
                    if i!=j:
                        for k in i:
                            if k != self.my_ID:
                                notme1 = k
                        for l in j:
                            if l != self.my_ID:
                                notme2 = l
                        try:
                            self.mynet[notme1][notme2]
                            hit.append(1)
                        except:
                            hit.append(0)

            try:
                val = sum(hit)/float(len(hit))
            except:
                val = 0
            print("Count of triads inspected: "+str(len(hit)))
            print(val)
        else:
            print("ERROR: You must first enter information about strong ties [Command define_strong_ties()].")


    def test_Strong_Triadic_Closure_within_group(self, group):
        """ This method has the user test the principle of strong triadic closure within groups;
        there is a good chance that friends with whom the ego has strong ties are also friends (within groups).
        This algorithm will not work if the user hasn't already defined which ties are strong.
        The group value is the one associated with social contexts."""

        comps = []
        edges = nx.get_edge_attributes(self.mynet, "strong")
        if edges != {}:
            for e in edges:
                if edges[e] == 1 and (self.friend_db["known from"][e[0]] ==group or self.friend_db["known from"][e[1]]==group):
                    # the check above makes sure they are in the right group
                    comps.append(e)

            hit = []
            for i in comps:
                for j in comps:
                    if i!=j:
                        for k in i:
                            if k != self.my_ID:
                                notme1 = k
                        for l in j:
                            if l != self.my_ID:
                                notme2 = l
                        try:
                            self.mynet[notme1][notme2]
                            hit.append(1)
                        except:
                            hit.append(0)

            try:
                val = sum(hit)/float(len(hit))
            except:
                val = 0
            print("Count of triads inspected: "+str(len(hit)))
            print(val)
        else:
            print("ERROR: You must first enter information about your tie strengths.")



    def clean_mutuals(self):
        """This is a temporary fix for a consistency problem in which there are
        friends in the alters' mutual friend lists that aren't in the database as alters
        (because either a partial list loaded or a sample of all nodes was taken). It just
        removes those alters."""

        peeps = list(self.friend_db.index.values)
        for i in peeps:
            existing = []
            muts = list(self.friend_db["mutuals"][int(i)])
            for j in muts:
                if j in peeps:
                    existing.append(int(j))
            self.friend_db["mutuals"][int(i)] = existing

        print("Mutual friends lists now cleaned.")
