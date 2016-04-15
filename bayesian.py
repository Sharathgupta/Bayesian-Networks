#!/usr/bin/python

import sys
import copy
import itertools

fp = open(sys.argv[-1],'r')
line = fp.readlines()

#parse till "******"
i = 0
main_list = []
while (line[i].strip() != "******"):
	#print line[i]
	line[i] = line[i].replace(" ", "").strip()
	bracket1 = line[i].find('(')
	bracket2 = line[i].find(')')
	query_type = line[i][:bracket1]
	x = line[i][bracket1+1:bracket2]
	pipe = x.find('|')
	
	if pipe != -1:
		queries = x[:pipe]	
		given = x[pipe+1:]
	else:
		queries = x
		given = ""
	dict_value = []
	dict_value2 = []
	a = queries.split(',')	
	b = given.split(',')
	for eacha in a:
		xy = eacha.split("=")
		dict_value.append(xy)

	for eachb in b:
		xy = eachb.split("=")
		dict_value2.append(xy)
	dictionary = {}
	dictionary['query'] = dict_value
	dictionary['type'] = query_type
	if pipe != -1:
		dictionary['given'] = dict_value2
	else:
		dictionary['given'] = []
	main_list.append(dictionary)
	i = i + 1

i = i + 1
j = 0

net_dict = {}

def network_build(temp):
	i = 0
	key_index = temp[i].find("|")
	if key_index != -1:
		key = temp[i][:key_index]
		parent = temp[i][key_index+1:]
		parent = parent.strip().split(" ")
	else:
		key = temp[i]
		parent = []
	internal_dict = {}
	internal_dict2 = {}
	internal_dict["parent"] = parent
	for each_value in temp[1:]:
		if parent:
			index = each_value.find(" ")
			prob_val = each_value[:index]
			prob_type = each_value[index+1:].replace(" ", "")
			internal_dict2[prob_type] = prob_val
			internal_dict['cond_prob'] = internal_dict2
			internal_dict['abs_prob'] = ''
		else:
			internal_dict['abs_prob'] = each_value.strip()
			internal_dict['cond_prob'] = {}
	net_dict[key.strip()] = internal_dict


while(i < len(line)):
	temp = []
	while i < len(line) and line[i].strip() != "***":
		if line[i].strip() == "******":
			break
		temp.append(line[i].strip())
		i = i + 1
	network_build(temp)
	i = i + 1

#topological sorting
variables = list(net_dict.keys())
variables.sort()
s = set()   # used to mark variables
l = []
while len(s) < len(variables):
	for v in variables:
		if v not in s and all(x in s for x in net_dict[v]['parent']):
			s.add(v)
			l.append(v)

print "network_build: ", net_dict
print
print "Query list: ", main_list
print
print "SORTED VARS: ", l

def get_value(y, lists):
	if net_dict[y]['abs_prob'] == "":
		all_parents = ""
		for parent in net_dict[y]['parent']:
			all_parents = all_parents + lists[parent]
		prob_value = float(net_dict[y]['cond_prob'][all_parents])
		if lists[y] == "-":
			return 1 - prob_value
		else:
			return prob_value
	else:
		prob_value = float(net_dict[y]['abs_prob'])
		if lists[y] == "+":
			return prob_value
		else:
			return (1 - prob_value)

def permutation_generate(num):
	pset = set()
	for count in itertools.combinations_with_replacement(['+', '-'], num):
		for inner_count in itertools.permutations(count):
			pset.add(inner_count)
	return list(pset)

def enumeration_ask(query):
	X = query["query"]
	e = query["given"]
	bn = copy.deepcopy(l)	
	X_dict = {}
	e_dict = {}
	ex_dict = {}
	X_dict = dict(X)
	if e:
		e_dict = dict(e)
	ex_dict = dict(e_dict)
	ex_dict.update(X_dict)
	qx = []
	qe = enumerate_all(l, ex_dict)
	
	permutations = permutation_generate(len(X_dict))
	
	for each_perm in permutations:
		x = 0
		for each_X in X_dict.keys():
			ex_dict[each_X] = each_perm[x]
			x = x + 1
		qx.append(enumerate_all(l, ex_dict))
	return qe/sum(qx)

def enumerate_all(svars, e):
	if len(svars) == 0:
		return 1.0
	Y = svars[0]
	res = 1.0
	e_dict = dict(e)
	probs = []
	if Y not in e:
		for value in ['+', '-']:
			e_dict[Y] = value
			value = get_value(Y, e_dict)
			probs.append(value * enumerate_all(svars[1:], e_dict))
		res = sum(probs)
	else:
		value = get_value(Y, e_dict)
		res = value * enumerate_all(svars[1:], e)

	return res

for each_query in main_list:
	print enumeration_ask(each_query)
