# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import tensorflow as tf


class Loss:
    def __init__(self):
        pass

    def calculate_loss(self, batch, state):
        """this is the function that calculates the loss given the batch data
        
        Args:
            batch (dict): batch data after forward operation
            state(dict): current running state, has key 'mode', 'epoch' and 'step'
        
        Returns:
            loss (scalar): scalar loss for the model update
        """
        loss = None
        return loss


class SparseCategoricalCrossentropy(Loss):
    def __init__(self, true_key, pred_key, **kwargs):
        """Calculate sparse categorical cross entropy, the rest of the keyword argument will be passed to tf.losses.SparseCategoricalCrossentropy
        
        Args:
            true_key (str): the key of ground truth label in batch data
            pred_key (str): the key of predicted label in batch data
        """
        self.true_key = true_key
        self.pred_key = pred_key
        self.loss_obj = tf.losses.SparseCategoricalCrossentropy(**kwargs)

    def calculate_loss(self, batch, state):
        loss = self.loss_obj(batch[self.true_key], batch[self.pred_key])
        return loss


class MixUpLoss(Loss):
    """
    This class should be used in conjunction with MixUpBatch to perform mix-up training, which helps to reduce
    over-fitting, stabilize GAN training, and against adversarial attacks (https://arxiv.org/abs/1710.09412)
    """
    def __init__(self, loss, true_key, pred_key, lambda_key):
        """
        Args:
            loss (func): A loss object (tf.losses) which can be invoked like "loss(true_batch, pred_batch)"
            true_key (str): the key of ground truth label in batch data
            pred_key (str): the key of predicted label in batch data
            lambda_key (str): the key of the lambda value generated by MixUpBatch
        """
        super(MixUpLoss, self).__init__()
        self.loss_obj = loss
        self.true_key = true_key
        self.pred_key = pred_key
        self.lambda_key = lambda_key

    def calculate_loss(self, batch, state):
        loss1 = self.loss_obj(batch[self.true_key], batch[self.pred_key])
        if state["mode"] != "train":
            return loss1
        lam = batch[self.lambda_key]
        loss2 = self.loss_obj(tf.roll(batch[self.true_key], shift=1, axis=0), batch[self.pred_key])
        return lam * loss1 + (1.0 - lam) * loss2

