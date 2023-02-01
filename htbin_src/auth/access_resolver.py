
# panzerfaust

# despite large amount of code it only takes a few milliseconds per evaluation
# and it's literally instant if "fore_each" is not activated
def resolver(pth, rule, wannawrite=False):
	declared = Path(rule['rule'])
	tgt = Path(pth)

	if not tgt.is_relative_to(declared):
		return False

	if rule['for_each']['use'] != True:

		if rule['recursive'] != True and tgt.parent != declared:
			# print('not recursive')
			return False

		if wannawrite == True:
			if rule['write'] == True:
				return True
			else:
				return False

		return True

	# inside = Path(rule['for_each']['inside'])
	frh_depth = rule['for_each']['deep']

	# if not tgt.is_relative_to(declared):
	# 	return False

	if tgt == declared:
		if wannawrite == True:
			if rule['write'] == True:
				return True
			else:
				return False
		return True

	# get first parent named as requested
	last = [prt for prt in tgt.parents if prt.name == rule['for_each']['with_name'] and prt.is_relative_to(declared)]

	if tgt.name == rule['for_each']['with_name'] and tgt.parents[frh_depth] == declared:
		last.append(tgt)

	if len(last) <= 0:
		for within in range(frh_depth):
			if tgt.parents[within] == declared:
				return True
		# print('no last folder named')
		return False

	last = last[-1]

	if not last.is_relative_to(declared) or last.parents[frh_depth] != declared:
		# print('invalid parent', last.parents[frh_depth])
		return False

	if rule['recursive'] != True and tgt.parent != last and tgt != last:
		# print('not recursive')
		return False

	if wannawrite == True:
		if rule['write'] == True:
			return True
		else:
			return False

	return True



