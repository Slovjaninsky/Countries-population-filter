import parse_csv
from database import Database
from Gui_interface import Gui_interface

if __name__ == '__main__':
	db_name = 'countries'
	#database = parse_csv.parse('country_and_area_data.csv', 'countries')
	database = Database(db_name)
	database.connect_table(db_name)
	gui = Gui_interface('Countries population', data=database)

