from __future__ import division
from __future__ import print_function

from torch.utils.data import Dataset
import numpy as np
import scipy.io
import os
import torch
import pickle
import sklearn.preprocessing
from config import LOCS
from config import data_transform_path

import utils

import pdb
import pandas as pd
LOCS_JIGSAWS = LOCS
# column index
# For: raw feature
class RawFeatureDataset(Dataset):
    def __init__(self, dataset_name,
                 trail_list, feature_type,
                sample_rate=1, sample_aug=True,
                 normalization=None):

                 # n_layers = len(model_params['encoder_params']['layer_sizes']) = encoder level
        super(RawFeatureDataset, self).__init__()

        self.trail_list = trail_list

        if feature_type not in ['visual', 'sensor']:    # 运动学特征通过传感器测量而来
            raise Exception('Invalid Feature Type')

        self.sample_rate = sample_rate
        self.sample_aug = sample_aug
        self.encode_level = 3
        self.all_feature = []
        self.all_gesture = []
        self.marks = []

        start_index = 0
        for idx in range(len(self.trail_list)):

            trail_name = self.trail_list[idx]
            #print(trail_name)
            #breakpoint()

            if dataset_name in ["JIGSAWS", "PT", "All-5a","All-5b", "S", "NP", "KT", "PoaP", "PaS", "SNP", "PTPaS", "All", "ROSMA"]:
                data_file = trail_name

                #读取数据标签（标签编码后）
                with open(data_transform_path, 'rb') as f:
                    label_transform =  pickle.load(f)     # 标签编码转换器

                #print(data_file)

                # need to add the new dataset name
            elif dataset_name == 'GTEA':
                data_file = trail_name
            else:
                raise Exception('Invalid Dataset Name!')

            trail_data = pd.read_csv(data_file, sep=',')
            #print(trail_data)

            # 33 = numb of cols in file
            #colv = [i for i in range(1,33)]
            #colv.append('MP')
            #trail_data.columns=colv

            #scipy.io.loadmat(data_file)

            if feature_type == 'visual':
                trail_feature = trail_data['A']
            elif feature_type == 'sensor':
                trail_feature = trail_data[LOCS] #trail_data['S'].T

            #breakpoint()

            trail_gesture_ = trail_data['Y']
            ty = [type(t) for t in trail_gesture_]

            # np.where(np.array(ty) != str)-----([])  元组里面有一个元素，该元素为列表
            index_to_remove = np.where(np.array(ty)!=str)[0].tolist()    # 原始标签为文本标签

            trail_gesture_ = np.array(trail_gesture_)
            trail_gesture_ = np.delete(trail_gesture_, index_to_remove)

            trail_feature = np.array(trail_feature)
            trail_feature = np.delete(trail_feature, index_to_remove, axis=0) # 将非字符串的文本标签对应的特征删除

            trail_gesture=label_transform.transform(trail_gesture_)           # 文本标签转化为编码的数值标签

            trail_len = len(trail_gesture)
            #breakpoint()
            self.all_feature.append(trail_feature)    # [np.array([[]]),np.array([[]]),...]
            self.all_gesture.append(trail_gesture)    # [np.array([],np.array([]),...]

            self.marks.append([start_index, start_index + trail_len])    # 二维list,[[]]标记每个文件的标签开始帧到标签结束帧
            start_index += trail_len

        self.all_feature = np.concatenate(self.all_feature)    # 二维向量---多个文件的特征矩阵组成
        self.all_gesture = np.concatenate(self.all_gesture)    # 列向量--多个文件的标签构成
        print("All_gesture", self.all_gesture)
        print("all_feature shape: {},all gesture shape:{}".format(self.all_feature.shape, self.all_gesture.shape))

        # Normalization
        # can't norm a string, so only norm data
        if normalization is not None:

            if normalization[0] is None:

                #print(self.all_feature[:, 0:-1])
                self.feature_means = self.all_feature.mean(0)
            else:

                self.feature_means = normalization[0]

            if normalization[1] is None:
                #print(self.all_feature[:,0:-1])
                #myArray = self.all_feature[:,0:-1].astype(float)
                #print(myArray.shape)
                #print(np.std(myArray, axis=0))
                #print(self.all_feature[:,0:-1].astype(float).std(0))
                self.feature_stds = self.all_feature.std(0)
            else:

                self.feature_stds = normalization[1]

            self.all_feature = self.all_feature - self.feature_means
            self.all_feature = self.all_feature / self.feature_stds
        else:

            self.feature_means = None
            self.feature_stds = None


    def __len__(self):
        if self.sample_aug:
            return len(self.trail_list) * self.sample_rate
        else:
            return len(self.trail_list)

    def __getitem__(self, idx):         # 重载运算符[] one idx corresponding to one file

        if self.sample_aug:
            trail_idx = idx // self.sample_rate    #sample_rate>1  间隔采样
            sub_idx = idx % self.sample_rate
        else:
            trail_idx = idx
            sub_idx = 0

        trail_name = self.trail_list[trail_idx]

        start = self.marks[trail_idx][0]
        end = self.marks[trail_idx][1]

        feature = self.all_feature[start:end,:]    #每个文件的特征矩阵
        gesture = self.all_gesture[start:end]      #每个文件的目标变量
        feature = feature[sub_idx::self.sample_rate]
        gesture = gesture[sub_idx::self.sample_rate]

        """扩充----------------为什么要进行扩充呢"""
        trail_len = gesture.shape[0]

        padded_len = int(np.ceil(trail_len /
                          (2**self.encode_level)))*2**self.encode_level

        mask = np.zeros([padded_len, 1])
        mask[0:trail_len] = 1

        #扩充特征矩阵
        padded_feature = np.zeros([padded_len, feature.shape[1]])    # 扩充样本数，原始特征外的特征值用0填充
        padded_feature[0:trail_len] = feature

        # 扩充标签
        padded_gesture = np.zeros([padded_len, 1])-1                 #原始标签外的标签值的标签值用-1填充

        padded_gesture[0:trail_len] = np.reshape(gesture,(len(gesture),1))
        #breakpoint()
        return {'feature': padded_feature,
                'gesture': padded_gesture,
                'mask': mask,
                'name': trail_name}

    # each file transformered to the dict {'feature':,'gesture':,'mask':,'name':,}

    def get_means(self):
        return self.feature_means

    def get_stds(self):
        return self.feature_stds
