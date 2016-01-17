#Independent Data Analysis Project looking at occurence of (significant) win streaks in Baseball
#Using Markov Chain inspired analysis

def zip(file):
    r = requests.get(file).content
    s = StringIO.StringIO(r)
    zf = zipfile.ZipFile(s, 'r') 
    return zf

#get data from url    
url = 'http://www.retrosheet.org/gamelogs/gl2010_14.zip'
zf = zip(url)
tablenames = zf.namelist()
GL2010 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2010.TXT')]), header=None)
GL2011 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2011.TXT')]), header=None)
GL2012 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2012.TXT')]), header=None)
GL2013 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2013.TXT')]), header=None)
GL2014 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2014.TXT')]), header=None)

url2 = 'http://www.retrosheet.org/gamelogs/gl2000_09.zip'
zf2 = zip(url2)
tablenames2 = zf2.namelist()
GL2009 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2009.TXT')]), header=None)
GL2008 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2008.TXT')]), header=None)
GL2007 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2007.TXT')]), header=None)
GL2006 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2006.TXT')]), header=None)
GL2005 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2005.TXT')]), header=None)
GL2004 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2004.TXT')]), header=None)
GL2003 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2003.TXT')]), header=None)
GL2002 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2002.TXT')]), header=None)
GL2001 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2001.TXT')]), header=None)
GL2000 = pd.read_csv(zf2.open(tablenames2[tablenames2.index('GL2000.TXT')]), header=None)

#process relevant data, create Data Frames
keepFieldsN = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 19, 20]
keepFields = ['date', 'day', 'vTeam', 'vTeamLeague', 'vTeamGame', 'hTeam', 'hTeamLeague', 'hTeamGame', 'vTeamScore', 'hTeamScore', 'outs', 'time', 'parkID', 'attendance', 'lineScoreV', 'lineScoreH']
gamesClean = []

for filename in tablenames: 
    file = zf.open(tablenames[tablenames.index(filename)]).readlines()
    for each in file:
        row = [x.replace('"', "") for x in each.split(',')]
        game = [row[i] for i in range(0, len(row)) if i in keepFieldsN]
        gamesClean.append(game)
for filename in tablenames2: 
    file = zf2.open(tablenames2[tablenames2.index(filename)]).readlines()
    for each in file:
        row = [x.replace('"', "") for x in each.split(',')]
        game = [row[i] for i in range(0, len(row)) if i in keepFieldsN]
        gamesClean.append(game)
gamesDF = pd.DataFrame(gamesClean, columns = keepFields)

#clean data for easier analysis
gamesDF['year'] = [s[0:4] for s in gamesDF.date.tolist()]
gamesDF['winner'] = [gamesDF.vTeam.tolist()[i] if gamesDF.vTeamScore.tolist()[i] > gamesDF.hTeamScore.tolist()[i] else gamesDF.hTeam.tolist()[i] for i in range(0, len(gamesDF))]
teams = pd.unique(gamesDF.vTeam)

#column names for final, cleaned dataframe
cols = ['team', 'year', 'record', 'win', 'opponent', 'streakAtStart', 'newOpponent']


#functions for creating final dataframe
def calculateRecord(winnerList, team):
    total = len(winnerList)
    wins = sum([1 for x in winnerList if x == team])
    return float(wins)/total

def findOpponent(hTeam, vTeam, TEAM):
    if hTeam != TEAM:
        return hTeam
    else:
        return vTeam

def isNewOpponent(hTeamLast, vTeamLast, TEAM, opponent):
    lastOpponent = findOpponent(hTeamLast, vTeamLast, TEAM)
    if lastOpponent == opponent:
        return False
    else:
        return True

#create useable dataframe for analysis
#calculate win/loss streaks (positive for win streak, negative for loss streak)
#calculate new opponents, overall season record, etc. 
dfRows = []
for TEAM in teams: 
    teamDF = gamesDF[(gamesDF.vTeam == TEAM) | (gamesDF.hTeam == TEAM)]
    years = pd.unique(teamDF.year)

    for YEAR in years:
        yearTeamDF = teamDF[teamDF.year == YEAR]
        overallRecord = calculateRecord(yearTeamDF.winner.tolist(), TEAM)
        streak = 0

        for i in range(len(yearTeamDF)):
            winner = yearTeamDF.winner.tolist()[i]
            opponent = findOpponent(yearTeamDF.hTeam.tolist()[i], yearTeamDF.vTeam.tolist()[i], TEAM)
            newOpponent = isNewOpponent(yearTeamDF.hTeam.tolist()[i-1], yearTeamDF.vTeam.tolist()[i-1], TEAM, opponent)
            if winner == TEAM and streak >= 0:
                newStreak += 1
                win = True
            elif winner == TEAM and streak < 0:
                newStreak = 1
                win = True
            elif winner != TEAM and streak < 0:
                newStreak -= 1
                win = False
            elif winner != TEAM and streak >=0:
                newStreak = -1
                win = False

            row = [TEAM, YEAR, overallRecord, win, opponent, streak, newOpponent]
            dfRows.append(row)
            streak = newStreak
cleanDF = pd.DataFrame(dfRows, columns = cols)

#create dataframe of games where each team was playing *new* opponent
newDF = cleanDF[cleanDF.newOpponent == True]



#significance testing and analysis

#ztest to check significance of p(win after win) vs. p(win after loss)
def ztest_2prop(x1, n1, x2, n2):
    p1 = float(x1)/n1
    p2 = float(x2)/n2
    p0 = float(p1*n1 + p2*n2)/(n1 + n2)
    se = np.sqrt(p0*(1-p0)*((float(1)/n1)+(float(1)/n2)))
    z = float(p1-p2)/se
    p_val = scipy.stats.norm.sf(abs(z))*2
    return z, p_val

#test, print significant results
summaryStats = []
for TEAM in teams: 
    gamesAfterWin = len(newDF[(newDF.streakAtStart > 0) & (newDF.team == TEAM)])
    winsAfterWin = len(newDF[(newDF.streakAtStart > 0) & (newDF.win == True) & (newDF.team == TEAM)])
    
    gamesAfterLoss = len(newDF[(newDF.streakAtStart < 0) & (newDF.team == TEAM)])
    winsAfterLoss = len(newDF[(newDF.streakAtStart < 0) & (newDF.win == True) & (newDF.team == TEAM)])
    
    z, p = ztest_2prop(winsAfterWin, gamesAfterWin, winsAfterLoss, gamesAfterLoss)

    summaryStats.append([winsAfterWin, gamesAfterWin, winsAfterLoss, gamesAfterLoss, z, p])
    if z > 1.5:
        print TEAM
        print z
        print p

#first conclusions: 
#very few significant results (those that are significant likely due to fact that there are multiple comparisons)
#appears to be very little evidence that an outcome is significantly tied to the outcome of the previous game 
#(little evidence for streakiness beyond what we would expect to see from iid trials)
