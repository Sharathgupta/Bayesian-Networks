#!/usr/bin/python

import sys
import copy
import itertools
from compiler.ast import flatten
from collections import OrderedDict
from decimal import Decimal

fp = open(sys.argv[-1],'r')
line = fp.readlines()
fp2 = open("output.txt", "w")
#parse till "******"
i = 0
main_list = []
while (line[i].strip() != "******"):
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
		if len(xy) < 2:
			xy.append("")
		dict_value.append(xy)

	for eachb in b:
		xy1 = eachb.split("=")
		dict_value2.append(xy1)

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
	internal_dict["decision"] = 0
	for each_value in temp[1:]:
		if parent:
			index = each_value.find(" ")
			prob_val = each_value[:index]
			prob_type = each_value[index+1:].replace(" ", "")
			internal_dict2[prob_type] = prob_val
			internal_dict['cond_prob'] = internal_dict2
			internal_dict['abs_prob'] = ''
		else:
			if each_value.strip() != "decision":
				internal_dict['abs_prob'] = each_value.strip()
			else:
				internal_dict['abs_prob'] = 1
				internal_dict["decision"] = 1
			internal_dict['cond_prob'] = {}
	return key.strip(), internal_dict

while(i < len(line)):
	temp = []
	while i < len(line) and line[i].strip() != "***":
		if line[i].strip() != "******":
			temp.append(line[i].strip())
			i = i + 1
		elif line[i].strip() == "******":
			break
	key, dicti = network_build(temp)
	net_dict[key] = dicti
	if i < len(line) and line[i].strip() == "******":
		break
	i = i + 1

utility_list = []
utility_dict = {}
i = i + 1
while(i < len(line)):
	utility_list.append(line[i].strip())
	i = i + 1
if utility_list:
	u_key, u_dict = network_build(utility_list)
	utility_dict[u_key] = u_dict


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


def get_value(y, lists):
	if net_dict[y]['decision'] == 1:
		return 1.0
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
	signs = ['+', '-']
	for count in itertools.combinations_with_replacement(signs, num):
		for inner_count in itertools.permutations(count):
			pset.add(inner_count)
	output = list(pset)
	return output

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
	for index in range(len(permutations)):
		x = 0
		for each_X in X_dict.keys():
			ex_dict[each_X] = permutations[index][x]
			x = x + 1
		partial = enumerate_all(l, ex_dict)
		qx.append(partial)
	output =  qe/sum(qx)
	return output

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
			value2 = enumerate_all(svars[1:], e_dict)
			probs.append(value * value2)
		res = sum(probs)
	else:
		value = get_value(Y, e_dict)
		res = value * enumerate_all(svars[1:], e)

	return res

def EU_ask(X, E):
	
	E = flatten(E)
	E_dict = {}
	new = OrderedDict()
	for i in range(0, len(E), 2):
		E_dict[E[i]] = E[i+1]

	for each in utility_dict['utility']['parent']:
		new[each] = ""
	for each in E_dict.keys():
		if each not in new.keys():
			pass
		elif each in new.keys():
			new[each] = E_dict[each]
	for each in X:
		if each in E_dict.keys():
			X.remove(each)
	perms = permutation_generate(len(X))
	total = 0
	for each_perm in perms:
		x_dict = dict()
		i = 0
		new_dict = {}
		new_dict['given'] = E_dict
		for index in range(len(X)):
			new[X[index]] = each_perm[i]
			x_dict[X[index]] = each_perm[i]
			i = i + 1

		new_dict['query'] = x_dict
		res = enumeration_ask(new_dict)
		signs = ""
		for each in new.keys():
			signs = signs + new[each]
		total = total + res * float(utility_dict['utility']['cond_prob'][signs])
	return total

def MEU_ask(query):

	X = []
	Y= []
	Y = query['query']
	E = []
	E = query['given']
	X = Y + E
	x_dict = OrderedDict()
	real_X = copy.deepcopy(utility_dict['utility']['parent'])
	X = flatten(X)
	j = 0
	new_li = []
	for i in range(0, len(X), 2):
		x_dict[X[i]] = X[i+1]
	for each in x_dict:
		if x_dict[each] != "":
			pass
		elif x_dict[each] == "":
			j = j + 1
			new_li.append(each)
	perms = permutation_generate(j)
	output = {}
	k = 0
	for each in perms:
		k = 0
		for eachx in x_dict.keys():
			if eachx not in new_li:
				pass
			elif eachx in new_li:
				x_dict[eachx] = each[k]
				k = k + 1
		xitems = x_dict.items()
		res = EU_ask(real_X, xitems)
		key=""
		for k in x_dict.keys():
			if k not in new_li:
				pass
			else:
				key=key+x_dict[k]
				key = key + " "
		output[res]=key
	max_value=max(output.keys())
	sign=output[max_value]
	return sign, max_value

for each_query in main_list:
	if each_query['type'] == "P":
		P_answer = enumeration_ask(each_query)
		P_answer = str(Decimal(str(P_answer)).quantize(Decimal('.01'))) + '\n'
		fp2.write(P_answer)
	if each_query['type'] == "EU":
		Y = copy.deepcopy(utility_dict['utility']['parent'])
		E = []
		E = each_query['given']
		X = []
		X = each_query['query']
		E.append(X)
		EU_answer = EU_ask(Y, E)
		EU_answer = str(int(round(EU_answer)))+"\n"
		fp2.write(EU_answer)
	if each_query['type'] == "MEU":
		sign, value = MEU_ask(each_query)		
		MEU_answer = str(sign)+str(int(round(value)))+"\n"
		fp2.write(MEU_answer)
