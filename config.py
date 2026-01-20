import os
# Konfiguracja ścieżek, URL-i, parametrów itp.
END_SEASON = '2024-2025'
START_SEASON = '2014-2015' #od tego momentu zaczynają się dokładne statystyki 
# Definiujesz template
FBREF_URL_TEMPLATE = "https://fbref.com/en/comps/9/{season}/{season}-Premier-League-Stats"
CLUBELO_URL_TEMPLATE = "http://clubelo.com/{country}/Ranking"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

#Ściezka do DB
DB_PATH = os.path.join("data", "pl_match_data.db")


#Sets drużyn angielskich potrzebnych do obsluzenia API clubelo
ENG_TEAMS_SET = {
    "Liverpool", "Arsenal", "ManCity", "Chelsea", "AstonVilla", "Newcastle",
    "CrystalPalace", "Brighton", "Brentford", "Bournemouth", "Forest", "ManUnited",
    "Everton", "Fulham", "Tottenham", "WestHam", "Wolves", "Burnley", "Leeds",
    "SheffieldUnited", "Leicester", "Ipswich", "Southampton", "Sunderland",
    "Coventry", "WestBrom", "Middlesbrough", "Millwall", "BristolCity", "Swansea",
    "Blackburn", "Norwich", "Luton", "QPR", "Hull", "SheffieldWeds", "Portsmouth",
    "Stoke", "Watford", "Preston", "Derby", "Oxford", "Plymouth", "Cardiff"
}

#słownik parujący skrót nazwy drużyny w FBREF do pełnej nazwy w FBREF
FBREF_ABR_TO_FBREF = {"Liverpool":"Liverpool", "Arsenal":"Arsenal",'Manchester City':'Manchester City',
                      'Chelsea':'Chelsea', 'Newcastle Utd':'Newcastle United', 'Aston Villa':'Aston Villa',
                      "Nott'ham Forest":'Nottingham Forest', 'Brighton':'Brighton and Hove Albion', 'Bournemouth':'Bournemouth',
                      'Brentford':'Brentford', 'Fulham':'Fulham','Crystal Palace':'Crystal Palace',
                      'Everton':'Everton','West Ham':'West Ham United', 'Manchester Utd':'Manchester United',
                      'Wolves':'Wolverhampton Wanderers', 'Tottenham':'Tottenham Hotspur','Leicester City':'Leicester City',
                      'Ipswich Town':'Ipswich Town', 'Southampton':'Southampton','Burnley':'Burnley',
                      'Sheffield Utd':'Sheffield United','Leeds United':'Leeds United','Watford':'Watford',
                      'Norwich City':'Norwich City','West Brom':'West Bromwich Albion','Swansea City':'Swansea City',
                      'Stoke City':'Stoke City','Hull City':'Hull City', 'Middlesbrough':'Middlesbrough',
                      'Sunderland':'Sunderland','QPR':'Queens Park Rangers'}