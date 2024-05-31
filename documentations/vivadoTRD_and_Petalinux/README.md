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

### Java
> Details on adding layers and recipes can be found [here](https://docs.amd.com/r/2022.2-English/ug1144-petalinux-tools-reference-guide/Adding-Layers). Below I will show how to add specifically Java.
1. Find somewhere you want the layer to go, for Petalinux, usually, it goes in `<plnc project>/project-spec/meta-user`, so cd there, and run: `git clone https://github.com/meta-java/meta-java.git -b honister` (honister is the Yocto version Petalinux v2022.2 comes with, and all meta- stuff needs to match that).
2. Run `petalinux-config` and go to Yocto Settings --> User Layers -> () User Layer x --> Type in the location of the meta-java folder, e.g. `${PROOT}/project-spec/meta-user/meta-java`. Save.
3. Figure out what the recipes are called for meta-java, you can do a find (in project root run: `find . -name "openjdk*.bb"`). Recipes all end with `.bb` so it makes searching easy. Also, the recipes' naming convention is `recipename_version.bb`. Once you find them, open up `<plnx-proj-root>/project-spec/meta-user/conf/user-rootfsconfig`, and add "CONFIG_" += the recipe name to the file, for example,
    My search result was:
    ```
    jonathan@ubuntu4haml:~/cats_and_dogs/kria_cats_and_dogs $ find . -name "openjdk*.bb"
    ./project-spec/meta-user/meta-catsdogs/meta-java/recipes-core/openjdk/openjdk-8_272.bb
    ./project-spec/meta-user/meta-catsdogs/meta-java/recipes-core/openjdk/openjdk-7_99b00-2.6.5.bb
    ./project-spec/meta-user/meta-catsdogs/meta-java/recipes-core/openjdk/openjdk-8-native_272.bb
    ./project-spec/meta-user/meta-catsdogs/meta-java/recipes-images/images/openjdk-8-test-image.bb
    ./project-spec/meta-user/meta-catsdogs/meta-java/recipes-images/images/openjdk-7-test-image.bb
    ```
    The ones in the recipes-images folder isn't actually recipes (to the best of my knowledge). We are more concerned with the ones in recipes-core, so, we add these to the user-rootfsconfig file:
    ```
    CONFIG_openjdk-8
    CONFIG_openjdk-7
    CONFIG_openjdk-8-native
    CONFIG_openjre-8
    ```
4. Go to `petalinux-config -c rootfs` --> user packages --> and select the ones you want. In our case, we select only the openjdk-8. Note: Notice how the name of openjdk-7 is a bit weird, don't ever select that, that is probably a bug on the meta-java end.
5. There is one more bug on the meta-java end, as per [this post](https://github.com/meta-java/meta-java/issues/10), the URL in the recipe is wrong. Hence, if you `petalinux-build` you will get a do_fetch error. To fix it, cd into `/project-spec/meta-user/meta-catsdogs/meta-java/recipes-core/xerces-j`, edit the file `xerces-j_2.11.0.bb`, in the URI part comment out the original line and change it to:
    ```
    # SRC_URI = "http://archive.apache.org/dist/xerces/j/Xerces-J-src.${PV}.tar.gz"
    SRC_URI = "http://ftp.deu.edu.tr/pub/Infosystem/Apache/xerces/j/source/Xerces-J-src.${PV}.tar.gz"
    ```
6. Now, build.

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
- If you add too much stuff, the default 2nd partition might not be big enough because it is, by default, limited to 4G. This will cause packagging issue when running `petalinux-package --wic ...`. To increase the second partition size for the wic file, in to `<plnx project>/build/rooft.wks`, change `part / --source rootfs --ondisk mmcblk1 --fstype=ext4 --label root --align 4 --fixed-size 4G` to `part / --source rootfs --ondisk mmcblk1 --fstype=ext4 --label root --align 4 --fixed-size 10G` (4G to 10G for at the very last argument). Now you can add more stuff and package using wic. See more [here](https://docs.amd.com/r/2022.2-English/ug1144-petalinux-tools-reference-guide/petalinux-package-wic-Command-Examples).
