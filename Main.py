from Riot import RiotAPI

def main():
	API = RiotAPI('9cbaeb76-ef0b-4549-b7b3-29d82cdf3acf')                             # The RiotAPI Class makes a call to the api.pvp.net servers 
	all_abilities = []                                                       		  # with the api_key given as input 
	r = API.get_all_abilities()
	data = r['data']                                                                  # Each key in data is a champion, within each champion is a multitude of data                                                      
	for key in data:
		first_spell = r['data'][key]['spells'][0]					                  # Extract the data for each of the four abilities that every champion posses
		second_spell = r['data'][key]['spells'][1] 
		third_spell = r['data'][key]['spells'][2]
		fourth_spell = r['data'][key]['spells'][3]

		first_spell_name = first_spell['name']
		second_spell_name = second_spell['name']
		third_spell_name = third_spell['name']
		fourth_spell_name = fourth_spell['name']

		first_spell_adjusted_cost = calculate_cost(first_spell)                       # calculate_cost calculates the resource cost of each ability, adjusts for                         
		second_spell_adjusted_cost = calculate_cost(second_spell)					  # different resource types(e.g. Mana, Energy, Health), and calculates the
		third_spell_adjusted_cost = calculate_cost(third_spell)                       # efficiency of that resource usage.
		fourth_spell_adjusted_cost = calculate_cost(fourth_spell)

		first_spell_coefficient = calculate_coefficient(first_spell)				  # calculate_coefficient calculates the scaling coefficient for each ability
		second_spell_coefficient = calculate_coefficient(second_spell)				  # (e.g. 60% AP scaling) and determines the efficiency of that
		third_spell_coefficient = calculate_coefficient(third_spell)                  # coefficient
		fourth_spell_coefficient = calculate_coefficient(fourth_spell)

		first_spell_baseDamage = calculate_baseDamage(first_spell)					  # calculate_baseDamage calculates the base damage of each ability, then 
		second_spell_baseDamage = calculate_baseDamage(second_spell)                  # calculates how efficient an ability with that base damage is
		third_spell_baseDamage = calculate_baseDamage(third_spell)
		fourth_spell_baseDamage = calculate_baseDamage(fourth_spell)
                                                                                      # Total efficiency index is calculated by summing all previous efficiency 
                                                                                      # indices
		first_spell_efficiency = first_spell_adjusted_cost + first_spell_baseDamage + coefficient_adjustment(first_spell_coefficient)
		second_spell_efficiency = second_spell_adjusted_cost + second_spell_baseDamage + coefficient_adjustment(second_spell_coefficient)
		third_spell_efficiency = third_spell_adjusted_cost + third_spell_baseDamage + coefficient_adjustment(third_spell_coefficient)
		fourth_spell_efficiency = fourth_spell_adjusted_cost + 0.33 *fourth_spell_baseDamage + coefficient_adjustment(fourth_spell_coefficient)

		first_tuple = (first_spell_efficiency, key, first_spell_name)				 # Each ability is stored as a tuple containing the efficiency of that
		second_tuple = (second_spell_efficiency, key, second_spell_name)			 # ability, the name of that ability, and the name of the champion who
		third_tuple = (third_spell_efficiency, key, third_spell_name)				 # casts that ability.
		fourth_tuple = (fourth_spell_efficiency, key, fourth_spell_name)

		if (first_spell_coefficient != -1 and first_spell_baseDamage != -1):
			all_abilities.append(first_tuple)
		if (second_spell_coefficient != -1 and second_spell_baseDamage != -1):
			all_abilities.append(second_tuple)
		if (third_spell_coefficient != -1 and third_spell_baseDamage != -1):
			all_abilities.append(third_tuple)
		if (fourth_spell_coefficient != -1 and fourth_spell_baseDamage != -1):
			all_abilities.append(fourth_tuple)

	print("Top ten most efficient champion abilities!")                             
	all_abilities.sort(reverse=True)
	for i in range (0,10):
		print("%d. Champion(Ability) = %s(%s), Efficiency Score = %d" % ((i+1), all_abilities[i][1], all_abilities[i][2], all_abilities[i][0]))

def calculate_coefficient(spell):                                                   # calculate_coefficient essentially adds together all the offensive 
	forget_spell = 10                                                               # coefficients for an ability(e.g. if an ability has 60%(0.6) AP scaling and
	coeff = 0                                                                       # 40%(0.4) AD scaling the calculated coefficient would be 0.6 + .0.4 = 1)
	if 'vars' in spell:                                                              
			spell_variables = spell['vars']
			forget_spell = 0
	if(forget_spell == 0):
		forget_spell = 1
		for var in spell_variables:
			link = var['link']
			coeff = coeff + var['coeff'][0]
			if link == "spelldamage" or link == "attackdamage" or link == "bonusattackdamage" or link =="@dynamic.abilitypower":
				forget_spell = 0
	if (forget_spell==0):
		return coeff
	else:
		return -1
def calculate_baseDamage(spell):                                                     # calculate_baseDamage returns the efficiency of the base damage of an 
	forget_spell = 1                                                                 # ability at level 1. The baseDamage is contained within the 'effect' array.  
	spell_baseDamage = 0                                                             # The code here gets alittle hairy because the ordering of elements in the 
	if 'effect' in spell:															 # effect array seems very random. The effect[0] is always null, but after 
			spell_effects = spell['effect']										     # that sometimes effect[1] is base damage, other times it is range or another  
			forget_spell = 0														 # stat. So I MacGyver'd that with a few min/max statements.
	if (forget_spell == 0):
			if spell_effects[1]:
				spell_baseDamage = spell_effects[1][0]
			if len(spell_effects) >= 3 and spell_effects[1] and spell_effects[2]:
				spell_max = max(spell_effects[1][0],spell_effects[2][0])
				spell_min = min(spell_effects[1][0],spell_effects[2][0])

				if (spell_max< 500):
					spell_baseDamage = spell_max
				elif (spell_min < 500):
					spell_baseDamage = spell_min
				elif spell_effects[3]:
					spell_baseDamage = spell_effects[3][0]
				else:
					return -1
			else:
				return -1
	else:
		return -1
	return spell_baseDamage

def calculate_cost(spell):															# Returns the efficiency of the resource usage (adjsuted for resource type)
	spell_cost = spell['cost'][0]													# for a given spell.
	spell_costType = spell['costType']
	return(costType_adjustment(spell_cost, spell_costType))

def coefficient_adjustment(coefficient):                                            # Helper method that calculates the efficiency of a given coefficienct
	if coefficient > 2:
		coefficient /= 2
	return (8*(coefficient - 1))

def costType_adjustment(cost, costType):                                            # Helper method that calculates the efficiency of resources usage, taking  
	if costType == "Mana" or costType == "Health":                                  # into account the resource type.
		return (120 - cost)
	elif costType == "Energy":
		return (150-cost)	 
	elif costType == "NoCost":
		return 100
	elif costType == "pofcurrentHealth":
		return(10*(10-cost))
	else:
		return 0

if  __name__ == "__main__":
	main()
