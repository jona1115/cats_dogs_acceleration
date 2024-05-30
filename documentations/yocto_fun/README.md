# Yocto Fun

While this project is mainly run on Petalinux, which is a wrapper of Yocto, I find Yocto facinating and this side side project's goal is to understand how to use it.

> This is based on [kickstartembedded.com](https://kickstartembedded.com/2021/12/21/yocto-part-3-build-run-your-first-ever-image/)'s tutorial.

### Building the Base Project
1. Clone the Yocto repo to get started: `git clone git://git.yoctoproject.org/poky` (Poky is Yocto's base layer), or using HTTPS: `git clone https://git.yoctoproject.org/poky`
2. cd into it: `cd poky` and checkout the [version of Yocto](https://wiki.yoctoproject.org/wiki/Releases) you want. For me, I selected Scarthgap as that is the most relevant at the time of this: `git checkout -b Scarthgap origin/scarthgap`
3. 