# -*- coding: utf-8 -*-
"""
 Student Name:   Kevin O'Mahony
 Student Number: R00105946
 Date: 06-12-2016
 
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot') 

# Prompt user with submenu for query 1 
# Top director/actor by movie gross
# Call appropriate function to handle user response
#
def question1():
    userResponse = promptUserMenu(subMenu1)
    df = pd.read_csv("movie_metadata.csv")
    subMenu1Funcs[userResponse](df)
    return 0


# Do query for top directors as decided by highest
# grossing films
#
def question11(df):
    # Remove rows with null elements in columns we will use in query
    df = df.dropna(subset=['gross','director_name'])  
    
    n = input("Please enter the number of Directors to display: ")
    a = df.groupby('director_name')
    b = a['gross'].sum()
    c = b.sort_values(ascending=False).head(n)
    i = np.array(range(1,n+1))
    my_xticks = c.index
    plt.xticks(i+.2, my_xticks)
    plt.xticks(rotation=90)
    plt.bar(i,c)
    plt.title('Top '+str(n)+' Directors by Gross Film Earnings ($)\n')
    plt.ylabel('Gross Film Earnings ($)')
    plt.xlabel('\nDirectors')   
    plt.show()
    return 0


# Do query for top actor as decided by highest
# grossing films. We are only using actor_1_name column
# for actor and ignoring the other 2 actor name columns
#
def question12(df):
    # Remove rows with null elements in columns we will use in query
    df = df.dropna(subset=['gross','actor_1_name'])  
   
    n = input("Please enter the number of Actors to display: ")
    a = df.groupby('actor_1_name')
    b = a['gross'].sum()
    c = b.sort_values(ascending=False).head(n)
    i = np.array(range(1,n+1))
    my_xticks = c.index
    plt.xticks(i+.2, my_xticks)
    plt.xticks(rotation=90)
    plt.bar(i,c)
    plt.title('Top '+str(n)+' Actors by Gross Film Earnings ($)\n')
    plt.ylabel('Gross Film Earnings ($)')
    plt.xlabel('\nActors')
    plt.show()
    return 0


# Display the max,mean and min gross film earnings between
# user specified start and end years
# 
def question2():
    # read data file and remove rows with null elements
    # in columns we will use in query
    df = pd.read_csv("movie_metadata.csv")
    df = df.dropna(subset=['gross','title_year'])  
   
    sdate = input("Please enter the start year (yyyy): ")
    edate = input("Please enter the end year (yyyy): ")
    f1 = df['title_year'] >= sdate 
    f2 = df['title_year'] <= edate
    d = df[['title_year','gross']][f1 & f2]
    a = d.groupby('title_year')
    theMean = a['gross'].mean()
    theMax = a['gross'].max()
    theMin = a['gross'].min()
  
    plt.plot(theMax,linewidth=3)
    plt.plot(theMean,linewidth=3)
    plt.plot(theMin,linewidth=3)
    plt.xticks(theMax.index,rotation=45)
    plt.xlim(min(theMax.index),max(theMax.index))
     
    plt.ylabel('Gross Earnings ($)')
    plt.legend(['Max','Mean','Min'],loc=0)
    plt.title('Max,Mean,Min Gross Earnings ($)\n'+
                str(sdate)+' to '+str(edate)+'\n')
    plt.show()
    return 0


# floating point version of range
#
def frange(start,stop,step):
    i = [start]
    while start < stop:
        i.append(start+step)
        start += step
    return i


# Display average movie gross earnings against IMDB scores.
# 
def question3():
    # read data file and remove rows with null elements
    # in columns we will use in query
    df = pd.read_csv("movie_metadata.csv")
    df = df.dropna(subset=['gross','imdb_score'])  
  
    labels = ['0-0.5','0.5-1','1-1.5','1.5-2','2-2.5','2.5-3',
            '3-3.5','3.5-4','4-4.5','4.5-5','5-5.5','5.5-6',
            '6-6.5','6.5-7','7-7.5','7.5-8','8-8.5','8.5-9',
            '9-9.5','9.5-10']
    bins = frange(0, 10, 0.5)
    
    df['imdb_score_bins'] = pd.cut(df.imdb_score, bins, labels=labels)
    a = df.groupby('imdb_score_bins')
    x = bins[0:len(bins)-1]
    y = a['gross'].mean() 
    
    plt.xticks(x, y.index,rotation=45)
    plt.bar(x,y,0.35)
    plt.xlabel('IMDB Score')
    plt.ylabel('Average Gross Earnings ($)')
    plt.title('IMDB Score vs. Average Gross Earnings ($)\n')
    plt.show()
    return 0


# Displays average IMDB score for a user selected genre
#
def question4():
    # read data file and remove rows with null elements
    # in columns we will use in query
    df = pd.read_csv("movie_metadata.csv")
    df = df.dropna(subset=['genres','imdb_score'])  

    # Create list of unique genres first  
    a = df['genres']
    b = (np.unique(a))
    genreSet = set()
    for genres in b:        
        glist = genres.split('|')
        for genre in glist:
            genreSet.add(genre)
    genreMenuItems = sorted(genreSet)
    
    # now prompt user with genre list and
    # read user's selection
    n = 0
    while True:
        print("==== Film Genres ====" )
        for i in range(0,len(genreMenuItems)-1):
            print str(i+1)+". "+genreMenuItems[i]
        print "\nPlease select one of the options above"
        n = input("=> ")
        if n in range(0,len(genreMenuItems)):
            break
        else:
            raw_input("Invalid choice, press enter to try again ")

    # get the scores for the given genre    
    imdbScore = []
    for i in range(0,len(df.genres)-1):
        s =  df.iloc[i,9]
        if(genreMenuItems[n-1] in s):
            imdbScore.append(df.iloc[i,25])
            
    # display results
    l = len(imdbScore)
    a = sum(imdbScore)/l
    print "There are "+str(l)+" films in the "+\
            genreMenuItems[n-1] + " genre"
    print "Their average IMDB score is "+ str(format(a,'.1f'))
    return 0


# Insert a newline into long movie titles
#
def compactFilmTitle(strs):
    for i in (range(0,len(strs)-1)):
        t = strs[i].split()
        if (len(t) >= 5):
            t.insert(3,'\n')
            strs[i] = '-'.join(t )         
    return strs      


# Custom Query: displays films with the highest gross 
# earning / budget ratio.
# 
def question5():
    # read data file and remove rows with null elements
    # in columns we will use in query
    df = pd.read_csv("movie_metadata.csv")
    df = df.dropna(subset=['gross','budget','movie_title'])  
  
    # create new column for our ratio
    df['grossBudgetRatio'] = df['gross']/df['budget']  
    
    # get the columns we are interested in
    b = df[['movie_title','grossBudgetRatio','gross','budget']]
    nItems = 10
    a = b.sort_values(by='grossBudgetRatio',ascending=False).drop_duplicates().head(nItems)
 
    # remove control character at end of movie title strings
    titles = a.movie_title.tolist()
    for i in range(len(titles)):
        s = titles[i]
        titles[i] = s[:-2]    

    # create 3 subplots in one column
    f, p = plt.subplots(3, 1, sharex=True)

    # set up x axis ticks
    plt.xlabel('\nFilm') 
    i = np.array(range(1,nItems+1));
    titles = compactFilmTitle(titles)
    plt.xticks(i,titles,rotation=75)
    
    # define the 3 bar charts with legends
    p[0].bar(i,a.grossBudgetRatio,color='b')
    p[0].legend(['Gross/Budget Ratio'],loc=1) 
    p[1].bar(i,a.gross,color='g')
    p[1].legend(['Gross Earnings ($)'],loc=0)
    p[2].bar(i,a.budget,color='r')
    p[2].legend(['Budget ($)'],loc=0) 

    # fix up white space around subplots and add main title
    f.subplots_adjust(left=None, bottom=None, right=None, 
                    top=2, wspace=0, hspace=.2)
    f.suptitle('Top '+str(nItems)+
        ' Films\nGross Earnings / Budget Ratio\n',
        y=2.2, fontsize=16)
        
    plt.show()      
    return 0


# Will cause main loop to exit.
#
def doExit():
    return 1

    
# Display given menu and prompt user for selection
# Returns user menu item number selection
#
def promptUserMenu(menuDict,title="",prompt=""):
    while (True):           
        if len(title):
            print "\n",title
        print(prompt)
        for i,menuItem in menuDict.items():
            print str(i)+".",menuItem        
        n = input("=> ")
        if n in menuDict:
            return n
        else:
            raw_input("Invalid choice, press enter to try again ")


# Menu items and associated function pointers for  main menu
#  
mainMenuFuncs = {
1 : question1,
2 : question2,
3 : question3,
4 : question4,
5 : question5,
6 : doExit }

mainMenu = {
1 : "Most successful directors or actors",
2 : "Analyse the distribution of gross earnings",
3 : "Earnings and IMDB scores",
4 : "Genre Analysis",
5 : "Gross Earnings / Budget Ratio",
6 : "Exit" }


# Menu items and associated function pointers for sub menu 
# for query 1 - top director/actor by film gross
#
subMenu1Funcs = {
1 : question11,
2 : question12 }

subMenu1 = {
1 : "Top Directors",
2 : "Top Actors" }


# Display the main menu to the user and execute the selected query
# Loop until user selects Exit menu item
#
def main(): 
    while (True):
        userResponse = promptUserMenu(mainMenu,
                          prompt="\nPlease select one of the following options: \n")
        if (mainMenuFuncs[userResponse]() == 1):
            break
       
main()