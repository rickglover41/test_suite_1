def flo_finance(staff_rate,agency_rate,rn_need):
	hours_replaced = rn_need*1872*3
	agency_staff_diff = agency_rate-staff_rate
	agency_cost = hours_replaced*agency_staff_diff
	flo_costs = rn_need*50000
	savings = agency_cost-flo_costs
	return savings

