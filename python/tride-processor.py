""" 
 A simple tride processor.

@author: Michael Hausenblas, http://sw-app.org/mic.xhtml#i
@since: 2012-05-09
@status: init
"""
import sys, csv, os, StringIO, json, uuid


class CSVDataSource:
	def __init__(self, src):
		self.src = src
		self.header = ""
		self.rows = {}
		self.entities = {}
	
	# load CSV data from file into memory
	def load(self):
		rownum = 0
		rows = {}
		try:
			csvdata = csv.reader(open(self.src, 'rb'))
			for row in csvdata:
				if rownum == 0:
					self.header = row
				else:
					self.rows[rownum] = row
					self.entities[rownum] = str(uuid.uuid1())
				rownum += 1
		except csv.Error, e:
		    sys.exit('%s' %e)
	
	# return the value of a cell via named column and row index
	def get(self, col, row):
		r = self.rows[row]
		return r[self.header.index(col)]

	# return the ID of the entity with a given row index
	def id(self, row):
		return self.entities[row]

	# return the ID of the entity via named column and value of the cell
	def id_where(self, col, val):
		for row in self.rows:
			if self.rows[row][self.header.index(col)] == val: return self.entities[row]
		
	
class TrideProcessor:
	def __init__(self, mapfile):
		self.mapf = mapfile
		self.datasources = {}
		self.baseURI = ""
		self.init_map()
		self.result = {}
		
	def process(self):
		# go through the mappings and apply base
		for dsname, mapping in self.mappings.items():
			entities = []
			if dsname in self.datasources:
				for row in self.datasources[dsname].rows:
					entity = {}
					for fieldk, fieldv in mapping['with'].items():
						if fieldv.startswith('where:'): # process joins
							where = fieldv.split(' ')[0].split(':')[1] # after the where:
							joinsrc = where.split('=')[0].split('.')[0]
							joincol = where.split('=')[0].split('.')[1]
							refsrc = where.split('=')[1].split('.')[0]
							refcol = where.split('=')[1].split('.')[1]
							link = fieldv.split(' ')[1].split(':')[1] # after the link:
							linksrc = link.split('.')[0]
							linkcol = link.split('.')[1]
							to = fieldv.split(' ')[2].split(':')[1] # after the to:
							tosrc = to.split('.')[0]
							tocol = to.split('.')[1]
							entity[fieldk] = []
							for r in self.datasources[joinsrc].rows:
								if self.datasources[joinsrc].get(joincol, r) == self.datasources[refsrc].get(refcol, row):
									eid = self.datasources[tosrc].id_where(tocol, self.datasources[joinsrc].get(linkcol, r))
									entity[fieldk].append(self.mappings[tosrc]['base'] + eid + '.json')
						elif fieldv.startswith('link:'): # process references
							link = fieldv.split(' ')[0].split(':')[1] # after the link:
							linksrc = link.split('.')[0]
							linkcol = link.split('.')[1]
							to = fieldv.split(' ')[1].split(':')[1] # after the to:
							tosrc = to.split('.')[0]
							tocol = to.split('.')[1]
							eid = self.datasources[tosrc].id_where(tocol, self.datasources[linksrc].get(linkcol, row))
							entity[fieldk] = self.mappings[tosrc]['base'] + eid + '.json'
						else: # process simple values
							ds = fieldv.split('.')[0]
							col = fieldv.split('.')[1]
							entity[fieldk] = self.datasources[ds].get(col, row)
					entity['all'] = mapping['base'] + 'all.json'
					entities.append(entity)
				self.result[dsname] = entities
		return self.result
	
	def dump_all(self):
		for dsname in self.mappings.keys():
			self.dump(dsname)
		
	def dump(self, dsname):
		outputdir = self.mappings[dsname]['output']
		if not os.path.exists(outputdir): # make sure output dir exists
			os.makedirs(outputdir)
		allf = open(outputdir + 'all.json', 'w')
		all = []
		idx = 0
		for entity in self.result[dsname]:
			outf = open(outputdir + self.datasources[dsname].id(idx + 1) + '.json', 'w')
			outf.write(json.JSONEncoder().encode(entity))
			all.append(self.mappings[dsname]['base'] + self.datasources[dsname].id(idx + 1) + '.json')
			idx += 1
		allf.write(json.JSONEncoder().encode(all))
	
	def init_map(self):
		self.config = json.JSONDecoder().decode(open(self.mapf, 'r').read())
		for input in self.config['input']: # init data sources
			self.datasources[input['name']] = CSVDataSource(input['src'])
			self.datasources[input['name']].load()
		self.mappings = self.config['map']

def main():
	mapfile = sys.argv[1]
	tp = TrideProcessor(mapfile)
	tp.process()
	tp.dump_all()

if __name__ == '__main__':
	main()