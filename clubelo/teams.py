#tworzy globalne zmienne - sety zespołów z roznych krajów
from scraping.fetch import fetch_url
from clubelo.parse import parse_clubelo_teamset
import config


#tworze mapę nazwa klubu z fbref -> nazwa klubu z clubelo (Clubelo nie ma niektorych zespolow ktore byly w dawnych sezonach w fbref)
FBREF_CLUEBLO_TEAMS_MAPPING = {"Liverpool":'Liverpool','Arsenal':'Arsenal', 'Manchester City': 'ManCity',
                               'Chelsea':'Chelsea','Newcastle United': 'Newcastle', 'Aston Villa':'AstonVilla',
                               'Nottingham Forest':'Forest', 'Brighton and Hove Albion':'Brighton', 'Bournemouth':'Bournemouth',
                               'Brentford':'Brentford','Fulham':'Fulham', 'Crystal Palace':'CrystalPalace',
                               'Everton':'Everton','West Ham United':'WestHam','Manchester United':'ManUnited',
                               'Wolverhampton Wanderers':'Wolves','Tottenham Hotspur':'Tottenham', 'Leicester City':'Leicester',
                               'Ipswich Town':'Ipswich', 'Southampton':'Southampton', 'Leeds United':'Leeds',
                               'Burnley':'Burnley', 'Sheffield United':'Sheffield United', 'Watford':'Watford',
                               'Norwich City':'Norwich','West Bromwich Albion':'WestBrom', 'Sunderland':'Sunderland',
                               'Swansea City':'Swansea', 'Stoke City':'Stoke', 'Hull City':'Hull',
                               'Middlesbrough':'Middlesbrough', 'Queens Park Rangers':'QPR',
                               }



CLUBELO_TEAMS_SET = set(FBREF_CLUEBLO_TEAMS_MAPPING.values())


CLUBELO_TO_FBREF_MAPPING = {v: k for k, v in FBREF_CLUEBLO_TEAMS_MAPPING.items()}

print(f"ClubELO mappings loaded: {len(FBREF_CLUEBLO_TEAMS_MAPPING)} teams (OFFLINE mode, no HTTP requests)")