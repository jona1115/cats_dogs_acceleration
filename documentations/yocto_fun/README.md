# Yocto Fun

While this project is mainly run on Petalinux, which is a wrapper of Yocto, I find Yocto facinating and this side side project's goal is to understand how to use it.

> This is based on [kickstartembedded.com](https://kickstartembedded.com/2021/12/21/yocto-part-3-build-run-your-first-ever-image/)'s tutorial. Checkout the tutorial if you want to understand what is going on, this README will just be the summary of steps.

### Building A Basic x86-64 Project
1. Clone the Yocto repo to get started: `git clone git://git.yoctoproject.org/poky` (Poky is Yocto's base layer), or using HTTPS: `git clone https://git.yoctoproject.org/poky`
2. cd into it: `cd poky` and checkout the [version of Yocto](https://wiki.yoctoproject.org/wiki/Releases) you want. For me, I selected Scarthgap as that is the most relevant at the time of this: `git checkout -b Scarthgap origin/scarthgap`
3. Source the environment and create a build/ directory: `source oe-init-build-env build-x86` (You should be `cd`ed into the build directory).
4. Build! (~2Hr23Min for me): `bitbake core-image-sato`
5. Run the emulator (Unless you have a x86 board you will like to flash): `runqemu qemux86-64 nographic`

### Building A Basic Rasp Pi Project
Pre-req: You did "Building A Basic x86-64 Project"
1. Create a new build dir: `source oe-init-build-env build-rpi`
2. Clone the [Open Embedded Layer](https://git.openembedded.org/meta-openembedded): `git clone https://git.openembedded.org/meta-openembedded -b scarthgap`. Note: change the `-b` value to whatever yocto version you are using.
3. Clone the meta-raspberrypi layer: `git clone https://git.yoctoproject.org/meta-raspberrypi -b scarthgap`. Note: change the `-b` value to whatever yocto version you are using.
4. To add layers (like the ones we just added in steps 2 and 3), you can either modify the `build-rpi/conf/bblayers.conf` file (NOT RECOMMENDED), or use the bb commands:  
    ```
    bitbake-layers add-layer ./meta-openembedded/meta-oe/
    bitbake-layers add-layer ./meta-openembedded/meta-python/
    bitbake-layers add-layer ./meta-openembedded/meta-networking/
    bitbake-layers add-layer ./meta-openembedded/meta-multimedia/
    bitbake-layers add-layer ./meta-raspberrypi/
    ```
5. Sanity check by either viewing the `build-rpi/conf/bblayers.conf` or running `bitbake-layers show-layers`.
6. Select the machine:  
    1. `nano build-rpi/conf/local.conf`
    2. Go to this line:  
        ```
        # This sets the default machine to be qemux86-64 if no other machine is selected:
        MACHINE ??= "qemux86-64"
        ```
        Comment out/replace `MACHINE ??= "qemux86-64"` with `MACHINE ??= "raspberrypi4"` to like so:
        ```
        # This sets the default machine to be qemux86-64 if no other machine is selected:
        #MACHINE ??= "qemux86-64"
        MACHINE ??= "raspberrypi4"
        ```
    3. Add `ENABLE_UART = "1"` to the end of this file because the tutorial said so, but I don't think is necessary if you are emulating.
7. IMPORTANT (Not in tutorial): Aparently there is some weird stuff about licensing and crap regarding rpi, anyway, follow [this link](https://meta-raspberrypi.readthedocs.io/en/latest/ipcompliance.html#linux-firmware-rpidistro) and add `LICENSE_FLAGS_ACCEPTED = "synaptics-killswitch"` to the end of `build-rpi/conf/local.conf`.
8. Build (~75Min): `cd build-rpi` and then `bitbake rpi-test-image`

### Building A Basic AARCH64 Project
> Finally, let's build a basic aarch64 project because that aligns with the parent project (Cats and Dogs on Kria) better. Let's shoot to make this bootable on the [TI SK-AM62B-P1](https://www.ti.com/tool/SK-AM62B-P1). Which has a quad-core 64-bit Arm®-Cortex®-A53 microprocessor and single-core Arm Cortex-M4F MCU

Pre-req: This tutorial is in series, so you should already did "Building A Basic x86-64 Project", and "Building A Basic Rasp Pi Project".  
1. Remove the raspberry pi layer: `bitbake-layers remove-layer ./meta-raspberrypi/`, you can run `bitbake-layers show-layers` before and after for sanity check.
2. Create new build directory: `source oe-init-build-env build-aarch64`
3. We also want to change the machine to aarch64:  
    1. When in build-aarch64/: `nano conf/local.conf`
    2. Uncomment the line `#MACHINE ?= "qemuarm64"`.
4. Add the meta-openembedded layers(?), IDK if you really need it (I will think so?), I just included them anyway, which are the commands in step 4 in the above section "Building A Basic Rasp Pi Project".
5. Build: `bitbake core-image-base` (The decision to choose core-image-base is somewhat arbitrary). Protip: To search for all files starting with "core" but exclude search in the build folders, you can run `find . -type d -name "build*" -prune -o -name "core-*" -print`
6. Run the emulator: `runqemu qemuarm64 nographic`
7. You probably will notice at this point, this is the barest of bare Linux, THERE IS NOTHING! You can't even sudo.