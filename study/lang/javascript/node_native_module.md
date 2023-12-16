npm install node-gyp

node-gyp configure
node-gyp build

```
# binding.gyp ---------
{
  "targets": [
    {
      "target_name": "binding",
      "sources": [ "binding.cc" ]
    }
  ]
}

# binding.cc ----------
#include <node.h>
#include <v8.h>

using namespace v8;

void Method(const FunctionCallbackInfo<Value>& args) {
  Isolate* isolate = Isolate::GetCurrent();
  HandleScope scope(isolate);
  args.GetReturnValue().Set(String::NewFromUtf8(isolate, "world"));
}

void init(Handle<Object> target) {
  NODE_SET_METHOD(target, "hello", Method);
}

NODE_MODULE(binding, init);


# test.js -------------
var binding = require('./build/Release/binding');
```

ref: https://github.com/nodejs/node-v0.x-archive/tree/master/test/addons
