from evaluation_metrics.metrics import Abstract_Metric
import configuration.citations as citations
import configuration.defaults as defaults
import itertools
import numpy as np
from evaluation_metrics.rbo import rbo


class Topic_diversity(Abstract_Metric):
    def __init__(self, metric_parameters=defaults.em_topic_diversity.copy()):
        """
        Initialize metric

        Parameters
        ----------
        metric_parameters : dictionary with key 'topk'
                            topk: top k words on which the topic diversity
                            will be computed
        """
        self.topk = metric_parameters["topk"]

    def info(self):
        return {
            "citation": citations.em_topic_diversity,
            "name": "Topic diversity"
        }

    def score(self, model_output):
        """
        Retrieves the score of the metric

        Parameters
        ----------
        model_output : dictionary, output of the model 
                       key 'topics' required.

        Returns
        -------
        td : score
        """
        self.topics = model_output["topics"]
        if self.topk > len(self.topics[0]):
            raise Exception('Words in topics are less than '+str(self.topk))
        else:
            unique_words = set()
            for topic in self.topics:
                unique_words = unique_words.union(set(topic[:self.topk]))
            td = len(unique_words) / (self.topk * len(self.topics))
            return td


class InvertedRBO(Abstract_Metric):
    def __init__(self):
        super().__init__()

    def score(self, model_output, topk = 10, weight=0.9):
        '''
        :param weight: p (float), default 1.0: Weight of each agreement at depth d:
        p**(d-1). When set to 1.0, there is no weight, the rbo returns to average overlap.
        :param topic_list: a list of lists of words
        :return: rank_biased_overlap over the topics
        '''
        self.topics = model_output['topics']
        if topk > len(self.topics[0]):
            raise Exception('Words in topics are less than topk')
        else:
            collect = []
            for list1, list2 in itertools.combinations(self.topics, 2):
                word2index = self.get_word2index(list1, list2)
                indexed_list1 = [word2index[word] for word in list1]
                indexed_list2 = [word2index[word] for word in list2]
                rbo_val = rbo(indexed_list1[:topk], indexed_list2[:topk], p=weight)[2]
                collect.append(rbo_val)
            return 1 - np.mean(collect)

    def get_word2index(self, list1, list2):
        words = set(list1)
        words = words.union(set(list2))
        word2index = {w: i for i, w in enumerate(words)}
        return word2index

