# Yocto Fun

While this project is mainly run on Petalinux, which is a wrapper of Yocto, I find Yocto facinating and this side side project's goal is to understand how to use it.

> This is based on [kickstartembedded.com](https://kickstartembedded.com/2021/12/21/yocto-part-3-build-run-your-first-ever-image/)'s tutorial. Checkout the tutorial if you want to understand what is going on, this README will just be the summary of steps.

### Building the Base x86-64 Project
1. Clone the Yocto repo to get started: `git clone git://git.yoctoproject.org/poky` (Poky is Yocto's base layer), or using HTTPS: `git clone https://git.yoctoproject.org/poky`
2. cd into it: `cd poky` and checkout the [version of Yocto](https://wiki.yoctoproject.org/wiki/Releases) you want. For me, I selected Scarthgap as that is the most relevant at the time of this: `git checkout -b Scarthgap origin/scarthgap`
3. Source the environment and create a build/ directory: `source oe-init-build-env build-x86` (You should be `cd`ed into the build directory).
4. Build! (~2Hr23Min for me): `bitbake core-image-sato`
5. Run the emulator (Unless you have a x86 board you will like to flash): `runqemu qemux86-64 nographic`