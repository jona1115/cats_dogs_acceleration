#### This Tutorial will guide you on how to set up the DPU IP, and Petalinux system for development, including some important troubleshooting tips.

Tested and worked with:
- Petalinux v2022.2
- Kria's 2022.2 bsp
- Vitis-AI 3.0's TRD
- Xilinx Kria KV260 Board
- Vivado v2023.1

<br>

> First two parts of this tutorial are based on [this Hackster's Tutorial](https://www.hackster.io/shreyasnr/kv260-dpu-trd-petalinux-2022-1-vivado-flow-000c0b)

***
# DPU in Vivado
Note: If you wish to skip this part, download the generated xsa file for the next step, it is with this README, a file called `top_wrapper.xsa`.
1. Download the DPU TRD (To the best of my knowledge TRD means it is an example project) [here](https://github.com/Xilinx/Vitis-AI/tree/3.0/dpu)
2. Follow the tutorial (step 1) and edit the following files      
    Edit trd_prj.tcl located at D:\SampleProjects\Vivado\DPU_TRD\DPUCZDX8G\prj\Vivado\scripts\trd_prj.tcl       
    ```
    dict set dict_prj dict_sys prj_name                  {KV260}
    dict set dict_prj dict_sys prj_part                  {xck26-sfvc784-2LV-c}
    dict set dict_prj dict_sys prj_board                 {KV260}
    dict set dict_prj dict_param  DPU_CLK_MHz            {275}
    dict set dict_prj dict_param  DPU_NUM                {1}
    dict set dict_prj dict_param  DPU_SFM_NUM            {0}
    dict set dict_prj dict_param  DPU_URAM_PER_DPU       {50}
    ```
    Edit trd_bd.tcl located at      D:\SampleProjects\Vivado\DPU_TRD\DPUCZDX8G\prj\Vivado\scripts\base\trd_bd.tcl       
    ```
    dict set dict_prj dict_param HP_CLK_MHz              {274}
    ```
    Then source the tcl in Vivado terminal: source path/to/trd_prj.tcl
3. Generate Bitstream

***
# Petalinux (Base build)
> Important: If you never build Petalinux before, there are several dependencies you need: [CMake and libidn11](https://support.xilinx.com/s/question/0D54U00007wTNEoSAO/problem-running-tcl-command-swrfdcv111generate-failed-to-generate-cmake-files-linux?language=en_US)
1. Follow steps 2.4-2.11, summary:  
    1. `petalinux-create -t project -s <location-of-bsp-file>.bsp [--name <project name>]  ` 
    2. `cd` into the folder `petalinux-create` made.
    3. `petalinux-config --get-hw-description <location-of-xsa-file>`
    4. `petalinux-config -c kernel`
        ```
        Device Drivers -->
        Misc devices -->
        <*> Xilinux Deep learning Processing Unit (DPU) Driver
        ```
    5. Copy stuff is in the TRD's project's /prj/Vivado/sw/meta-vitis (There should be four folders):   
        `recipes-apps, recipes-core, recipes-kernel, recipes-vitis-ai`    
        copy them into petalinux project's `project-spec/meta-user` folder, replace existing file
    6. Add to <your_petalinux_project_dir>/project-spec/meta-user/conf/user-rootfsconfig:
        ```
        CONFIG_vitis-ai-library
        CONFIG_vitis-ai-library-dev
        CONFIG_vitis-ai-library-dbg
        ```
    7. Add these to petalinuxbsp.conf:  
        ```
        IMAGE_INSTALL:append = " vitis-ai-library "     
        IMAGE_INSTALL:append = " vitis-ai-library-dev "     
        #IMAGE_INSTALL:append = " dpu-sw-optimize "     
        IMAGE_INSTALL:append = " resnet50 "     
        ```
        Note: Idk what dpu-sw-optimize is so I skipped it       
    8. Run `petalinux-config -c rootfs`
        Select the required packages, Don't select vitis-ai-library-dbg.
    9. Build (took me 151 minutes): petalinux-build    
    10. Package: `petalinux-package --wic --images-dir images/linux/ --bootfiles "ramdisk.cpio.gz.u-boot,boot.scr,Image,system.dtb,system-zynqmp-sck-kv-g-revB.dtb" --disk-name "mmcblk1" --wic-extra-args "-c gzip"`
2. Burn it (use [Balena Etcher](https://etcher.balena.io/)) onto an SD card, and you should be good to go!  
<br>

> Note: I skipped step 5 as IDK what that is doing  
> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; I will probably regret this later :-/

***
# More
- Now that we have that (a bootable OS!), it is kinda barebone, lets add gcc, g++, open-ssh, kernel tracers, etc.

### openssh
Now this is important for easy GitHub push/pull.
1. Run `petalinux-config -c rootfs`.
2. Go into `Image Features` and deselect the dropbear version and select the openssh option. This will introduce some issues, follow these fix:
    1. [Fix for build error because something requires dropbear](https://support.xilinx.com/s/question/0D54U00005WcRhqSAF/petalinux-20221-building-sdk-package-dropbear-conflicting-requests?language=en_US). Summary:  
    Look for the file “packagegroup-petalinux-som.bb” in the yocto layers (petalinux_prj_dir/components/yocto/layers/meta-som/recipes-core/packagegroups). Replace `packagegroup-core-ssh-dropbear` by `packagegroup-core-ssh-openssh`.
    2. Deselect `Filesystem Packages -> misc -> package-group-core-ssh-dropbear` [as mentioned here](https://support.xilinx.com/s/question/0D52E00006sl3paSAA/petalinux-cannot-use-openssh-instead-of-dropbear?language=en_US). Summary:  
        1. `Filesystem Packages -> misc -> package-group-core-ssh-dropbear`
        2. Deselect `packagegroup-core-ssh-dropbear`
3. Search for "openssh" and option (1), or other options, of the path: `Filesystem Packages -> console -> network -> openssh`
4. Go into that option, there should be a bunch of openssh stuff, e.g. `openssh`, `openssh-ssh`, `openssh-sftp`, ..., `openssh-scp` I just selected all of them.

### gcc, g++
1. [Followed this](https://support.xilinx.com/s/question/0D52E00006iHvSBSA0/adding-gcc-and-g-to-petalinux-project-revisited-2018?language=en_US), summary:
    1. `petalinux-config -c rootfs`
    2. Turned on `Filesystem Packages -> misc -> gcc-runtime` 
2. Also: `misc/packagegroup-core-buildessential`

### opencv, libmetal
1. Just search (press `/`) for opencv and go trigger happy on all opencv related options.
2. Do the same for libmetal

> Tip: When you search, options will have numbers next to them "(1)", "(2)", etc. To select them, type the number and you will teleport to that part of the menu.

### Kernel Tracers
This is for using vaitrace
1. Follow: https://docs.amd.com/r/en-US/ug1414-vitis-ai/Installing-the-Vitis-AI-Profiler

### Other important(-ish) stuff
"ish" because these are probably stuff you can dnf install on the board later.
- **pkgconfig**: Search for pkgconfig and select all of them.
- (I didn't end up doing this because it was generating an error when packing) **Python stuff**: Go to `Filesystem Packages -> misc -> python3...` and I just selected all of them. (I also have a 128GB SD card, so I can splurge)
- **Git**: Search for git and select all of them.
- This is more of a quality of life thing, to make the bash colorful, add this line to the back of `~/.bashrc`:  
  `PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '`
- Tensorflow Lite C API: Checkout my [tflite c on Kria guide](https://github.com/jona1115/cats_dogs_acceleration/blob/main/documentations/tflite_c_on_kria/README.md).
- Tensorflow Lite Python Runtime: Checkout my [tflite python on Kria guide](https://github.com/jona1115/cats_dogs_acceleration/blob/main/documentations/tflite_python_on_kira/README.md).

***
# Troubleshooting
- When adding stuff, I got an error while building:  
    `ERROR: Task (.../petalinux-image-minimal.bb:do_image_cpio) failed with exit code '1'`  
    I believe is some kind of file system type issue when trying to include big stuff like OpenCV into the project. To fix this, I followed [this answer by dark-dante](https://support.xilinx.com/s/question/0D54U00006OjQLCSA3/cannot-build-petalinux-due-to-componentsyoctolayersmetapetalinuxrecipescoreimagespetalinuximageminimalbb?language=en_US), summary:  
    1. Change the root filesystem type:  
        Run `petalinux-config` -> `Image Packaging Configuration` -> Change `Root filesystem type` from `INITRAMFS` to `EXT4 (SD/eMMC/SATA/USB)`
    2. Add these lines to `<plnx-proj-root>/project-spec/meta-user/conf/petalinuxbsp.conf`:  
    ```
    IMAGE_FSTYPES:remove = "cpio cpio.gz cpio.bz2 cpio.xz cpio.lzma cpio.lz4 cpio.gz.u-boot"
    IMAGE_FSTYPES_DEBUGFS:remove = "cpio cpio.gz cpio.bz2 cpio.xz cpio.lzma cpio.lz4 cpio.gz.u-boot"
    ```
- When booted Petalinux, for some reason, they will only allocate necessary space for the second partition. Idk if this is Balena Etcher's fault or Petalinux's tools, but it is what it is. This will cause **errors when trying to write to the filesystem** when booted (like when you `dnf update`), and it will give you an error that looks like:  
`... [Failure writing output to destination] ...`  
To fix this, in Petalinux OS (i.e. not on your host machine where you build Petalinux but on the BOOTED Petalinux OS), do these:  
    1. Check disk space: `df -h` (You want to see a size that is big, but you won't thats why it errored out)
    2. Do `lsblk`, and find the name of the 2nd partition (mine is called `/dev/mmcblk1`)
    3. Run `sudo parted /dev/mmcblk1`  
        1. Type: `resizepart 2 100%` then `yes`
        2. Type: `quit`  
        (At this point if you `lsblk` again you should see the 2nd partition size become bigger)
    4. Now, you want to resize the filesystem: `sudo resize2fs /dev/mmcblk1p2`  
    5. Verify using `df -h` that `/dev/mmcblk1p2` is now bigger in size. Also, try writting to it again (`dnf update`), it shouldn't errored out anymore.
- In Petalinux OS, one thing I find annoying is that **pip is not in PATH**, and you have to use pip3, yes, I am too lazy to type one extra character, so, to add it to PATH:  
    1. `vi ~/.bashrc`
    2. Add this line: `export PATH=$PATH:/home/petalinux/.local/bin`
    3. `source ~/.bashrc`
