#coding=utf-8
import solr
import sys

if __name__ == "__main__":
	if len(sys.argv)>2:
		dir_path = sys.argv[1]
		list_file = sys.argv[2]

		s = solr.SolrConnection('http://140.112.91.193:12011/solr/',debug=True)
		with open(list_file) as fin:
			for line in fin.readlines():
				print line
				tmp = line.strip().split(':')
				sid = tmp[0]
				tmp = tmp[1].split(' ')
				label = tmp[0]
				title = tmp[1]
				content = open("%s/%s"%(dir_path,sid)).read()
				#print label
				s.add(id=sid, title=unicode(title,'utf-8'), content=unicode(content,'utf-8'), emotion=label)
				s.commit()
