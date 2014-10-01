#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi			# CGI
import cgitb		# CGI- info de debug en cas de plantage
import urlparse
import urllib
import urllib2
import datetime
import os
import sys
import json
import PyJSONSerialization

BRANCHES_STATUS     = "branches_status.json" # JSON status of branches
MAX_BRANCH_PER_PAGE = 10

CSS = '''
html { 
  height: 100%;
}

* {
  margin: 0;
  padding: 0;
  background-color: #000000;
  font-color: #FFFFFF;
  color: #FFFFFF;
}

#titre {
  font-size: 4em;
  font-family: "Arial", Arial, sans-serif;
  text-align: center;
}

table {
  margin: 10px 0 30px 0;
}

table tr th, table tr td {
  background: #554444;
  color: #FFF;
  border-radius: 10px;
  padding: 7px 4px;
  font-family: "Arial", Arial, sans-serif;
  font-size: 2em;
  text-align: left;
}

table tr th {
  text-align: center;
}
  
table tr td {
  background: #444444;
}

table .branche {
  font-size: 3em;
}

table .SUCCESS { 
  background: #00BB00;
}

table .FAILURE {
  background: #BB0000;
}

a {
  text-decoration: none;
}'''

# Enable exception formating to HTML
cgitb.enable()

def escape(txt):
	return cgi.escape(txt, True)

# Variant of a branch  - Allow to monitor different jobs 
# 1 variant = 1 column shown on the display
class VariantStatus:
	def __init__(self):
		self.status = None
		self.url    = None

	@classmethod
	def create(cls, status, url):
		retour = cls()
		retour.status = status
		retour.url    = url
		return retour

# Status of a branch
class BranchStatus:
	def __init__(self):
		self.date_maj = None
		self.variants = dict()
		
	def set_result (self, variant, status, url):
		self.variants[variant] = VariantStatus.create(status, url)
		self.date_maj = datetime.datetime.now().isoformat()


#########################################################################################################################
#
#          Main


status = None
branch = None

# Read parameters passed by the command line (CGI)
try:
	get_params = urlparse.parse_qs(os.environ['QUERY_STRING'])
	variant  = get_params['variant'][0]
except:
	variant = None

# Read (if available) json data in the body of the request
try:
	myjson  = json.load(sys.stdin);
	status  = str(myjson["build"]["status"])
	branch = str(myjson["build"]["scm"]["branch"])
	url     = str(myjson["build"]["full_url"])
except:
	# no data, this is not a jenkins request
	pass


# Chargement des données à partir du fichier
try:
	with open(BRANCHES_STATUS, "r") as f:
		branch_list = PyJSONSerialization.load(f.read(), globals())
except:
	branch_list = dict()

# Mise à jour des informations si elles sont fournies
# (invoqué par Jenkins)
if branch and variant and status :
	if branch not in branch_list:
		branch_list[branch] = BranchStatus()
		
	branch_list[branch].set_result(variant, status, url)

	# Sauvegarde le résultat
	with open(BRANCHES_STATUS, "w") as f:
		f.write (PyJSONSerialization.dump(branch_list))

# Présente le résultat
print '''Content-type: text/html;charset=utf-8'

<html>
<head>
  <title>Etat des branches</title>
  <meta name="description" content="Etat des branches de l'intégration continue" />
  <meta name="keywords"    content="Jenkins, Navineo, Embarqué" />
  <style>''' + CSS + '''
  </style>
</head>
'''

# ###############################################################
# Build a table showing :
# - Branch name
# - status of all the variant of this branch

# Iterate through branch list to extract the list of variants
variant_list = []
for branch_name, branch_status in branch_list.iteritems():
	for variant_name, variants in branch_status.variants.iteritems():
		if variant_name not in variant_list :
			variant_list.append(variant_name)

# Header of the table
print '''<div id="titre">Branch Status</div>'''
print '''<table>'''
print '''<tr><th/>'''
for variant in variant_list:
	print '''<th class="titre">''' + variant + '''</td>'''
print '''</tr>'''

# Iterate through branches sorted by date of the last update
cpt = 0
for (branch_name, branch_status) in sorted(branch_list.items(), key=lambda(k,v): v.date_maj, reverse=True):
	# Remove "origin/" (it's not the interesting part)
	branch_name = branch_name.replace("origin/", "")
	print '''<tr><td class="branche">''' + branch_name + '''</td>'''
	
	# Add a column for each variant
	for variant in variant_list:
		try:
			status = branch_status.variants[variant].status
			url    = branch_status.variants[variant].url
			print '''<td class="''' + status + '''"><a class="''' + status + '''" href="''' + url + '''">''' + status + '''</a></td>'''
		except KeyError:
			# The variant doen't exists for this branch
			print '''<td/>'''

	print '''</tr>'''
	cpt += 1
	if cpt > MAX_BRANCH_PER_PAGE:
		# Stop when whe reach the maximum number of branch to display
		break
	
print '''</table>
</html>'''
