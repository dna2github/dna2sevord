# tensorboard: graph visualizer

- modify `/site-packages/tensorboard/plugins/graph/graphs_plugin.py`:

```
import os.path

...
    def __init__(...):
        ...
        self._context = context
...
    def graph_impl(...):
        graph_filename = os.path.join(self._context.logdir, run, "graph.proto")
        if os.path.isfile(graph_filename):
            with open(graph_filename, "r") as f:
                return (f.read(), "text/x-protobuf")
        ...
...
```

- write `graph.proto` in a tensorboard log dir:

```
# test --[data flow]--> test2/basic
# test2/basic --[ctrl flow]--> test

node {
   name: "test"
   op: "Test"
   input: "test2/basic"
}
node {
   name: "test2/basic"
   op: "Test"
   input: "^test"
   attr {
      key: "_output_shapes"
      value {
         list {
            shape {
            }
         }
      }
   }
}
versions {
  producer: 987
}
```

- `tensorboard -logdir log_dir`
- open `http://127.0.0.1:6006` and `graphs` tab
