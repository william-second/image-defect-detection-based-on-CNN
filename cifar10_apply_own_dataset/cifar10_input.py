#By @Kevin Xu
#kevin28520@gmail.com
#Youtube: https://www.youtube.com/channel/UCVCSn4qQXTDAtGWpWAe4Plw
#Chinese weibo: http://bit.ly/2nAmOcO

    
#The aim of this project is to use TensorFlow to process our own data.
#    - cifar10_input.py:  read in data and generate batches
#    - cifar10.py: build the model architecture, train, evaluate


# I used Ubuntu with Python 3.5, TensorFlow 1.0*, other OS should also be good.
# I didn't use data argumentation, I spent less than 30 mins with 10K steps.


# data: cifar10 binary version
# https://www.cs.toronto.edu/~kriz/cifar.html
# data size: ~184M

# How to run?
# 0. you need to change the data directory
# 1. run cifar10.py
# 2. call train() in the console to train the model
# 3. call evaluate() in the console to test on the test data

# Note: 
# it is suggested to restart your kenel to train the model multiple times 
# (in order to clear all the variables in the memory)
# Otherwise errors may occur: conv1/weights/biases already exist......

#%%

import tensorflow as tf
import numpy as np
import os

#%% Reading data

def read_cifar10(data_dir, is_train, batch_size, shuffle):
    """Read cifar10_apply_own_dataset
    Args:
        data_dir: the directory of cifar10_apply_own_dataset
        is_train: boolen  true--->read traindata
        batch_size:
        shuffle:       
    Returns:
        label: 1D tensor, tf.int32
        image: 4D tensor, [batch_size, height, width, 3], tf.float32
    """
    img_width = 32
    img_height = 32
    img_depth = 3
    label_bytes = 1
    image_bytes = img_width*img_height*img_depth
    
    
    with tf.name_scope('input'):
        
        if is_train:
            #查找data_dir目录下的data_batch_%d.bin格式的文件pathname
            filenames = [os.path.join(data_dir, 'data_batch_%d.bin' %ii)
                                        for ii in np.arange(1, 6)]
        else:
            filenames = [os.path.join(data_dir, 'test_batch.bin')]

        #产生队列，image和label都在一个二进制文件中string_input_producer
        filename_queue = tf.train.string_input_producer(filenames)
        reader = tf.FixedLengthRecordReader(label_bytes + image_bytes)
        key, value = reader.read(filename_queue)#读取队列
        record_bytes = tf.decode_raw(value, tf.uint8)#解码
        label = tf.slice(record_bytes, [0], [label_bytes])   #切除第一个元素
        label = tf.cast(label, tf.int32)#转换格式label
        
        image_raw = tf.slice(record_bytes, [label_bytes], [image_bytes])     
        image_raw = tf.reshape(image_raw, [img_depth, img_height, img_width])     
        image = tf.transpose(image_raw, (1,2,0)) # convert from D/H/W to H/W/D       
        image = tf.cast(image, tf.float32)#转换格式image

     
#        # data argumentation 特征工程，数据增强

#        image = tf.random_crop(image, [24, 24, 3])# randomly crop the image size to 24 x 24
#        image = tf.image.random_flip_left_right(image)
#        image = tf.image.random_brightness(image, max_delta=63)
#        image = tf.image.random_contrast(image,lower=0.2,upper=1.8)
        #输入到神经网络的数据0-255需要做标准化，范围需要标准化为0-1之间，或者是-1 - 1之间
        image = tf.image.per_image_standardization(image) #substract off the mean and divide by the variance

        if shuffle:
            images, label_batch = tf.train.shuffle_batch(
                                    [image, label], 
                                    batch_size = batch_size,
                                    num_threads= 16,
                                    capacity = 2000,
                                    min_after_dequeue = 1500)#每一次从队列中取走数据之后，队列中还剩下
        else:
            images, label_batch = tf.train.batch(
                                    [image, label],
                                    batch_size = batch_size,
                                    num_threads = 16,
                                    capacity= 2000)
#        return images, tf.reshape(label_batch, [batch_size])
## 需要ONE-HOT encoding     #因为在损失层用到了softmax_cross_entropy_with_logits
        n_classes = 10
        label_batch = tf.one_hot(label_batch, depth= n_classes)
        return images, tf.reshape(label_batch, [batch_size, n_classes])
    




#%%   TEST
# To test the generated batches of images
# When training the model, DO comment the following codes
import matplotlib.pyplot as plt

data_dir = './data/cifar-10-batches-bin/'
BATCH_SIZE = 10
image_batch, label_batch = read_cifar10(data_dir,
                                       is_train=True,
                                       batch_size=BATCH_SIZE,
                                       shuffle=False)  # 不打乱顺序

with tf.Session() as sess:
   i = 0
   coord = tf.train.Coordinator()
   threads = tf.train.start_queue_runners(coord=coord)

   try:
       while not coord.should_stop() and i<1:

           img, label = sess.run([image_batch, label_batch])
           # print("label: %d" %(label[0]))#有问题
           # just test one batch
           for j in np.arange(BATCH_SIZE):
               print("label: ", label[j])
               # print("j: ", j)
               plt.imshow(img[j,:,:,:])  #做了标准化之后的图片，像素值是0-1之间
               plt.show()
           i+=1

   except tf.errors.OutOfRangeError:
       print('done!')
   finally:
       coord.request_stop()
   coord.join(threads)



#%%
    
    
    
