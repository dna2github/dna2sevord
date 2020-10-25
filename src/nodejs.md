### How `Math.random()` works?

```
/deps/v8/src/base/utils/random-number-generator.h
119   static inline void XorShift128(uint64_t* state0, uint64_t* state1) {

/deps/v8/src/numbers/math-random.cc
62     base::RandomNumberGenerator::XorShift128(&state.s0, &state.s1);
```
