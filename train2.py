# -*- coding: utf-8 -*-
#/usr/bin/python2

from __future__ import print_function

from hyperparams import Hyperparams as hp
from tqdm import tqdm

import tensorflow as tf
from models import Model


def main():
    model = Model(mode="train2")

    # Load trained model from train1
    load_model_variables()

    # Loss
    loss_op = model.loss_net2()

    # Training Scheme
    global_step = tf.Variable(0, name='global_step', trainable=False)
    optimizer = tf.train.AdamOptimizer(learning_rate=hp.lr)
    var_list = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'net/net2')
    train_op = optimizer.minimize(loss_op, global_step=global_step, var_list=var_list)

    # Summary
    summ_op = summaries(loss_op)

    saver = tf.train.Saver()

    session_conf = tf.ConfigProto(
        device_count={'CPU': 1, 'GPU': 1},
        gpu_options=tf.GPUOptions(
            allow_growth=True,
            per_process_gpu_memory_fraction=0.25
        ),
    )
    # Training
    with tf.Session(config=session_conf) as sess:
        writer = tf.summary.FileWriter('logdir/train2', sess.graph)

        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)

        sess.run(tf.global_variables_initializer())

        for epoch in range(1, hp.num_epochs + 1):
            for step in tqdm(range(model.num_batch), total=model.num_batch, ncols=70, leave=False, unit='b'):
                sess.run(train_op)

            # Write checkpoint files at every epoch
            summ, gs = sess.run([summ_op, global_step])
            writer.add_summary(sess.run(summ_op), global_step=gs)

            saver.save(sess, 'logdir/train2/step_%d' % gs)

        coord.request_stop()
        coord.join(threads)


def summaries(loss):
    for v in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'net/net2'):
        tf.summary.histogram(v.name, v)
    tf.summary.scalar('net2/train/loss', loss)
    return tf.summary.merge_all()


def load_model_variables():
    with tf.Session() as sess:
        ckpt = tf.train.latest_checkpoint('logdir/train1')
        if ckpt:
            tf.train.Saver().restore(sess, ckpt)
            print('Model loaded.')


if __name__ == '__main__':
    main()
    print("Done")