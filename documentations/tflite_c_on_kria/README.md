#### In this tutorial, I will guide you on compiling Tensorflow Lite (for C) on the Kria board, this tutorial probably works with other Xilinx boards.
 
Tested and worked with:
- Xilinx Kria KV260 Board
- gcc version 11.2.0 (GCC)
- [Tensorflow Lite 2.6.0 for ARM](https://github.com/jona1115/cats_dogs_acceleration/tree/main/documentations/tflite_c_on_kria#tflite-260-arm-possibly-x86-too-but-i-didnt-try)
- [Tensorflow Lite 2.16.1 for x86 Linux](https://github.com/jona1115/cats_dogs_acceleration/tree/main/documentations/tflite_c_on_kria#tflite-2160-x86-linux-incomplete)
- Tensorflow Lite 2.16.1 for ARM (Haven't try yet)

> This tutorial is based on [this tutorial](https://qengineering.eu/install-tensorflow-2-lite-on-raspberry-64-os.html), with some modifications to work on Xilinx's boards

> The current (as of 5/27/2024) TFLite version is 2.16, which you find the [download link here](https://github.com/tensorflow/tensorflow/releases/tag/v2.16.1). However, I still haven't found a good way to install it on the board.

<br>

# Cross compile TFLite 2.16.0 for ARM on Ubuntu Host
> Skip to step 3 if you don't want to compile yourself.
1. Install Bazel 6.5.0:
    1. Follow [step 1](https://bazel.build/install/ubuntu#add-dis-uri):
       ```
       sudo apt install apt-transport-https curl gnupg -y
       curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg
       sudo mv bazel-archive-keyring.gpg /usr/share/keyrings
       echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
       ```
    2. `sudo apt install bazel-6.5.0` (It should install properly, if not, do like a `sudo apt update && sudo apt full-upgrade` or something like that)
2. Follow [this to build ARM Binary](https://www.tensorflow.org/lite/guide/build_arm#c_library): `bazel build --config=elinux_aarch64 -c opt //tensorflow/lite/c:libtensorflowlite_c.so`, the resulting `.so` file should be in `bazel-bin/tensorflow/lite/libtensorflowlite.so`. Which you can then SCP to the board or something.
3. The generated `libtensorflowlite_c.so` is included with this README.

# TFLite 2.16.0 x86 Linux (incomplete)
1. Make sure you have CMake installed
2. Download the tflite source: `wget -O tensorflow.zip https://github.com/tensorflow/tensorflow/archive/refs/tags/v2.16.1.zip`
3. Unzip: `unzip tensorflow.zip`
4. Cd into the new folder: `cd tensorflow-2.16.1`
5. Follow [this guide](https://www.tensorflow.org/lite/guide/build_cmake), summary:
    1. `mkdir tflite_build`
    2. `cd tflite_build`
    3. `cmake ../tensorflow/lite`, note: If you need special builds (like debug build, etc.), go to the tutorial and check out the flags you need.
    4. Compile it: `cmake --build . -j` (I never get it to compile correctly and I just gave up and used the Bazel method instead)
6. I like to copy the `tensorflow` folder (not only its contents but the entire folder) into `/usr/local/include`. This will make linking c/c++ code later easier.
7. TODO: Incomplete need to copy .so or .a to /usr/local/lib and stuff like that.

# TFLite 2.6.0 ARM (Possibly x86 too, but I didn't try)
1. This should already be installed, but just in case: `sudo dnf install cmake curl`
2. Download the tflite source: `wget -O tensorflow.zip https://github.com/tensorflow/tensorflow/archive/v2.6.0.zip`
3. Unzip: `unzip tensorflow.zip`
4. Cd into the new folder: `cd tensorflow-2.6.0`
5. Get dependencies: `./tensorflow/lite/tools/make/download_dependencies.sh`
6. **(Important)** Because the gcc target is different on Xilinx boards if you followed the original tutorial, you will realize that they had `--target=aarch64-linux-gnu` but if you run `gcc -v` on the Kria, you will get `--target=aarch64-xilinx-linux`, so, you need to change the build script a bit:  
    1. Open the script: `vi tensorflow/lite/tools/make/build_aarch64_lib.sh`
    2. In the last line (`make ...`), change the `TARGET` from `TARGET=aarch64` to `Target=aarch64-xilinx` (basically append a `-xilinx`).
7. Run the script: `./tensorflow/lite/tools/make/build_aarch64_lib.sh` (Takes a while ~15 min)
8. Now we need to build this flatbuffer thingy:  
    1. Go to the folder: `cd ~/tensorflow-2.6.0/tensorflow/lite/tools/make/downloads`
    2. Remove the problematic flatbuffer: `rm -rf flatbuffers`
    3. Get the non-problematic version: `git clone -b v2.0.0 --depth=1 --recursive https://github.com/google/flatbuffers.git`
    4. `cd flatbuffers`
    5. `mkdir build`
    6. `cd build`
    7. `cmake ..`
    8. `make -j4`
    9. `sudo make install`
    10. `sudo ldconfig`
9. When done you should have:  
    1. These two files in `tensorflow/lite/tools/make/gen/aarch64-xilinx_aarch64/lib`: `benchmark-lib.a`  `libtensorflow-lite.a`
    2. A bunch of stuff in `tensorflow/lite` (See the slideshow in the original tutorial for how the stuff looks like, but it is a bunch of `.cc`, `.h` files and a couple of folders)
    3. There will be a `libflatbuffers.a` in `/usr/local/lib64`
    4. There will be a `flatbuffers` folder in `/usr/local/include`
10. At this point you are free to delete the zip from step 2.
11. TODO COPY BINARY FILE TO SOMEWHERE TOO I like to copy the `tensorflow` folder (not only its contents but the entire folder) into `/usr/local/include`. This will make linking c/c++ code later easier.
