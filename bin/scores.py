
import redis, shlex, json

HOST = "localhost"
PORT = 6379
DB = 0

BASE = 'org.srobo'

actor = redis.Redis(host=HOST, port=PORT, db=DB)

def get_parts(data):
	lexer = shlex.shlex(data, posix=True)
	lexer.whitespace_split = True
	return tuple(lexer)

def split_match(data):
	a = json.loads(data)
	res = {'mtime':a["time"],
	       'teamz0':a["teams"][0],
	       'teamz1':a["teams"][1],
	       'teamz2':a["teams"][2],
	       'teamz3':a["teams"][3]}
	return res

def game_points(score):
	total = 0
	total += int(score[2])
	total += 2*int(score[3])
	total += 5*int(score[4])
	if int(score[5]) > 1:
		total *= int(score[5])
	return total

def print_match(match):
	print('Match {0}'.format(match))
	try:
		mat = split_match(actor.lindex('{0}.matches'.format(BASE), match))
	except AttributeError:
		print('There is no expected match {0}'.format(match))
		return
	for i in range(4):
		zone = actor.hgetall('{0}.scores.match.{1}.{2}'.format(BASE,match,i))
		if zone == {}:
			print('Match data not stored for Match {0}, Zone {1}'.format(match,i))
			continue
		print('Zone {0} ({1}): {2}'.format(i,mat['teamz{0}'.format(i)],game_points([0,0,zone['trobot'],zone['tzone'],zone['tbucket'],zone['nbuckets']])))
		print('\tRobot:  {0}'.format(zone['trobot']))
		print('\tZone:   {0}'.format(zone['tzone']))
		print('\tBucket: {0}'.format(zone['tbucket']))
		print('\tNo. Buckets: {0}'.format(zone['nbuckets']))
		print('\tDisqualified: {0}'.format(zone.get('disqualified', False)))

def results():
	while True:
		str = raw_input("Enter match number: ")
		if str is '':
			return
		try:
			print_match(int(str))
			check_match(int(str))
		except ValueError:
			print("Invalid match number, please try again")

def val_entry(mod,string,ori):
	res = None
	while res is None:
		str = raw_input(string)
		if str == '':
			if mod is True:
				res = ori
			else:
				res = 0
		else:
			try:
				res = int(str)
			except ValueError:
				print('Invalid number, please try again')
	return res

def bool_entry(mod, string, ori):
	str = raw_input(string)
	if str == '' and mod is True:
		res = ori
	else:
		res = str.lower() == 'y'

	return res

def modify(mod):
	if mod is True:
		print('Modify')
	else:
		print('Score')
	while True:
		str = raw_input('Match: ')
		if str == '':
			return
		try:
			match = int(str)
		except ValueError:
			print('Invalid match number, please try again')
			continue
		if mod is True:
			print_match(match)
			z = None
			while z is None:
				str = raw_input('Zone: ')
				if str == '':
					z = -1
					continue
				try:
					z = int(str)
					if not z in range(4):
						print('Please enter a valid zone number (0-3)')
						z = None
				except ValueError:
					print('Invalid zone number, please try again')
			if z == -1:
				continue
			zone = actor.hgetall('{0}.scores.match.{1}.{2}'.format(BASE,match,z))
			if zone == {}:
				print('Match data not stored for Match {0}, Zone {1}\nPlease use score mode to enter new scores'.format(match,z))
				continue
			print('Please enter new values, leave blank for unchanged')
			match_rank(match,True)
			zone_entry(mod,match,z,zone)
			match_rank(match,False)
		else:
			zone = {'trobot':0,'tzone':0,'tbucket':0,'nbuckets':0}
			print('Please enter new values, defaults to 0 if left blank')
			tester = False
			for z in range(4):
				if(actor.exists('{0}.scores.match.{1}.{2}'.format(BASE,match,z))):
					print('Details for zone {0} exist, please use modify to change'.format(z))
					continue
				print('Zone {0}:'.format(z))
				tester |= zone_entry(mod,match,z,zone)
			if tester == True:
				match_rank(match,False)
		print_match(match)
		check_match(match)

def zone_entry(mod,match,z,zone):
	trobot = val_entry(mod,'\tRobot: ',zone['trobot'])
	tzone = val_entry(mod,'\tZone: ',zone['tzone'])
	tbucket = val_entry(mod,'\tBucket: ',zone['tbucket'])
	nbuckets = val_entry(mod,'\tNo. Buckets: ',zone['nbuckets'])
	dsq_orig = zone.get('disqualified', False)	# missing means not dsq
	dsq = bool_entry(mod, '\tDisqualify [y/N]: ', dsq_orig)
	if actor.exists('{0}.scores.match.{1}.{2}'.format(BASE,match,z)):
		if trobot == zone['trobot'] and tzone == zone['tzone'] and tbucket == zone['tbucket'] and nbuckets == zone['nbuckets'] and dsq == dsq_orig:
			return False
	data = {'trobot':trobot,'tzone':tzone,'tbucket':tbucket,'nbuckets':nbuckets,'game_points':game_points([match,z,trobot,tzone,tbucket,nbuckets])}
	data['disqualified'] = dsq
	actor.hmset('{0}.scores.match.{1}.{2}'.format(BASE,match,z),data)
	return True

