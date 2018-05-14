# https://www.tensorflow.org/install/install_sources

git clone https://github.com/tensorflow/tensorflow
cd tensorflow
./configure
# if cuda, plus --config=cuda
bazel build --config=opt //tensorflow/tools/pip_package:build_pip_package
bazel-bin/tensorflow/tools/pip_package/build_pip_package /path/to/target
pip install /path/to/target/tensorflow-*.whl

# import tensorflow as tf
# hello = tf.constant('Hello, TensorFlow!')
# sess = tf.Session()
# print(sess.run(hello))


# https://www.tensorflow.org/extend/adding_an_op

cat zero_out.cc <<EOF
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"

using namespace tensorflow;

REGISTER_OP("ZeroOut")
    .Input("to_zero: int32")
    .Output("zeroed: int32")
    .SetShapeFn([](::tensorflow::shape_inference::InferenceContext* c) {
      c->set_output(0, c->input(0));
      return Status::OK();
    });


#include "tensorflow/core/framework/op_kernel.h"

using namespace tensorflow;

class ZeroOutOp : public OpKernel {
 public:
  explicit ZeroOutOp(OpKernelConstruction* context) : OpKernel(context) {}

  void Compute(OpKernelContext* context) override {
    // Grab the input tensor
    const Tensor& input_tensor = context->input(0);
    auto input = input_tensor.flat<int32>();

    // Create an output tensor
    Tensor* output_tensor = NULL;
    OP_REQUIRES_OK(context, context->allocate_output(0, input_tensor.shape(),
                                                     &output_tensor));
    auto output_flat = output_tensor->flat<int32>();

    // Set all but the first element of the output tensor to 0.
    const int N = input.size();
    for (int i = 1; i < N; i++) {
      output_flat(i) = 0;
    }

    // Preserve the first input value if possible.
    if (N > 0) output_flat(0) = input(0);
  }
};

REGISTER_KERNEL_BUILDER(Name("ZeroOut").Device(DEVICE_CPU), ZeroOutOp);
EOF

g++ -std=c++11 -shared zero_out.cc -o zero_out.so -fPIC -O2 \
    -I/path/to/python/site-packages/tensorflow/include \
    -I/path/to/python/site-packages/tensorflow/include/external/nsync/public \
    -L/path/to/python/site-packages/tensorflow -ltensorflow_framework


# import tensorflow as tf
# zero_out_module = tf.load_op_library('./zero_out.so')
# with tf.Session(''):
#   zero_out_module.zero_out([[1, 2], [3, 4]]).eval()


# add build file at tensorflow/core/user_ops (tensorflow source code)
# load("//tensorflow:tensorflow.bzl", "tf_custom_op_library")
#   tf_custom_op_library(
#       name = "zero_out.so",
#       srcs = ["zero_out.cc"],
#   )
# bazel build --config opt //tensorflow/core/user_ops:zero_out.so

