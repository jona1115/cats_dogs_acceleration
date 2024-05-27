#### In this tutorial, I will guide you on how to compile Tensorflow Lite (for C) on the Kria board, this tutorial probably works with other Xilinx boards.

Tested and worked with:
- Xilinx Kria KV260 Board
- gcc version 11.2.0 (GCC)
- Tensorflow Lite 2.6.0

> This tutorial is based on [this tutorial](https://qengineering.eu/install-tensorflow-2-lite-on-raspberry-64-os.html), with some modifications to work on Xilinx's boards

<br>

Summary (step 7 is different from the original tutorial):
1. This should already be installed but just in case: `sudo dnf install cmake curl`
2. Download the tflite source: `wget -O tensorflow.zip https://github.com/tensorflow/tensorflow/archive/v2.6.0.zip`
3. Unzip: `unzip tensorflow.zip`
4. Rename folder: `mv tensorflow-2.6.0 tensorflow`
5. Cd into the new foler: `cd tensorflow`
6. Get dependencies: `./tensorflow/lite/tools/make/download_dependencies.sh`
7. (Important) Because the gcc target is different on Xilinx boards, if you followed the original tutorial you will realize that they had `--target=aarch64-linux-gnu` but if you run `gcc -v` on the Kria you will get `--target=aarch64-xilinx-linux`, so, you need to change the build script a bit:  
    1. Open the script: `vi tensorflow/lite/tools/make/build_aarch64_lib.sh`
    2. In the last line (`make ...`), change the `TARGET` from `TARGET=aarch64` to `Target=aarch64-xilinx` (basically append a `-xilinx`).
8. Run the script: `./tensorflow/lite/tools/make/build_aarch64_lib.sh` (Takes a while ~15 min)
9. Now we need to build this flatbuffer thingy:  
    1. Go to the folder: `cd ~/tensorflow/tensorflow/lite/tools/make/downloads`
    2. Remove the problematic flatbuffer: `rm -rf flatbuffers`
    3. Get the non-problematic version: `git clone -b v2.0.0 --depth=1 --recursive https://github.com/google/flatbuffers.git`
    4. `cd flatbuffers`
    5. `mkdir build`
    6. `cd build`
    7. `cmake ..`
    8. `make -j4`
    9. `sudo make install`
    10. `sudo ldconfig`
10. When done you should have:  
    1. These two files in `tensorflow/lite/tools/make/gen/aarch64-xilinx_aarch64/lib`: `benchmark-lib.a`  `libtensorflow-lite.a`
    2. A bunch of stuff in `tensorflow/lite` (See the slideshow in the original tutorial for how the stuff looks like, but it is a bunch of `.cc`, `.h` files and a couple of folders)
    3. There will be a `libflatbuffers.a` in `/usr/local/lib64`
    4. There will be a `flatbuffers` folder in `/usr/local/include`
11. At this point you are free to delete the zip from step 2.