def check_match(match):
	max_tokens = 20
	max_buckets = 4
	tokens = 0
	buckets = 0
	for z in range(4):
		zone = actor.hgetall('{0}.scores.match.{1}.{2}'.format(BASE,match,z))
		if zone == {}:
			continue
		tokens += int(zone['trobot'])
		tokens += int(zone['tzone'])
		tokens += int(zone['tbucket'])
		buckets += int(zone['nbuckets'])
		if int(zone['tbucket']) > 0 and int(zone['nbuckets']) == 0:
			print('WARNING! Zone {0}, Tokens are marked as being in a bucket however no buckets are in the zone'.format(z))
	if tokens > max_tokens:
		print('WARNING! Too many tokens in this match! ({0})'.format(tokens))
	if buckets > max_buckets:
		print('WARNING! Too many buckets in this match! ({0})'.format(buckets))

def calc_positions(zpoints, dsq_list):
	"""
	A function to work out the placings of zones in a game, given the game points.
	@param zpoints: a dict of zone number to game points.
	@param dsq_list: a list of zones that should be considered below last.
	@returns: a dict of position to array of zone numbers.
	"""

	pos_map = {}
	points_map = {}

	for z, p in zpoints.iteritems():
		if z in dsq_list:
			p = -1
		if not points_map.has_key(p):
			points_map[p] = []
		points_map[p].append(z)

	i = 1
	for p in sorted(points_map.keys(), reverse = True):
		pos_map[i] = points_map[p]
		i += len(points_map[p])

	return pos_map

def calc_league_points(pos_map, dsq_list):
	"""
	A function to work out the league points for each zone, given the rankings within that game.
	@param pos_map: a dict of position to array of zone numbers.
	@param dsq_list: a list of zones that shouldn't be awarded league points.
	@returns: a dict of zone number to league points.
	"""

	lpoints = {}

	for pos, zones in pos_map.iteritems():
		# remove any that are dsqaulified
		# note that we do this before working out the ties, so that any
		# dsq tie members are removed from contention
		zones = [ z for z in zones if z not in dsq_list ]
		if len(zones) == 0:
			continue

		# max points is 4, add one because pos is 1-indexed
		points = (4 + 1) - pos
		# Now that we have the value for this position if it were not a tie,
		# we need to allow for ties. In case of a tie, the available points
		# for all the places used are shared by all those thus placed.
		# Eg: three first places get 3pts each (4+3+2)/3.
		# Rather than generate a list and average it, it's quicker to just
		# do some maths using the max value and the length of the list
		points = points - ( (len(zones) - 1) / 2.0 )
		for z in zones:
			lpoints[z] = points

	# those that were dsq get 0
	for z in dsq_list:
		lpoints[z] = 0.0

	return lpoints

def get_league_points(zpoints, dsq):
	"""
	A function to work out the league points for each zone, given the game points.
	This is a thin convenience wrapper around `calc_positions` and `calc_league_points`.
	@param zpoints: a dict of zone number to game points.
	@param dsq: a list of zones that shouldn't be awarded league points.
	@returns: a dict of zone number to league points.
	"""
	pos_map = calc_positions(zpoints, dsq)
	lpoints = calc_league_points(pos_map, dsq)
	return lpoints

def match_rank(match,sub):
	zpoints, dsq = _get_zone_data(match)
	lpoints = get_league_points(zpoints, dsq)
	_store_league_points(match, sub, lpoints)

def _get_zone_data(match):
	"""
	@returns: A tuple of:
		a dict that contains the points for each zone
		a list that contains any zones that were disqualified
	"""
	zpoints = dict()
	dsq = []
	for z in range(4):
		zone = actor.hgetall('{0}.scores.match.{1}.{2}'.format(BASE,match,z))
		if zone != {}:
			zpoints['{0}'.format(z)] = game_points([match,z,zone['trobot'],zone['tzone'],zone['tbucket'],zone['nbuckets']])
			if zone.get('disqualified', None) == "True":
				dsq.append('{0}'.format(z))
		else:
			zpoints['{0}'.format(z)] = -1
	return zpoints, dsq

def _store_league_points(match, sub, lpoints):
	mat = split_match(actor.lindex('{0}.matches'.format(BASE), match))

	scored = 4
	for z, pts in lpoints.iteritems():
		if sub is True:
			pts *= -1.0
			_float_incr('{0}.scores.team.{1}'.format(BASE, mat['teamz{0}'.format(z)]), pts)
		else:
			_float_incr('{0}.scores.team.{1}'.format(BASE, mat['teamz{0}'.format(z)]), pts)
			actor.hset('{0}.scores.match.{1}.{2}'.format(BASE, match, z),'league_points', pts)

def _float_incr(key, incr):
	"""
	Increments a redis (float) key value by a given float.
	The float may be negaitve to achieve decrements.
	"""

	"""
	Currently, this is a very bad implementation, as we are unable to
	get a value inside the atomic operation.
	"""

	value = actor.get(key)
	with actor.pipeline(transaction = True) as pipe:
		try:
			fvalue = float(value)
		except TypeError:
			"it was empty, thus None"
			fvalue = 0.0

		fvalue += incr
		pipe.set(key, fvalue)
		pipe.execute()
