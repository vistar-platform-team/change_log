# from IPython import embed
import datetime
import json,requests,csv,sys
import dateutil.parser as parser

### ENTER YOUR CREDENTIALS HERE ###

options_prod = {'cred':{"email":"***@vistarmedia.com",
				"password":"***"},
			'url':'https://trafficking.vistarmedia.com'}


def write_to_csv(revision_log):
	today = str(datetime.datetime.today())[:10]
	with open('revision_log_{0}.csv'.format(today),'w',newline='') as csvfile:
		new_file = csv.writer(csvfile, delimiter=',')
		for f in revision_log:
			new_file.writerow(f)

def create_values(creation_d,log,orig_imps,updated_imps):					
	date_of_change = datetime.datetime.fromtimestamp(log['timestamp'])
	start_date = parser.parse(log['attributes']['start_date'])
	end_date = parser.parse(log['attributes']['end_date'])

	cpm = log['attributes']['cpm']
	campaign_name = log['attributes']['name']
	io = log['attributes']['insertion_order_id']

	duration = end_date - start_date

	return [
		io,
		campaign_name,
		cpm,
		orig_imps,
		updated_imps,
		str(date_of_change)[:10]]

def create_revision_log(all_insertion_orders,logs):
	revision_log = [[
			'IO',
			'campaign',
			'bid cpm',
			'original imps',
			'updated imps',
			'date of change']]

	for io in logs:
		creation_d = {}

		for log in io.json(): #store info on creation logs
			if log['action'] == 'create':
				try:
					creation_d.update({log['attributes']['id']:log['attributes']['budget_impressions']})
				except:
					continue

		for log in io.json(): #look for updates
			try:
				log['attributes']['insertion_order_id']
			except KeyError:
				continue
			if log['action'] == 'update':
				orig_imps = creation_d[log['attributes']['id']]
				updated_imps = log['attributes']['budget_impressions']	
				if orig_imps == updated_imps: #ignore non-impression-amended edits
					continue
				else:
					creation = create_values(creation_d,log,orig_imps,updated_imps)
					revision_log.append(creation)
				
	for log in revision_log: #replace IO ids with IO names
		for io in all_insertion_orders:
			if log[0] == io['id']:
				log.pop(0)
				log.insert(0,io['name'])
	
	return revision_log

def retrieve_logs(cookies,active_ios):
	log_url = options_prod['url'] + "/change_history/insertion_order/"
	logs = []

	for io_id in active_ios:
		log = requests.get(log_url+io_id[0],cookies=cookies)
		logs.append(log)

	return logs

def get_active_ios(start_of_active_period,all_insertion_orders):
	active_ios = []

	for io in all_insertion_orders:
		enddate = io['end_date'][:10]
		f_e = datetime.datetime.strptime(enddate,'%Y-%m-%d') #formatted_enddate
		if f_e >= start_of_active_period:
			active_ios.append([io['id']])

	return active_ios

def get_insertion_orders(cookies):
	insertion_order_url = options_prod['url'] + "/insertion_order/"
	r = requests.get(insertion_order_url,cookies=cookies)
	all_insertion_orders = r.json()

	return all_insertion_orders

def get_session_cookie(options_prod):	
	session_url = options_prod['url'] + "/session/"
	payload = options_prod['cred']
	r = requests.post(session_url, data=json.dumps(payload))

	return r.cookies

def main(start_of_active_period):
	start_of_active_period = parser.parse(start_of_active_period)
	cookies = get_session_cookie(options_prod)
	all_insertion_orders = get_insertion_orders(cookies)
	
	active_ios = get_active_ios(start_of_active_period,all_insertion_orders)
	logs = retrieve_logs(cookies,active_ios)
	revision_log = create_revision_log(all_insertion_orders,logs)

	write_to_csv(revision_log)


if __name__ == "__main__":
	main(sys.argv[1])