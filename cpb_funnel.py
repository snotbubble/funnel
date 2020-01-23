# merge all visible sops from one object into another.
# useful for converting assets, FBX and Alembics.
# by c.p.brown. 2014~2018

import os

nos = []
ds = []
dp = []
tn = ""

us = hou.selectedNodes()

for i in us :
	if i.type().category().name() == "Object" :
		nos.append(i)
	tn = i.name()

c = 0

while len(nos) > c :
	for i in nos :
		subs = i.children()
		for s in subs :
			if s.type().category().name() == "Sop" : 
				if s.type().isManager() == False :
					if s.isDisplayFlagSet() == True :
						if (s in ds) != True :
							ds.append(s)
							dp.append(s.path())
			else:
				try:
					if s.isDisplayFlagSet() == True :
						nos.append(s)
				except:
					print("\tinvisible node found")
		c = (c + 1)

c = 0
if len(ds) > 0 :
	for i in ds :
		print("harvested display SOP: " + i.name())
		print("\t" + dp[c])
		c = (c + 1)
	
	try:
		co = hou.node('/obj/funneled')
		print('found existing bgeo node : ' + co.name() + ', using it...')
				
	except:
		print("bgeo node not found, creating it...")
		obj = hou.node('/obj')
		co = obj.createNode("geo", "funneled")
		xu = co.children()
		for u in xu : u.destroy()

	omcr = 0
	cvcr = 0
	xfcr = 0
	sncr = 0
	swncr = 0
	svcr = 0
	swvcr = 0
	cvncr = 0
	rfcr = 0
	bfcr = 0
	swcr = 0
	smcr = 0
	outncr = 0

	try:
		om = hou.node('/obj/funneled/merge_display_sops')
		print('object merge exists, clearing it...')
		om.parm("numobj").set(0)
	except:
		print('object merge SOP not found, creating it...')
		om = co.createNode("object_merge", "merge_display_sops")
		om.setCurrent(True)
		om.setSelected(True)
		om.setDisplayFlag(True)
		om.parm("xformtype").set(1)
		omcr = 1
					
	c = 1
	om.parm("numobj").set(len(ds))
	for i in dp :
		om.parm("objpath" + str(c)).set(i)
		c = (c + 1)
			
	try:
		xf = hou.node('/obj/funneled/xf_fix')
		print('transform fix found: ' + xf.name() + ', using it...')
		if omcr == 1 : xf.setInput(0,om)
	except:
		print('transform SOP not found, creating it...')
		xf = co.createNode('xform', 'xf_fix')
		xf.setInput(0,om)
		xfcr = 1
			
	try:
		cv = hou.node('/obj/funneled/convert_to_poly')
		print('converter found: ' + cv.name() + ', using it...')
		if xfcr == 1 : cv.setInput(0,xf)
	except:
		print('convert_to_poly SOP not found, creating it...')
		cv = co.createNode('convert', 'convert_to_poly')
		cv.setInput(0,xf)
		cvcr = 1

	try:
		sn = hou.node('/obj/funneled/set_normals')
		print('normal found: ' + sn.name() + ', using it...')
		if cvcr == 1 : sn.setInput(0,cv)
	except:
		print('normals SOP not found, creating it...')
		sn = co.createNode('normal', 'set_normals')
		sn.setInput(0,cv)
		sncr = 1        

	try:
		swn = hou.node('/obj/funneled/normals_switch')
		print('normals switcher found: ' + swn.name() + ', using it...')
		if cvcr == 1: swn.setNextInput(cv)
		if sncr == 1: swn.setNextInput(sn)    
	except:
		print('switch normals SOP not found, creating it...')
		swn = co.createNode('switch', 'normals_switch')
		swn.setNextInput(cv)
		swn.setNextInput(sn)
		swncr = 1

	try:
		sv = hou.node('/obj/funneled/set_v')
		print('normal found: ' + sv.name() + ', using it...')
		if swncr == 1 : sv.setInput(0,swn)
	except:
		print('trail SOP not found, creating it...')
		sv = co.createNode('trail', 'set_v')
		sv.parm('result').set(3)
		sv.setInput(0,swn)
		svcr = 1        

	try:
		swv = hou.node('/obj/funneled/vel_switch')
		print('velocity switcher found: ' + swv.name() + ', using it...')
		if swncr == 1: swv.setNextInput(swn)
		if svcr == 1: swv.setNextInput(sv) 
	except:
		print('switch velocity SOP not found, creating it...')
		swv = co.createNode('switch', 'vel_switch')
		swv.setNextInput(swn)
		swv.setNextInput(sv)
		swvcr = 1
			   
	try:
		cvn = hou.node('/obj/funneled/converted')
		print('Null found: ' + cvn.name() + ', using it...')
		if swvcr == 1 : cvn.setInput(0,swv)
	except:
		print('null SOP not found, creating it...')
		cvn = co.createNode('null', 'converted')
		cvn.setInput(0,swv)
		cvncr = 1
 
	try:
		rf = hou.node('/obj/funneled/save_bgeo')
		print('ROP found: ' + rf.name() + ', using it...')
	except:
		print('ROP not found, creating it...')
		rf = co.createNode('rop_geometry', 'save_bgeo')
		rf.parm('trange').set(1)
		rf.parm('sopoutput').set('$HIP/bgeo/`opname("..")`/`opname("..")`.$F.bgeo.sc')
		rf.setInput(0,cvn)
		rfcr = 1
		
	try:
		bf = hou.node('/obj/funneled/saved_bgeo')
		print('file-sop found: ' + bf.name() + ', using it...')
	except:
		print('file SOP not found, creating it...')
		bf = co.createNode('file', 'saved_bgeo')
		bf.parm('file').set('$HIP/bgeo/`opname("..")`/`opname("..")`.$F.bgeo.sc')
		bfcr = 1

	try:
		sw = hou.node('/obj/funneled/geo_switcher')
		print('geo switcher found: ' + sw.name() + ', using it...')
		if xfcr == 1: sw.setNextInput(xf)
		if cvncr == 1: sw.setNextInput(cvn)
		if bfcr == 1: sw.setNextInput(bf)        
	except:
		sw = co.createNode('switch', 'geo_switcher')
		sw.setNextInput(xf)
		sw.setNextInput(cvn)
		sw.setNextInput(bf)
		swcr = 1

	try:
		sm = hou.node('/obj/funneled/set_material')
		print('set_material found: ' + sm.name() + ', using it...')
		if swcr == 1 : sm.setInput(0,sw)
	except:
		print('material SOP not found, creating it...')
		sm = co.createNode('material', 'set_material')
		sm.parm('shop_materialpath1').set('/shop/`opname("..")`')
		sm.setInput(0,sw)
		smcr = 1          

	try:
		outn = hou.node('/obj/funneled/OUT')
		print('OUT Null found: ' + outn.name() + ', using it...')
		if smcr == 1 : outn.setInput(0,sm)
	except:
		print('OUT null SOP not found, creating it...')
		outn = co.createNode('null', 'OUT')
		outn.setInput(0,sm)
		outncr = 1        

	outn.setCurrent(True)
	outn.setSelected(True)
	outn.setDisplayFlag(True)
	outn.setRenderFlag(True)        
			
	acr = omcr + cvcr + xfcr + sncr + swncr + svcr + swvcr + cvncr + rfcr + bfcr + swcr + smcr + outncr
	if acr > 0 : co.layoutChildren()
