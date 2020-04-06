#coding = utf-8

""" EM算法分词接口，测试 """

from Desktop import pku_data
from Desktop import convi_cache
import math
""" 

1. 还不清楚具体的应用效果, 需要测试的结果作为补充说明。

"""

# EM算法 -- 分词
# Input : 联合概率分布 P(x,y),条件分布 P(y|x), 初始参数 w=(0,0,0....)^T
# 	   由于此问题是一个凸优化，初始参数任意设置均可。
# Output : 更新后的 w.
""" 已经测试通过 """
def excute_EM():
	# 输入
	# p_xi_zi : p(zi|xi)
	dict_p_xi_zi_s = pku_data.load_prob()[0]
	dict_p_xizi_s = pku_data.load_prob()[1]

	N = len(dict_p_xi_zi_s.values())		# N : 经过消除重复后的 (x,y)对的总数目
	w = [0 for i in range(N)]

	p_xi_zi_s = list(dict_p_xi_zi_s.values())
	p_xizi_s = list(dict_p_xizi_s.values())

	for i in range(N):
		w_xi_zi = w[i]
		p_xi_zi = p_xi_zi_s[i]
		p_xizi = p_xizi_s[i]
		while(True):
			delta_w_xi_zi = p_xizi/(math.e*p_xi_zi) - w_xi_zi
			# 更新 w
			w_xi_zi += delta_w_xi_zi
		
			if delta_w_xi_zi == 0:
				break
		# 替换为最佳的 w
		w[i] = w_xi_zi

	# 得出最佳的 p(z|x)
	for i in range(len(dict_p_xi_zi_s.keys())):
		k = list(dict_p_xi_zi_s.keys())[i]
		dict_p_xi_zi_s[k] = p_xi_zi_s[i]*w[i]
	#print(dict_p_xi_zi_s)

	return dict_p_xi_zi_s


""" 已经测试通过 """
def load_EM_data():
	cache_file_name = 'EM_data.cache'
	
	# 在这里，异常处理，是好的的选择吗？
	try:
		EM_data = convi_cache.load_data(cache_file_name)
	except FileNotFoundError as e:
		print(e)
		EM_data = excute_EM()
		convi_cache.dump_data(cache_file_name,EM_data)
		
	else:
		pass

	print("Got EM data !!!")
	return EM_data

# Hmm的初始位置，即每个句子第一个字符影响整个结果
# Input : 发射概率矩阵，转移概率矩阵，初始概率矩阵
# Output : 分词结果
# version---1 : 不是用 EM算法，直接从语料库统计
def hmm(dict_trans,sent,dict_p_xi_zi_s):


	N = len(sent)
	print(N)

	ans = list()	# 用于装载结果
	
	trans_rule = {'S':{'S','B'},
			'B':{'M','E'},
			'M':{'M','E'},
			'E':{'S','B'}
			}

	# 开头
	init_char = sent[0]
	e_1 = dict_p_xi_zi_s[init_char+'S']
	e_2 = dict_p_xi_zi_s[init_char+'B']
	if  e_1 > e_2:
		ans.append('S')
		init_prob = e_1
	else:
		ans.append('B')
		init_prob = e_2
	max_prob = init_prob

	for i in range(1, N):
		pre_y = ans[-1]
		char = sent[i]
		# 可能的转移
		token_1 = pre_y+'->'+list(trans_rule[pre_y])[0]
		token_2 = pre_y+'->'+list(trans_rule[pre_y])[1]
		# 可能的发射
		emit_1 = dict_p_xi_zi_s[char+list(trans_rule[pre_y])[0]]
		emit_2 = dict_p_xi_zi_s[char+list(trans_rule[pre_y])[1]]
		
		prob_1 = dict_trans[token_1] * emit_1
		prob_2 = dict_trans[token_2] * emit_2
		if prob_1 > prob_2:
			max_prob *= prob_1
			ans.append(list(trans_rule[pre_y])[0])
		else:
			max_prob *= prob_2
			ans.append(list(trans_rule[pre_y])[1])
		
	seg = change_ans(sent,ans)
	return seg


# 改变 SBME序列为 [我，爱，北京，天安门]这样的形式
""" 已经测试通过 """
def change_ans(sent,ans):
	l_seg_pos = list()		# 装载分词结果索引，
	pos = list()			# 中转站
	for i in range(len(ans)):
		e = ans[i]
		if e == 'S': 
			pos.append(i)
			l_seg_pos.append(pos)
			pos = list()
		elif e == 'E':
			pos.append(i)
			l_seg_pos.append(pos)
			pos = list()
		else:
			pos.append(i)
			if i == len(ans)-1:
				l_seg_pos.append(pos)

	seg = list()			# [我，爱，北京，天安门]这样的形式
	for pos in l_seg_pos:
		if len(pos) > 1:	
			seg.append(sent[pos[0]:pos[-1]+1])
		else:			# 此时，特意防止尾部单独出现 'M','B'等'非正常'状态
			seg.append(sent[pos[0]])


	return seg
			




		

