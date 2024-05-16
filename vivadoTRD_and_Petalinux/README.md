This Tutorial will guide you on how to set up the DPU IP, and Petalinux system for development.

> First two parts of this tutorial is based on [this Hackster's Tutorial](https://www.hackster.io/shreyasnr/kv260-dpu-trd-petalinux-2022-1-vivado-flow-000c0b)

Tested and worked with:
- Petalinux v2022.2
- Kria's 2022.2 bsp
- Vitis-AI 3.0's TRD
- Xilinx Kria KV260 Board
- Vivado v2023.1

***
# DPU in Vivado
1. Download the DPU TRD (To the best of my knowledge TRD just means it is an example project) [here](https://github.com/Xilinx/Vitis-AI/tree/3.0/dpu)
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
# Petalinux
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
2. Burn it (just use [Balena Etcher](https://etcher.balena.io/)) onto a SD card and you should be good to go!  
<br>

> Note: I skipped step 5 as IDK what that is doing  
> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; I will probably regret this later :-/

<br>

***
# More
- Now that we have that, it is kinda barebone, lets add gcc, g++, open-ssh, kernel tracers, etc.
- I also want to use squashFS instead of the current ramFS, this is so that I can drag and drop stuff from a Windows computer
### gcc, g++
1. [Followed this](https://support.xilinx.com/s/question/0D52E00006iHvSBSA0/adding-gcc-and-g-to-petalinux-project-revisited-2018?language=en_US), summary:
    1. `petalinux-config -c rootfs`
    2. Turned on `Filesystem Packages -> misc -> gcc-runtime` 
2. Also: `misc/packagegroup-core-buildessential`

### opencv
1. Just search (press `/`) for opencv and go trigger happy on all opencv related options.

> Note: When you search, options will have numbers next to them "(1)", "(2)", etc. To select them, type the number and you will teleport to that part of the menu.

### open-ssh
Now this is important for easy GitHub push/pull.
1. Run `petalinux-config -c rootfs`
2. Go into Image Features and deselect the dropbear version and select the openssh option
3. Search for "openssh" and option (1), or other options, of the path: `Filesystem Packages -> console -> network -> openssh`
4. Go into that option, there should be a bunch of openssh stuff, e.g. `openssh`, `openssh-ssh`, `openssh-sftp`, ..., `openssh-scp` I just selected all of them.

### Kernel Tracers
This is for using vaitrace
1. Follow: https://docs.amd.com/r/en-US/ug1414-vitis-ai/Installing-the-Vitis-AI-Profiler

