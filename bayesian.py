#!/usr/bin/python

import sys

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
	dictionary['given'] = dict_value2
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
			prob_type = each_value[index+1:]
			internal_dict2[prob_type] = prob_val
			internal_dict['cond_prob'] = internal_dict2
			internal_dict['abs_prob'] = ''
		else:
			internal_dict['abs_prob'] = each_value.strip()
			internal_dict['cond_prob'] = each_value.strip()
	net_dict[key] = internal_dict


while(i < len(line) and line[i].strip() != "******"):
	temp = []
	while i < len(line) and line[i].strip() != "***":
		temp.append(line[i].strip())
		i = i + 1
	network_build(temp)
	i = i + 1

print net_dict
