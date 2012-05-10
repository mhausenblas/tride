# Tride - turning tabular data into entities

Two widely used and popular data formats on the Web are [CSV](http://tools.ietf.org/html/rfc4180 "RFC 4180 - Common Format and MIME Type for Comma-Separated Values (CSV) Files") and [JSON](http://tools.ietf.org/html/rfc4627 "RFC 4627 - The application/json Media Type for JavaScript Object Notation (JSON)"). While data in CSV is of tabular-shaped, record-oriented nature, JSON represents the data in a tree-shaped, entity-centric way. **Tride** takes tabular data in the form of CSV files as an input and turns it into a set of inter-connected JSON documents enabling a fine-grained data access in an hypermedia-oriented fashion. 

Let's have a look at very simple example. The following CSV (a simplified version of `test/people.csv`):

	ID,last-name,first-name
	1,Capadisli,Sarven
	2,Cyganiak,Richard
	3,Dabrowska,Anna
	4,Hausenblas,Michael
	5,Iqbal,Aftab

can be mapped to a set of JSON documents, each of which looks like the following:

	http://example.org/people/ba8a41bd-9a94-11e1-bcab-3c07546a7679.json

	{
		'fname' : 'Sarven',
		'lname' : 'Capadisli'
	}

In order to map the CSV file to JSON documents, Tride needs a mapping file that declares what and how to map:

	{
		"input" : [
				{ "name" : "people", "src" : "people.csv" }
		],
		"map" : {
			"people" : {
				"base" : "http://example.org/people/",
				"output" : "people/",
				"with" : { "fname" : "people.first-name", "lname" : "people.last-name" }
			}
		}
	}

## Examples

In the following you'll learn how to map the content of the fields in a CSV file step-by-step. There is currently a Python implementation in the `python` directory that you can call from within the `test` directory like so:

	python ../python/tride-processor.py people-map.json

Depending on the content of the mapping file the respective directories and index files (`all.json`) that contain links to the JSON documents are generated in the `output` directory. After you've applied the mapping with the command above, change to the output-directory and launch a simple Web server to view the files in your browser or using tools such as curl:

	python -m SimpleHTTPServer

## Exposing a single CSV file

This example uses a single CSV file (`test/people.csv`) as the input. This CSV file lists people, that is their first and last names (amongst other things not relevant for now). 

`test/people.csv`:

	ID,last-name,first-name,group-id
	pe1,Capadisli,Sarven,g1
	pe2,Cyganiak,Richard,g1
	pe3,Dabrowska,Anna,g1
	pe4,Hausenblas,Michael,g1
	pe5,Iqbal,Aftab,g1
	pe6,Leggieri,Myriam,g2

The mapping file `test\people-map.json` maps three columns of the input CSV file (`ID`, `last-name`, `first-name`) to five JSON documents representing the five rows of the CSV file and in addition generates an index file (`all.json`) that links to the JSON documents:

	{
		"input" : [
				{ "name" : "people", "src" : "people.csv" }
		],
		"map" : {
			"people" : {
				"base" : "http://localhost:8000/",
				"output" : "../out/",
				"with" : { "pid" : "people.ID" , "fname" : "people.first-name", "lname" : "people.last-name" }
			}
		}
	}

Note that in the `input` section the data sources are declared. With `name` we're able to refer to them later in the mapping. Each entry in the `map` sections declares how the columns of the CSV file are to be mapped to key-value pairs in the resulting JSON document. You do not need to expose all columns if you don't want to. So, after executing the following command in the `test` directory:

	python ../python/tride-processor.py people-map.json

you should find files such as the following in the `out` directory:

	 3f2f60e8-9a9d-11e1-b7bb-3c07546a7679.json
	 3f36c5f3-9a9d-11e1-8106-3c07546a7679.json
	 3f36c299-9a9d-11e1-a508-3c07546a7679.json
	 3f36c482-9a9d-11e1-b753-3c07546a7679.json
	 3f36c751-9a9d-11e1-ac08-3c07546a7679.json
	 3f36c926-9a9d-11e1-9eec-3c07546a7679.json
	 all.json

where each of the individual JSON documents looks like:

	{
		"pid": "pe1", 
		"fname": "Sarven",
		"lname": "Capadisli",
		"all": "http://localhost:8000/all.json"
	}

Each JSON document contains a link to its container represented by the index file `all.json` which in turn points to the individual JSON documents like so:

	[
	"http://localhost:8000/3f2f60e8-9a9d-11e1-b7bb-3c07546a7679.json",
	"http://localhost:8000/3f36c299-9a9d-11e1-a508-3c07546a7679.json",
	"http://localhost:8000/3f36c482-9a9d-11e1-b753-3c07546a7679.json",
	"http://localhost:8000/3f36c5f3-9a9d-11e1-8106-3c07546a7679.json",
	"http://localhost:8000/3f36c751-9a9d-11e1-ac08-3c07546a7679.json",
	"http://localhost:8000/3f36c926-9a9d-11e1-9eec-3c07546a7679.json"
	]

Now, that was easy, or? Let's see how we can connect two CSV files in the next step.

## Exposing two CSV files with single references

This example uses two CSV files (`test/people.csv`, `test/group.csv`) as the input. In addition to the people listing we've already seen in the previous example, we have (research) groups listed in the latter CSV file.

`test/people.csv`:

	ID,last-name,first-name,group-id
	pe1,Capadisli,Sarven,g1
	pe2,Cyganiak,Richard,g1
	pe3,Dabrowska,Anna,g1
	pe4,Hausenblas,Michael,g1
	pe5,Iqbal,Aftab,g1
	pe6,Leggieri,Myriam,g2

`test/group.csv`:

	ID,title,homepage
	g1,LiDRC,http://linkeddata.deri.ie/
	g2,USS,http://soso.deri.ie/

Assuming each person can only be a member of a single group we use the mapping file `test\group-map.json` to expose both the people and their group membership:

	{
		"input" : [
				{ "name" : "people", "src" : "people.csv" },
				{ "name" : "group", "src" : "group.csv" }
		],
		"map" : {
			"people" : {
				"base" : "http://localhost:8000/people/",
				"output" : "../out/people/",
				"with" : { 
					"fname" : "people.first-name", 
					"lname" : "people.last-name",
					"member" : "link:people.group-id to:group.ID"
				}
			},
			"group" : {
				"base" : "http://localhost:8000/group/",
				"output" : "../out/group/",
				"with" : {
					"title" : "group.title",
					"homepage" : "group.homepage",
					"members" : "where:people.group-id=group.ID link:group.ID to:people.ID"
				}
			}
		}
	}

Note that now the content of `member` is not a simple value anymore but a link to the respective group the person is a member of (ignore the `members` content for now, this will be explained in the next example). After executing the following command in the `test` directory:

	python ../python/tride-processor.py group-map.json

you should find directories and files such as the following in the `out` directory:

	group/
	 140d619c-9a9f-11e1-a5bd-3c07546a7679.json
	 140d635c-9a9f-11e1-b668-3c07546a7679.json
	 all.json
	people/
	 140d5b47-9a9f-11e1-a6ee-3c07546a7679.json
	 140d5cc2-9a9f-11e1-a5e8-3c07546a7679.json
	 140d56ab-9a9f-11e1-907f-3c07546a7679.json
	 140d59e8-9a9f-11e1-aa6e-3c07546a7679.json
	 140d5880-9a9f-11e1-a4c7-3c07546a7679.json
	 140797ee-9a9f-11e1-b3b7-3c07546a7679.json
	 all.json

where each of the individual JSON documents in the `people` directory looks like:

	{
		"lname": "Capadisli", 
		"member": "http://localhost:8000/group/140d619c-9a9f-11e1-a5bd-3c07546a7679.json",
		"all": "http://localhost:8000/people/all.json",
		"fname": "Sarven"
	}

## Exposing two CSV files with mutual references

This example is a continuation of the previous example. We're still dealing with two data sources (group, people) and now look into how to expose one-to-many connections. While each person can only be member of one group, in the opposite direction, each group can have multiple members. This is expressed in the mapping file through the following entry:

	"members" : "where:people.group-id=group.ID link:group.ID to:people.ID"

Essentially this tells the processor to create a list of entries in the group output with links to the respective person JSON document. Hence, a single JSON document in the `out\group` directory looks like the following:

	{
	"all": "http://localhost:8000/group/all.json", 
	"homepage": "http://linkeddata.deri.ie/", 
	"members": [
		"http://localhost:8000/people/140797ee-9a9f-11e1-b3b7-3c07546a7679.json",
		"http://localhost:8000/people/140d56ab-9a9f-11e1-907f-3c07546a7679.json",
		"http://localhost:8000/people/140d5880-9a9f-11e1-a4c7-3c07546a7679.json",
		"http://localhost:8000/people/140d59e8-9a9f-11e1-aa6e-3c07546a7679.json",
		"http://localhost:8000/people/140d5b47-9a9f-11e1-a6ee-3c07546a7679.json"
	],
	"title": "LiDRC"
	}

## Exposing CSV files with separate join table

This example uses three CSV files (`test/people.csv`, `test/project.csv`, `test/people-project.csv`) as the input. The former two list people (as above) and projects (with their title, etc.) and the last one is a CSV file that states which person participates in which project.

`test/people.csv`:

	ID,last-name,first-name,group-id
	pe1,Capadisli,Sarven,g1
	pe2,Cyganiak,Richard,g1
	pe3,Dabrowska,Anna,g1
	pe4,Hausenblas,Michael,g1
	pe5,Iqbal,Aftab,g1
	pe6,Leggieri,Myriam,g2

`test/project.csv`:

	ID,project-title,project-acronym,homepage
	pr1,LOD Around-The-Clock,LATC,http://latc-project.eu/
	pr2,D2R RDB2RDF,D2R,http://d2rq.org/

`test/people-project.csv`:

	project-id,person-id
	pr1,pe1
	pr1,pe2
	pr1,pe3
	pr1,pe4
	pr2,pe2
	pr2,pe5

This is also known as many-to-many connection as one person might participate in more than one project and one project potentially has many contributors. The mapping file `test\project-map.json` exposes both the people and projects and links from projects to people:

	{
		"input" : [
				{ "name" : "people", "src" : "people.csv" },
				{ "name" : "project", "src" : "project.csv" },
				{ "name" : "p2p", "src" : "people-project.csv" }
		],
		"map" : {
			"people" : {
				"base" : "http://localhost:8000/people/",
				"output" : "../out/people/",
				"with" : { "pid" : "people.ID" , "fname" : "people.first-name", "lname" : "people.last-name" }
			},
			"project" : {
				"base" : "http://localhost:8000/project/",
				"output" : "../out/project/",
				"with" : { 
					"proid" : "project.ID" ,
					"title" : "project.project-title",
					"acronym" : "project.project-acronym" ,
					"participant" : "where:p2p.project-id=project.ID link:p2p.person-id to:people.ID"
				}
			}
		}
	}

Note that we can still use the `where` to link from the projects to the people. The only difference to the previous example is that the information about the connections comes from a separate CSV file (`test/people-project.csv`) which, due to its structure, allows to express multiple connections in both directions:

	"participant" : "where:p2p.project-id=project.ID link:p2p.person-id to:people.ID"

After executing the following command in the `test` directory:

	python ../python/tride-processor.py project-map.json

you should find directories and files such as the following in the `out` directory:

	people/
	 1d65b3e1-9aa2-11e1-8dd5-3c07546a7679.json
	 1d66ac82-9aa2-11e1-a30e-3c07546a7679.json
	 1d66ad7d-9aa2-11e1-b3ec-3c07546a7679.json
	 1d66ae38-9aa2-11e1-9cfb-3c07546a7679.json
	 1d66aef8-9aa2-11e1-8985-3c07546a7679.json
	 1d66afc0-9aa2-11e1-85fc-3c07546a7679.json
	 all.json
	project/
	 1d66b247-9aa2-11e1-99e1-3c07546a7679.json
	 1d66b326-9aa2-11e1-92b7-3c07546a7679.json
	 all.json

where each of the individual JSON documents in the `project` directory looks like:

	{
		"acronym": "LATC",
		"all": "http://localhost:8000/project/all.json",
		"proid": "pr1",
		"participant": [
			"http://localhost:8000/people/1d65b3e1-9aa2-11e1-8dd5-3c07546a7679.json",
			"http://localhost:8000/people/1d66ac82-9aa2-11e1-a30e-3c07546a7679.json", 
			"http://localhost:8000/people/1d66ad7d-9aa2-11e1-b3ec-3c07546a7679.json",
			"http://localhost:8000/people/1d66ae38-9aa2-11e1-9cfb-3c07546a7679.json"
		],
		"title": "LOD Around-The-Clock"
	}

A more advanced version of the mapping file is `test\project-map-alt.json`, which adds back-links from people to projects resulting in JSON document in the `people` directory as follows:

	{
		"lname": "Cyganiak",
		"all": "http://localhost:8000/people/all.json",
		"contribute": [
			"http://localhost:8000/project/41230980-9aa3-11e1-9324-3c07546a7679.json",
			"http://localhost:8000/project/41230bc2-9aa3-11e1-93e9-3c07546a7679.json"
		],
		"fname": "Richard"
	}

## Open issues and to dos

* JavaScript version (GDocs deployment)
* Dynamic version (non-dump)
* Explicit specification of mapping file
* Field manipulation functions (concat, trim, etc.)

## License

This software is Public Domain.
