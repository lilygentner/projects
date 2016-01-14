####
#Baseball
####

def zip(file):
    r = requests.get(file).content
    s = StringIO.StringIO(r)
    zf = zipfile.ZipFile(s, 'r') 
    return zf
url = 'http://www.retrosheet.org/gamelogs/gl2010_14.zip'
#url2 = 'http://www.retrosheet.org/gamelogs/gl2000_09.zip'
zf = zip(url)
tablenames = zf.namelist()
GL2010 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2010.TXT')]), header=None)
GL2011 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2011.TXT')]), header=None)
GL2012 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2012.TXT')]), header=None)
GL2013 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2013.TXT')]), header=None)
GL2014 = pd.read_csv(zf.open(tablenames[tablenames.index('GL2014.TXT')]), header=None)

keepFieldsN = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 19, 20]
keepFields = ['date', 'day', 'vTeam', 'vTeamLeague', 'vTeamGame', 'hTeam', 'hTeamLeague', 'hTeamGame', 'vTeamScore', 'hTeamScore', 'outs', 'time', 'parkID', 'attendance', 'lineScoreV', 'lineScoreH']

gamesClean = []

for filename in tablenames: 
    file = zf.open(tablenames[tablenames.index(filename)]).readlines()
    for each in file:
        row = [x.replace('"', "") for x in each.split(',')]
        game = [row[i] for i in range(0, len(row)) if i in keepFieldsN]
        gamesClean.append(game)

gamesDF = pd.DataFrame(gamesClean, columns = keepFields)
gamesDF['year'] = [s[0:4] for s in gamesDF.date.tolist()]
gamesDF['winner'] = [gamesDF.vTeam.tolist()[i] if gamesDF.vTeamScore.tolist()[i] > gamesDF.hTeamScore.tolist()[i] else gamesDF.hTeam.tolist()[i] for i in range(0, len(gamesDF))]


teams = pd.unique(gamesDF.vTeam)

cols = ['team', 'year', 'record', 'win', 'opponent', 'streakAtStart', 'newOpponent']


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


cleanDF = pd.DataFrame(DFrows, columns = cols)
