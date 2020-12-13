import os
import sys
import subprocess
from datetime import datetime
sys.path.append('../../utils')
from db import insert_into_db, get_db_info, select_db
from paths import parse_data_path

def insert(proc, savename):

	print(proc)
	paths = get_db_info()
	mouse_name, file_date, file_date_id = parse_data_path(os.path.dirname(savename))
	print(mouse_name, file_date, file_date_id)

	subprocess.run(['rsync', '-avx', '--progress', '--relative',
	                os.path.join(paths['facemap_root'], '.', mouse_name, file_date_id, os.path.basename(savename)),
	                'alowet@login.rc.fas.harvard.edu:' + paths['remote_facemap_root']])
	print('Processed video transferred to cluster.')

	db_entry = select_db(paths['db'], 'facemap', '*', 'name=? AND file_date_id=?', (mouse_name, file_date_id))
	db_dict = {k: db_entry[k] for k in db_entry.keys()}

	db_dict['processed_data_path'] = os.path.join(paths['remote_facemap_root'], mouse_name, file_date_id, os.path.basename(savename))
	db_dict['date_facemap'] = datetime.today().strftime('%Y%m%d')

	to_check = {'pupil': 'has_pupil',
	            'blink': 'has_blink',
	            'motMask': 'has_motion',
	            'running': 'has_running',
	            'pupil_mean': 'pupil_mean'
	            }

	for k, v in zip(to_check.keys(), to_check.values()):
		if proc[k]:
			db_dict[v] = 1
		# cover the multi camera case by ensuring that we only ever insert a 0 if the field is blank to begin
		elif db_dict[v] == None:
			db_dict[v] = 0

	insert_into_db(paths['db'], 'facemap', tuple(db_dict.keys()), tuple(db_dict.values()))
	print('Inserted ' + savename + ' into database.')






