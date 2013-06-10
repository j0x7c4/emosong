#coding=utf-8
import json
import urllib
import operator
import math

class VSM:
	def __init__(self,url):
		query_term_list="/terms?terms.fl=text&terms.sort=index&terms.limit=-1&wt=json"
		self.url = url
		
		self.inv = {}
		
		temp_terms = {}
		f = urllib.urlopen(url+query_term_list)
		j = json.loads(f.read())
		temp_term_list = j["terms"]["text"]
		for idx in range(0,len(temp_term_list),2):
			term_text = temp_term_list[idx]
			temp_terms.update({term_text:temp_term_list[idx+1]})

		sorted_terms = sorted(temp_terms.items(), key=lambda temp_terms:temp_terms[1], reverse=True)
		self.terms = [x[0] for x in sorted_terms[0:int(len(sorted_terms)*0.1)]]
		self.df = [x[1] for x in sorted_terms[0:int(len(sorted_terms)*0.1)]]
		#print self.terms
		#print self.df
		for idx in range(len(self.terms)):
			self.inv.update({self.terms[idx]:idx})
		print "#terms = %d"%(len(self.terms))


	def get_vectors ( self, docs, tvs , start ):
		ndocs = len(docs)
		ret = []
		for idx in range(ndocs):
			emo = docs[idx]["emotion"]
			tv = {}
			doc_id = int(docs[idx]["id"])
			title = docs[idx]["title"]
			
			for term_idx in range(0,len(tvs[2*idx+1][3]),2):
				term_text = tvs[2*idx+1][3][term_idx]
				if term_text in self.inv:
					term_id = int(self.inv[term_text])
					tf = tvs[2*idx+1][3][term_idx+1][1]
					df = tvs[2*idx+1][3][term_idx+1][3]
					tv.update({term_id:tf/float(str(df))})
			sorted_tids = sorted(tv.keys())
			w = [ tv[i] for i in sorted_tids]

			ret.append({"id":doc_id,"title":title,"label":emo,"tids":sorted_tids,"weights":w})
			
		return ret
			
	def get_vector ( self, content ):
		query_field = "/analysis/field?wt=json&analysis.fieldvalue=%s&analysis.showmatch=true&analysis.fieldname=text" % (content)
		f = urllib.urlopen(self.url+query_field)
		j = json.loads(f.read())
		terms = j["analysis"]["field_names"]["text"]["index"][1:][0]
		tv = {}
		tf = {}

		for term in terms:
			term_text = term["text"]
			if term_text in self.inv:
				term_id = self.inv[term_text]
				if term_id in tf:
					tf[term_id]+=1
				else:
					tf[term_id]=1


		tids = sorted(tf.keys())
		w = [ tf[i]/float(self.df[i]) for i in tids ]	
		return {"tids":tids,"weights":w}

	def get_all_vectors (self):
		query_term_vector_fmt = "/tvrh/?q=[text: * ]&limit=-1&version=2.2&indent=on&tv.df=true&tv.tf=true&wt=json&tv.sorted=true&start=%d&rows=%d"
		query_term_vector=query_term_vector_fmt%(0,10)
		
		f = urllib.urlopen(self.url+query_term_vector)
		j = json.loads(f.read())
		ndocs = j["response"]["numFound"]
		nstep = 10
		docs = j["response"]["docs"]
		tvs = j["termVectors"][2:]
		
		all_vectors=[term for term in self.get_vectors(docs,tvs,0)]
		
		for start in range(nstep,ndocs,nstep):
			
			query_term_vector=query_term_vector_fmt%(start,nstep)
			f = urllib.urlopen(self.url+query_term_vector)
			j = json.loads(f.read())
			docs = j["response"]["docs"]
			tvs = j["termVectors"][2:]
			for term in self.get_vectors(docs,tvs,start):
				all_vectors.append(term)
		return all_vectors
	def get_score( self, v1,v2 ):
		N = len(v1)
		i = j = 0
		score = 0 
		nv1 = nv2 = 0
		while i<N and j<N:
			if v1['tids'][i]==v2['tids'][j]:
				score+=v1['value'][i]*v2['value'][j]
				nv1 += v1['value'][i]*v1['value'][i]
				nv2 += v2['value'][j]*v2['value'][j]
				i+=1
				j+=1
			elif v1['tids'][i]<v2['tids'][j]:
				nv1 += v1['value'][i]*v1['value'][i]
				i+=1
			else:
				nv2 += v2['value'][j]*v2['value'][j]
				j+=1

		while i<N :
			nv1 += v1['value'][i]*v1['value'][i]
			i+=1
		while j<N :
			nv2 += v2['value'][j]*v2['value'][j]
			j+=1

		return score/math.sqrt(nv1*nv2)


	def query ( self, text ):
		test_vector = self.get_vector(text)
		sample_vectors = self.get_all_vectors()
		rank = {}
		for sample in sample_vectors:
			title = sample['title'][0]
			score = self.get_score({'tids':sample['tids'],'value':sample['weights']},
				{'tids':test_vector['tids'],'value':test_vector['weights']})
			rank.update({title:score})

		sorted_rank_keys = sorted(rank.items(), key=lambda rank:rank[1], reverse=True)
		sorted_rank = {}
		for key in sorted_rank_keys[0:10]:
			sorted_rank.update({key[0]:key[1]})
		return sorted_rank


	
	


if __name__=="__main__":

	url="http://140.112.91.193:12011/solr"
	vsm = VSM(url)
	text = """作詞：天天作曲：李偲菘我翻開書　突然變立體飛了進去　穿越過時空滿街人群戴上了耳機　頻道的聲音震撼了我　這就是海頓四季交響曲古老的奏鳴又有個人　頭髮捲又長他是牛頓　蘋果落地是地球吸引千年的定律　他要去挑釁不斷證明　顛覆後成了地球的引力千萬分機率　我經歷了奇境　還交錯了古今瞬間　飛起　我的心　隨海頓牛頓遲鈍的自己海頓的旋律　牛頓的引力地心的重音　無法去抗拒跳回出發地　書本在手裡興奮和莫名　無言的動力海頓的奏鳴　牛頓的發明轉載來自 ※ Mojim.com　魔鏡歌詞網 遲鈍的自己　還有股衝勁海頓的旋律　牛頓的引力遲鈍的自己　穿越了古今　我在天上飛我問海頓　音樂太著迷他點了頭　卻偏要牛頓回答奧秘我站起身來　再穿牆過壁憑著念力　擠到另一個不同的世紀只要你願意　愛有穿透力　古今能交集我們的旋律　海頓的旋律　牛頓的引力地心的重音　無法去抗拒跳回出發地　書本在手裡興奮和莫名　無言的動力海頓的奏鳴　牛頓的發明遲鈍的自己　還有股衝勁海頓的旋律　牛頓的引力遲鈍的自己　穿越了古今我在天上飛　天上飛　天上飛"""
	rank = vsm.query(text)
	print rank


	